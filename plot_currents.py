#!/usr/bin/env python3

import os
import argparse
import pandas as pd


from config import Paths, SIMULATION_PERIOD, CURRENT_TEMP_MODE
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

    all_filtered_columns = []
    for sensor in sensors_to_use:
        sensor_columns = [col for col in df.columns if col.endswith(f"_{sensor}")]
        all_filtered_columns.extend(sensor_columns)
    
    if not all_filtered_columns:
        print(f"No data found for sensors: {', '.join(sensors_to_use)}")
        return
    
    result_df = df[all_filtered_columns]
    
    # Zastosuj filtr daty początkowej jeśli podano
    if args.start_date:
        start_date = pd.to_datetime(args.start_date)
        result_df = result_df[result_df.index >= start_date]
    
    # Apply temperature adjustment based on mode
    if not args.all_sensors:
        if CURRENT_TEMP_MODE == 'adjust_real':
            result_df = cpl.adjust_real_current_with_temperature(result_df, params, args.sensor)
        elif CURRENT_TEMP_MODE == 'adjust_sim':
            result_df = cpl.adjust_simulated_current_with_temperature(result_df, params, args.sensor)
    
    # Wyświetl wykresy lub zapisz do pliku
    if not args.all_sensors:
        import plot_utils
        sensor = args.sensor
        print(f"Creating plot for sensor {sensor}")
        plot_utils.plot_simulated_vs_real(result_df, sensor)
    else:
        import plot_utils
        print(f"Creating plots for all {len(sensors_to_use)} sensors")
        plot_utils.plot_all_sensors(result_df, sensors_to_use)


if __name__ == "__main__":
    main()
