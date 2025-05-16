import os
import pandas as pd
import numpy as np
from config import (
    Paths, FLUENCE_FILENAME, RUN_MODE, SENSOR_NAME, SELECTED_YEARS, OUTPUT_SIMULATED_DF_PATH,
    CURRENT_YEAR_LIST
)
from params import Parameters
import current_simulation_lib
from current_simulation_lib import load_real_current_data

def get_available_sensors(fluence_file):
    fluence_df = pd.read_csv(fluence_file, skiprows=4)
    sensor_columns = [col for col in fluence_df.columns if col not in ('bin_centre_date',)]
    return sorted(sensor_columns) #MP dodaj zeby temp tez otwieralo i wynik to sensory ktore sa w obydwu

def prepare_inputs(selected_years):
    paths = Paths()
    params = Parameters()
    fluence_file = paths.get_fluence_file(FLUENCE_FILENAME)
    temp_files = paths.get_temperature_files_for_years(selected_years)
    return params, paths, fluence_file, temp_files


def run_all_sensors(selected_years):
    params, paths, fluence_file, temp_files = prepare_inputs(selected_years)
    available_sensors = get_available_sensors(fluence_file)
    print(f"Found {len(available_sensors)} sensors available")
    
    real_df = load_real_current_data(paths)
    
    simulated_df, sensors = current_simulation_lib.run_leakage_current_pipeline(
        fluence_file, temp_files, params, available_sensors=available_sensors,
        real_df=real_df
    )
    
    if simulated_df is not None:
        if len(sensors) < len(available_sensors):
            print(f"Warning: Only {len(sensors)} out of {len(available_sensors)} sensors have complete data")
        
        output_path = paths.get_output_file(OUTPUT_SIMULATED_DF_PATH)
        simulated_df.to_csv(output_path)
        
        real_current_cols = [col for col in simulated_df.columns if col.startswith('real_current_')]
        if real_current_cols:
            real_data_sensors = len(real_current_cols)
            print(f"Real current data added for {real_data_sensors} out of {len(sensors)} sensors.")
        else:
            print("No real current data was found or added.")
            
        print(f"Simulation completed for {len(sensors)} sensors. Results saved to {output_path}")
        return simulated_df, sensors
    else:
        print("No data was processed. Check if sensors exist in both fluence and temperature datasets.")
        return pd.DataFrame(), []


def run_single_sensor(selected_years, sensor_name):
    params, paths, fluence_file, temp_files = prepare_inputs(selected_years)
    
    real_df = load_real_current_data(paths)
    
    simulated_df, sensors = current_simulation_lib.run_leakage_current_pipeline(
        fluence_file, temp_files, params, sensor_name=sensor_name,
        real_df=real_df
    )
    
    if simulated_df is not None:
        print(f"Simulated DataFrame for sensor {sensor_name}:\n{simulated_df.head()}")
        
        real_current_col = f"real_current_{sensor_name}"
        if real_current_col in simulated_df.columns:
            not_null_values = simulated_df[real_current_col].count()
            if not_null_values > 0:
                print(f"Real current data added for {sensor_name} with {not_null_values} non-null values.")
            else:
                print(f"Real current column exists for {sensor_name} but contains only null values.")
        else:
            print(f"No real current data was found for sensor {sensor_name}.")
        
        output_path = paths.get_output_file(OUTPUT_SIMULATED_DF_PATH)
        simulated_df.to_csv(output_path)
        print(f"Simulation completed for sensor {sensor_name}. Results saved to {output_path}")
        return simulated_df, sensor_name
    else:
        print(f"Failed to process sensor {sensor_name}")
        return pd.DataFrame(), sensor_name

if __name__ == "__main__":
    try:
        if RUN_MODE == "single":
            print(f"Running simulation for single sensor: {SENSOR_NAME}")
            sim, name = run_single_sensor(SELECTED_YEARS, SENSOR_NAME)
            print(f"Simulation completed for {name}. Results saved to {OUTPUT_SIMULATED_DF_PATH}")
        else:
            print(f"Running simulation for all available sensors")
            sim, sensors = run_all_sensors(SELECTED_YEARS)
            if sensors:
                print(f"Simulation completed for {len(sensors)} sensors. Results saved to {OUTPUT_SIMULATED_DF_PATH}")
            else:
                print("No sensors were processed successfully.")
    except Exception as e:
        print(f"Error during simulation: {str(e)}")
        import traceback
        traceback.print_exc()
