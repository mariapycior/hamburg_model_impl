#!/usr/bin/env python3

import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import plot_utils

from config import Paths, CURRENT_TEMP_MODE, TARGET_LUMINOSITIES
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
    parser.add_argument('--plot-currents-vs-position', action='store_true',
                        help='Plot currents vs position for all sensors')
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
        # Determine which sensors to use
        all_sensors = list_available_sensors(simulated_path)
        if not all_sensors:
            print("No sensors found in data")
            return
        
        sensors_to_use = all_sensors if args.all_sensors else [args.sensor]
        
        # Load data for selected sensors
        result_df = cpl.load_and_prepare_simulated_df(sensors_to_use, simulated_path)
        if result_df is None or result_df.empty:
            print(f"No data found for sensors: {', '.join(sensors_to_use)}")
            return
            
        print(f"Data loaded from {simulated_path}")
        
        # Prepare data for analysis (temperature adjustments, etc.)
        result_df = cpl.prepare_data_for_analysis(result_df, params, sensors_to_use, args.start_date)
        
        # Generate plots based on options
        if args.plot_currents_vs_position or args.all_sensors:
            curr_vs_pos_df = cpl.current_for_lumi(result_df)  # Uses TARGET_LUMINOSITIES from config
            plot_utils.plot_currents_vs_position(curr_vs_pos_df, TARGET_LUMINOSITIES)
        
        if not args.all_sensors:
            # Single sensor mode - create detailed plots for the selected sensor
            sensor = args.sensor
            print(f"Creating plots for sensor {sensor}")
            plot_utils.plot_simulated_vs_real(result_df, sensor)
            plot_utils.plot_currents_vs_integrated_luminosity(result_df, sensor)
        else:
            # Multi-sensor mode
            print(f"Creating plots for all {len(sensors_to_use)} sensors")
            #plot_utils.plot_all_sensors(result_df, sensors_to_use)
            #plot_utils.plot_all_currents_vs_luminosity(result_df, sensors_to_use)
            
    except Exception as e:
        print(f"Failed to process data: {e}")
        return


if __name__ == "__main__":
    main()
