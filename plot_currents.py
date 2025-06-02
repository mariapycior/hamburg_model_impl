#!/usr/bin/env python3

import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import plot_utils

from config import Paths, TARGET_LUMINOSITIES
from config_plot import CURRENT_TEMP_MODE, PLOT_RESAMPLING_PERIOD
from params import Parameters
params = Parameters()
import current_preparation_lib as cpl

def parse_arguments():
    parser = argparse.ArgumentParser(description='Load and process simulated and real current data')
    parser.add_argument('--sensor', type=str, default='VL02_CT', nargs='+',
                        help='Sensor name(s) to process. Can provide multiple sensors (max 5) separated by space, e.g. "--sensor VL02_CT VL03_CT"')
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
        sensors = {col.replace('current_', '') for col in df.columns if col.startswith('current_')}
        return sorted(list(sensors))
    except Exception as e:
        print(f"Error reading data file: {e}")
        return []

def load_simulated_data(simulated_path):
    try:
        sensors = list_available_sensors(simulated_path)
        if not sensors:
            return None
        return cpl.load_and_prepare_simulated_df(sensors, simulated_path)
    except Exception as e:
        print(f"Error loading simulated data: {e}")
        return None



def process_and_plot_data(result_df, sensors_to_use, args):
    # Get sensors to plot
    if not args.all_sensors:
        sensors_to_plot = args.sensor
        
        # Ogranicz liczbę sensorów do 5, jeśli podano więcej
        if isinstance(sensors_to_plot, list) and len(sensors_to_plot) > 5:
            print(f"Warning: Too many sensors specified. Limiting to first 5 sensors.")
            sensors_to_plot = sensors_to_plot[:5]
        
        # Upewnij się, że pracujemy na liście
        if not isinstance(sensors_to_plot, list):
            sensors_to_plot = [sensors_to_plot]
    else:
        sensors_to_plot = sensors_to_use
    
    # Przygotuj dane tylko dla sensorów, które będą rysowane
    result_df = cpl.prepare_data_for_analysis(result_df, params, sensors_to_plot, args.start_date)

    # Calculate fit quality metrics for each sensor and store in variable
    fit_metrics = cpl.calculate_fit_quality(result_df, sensors_to_plot)
    
    curr_vs_pos_df = cpl.current_for_lumi(result_df)
    #plot_utils.plot_integrated_luminosity(result_df)
    
    # Generate single or multi-sensor plots
    if not args.all_sensors:
        if len(sensors_to_plot) > 1:
            print(f"Creating plots for {len(sensors_to_plot)} sensors: {', '.join(sensors_to_plot)}")
            
            # Dla wielu sensorów - rysuj na wspólnym wykresie dla simulated_vs_real i currents_vs_parameter
            plot_utils.plot_simulated_vs_real(result_df, sensors_to_plot)
            plot_utils.plot_currents_vs_parameter(result_df, sensors_to_plot, param_type='luminosity')
            plot_utils.plot_currents_vs_parameter(result_df, sensors_to_plot, param_type='fluence')
            
            # Dla leakage_current - wywołaj oddzielnie dla każdego sensora
            #for sensor in sensors_to_plot:
               # plot_utils.plot_leakage_current(result_df, sensor)
                
            # Wyświetl metryki dopasowania dla wszystkich sensorów
            for sensor in sensors_to_plot:
                if sensor in fit_metrics:
                    print(f"\nFit metrics for sensor {sensor}:")
                    for metric, value in fit_metrics[sensor].items():
                        print(f"  {metric}: {value}")
                        
        else:
            sensor = sensors_to_plot[0]
                
            print(f"Creating plots for sensor {sensor}")
            if sensor in fit_metrics:
                print(fit_metrics[sensor])
                
            plot_utils.plot_simulated_vs_real(result_df, sensor)
            plot_utils.plot_leakage_current(result_df, sensor)
            plot_utils.plot_currents_vs_parameter(result_df, sensor, param_type='luminosity')
            plot_utils.plot_currents_vs_parameter(result_df, sensor, param_type='fluence')
    else:
        print(f"Creating plots for all {len(sensors_to_use)} sensors")
        plot_utils.plot_currents_vs_position(curr_vs_pos_df, TARGET_LUMINOSITIES)
        plot_utils.plot_all_sensors(result_df, sensors_to_use)
        plot_utils.plot_all_currents_vs_luminosity(result_df, sensors_to_use)
        plot_utils.plot_all_currents_vs_fluence(result_df, sensors_to_use)

def main():
    args = parse_arguments()
    paths = Paths()
    simulated_path = paths.get_output_file(args.simulated_file)

    print(f"Plot configuration from config_plot.py:")
    print(f" - Temperature adjustment mode: {CURRENT_TEMP_MODE}")
    print(f" - Resampling period: {PLOT_RESAMPLING_PERIOD if PLOT_RESAMPLING_PERIOD else 'None'}")
    print(f" - All plot settings can be modified in config_plot.py")
    
    # List sensors if requested
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
        
        # Load simulated data
        print(f"Data loaded from {simulated_path}")
        result_df = load_simulated_data(simulated_path)
        if result_df is None:
            print("Failed to load data")
            return
            
        # Process data and create plots
        try:
            process_and_plot_data(result_df, sensors_to_use, args)
            # Wyświetl wszystkie wykresy na raz na końcu
            print("Showing all plots...")
            plt.show()
        except Exception as e:
            print(f"Failed to process data: {e}")
            raise e
    
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
