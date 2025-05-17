#!/usr/bin/env python3

import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt

from config import Paths, CURRENT_TEMP_MODE
from params import Parameters
params = Parameters()
import current_preparation_lib as cpl

def parse_arguments():
    parser = argparse.ArgumentParser(description='Load and process simulated and real current data')
    parser.add_argument('--sensor', type=str, default='VL02_CT', 
                        help='Sensor name to process (default: VL02_CT)')
    parser.add_argument('--simulated-file', type=str, default='simulated_df.csv',
                        help='Filename of the simulated data')
    parser.add_argument('--start-date', type=str, default=None,
                        help='Start date for data (format: YYYY-MM-DD)')
    parser.add_argument('--all-sensors', action='store_true',
                        help='Process all sensors')
    parser.add_argument('--list-sensors', action='store_true',
                        help='List all available sensors')
    return parser.parse_args()

def list_available_sensors(simulated_path):
    try:
        df = pd.read_csv(simulated_path, index_col=0, parse_dates=True, nrows=1)
        sensors = set()
        for col in df.columns:
            if col.startswith('current_'):
                sensor = col.replace('current_', '')
                sensors.add(sensor)
        return sorted(list(sensors))
    except Exception as e:
        print(f"Error reading data file: {e}")
        return []

def load_simulated_data(simulated_path):
    try:
        sensors = list_available_sensors(simulated_path)
        if not sensors:
            return None
        all_data = cpl.load_and_prepare_simulated_df(sensors, simulated_path)
        return all_data
    except Exception as e:
        print(f"Error loading simulated data: {e}")
        return None

def dataframe_preparation(df: pd.DataFrame, start_date=None, sensors_to_use=None) -> pd.DataFrame:
    """Prepare DataFrame by applying date filtering and temperature adjustments."""
    result_df = df.copy()
    
    # Filter by date
    if start_date:
        start_date = pd.to_datetime(start_date)
        result_df = result_df[result_df.index >= start_date]

    # Adjust to temperature
    if CURRENT_TEMP_MODE == 'adjust_real':
        result_df = cpl.adjust_real_current_with_temperature(result_df, params, sensors_to_use)
    elif CURRENT_TEMP_MODE == 'adjust_sim':
        result_df = cpl.adjust_simulated_current_with_temperature(result_df, params, sensors_to_use)
    
    # Add cumulative fluence
    result_df = cpl.add_delivered_fluence(result_df, params, sensors_to_use)
        
    return result_df

def main():
    args = parse_arguments()
    paths = Paths()
    simulated_path = paths.get_output_file(args.simulated_file)
    
    if args.list_sensors:
        sensors = list_available_sensors(simulated_path)
        if sensors:
            for sensor in sensors:
                print(f"- {sensor}")
        return
    
    try:
        df = pd.read_csv(simulated_path, index_col=0, parse_dates=True)
        print(f"Data loaded from {simulated_path}")
        # Add integrated luminosity plot using plot_utils
        # plot_utils.plot_integrated_luminosity(df)
    except Exception as e:
        print(f"Failed to load simulation data: {e}")
        return
        
    all_sensors = list_available_sensors(simulated_path)    
    if not all_sensors:
        print("No sensors found in data")
        return
        
    if args.all_sensors:
        sensors_to_use = all_sensors
    else:
        sensors_to_use = [args.sensor]

    all_filtered_columns = ['integrated_luminosity']  # Dodajemy tę kolumnę jako pierwszą
    for sensor in sensors_to_use:
        sensor_columns = [col for col in df.columns if col.endswith(f"_{sensor}")]
        all_filtered_columns.extend(sensor_columns)
    
    if len(all_filtered_columns) <= 1:  # Zmienione z if not all_filtered_columns
        print(f"No data found for sensors: {', '.join(sensors_to_use)}")
        return
    
    result_df = df[all_filtered_columns]
    
    # Apply date filtering and temperature adjustments
    result_df = dataframe_preparation(result_df, args.start_date, sensors_to_use)
    
    if not args.all_sensors:
        import plot_utils
        sensor = args.sensor
        print(f"Creating plots for sensor {sensor}")
        plot_utils.plot_simulated_vs_real(result_df, sensor)
        #plot_utils.plot_leakage_current(result_df, sensor)
        plot_utils.plot_currents_vs_cumulative_fluence(result_df, sensor)
        #plot_utils.plot_currents_vs_integrated_luminosity(result_df, sensor)
    else:
        import plot_utils
        print(f"Creating plots for all {len(sensors_to_use)} sensors")
        plot_utils.plot_all_sensors(result_df, sensors_to_use)
        plot_utils.plot_all_currents_vs_delivered_fluence(result_df, sensors_to_use)


if __name__ == "__main__":
    main()
