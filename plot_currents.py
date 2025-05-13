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

from config import Paths, CURRENT_YEAR_RANGES, CURRENT_YEAR_LIST, SIMULATION_PERIOD, CURRENT_TEMP_MODE
from params import Parameters
import current_preparation_lib as cpl
import plot_utils

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Plot and compare simulated and real current data.')
    parser.add_argument('--sensor', type=str, default='VL02_CT', nargs='+',
                        help='Sensor name(s) to plot (default: VL02_CT). Can specify multiple sensors.')
    parser.add_argument('--simulated-file', type=str, default='simulated_df.csv',
                        help='Filename of the simulated data in the output directory')
    parser.add_argument('--output-dir', type=str, default='out_data/plots',
                        help='Directory to save plots (default: out_data/plots)')
    parser.add_argument('--start-date', type=str, default=None,
                        help='Start date for plotting (format: YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, default=None,
                        help='End date for plotting (format: YYYY-MM-DD)')
    parser.add_argument('--all-sensors', action='store_true',
                        help='Plot all sensors on a single plot')
    parser.add_argument('--list-sensors', action='store_true',
                        help='List all available sensors in the simulated data')
    return parser.parse_args()

def load_real_current_data(paths, sensor_name, simulated_df=None):
    """Load real current data for the specified sensor with temperature adjustment if needed.
    
    Args:
        paths: Paths object for file paths
        sensor_name: Name of the sensor to load data for
        simulated_df: Optional simulated DataFrame with temperature data
        
    Returns:
        DataFrame with real current data, adjusted if CURRENT_TEMP_MODE is 'adjust_real'
    """
    # Determine which current files contain data for the sensor
    current_files = []
    for file_name, _ in CURRENT_YEAR_LIST:
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
    
    # Check if we need to adjust real current with temperature
    if CURRENT_TEMP_MODE == 'adjust_real' and simulated_df is not None:
        print(f"Adjusting real current with temperature for {sensor_name}...")
        # Get temperature data from simulated_df
        temp_df = pd.DataFrame(index=simulated_df.index)
        # The temperature column in simulated_df is just 'temperature' because of how
        # load_and_prepare_simulated_df standardizes the column names
        temp_df[sensor_name] = simulated_df['temperature']
        
        # Adjust real current with temperature
        params = Parameters()
        adjusted_df = cpl.adjust_real_current_with_temperature(combined_df, temp_df, params, sensor_name)
        print(f"Adjusted real current with temperature")
        return adjusted_df
    
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

    args = parse_arguments()
    simulated_file = args.simulated_file
    paths = Paths()
    simulated_path = paths.get_output_file(simulated_file)
    

    if args.list_sensors:
        sensors = list_available_sensors(simulated_path)
        if sensors:
            print("Dostępne sensory:")
            for sensor in sensors:
                print(f"  - {sensor}")
        else:
            print("Nie znaleziono sensorów w pliku danych.")
        return
    

    start_date = pd.to_datetime(args.start_date) if args.start_date else None
    end_date = pd.to_datetime(args.end_date) if args.end_date else None
    

    if args.all_sensors:
        print("\nWykreślanie wszystkich sensorów na jednym wykresie...")
        

        all_sensors = list_available_sensors(simulated_path)
        print(f"Znaleziono {len(all_sensors)} sensorów")
        

        all_simulated_data = {}
        for sensor_name in all_sensors:
            try:
                sim_df = cpl.load_and_prepare_simulated_df(sensor_name, simulated_path)
                params = Parameters()
                if CURRENT_TEMP_MODE == 'adjust_sim':
                    sim_df = cpl.adjust_simulated_current_with_temperature(sim_df, params)
                all_simulated_data[sensor_name] = sim_df['current']
            except Exception as e:
                print(f"Błąd wczytywania danych dla {sensor_name}: {e}")
        

        simulated_combined = pd.DataFrame(all_simulated_data)
        simulated_combined.to_csv("simulated_current.csv")

        

        all_real_data = {}
        for sensor_name in all_sensors:
            sim_df = None
            if sensor_name in all_simulated_data:
                sim_df = pd.DataFrame({
                    'current': all_simulated_data[sensor_name],
                    'temperature': cpl.load_and_prepare_simulated_df(sensor_name, simulated_path)['temperature']
                }, index=all_simulated_data[sensor_name].index)
            
            real_df = load_real_current_data(paths, sensor_name, sim_df)
            if real_df is not None:
                all_real_data[sensor_name] = real_df[sensor_name]
        

        real_combined = pd.DataFrame(all_real_data)
        real_combined.to_csv("real_current.csv")
        

        plot_utils.plot_all_sensors(simulated_combined, real_combined, all_sensors, args.output_dir, start_date, end_date)
        print("Wyświetlono wykresy dla wszystkich sensorów")
        return
    

    for sensor_name in args.sensor:
        print(f"\n{'='*50}\nPrzetwarzanie sensora: {sensor_name}\n{'='*50}")
        

        print(f"Wczytywanie danych symulowanych dla {sensor_name}...")
        try:
            simulated_df = cpl.load_and_prepare_simulated_df(sensor_name, simulated_path)
            print(f"Wczytano dane symulowane: {len(simulated_df)} punktów")
            
            params = Parameters()
            if CURRENT_TEMP_MODE == 'adjust_sim':
                print(f"Dostosowywanie prądu symulowanego z temperaturą...")
                simulated_df = cpl.adjust_simulated_current_with_temperature(simulated_df, params)
                print(f"Dostosowano prąd symulowany z temperaturą")
        except Exception as e:
            print(f"Błąd wczytywania danych dla {sensor_name}: {e}")
            continue
        

        print(f"Wczytywanie danych rzeczywistych dla {sensor_name}...")
        real_df = load_real_current_data(paths, sensor_name, simulated_df)
        
        # Generuj wykresy
        if real_df is None:
            print(f"Brak danych rzeczywistych dla {sensor_name}. Wykreślanie tylko danych symulowanych.")
            plot_utils.plot_simulated_simple(simulated_df, sensor_name, None, start_date, end_date)
        else:

            plot_utils.plot_leakage_current(simulated_df, real_df, sensor_name, None, start_date, end_date)
            print(f"Wyświetlono szczegółowy wykres porównawczy dla {sensor_name}")

            plot_utils.plot_simulated_vs_real(
                simulated_df['current'], real_df[sensor_name], sensor_name, 
                None, start_date, end_date, False
            )
            print(f"Wyświetlono wykres nakładający dla {sensor_name}")
    
    print("\nWszystkie wykresy wygenerowane pomyślnie!")

if __name__ == "__main__":
    main()
