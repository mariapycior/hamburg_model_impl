import os
import pandas as pd
import numpy as np
from datetime import datetime
from config import Paths, RUN_MODE, SENSOR_NAME, SELECTED_YEARS, CURRENT_YEAR_RANGES, CURRENT_YEAR_LIST, OUTPUT_SIMULATED_DF_PATH
import fluence_simulation_lib
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
    simulated_df, sensors = fluence_simulation_lib.run_leakage_current_pipeline(
        fluence_file, temp_files, current_files, params, paths
    )
    if len(sensors) < len(available_sensors):
        print(f"Warning: Only {len(sensors)} out of {len(available_sensors)} sensors have complete data")
    # --- Nowe: budowanie dataframe z current, temperature, fluence dla każdego sensora ---
    # simulated_df: DataFrame z kolumnami = sensorami, wartości = current
    # Odtwórz temperature i fluence dla każdego sensora i zapisz jako osobne kolumny
    temp_df = pd.concat([pd.read_csv(f, index_col="TS", parse_dates=["TS"]) for f in temp_files], axis=0, join='outer')
    temp_df = temp_df.groupby(temp_df.index).max().sort_index()
    fluence_df = pd.read_csv(fluence_file, skiprows=4)
    fluence_df['bin_centre_date'] = pd.to_datetime(fluence_df['bin_centre_date'], format='%d-%m-%Y %H:%M:%S')
    fluence_df.set_index('bin_centre_date', inplace=True)
    fluence_df.index = fluence_df.index - pd.Timedelta(minutes=5)
    fluence_df.index.name = "TS"
    # Budujemy nowy DataFrame
    out_df = pd.DataFrame(index=simulated_df.index)
    for sensor in sensors:
        # current
        out_df[f"current_{sensor}"] = simulated_df[sensor]
        # temperature
        if sensor in temp_df.columns:
            out_df[f"temperature_{sensor}"] = temp_df[sensor].reindex(simulated_df.index, method='nearest')
        else:
            out_df[f"temperature_{sensor}"] = np.nan
        # fluence
        if sensor in fluence_df.columns:
            out_df[f"fluence_{sensor}"] = fluence_df[sensor].reindex(simulated_df.index, method='nearest')
        else:
            out_df[f"fluence_{sensor}"] = np.nan
    out_df.to_csv(OUTPUT_SIMULATED_DF_PATH)
    # --- wykres jak dotychczas ---
    simulated_df.plot(title="Simulated Current (all sensors)")
    import matplotlib.pyplot as plt
    plt.gcf().set_size_inches(12, 8)  # Increase figure size
    plt.xlabel("Time")
    plt.ylabel("Simulated Current")
    plt.tight_layout()
    plt.show()
    return simulated_df, sensors

def run_single_sensor(selected_years, sensor_name):
    params, paths, fluence_file, temp_files, current_files = prepare_inputs(selected_years)
    simulated_df, sensors = fluence_simulation_lib.run_leakage_current_pipeline(
        fluence_file, temp_files, current_files, params, paths, sensor_name=sensor_name
    )
    if sensor_name not in sensors:
        raise ValueError(f"Sensor {sensor_name} not found in the available sensors: {sensors}")
    if isinstance(simulated_df, pd.Series):
        simulated_df = simulated_df.to_frame(name=f"current_{sensor_name}")
    else:
        # Rename 'current' column if present
        if "current" in simulated_df.columns:
            simulated_df = simulated_df.rename(columns={"current": f"current_{sensor_name}"})
    # Dodaj kolumny temperature i fluence z nazwą sensora
    temp_df = pd.concat([pd.read_csv(f, index_col="TS", parse_dates=["TS"]) for f in temp_files], axis=0, join='outer')
    temp_df = temp_df.groupby(temp_df.index).max().sort_index()
    if sensor_name in temp_df.columns:
        simulated_df[f"temperature_{sensor_name}"] = temp_df[sensor_name].reindex(simulated_df.index, method='nearest')
    else:
        simulated_df[f"temperature_{sensor_name}"] = np.nan
    fluence_df = pd.read_csv(fluence_file, skiprows=4)
    fluence_df['bin_centre_date'] = pd.to_datetime(fluence_df['bin_centre_date'], format='%d-%m-%Y %H:%M:%S')
    fluence_df.set_index('bin_centre_date', inplace=True)
    fluence_df.index = fluence_df.index - pd.Timedelta(minutes=5)
    fluence_df.index.name = "TS"
    if sensor_name in fluence_df.columns:
        simulated_df[f"fluence_{sensor_name}"] = fluence_df[sensor_name].reindex(simulated_df.index, method='nearest')
    else:
        simulated_df[f"fluence_{sensor_name}"] = np.nan
    simulated_df.to_csv(OUTPUT_SIMULATED_DF_PATH)
    simulated_df.plot(title=f"Simulated Current ({sensor_name})")
    import matplotlib.pyplot as plt
    plt.xlabel("Time")
    plt.ylabel("Simulated Current")
    plt.tight_layout()
    plt.show()
    return simulated_df, sensor_name

if __name__ == "__main__":
    if RUN_MODE == "single":
        sim, name = run_single_sensor(SELECTED_YEARS, SENSOR_NAME)
        name = SENSOR_NAME
        import current_preparation_lib
        params = Parameters()
        df_for_adjust = current_preparation_lib.load_and_prepare_simulated_df(name)
        adjusted_df = current_preparation_lib.adjust_simulated_current_with_temperature(df_for_adjust, params)
        import matplotlib.pyplot as plt
        empty_real = pd.Series(index=adjusted_df.index, dtype=float)
        plot_utils.plot_simulated_vs_real(adjusted_df, empty_real, name, output_path=None)
        plt.show()
    else:
        # --- Najpierw uruchom symulację i wygeneruj poprawny simulated_df.csv ---
        #sim, sensors = run_all_sensors(SELECTED_YEARS)
        import current_preparation_lib
        params = Parameters()
        simulated_df = pd.read_csv(OUTPUT_SIMULATED_DF_PATH, index_col=0, parse_dates=True)
        sensors = [col.replace("current_", "") for col in simulated_df.columns if col.startswith("current_")]
        adjusted_dfs = []
        for sensor in sensors:
            col_map = {
                f"current_{sensor}": "current",
                f"temperature_{sensor}": "temperature",
                f"fluence_{sensor}": "fluence"
            }
            available = [k for k in col_map.keys() if k in simulated_df.columns]
            if len(available) < 3:
                print(f"Warning: Not all columns found for sensor {sensor}, skipping.")
                continue
            df_for_adjust = simulated_df[available].rename(columns={k: v for k, v in col_map.items() if k in simulated_df.columns})
            adjusted_df = current_preparation_lib.adjust_simulated_current_with_temperature(df_for_adjust, params)
            adjusted_df = adjusted_df.rename(columns={"current": f"current_{sensor}"})
            adjusted_dfs.append(adjusted_df[[f"current_{sensor}"]])
        # Połącz wszystkie prądy w jeden DataFrame
        if adjusted_dfs:
            all_currents = pd.concat(adjusted_dfs, axis=1)
            import matplotlib.pyplot as plt
            all_currents.plot(title="Simulated Current (all sensors, adjusted)")
            plt.gcf().set_size_inches(12, 8)
            plt.xlabel("Time")
            plt.ylabel("Simulated Current (adjusted)")
            plt.tight_layout()
            plt.show()
