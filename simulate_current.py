import os
import pandas as pd
import numpy as np
from config import Paths, FLUENCE_FILENAME, RUN_MODE, SENSOR_NAME, SELECTED_YEARS, OUTPUT_SIMULATED_DF_PATH
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
    fluence_file = paths.get_fluence_file(FLUENCE_FILENAME)
    fluence_df = pd.read_csv(fluence_file, skiprows=4)
    sensor_columns = [col for col in fluence_df.columns if col not in ('bin_centre_date',)]
    return sorted(sensor_columns)

def prepare_inputs(selected_years):
    paths = Paths()
    params = Parameters()
    fluence_file = paths.get_fluence_file(FLUENCE_FILENAME)
    temp_files = paths.get_temperature_files_for_years(selected_years)
    return params, paths, fluence_file, temp_files

def run_all_sensors(selected_years):
    params, paths, fluence_file, temp_files = prepare_inputs(selected_years)
    available_sensors = get_available_sensors(paths)
    print(f"Found {len(available_sensors)} sensors available")
    simulated_df, sensors = fluence_simulation_lib.run_leakage_current_pipeline(
        fluence_file, temp_files, params, available_sensors=available_sensors
    )
    
    if simulated_df is not None:
        if len(sensors) < len(available_sensors):
            print(f"Warning: Only {len(sensors)} out of {len(available_sensors)} sensors have complete data")
        
        simulated_df.to_csv(OUTPUT_SIMULATED_DF_PATH)
        return simulated_df, sensors
    else:
        print("No data was processed. Check if sensors exist in both fluence and temperature datasets.")
        return pd.DataFrame(), []

def run_single_sensor(selected_years, sensor_name):
    params, _, fluence_file, temp_files = prepare_inputs(selected_years)
    simulated_df, _ = fluence_simulation_lib.run_leakage_current_pipeline(
        fluence_file, temp_files, params, sensor_name=sensor_name
    )
    if simulated_df is not None:
        print(f"Simulated DataFrame for sensor {sensor_name}:\n{simulated_df.head()}")
        simulated_df.to_csv(OUTPUT_SIMULATED_DF_PATH)
        return simulated_df, sensor_name
    else:
        print(f"Failed to process sensor {sensor_name}")
        return pd.DataFrame(), sensor_name

if __name__ == "__main__":
    if RUN_MODE == "single":
        sim, name = run_single_sensor(SELECTED_YEARS, SENSOR_NAME)
    else:
        sim, sensors = run_all_sensors(SELECTED_YEARS)
