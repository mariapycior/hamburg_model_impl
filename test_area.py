import os
import pandas as pd
from datetime import datetime
from config import Paths, RUN_MODE, SENSOR_NAME, SELECTED_YEARS, CURRENT_YEAR_RANGES, CURRENT_YEAR_LIST
import fluence_lib
import plot_utils

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

def get_available_sensors(paths, selected_years):
    relevant_files = [
        file for file, years in CURRENT_YEAR_RANGES.items()
        if any(year in selected_years for year in years)
    ]
    all_current_dfs = [
        pd.read_csv(paths.get_current_file(file))
        for file in relevant_files
    ]
    common_sensors = set(all_current_dfs[0].columns) - {'TS'}
    for df in all_current_dfs[1:]:
        common_sensors &= (set(df.columns) - {'TS'})
    return sorted(list(common_sensors))

def get_current_files(paths, selected_years):
    return [paths.get_current_file(f) for f, years in CURRENT_YEAR_LIST 
            if any(year in selected_years for year in years)]

def prepare_inputs(selected_years):
    paths = Paths()
    params = Parameters()
    fluence_file = paths.get_fluence_file('avgFluenceBinned_1h.csv')
    temp_files = paths.get_temperature_files_for_years(selected_years)
    current_files = get_current_files(paths, selected_years)
    return params, paths, fluence_file, temp_files, current_files

def run_all_sensors(selected_years):
    params, paths, fluence_file, temp_files, current_files = prepare_inputs(selected_years)
    available_sensors = get_available_sensors(paths, selected_years)
    print(f"Found {len(available_sensors)} sensors available across all runs")
    simulated_df, real_df, sensors = fluence_lib.run_leakage_current_pipeline(
        fluence_file, temp_files, current_files, params, paths
    )
    if len(sensors) < len(available_sensors):
        print(f"Warning: Only {len(sensors)} out of {len(available_sensors)} sensors have complete data")
    # --- DODANE: prosty overlay wszystkich simulated current na jednym wykresie ---
    import plot_utils
    plot_utils.plot_simulated_simple(simulated_df, sensors)
    # --- DODANE: pandas plot wszystkich simulated current na jednym wykresie ---
    plot_utils.plot_simulated_pandas(simulated_df)
    # --- DODANE: zapis simulated_df jako pickle do niezależnego sprawdzenia ---
    if 'simulated_df' in locals():
        simulated_df.to_csv("out_data/simulated_df.csv")
    return simulated_df, real_df, sensors

def run_single_sensor(selected_years, sensor_name):
    params, paths, fluence_file, temp_files, current_files = prepare_inputs(selected_years)
    simulated_df, real_df, sensors = fluence_lib.run_leakage_current_pipeline(
        fluence_file, temp_files, current_files, params, paths, sensor_name=sensor_name
    )
    if sensor_name not in sensors:
        raise ValueError(f"Sensor {sensor_name} not found in the available sensors: {sensors}")
    # --- DODANE: zapis simulated_df jako pickle do niezależnego sprawdzenia ---
    if 'simulated_df' in locals():
        simulated_df.to_csv("out_data/simulated_df.csv")
    return simulated_df, real_df[sensor_name], sensor_name

if __name__ == "__main__":
    if RUN_MODE == "single":
        sim, real, name = run_single_sensor(SELECTED_YEARS, SENSOR_NAME)
        import pandas as pd
        if isinstance(sim, pd.Series):
            sim_df = sim.to_frame()
        else:
            sim_df = sim
        real_df = real.to_frame(name=name)
        plot_utils.plot_simulated_vs_real(sim_df, real_df, name, output_path=f"out_data/sim_vs_real_{name}.png")
        plot_utils.plot_simulated_vs_real(sim_df, real_df, name, output_path=f"out_data/sim_vs_real_{name}_7dmean.png", weekly_average=True)
        #plot_utils.plot_leakage_current(sim, real_df, name, output_path=f"out_data/leakage_current_{name}.png")
        #plot_utils.plot_temperature_only(sim, output_path=f"out_data/temperature_{name}.png")
    else:
        simulated_df, real_df, sensors = run_all_sensors(SELECTED_YEARS)
        plot_utils.plot_all_sensors(simulated_df, real_df, sensors, output_dir="out_data")
