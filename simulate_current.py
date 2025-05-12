import os
import pandas as pd
import numpy as np
from config import (
    Paths, FLUENCE_FILENAME, RUN_MODE, SENSOR_NAME, SELECTED_YEARS, OUTPUT_SIMULATED_DF_PATH
)
from params import Parameters
import fluence_simulation_lib

def get_available_sensors(fluence_file):
    """Get a list of all available sensors from the fluence file"""
    fluence_df = pd.read_csv(fluence_file, skiprows=4)
    sensor_columns = [col for col in fluence_df.columns if col not in ('bin_centre_date',)]
    return sorted(sensor_columns)


def prepare_inputs(selected_years):
    """Prepare all required inputs for simulation.
    
    Args:
        selected_years: List or range of years to include in the simulation
        
    Returns:
        tuple: (params, paths, fluence_file, temp_files)
    """
    paths = Paths()
    params = Parameters()
    fluence_file = paths.get_fluence_file(FLUENCE_FILENAME)
    temp_files = paths.get_temperature_files_for_years(selected_years)
    return params, paths, fluence_file, temp_files

def run_all_sensors(selected_years):
    """Run simulation for all available sensors"""
    params, paths, fluence_file, temp_files = prepare_inputs(selected_years)
    available_sensors = get_available_sensors(fluence_file)
    print(f"Found {len(available_sensors)} sensors available")
    
    # Run the pipeline for all available sensors
    simulated_df, sensors = fluence_simulation_lib.run_leakage_current_pipeline(
        fluence_file, temp_files, params, available_sensors=available_sensors
    )
    
    if simulated_df is not None:
        if len(sensors) < len(available_sensors):
            print(f"Warning: Only {len(sensors)} out of {len(available_sensors)} sensors have complete data")
        
        # Save results to CSV
        output_path = paths.get_output_file(OUTPUT_SIMULATED_DF_PATH)
        simulated_df.to_csv(output_path)
        print(f"Simulation completed for {len(sensors)} sensors. Results saved to {output_path}")
        return simulated_df, sensors
    else:
        print("No data was processed. Check if sensors exist in both fluence and temperature datasets.")
        return pd.DataFrame(), []


def run_single_sensor(selected_years, sensor_name):
    """Run simulation for a single specified sensor"""
    params, paths, fluence_file, temp_files = prepare_inputs(selected_years)
    
    # Run the pipeline for a single sensor
    simulated_df, sensors = fluence_simulation_lib.run_leakage_current_pipeline(
        fluence_file, temp_files, params, sensor_name=sensor_name
    )
    
    if simulated_df is not None:
        print(f"Simulated DataFrame for sensor {sensor_name}:\n{simulated_df.head()}")
        # Save results to CSV
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
