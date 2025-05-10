import os
import pandas as pd
import numpy as np
from config import Paths, RUN_MODE, SENSOR_NAME, SELECTED_YEARS, OUTPUT_SIMULATED_DF_PATH
import fluence_simulation_lib

KB = 8.617333262145e-5
T_REF = 294.15
E_I_STAR = 1.30
ALPHA_I = 1.23e-17
ALPHA_0_STAR = 6.74e-17
BETA = 3.29e-18
E_I = 1.11
K_0I = 1.2e13
T_0 = 1.0
V = 0.805
E_EFF = 1.21

class Parameters:
    def __init__(self):
        self.E_I_star = E_I_STAR
        self.kb = KB
        self.T_ref = T_REF
        self.k_0I = K_0I
        self.E_I = E_I
        self.alpha_I = ALPHA_I
        self.alpha_0_star = ALPHA_0_STAR
        self.beta = BETA
        self.t_0 = T_0
        self.V = V
        self.E_eff = E_EFF

def get_available_sensors(paths):
    fluence_file = paths.get_fluence_file('avgFluenceBinned_1h.csv')
    fluence_df = pd.read_csv(fluence_file, skiprows=4)
    sensor_columns = [col for col in fluence_df.columns if col not in ('bin_centre_date',)]
    return sorted(sensor_columns)

def prepare_inputs(selected_years):
    paths = Paths()
    params = Parameters()
    fluence_file = paths.get_fluence_file('avgFluenceBinned_1h.csv')
    temp_files = paths.get_temperature_files_for_years(selected_years)
    return params, paths, fluence_file, temp_files

def run_all_sensors(selected_years):
    params, paths, fluence_file, temp_files = prepare_inputs(selected_years)
    available_sensors = get_available_sensors(paths)
    print(f"Found {len(available_sensors)} sensors available")
    simulated_df, sensors = fluence_simulation_lib.run_leakage_current_pipeline(
        fluence_file, temp_files, params
    )
    if len(sensors) < len(available_sensors):
        print(f"Warning: Only {len(sensors)} out of {len(available_sensors)} sensors have complete data")
    temp_df = pd.concat([pd.read_csv(f, index_col="TS", parse_dates=["TS"]) for f in temp_files], axis=0, join='outer')
    temp_df = temp_df.groupby(temp_df.index).max().sort_index()
    fluence_df = pd.read_csv(fluence_file, skiprows=4)
    fluence_df['bin_centre_date'] = pd.to_datetime(fluence_df['bin_centre_date'], format='%d-%m-%Y %H:%M:%S')
    fluence_df.set_index('bin_centre_date', inplace=True)
    fluence_df.index = fluence_df.index - pd.Timedelta(minutes=5)
    fluence_df.index.name = "TS"
    out_df = pd.DataFrame(index=simulated_df.index)
    for sensor in sensors:
        out_df[f"current_{sensor}"] = simulated_df[sensor]
        if sensor in temp_df.columns:
            out_df[f"temperature_{sensor}"] = temp_df[sensor].reindex(simulated_df.index, method='nearest')
        else:
            out_df[f"temperature_{sensor}"] = np.nan
        if sensor in fluence_df.columns:
            out_df[f"fluence_{sensor}"] = fluence_df[sensor].reindex(simulated_df.index, method='nearest')
        else:
            out_df[f"fluence_{sensor}"] = np.nan
    out_df.to_csv(OUTPUT_SIMULATED_DF_PATH)
    return simulated_df, sensors

def run_single_sensor(selected_years, sensor_name):
    params, paths, fluence_file, temp_files = prepare_inputs(selected_years)
    simulated_df = fluence_simulation_lib.run_leakage_current_pipeline(
        fluence_file, temp_files, params, sensor_name=sensor_name
    )
    print(f"Simulated DataFrame for sensor {sensor_name}:\n{simulated_df.head()}")
    simulated_df.to_csv(OUTPUT_SIMULATED_DF_PATH)
    return simulated_df, sensor_name

if __name__ == "__main__":
    if RUN_MODE == "single":
        sim, name = run_single_sensor(SELECTED_YEARS, SENSOR_NAME)
    else:
        sim, sensors = run_all_sensors(SELECTED_YEARS)
