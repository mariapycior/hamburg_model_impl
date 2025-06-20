#!/usr/bin/env python3

import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import plot_utils

from config import Paths
from config_plot import CURRENT_TEMP_MODE, PLOT_RESAMPLING_PERIOD, TARGET_LUMINOSITIES
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
    parser.add_argument('--plot-by', type=str, choices=['time', 'luminosity'], default='time',
                        help='Type of plot to create (time or luminosity)')
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

    result_df = cpl.prepare_data_for_analysis(result_df, params, sensors_to_use)
    
    # Apply resampling before plotting
    from config_plot import PLOT_RESAMPLING_PERIOD
    result_df = cpl.resample_dataframe(result_df, PLOT_RESAMPLING_PERIOD)

    # Calculate fit quality metrics for each sensor and store in variable
    fit_metrics = cpl.calculate_fit_quality(result_df, sensors_to_use)
    
    curr_vs_pos_df = cpl.current_for_lumi(result_df)
    #plot_utils.plot_integrated_luminosity(result_df)
    
    # Generate single or multi-sensor plots
    if not args.all_sensors:
        sensor = args.sensor
        print(f"Creating plots for sensor {sensor}")
        print(fit_metrics)
        plot_utils.plot_simulated_vs_real(result_df, sensor)
        plot_utils.plot_leakage_current(result_df, sensor)
        plot_utils.plot_currents_vs_parameter(result_df, sensor, param_type='luminosity')
        plot_utils.plot_currents_vs_parameter(result_df, sensor, param_type='fluence')
    else:
        print(f"Creating plots for all {len(sensors_to_use)} sensors")
        plot_utils.plot_currents_vs_position(curr_vs_pos_df, TARGET_LUMINOSITIES)
        group_averages_df = plot_utils.plot_all_sensors(result_df, sensors_to_use)
        print(group_averages_df)
        plot_utils.plot_group_averages(group_averages_df, args.plot_by)
        #plot_utils.plot_all_currents_vs_luminosity(result_df, sensors_to_use)
        #plot_utils.plot_all_currents_vs_fluence(result_df, sensors_to_use)

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
