#!/usr/bin/env python3
"""Plot Currents - A program to plot and compare simulated and real current data.

This program loads simulated current data from the output directory and compares
it with real current data. It uses plot_utils for visualization.

Usage examples:
    # List all available sensors
    python plot_currents.py --list-sensors
    
    # Plot a single sensor with weekly averaging
    python plot_currents.py --sensor VL02_CT --weekly-average
    
    # Plot multiple sensors
    python plot_currents.py --sensor VL02_CT VL03_CT
    
    # Plot only temperature data
    python plot_currents.py --sensor VL02_CT --temperature-only
"""

import os
import argparse
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

from config import Paths, CURRENT_YEAR_RANGES, CURRENT_YEAR_LIST, SIMULATION_PERIOD
from params import Parameters
import current_preparation_lib as cpl
import plot_utils

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Plot and compare simulated and real current data.')
    parser.add_argument('--sensor', type=str, default='VL02_CT', nargs='+',
                        help='Sensor name(s) to plot (default: VL02_CT). Can specify multiple sensors.')
    parser.add_argument('--simulated-file', type=str, default='simulated_df_new.csv',
                        help='Filename of the simulated data in the output directory')
    parser.add_argument('--output-dir', type=str, default='out_data/plots',
                        help='Directory to save plots (default: out_data/plots)')
    parser.add_argument('--start-date', type=str, default=None,
                        help='Start date for plotting (format: YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, default=None,
                        help='End date for plotting (format: YYYY-MM-DD)')
    parser.add_argument('--weekly-average', action='store_true',
                        help='Plot weekly averaged data')
    parser.add_argument('--all-plots', action='store_true',
                        help='Generate all plot types')
    parser.add_argument('--list-sensors', action='store_true',
                        help='List all available sensors in the simulated data')
    parser.add_argument('--temperature-only', action='store_true',
                        help='Plot only temperature data')
    parser.add_argument('--no-show', action='store_true',
                        help='Do not display plots (only save to files)')
    return parser.parse_args()

def load_real_current_data(paths, sensor_name):
    """Load real current data for the specified sensor without temperature adjustment.
    We'll use the simulated_df for temperature and fluence data.
    """
    # Determine which current files contain data for the sensor
    current_files = []
    for file_name, years in CURRENT_YEAR_LIST:
        current_files.append(file_name)
    
    # Load and concatenate current data
    all_current_dfs = []
    for file_name in current_files:
        file_path = paths.get_current_file(file_name)
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path, index_col=0, parse_dates=True)
                if sensor_name in df.columns:
                    # Extract only the sensor column we need
                    sensor_df = df[[sensor_name]]
                    all_current_dfs.append(sensor_df)
                    print(f"Loaded real current data for {sensor_name} from {file_name}")
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
    
    if not all_current_dfs:
        print(f"No real current data found for sensor {sensor_name}")
        return None
    
    # Concatenate all current data
    combined_df = pd.concat(all_current_dfs)
    return combined_df

def list_available_sensors(simulated_path):
    """List all available sensors in the simulated data file."""
    try:
        df = pd.read_csv(simulated_path, index_col=0, parse_dates=True, nrows=1)
        sensors = set()
        for col in df.columns:
            if col.startswith('current_'):
                sensor = col.replace('current_', '')
                sensors.add(sensor)
        return sorted(list(sensors))
    except Exception as e:
        print(f"Error reading simulated data file: {e}")
        return []

def main():
    """Main function to load data and generate plots."""
    # Parse command line arguments
    args = parse_arguments()
    simulated_file = args.simulated_file
    
    # Initialize paths and parameters
    paths = Paths()
    
    # Get the path to the simulated data file
    simulated_path = paths.get_output_file(simulated_file)
    
    # --- OPTION 1: List available sensors ---
    if args.list_sensors:
        sensors = list_available_sensors(simulated_path)
        if sensors:
            print("Available sensors in the simulated data:")
            for sensor in sensors:
                print(f"  - {sensor}")
        else:
            print("No sensors found in the simulated data file.")
        return
    
    # Parse date range if provided
    start_date = pd.to_datetime(args.start_date) if args.start_date else None
    end_date = pd.to_datetime(args.end_date) if args.end_date else None
    
    # --- OPTION 2: Process and plot each sensor ---
    for sensor_name in args.sensor:
        print(f"\n{'='*50}\nProcessing sensor: {sensor_name}\n{'='*50}")
        
        # Step 1: Load simulated data
        print(f"Loading simulated data for sensor {sensor_name}...")
        try:
            simulated_df = cpl.load_and_prepare_simulated_df(sensor_name, simulated_path)
            print(f"Loaded simulated data with {len(simulated_df)} points")
        except Exception as e:
            print(f"Error loading simulated data for {sensor_name}: {e}")
            continue
        
        # Step 2: Load real current data for comparison
        print(f"Loading real current data for sensor {sensor_name}...")
        real_df = load_real_current_data(paths, sensor_name)
        
        # Step 3: Generate plots based on available data and options
        if real_df is None:
            # Case 3.1: No real data available - plot only simulated data
            print(f"No real current data available for {sensor_name}. Plotting only simulated data.")
            plot_utils.plot_simulated_simple(simulated_df, sensor_name, None, start_date, end_date)
            print(f"Displayed simulated data plot for {sensor_name}")
        else:
            # Case 3.2: Plot temperature data if requested
            if args.temperature_only:
                print(f"Displaying temperature plot for {sensor_name}")
                plot_utils.plot_temperature_only(simulated_df, None, start_date, end_date)
                continue
                
            # Case 3.3: Generate detailed comparison plot if requested
            if args.all_plots or not args.weekly_average:
                plot_utils.plot_leakage_current(simulated_df, real_df, sensor_name, None, start_date, end_date)
                print(f"Displayed detailed comparison plot for {sensor_name}")
            
            # Case 3.4: Plot simulated vs real overlay (default plot)
            plot_utils.plot_simulated_vs_real(
                simulated_df['current'], real_df[sensor_name], sensor_name, 
                None, start_date, end_date, args.weekly_average
            )
            print(f"Displayed overlay plot for {sensor_name}")
    
    print("\nAll plots generated successfully!")

if __name__ == "__main__":
    main()
