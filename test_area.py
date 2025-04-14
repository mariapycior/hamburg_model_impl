import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from importlib import reload

import fluence_lib
from config import Paths

# Physical constants
KB = 8.617333262145e-5  # Boltzmann constant in eV/K
T_REF = 294.15  # Reference temperature in K (21°C)
E_I_STAR = 1.30  # Activation energy in eV

# Default parameters for leakage current calculation
ALPHA_I = 1.23e-17  # A/cm
ALPHA_0_STAR = 7.07e-17  # A/cm
BETA = 3.29e-18  # A/cm
E_I = 1.11  # eV
K_0I = 1.2e13  # 1/s
T_0 = 1.0  # min
V = 8.5  # cm3

class Parameters:
    """Class to store physical parameters for leakage current calculations."""
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

def main():
    """Main function to run the leakage current simulation."""
    params = Parameters()
    paths = Paths()
    
    # File paths for run1
    fluence_file = paths.get_fluence_file('avgFluenceBinned.csv')
    
    # Select years for simulation
    selected_years = [2011,2012,2013,2014,2015,2016,2017,2018]  # Example: Change this to select different years
    print(f"Selected years: {selected_years}")
    
    temp_files = paths.get_temperature_files_for_years(selected_years)
    print(f"Temperature files: {temp_files}")
    
    # Determine which current files to use based on years  
    current_files = []
    if any(year in selected_years for year in [2011, 2012]):
        current_files.append(paths.get_current_file('run1_current_sample.csv'))
    if any(year in selected_years for year in [2013, 2014, 2015]):
        current_files.append(paths.get_current_file('ls1_current_sample.csv'))
    if any(year in selected_years for year in [2016, 2017, 2018]):
        current_files.append(paths.get_current_file('run2_current_sample.csv'))
    
    # Load and concatenate current files if needed
    if len(current_files) == 1:
        current_df = fluence_lib.load_sensor_current(current_files[0])
    else:
        # Load both files and concatenate them
        current_dfs = [fluence_lib.load_sensor_current(file) for file in current_files]
        current_df = pd.concat(current_dfs, axis=0)
        # Drop duplicates, keeping the last (most recent) value
        current_df = current_df.groupby(current_df.index).last()
        current_df = current_df.sort_index()
    
    # Load data
    fluence_df, temp_df = fluence_lib.load_data(fluence_file, temp_files)
    
    # Sensor configuration
    sensor_name = 'VL02_CT'  # Change this to select different sensor
    
    # Simulate current for sensor
    fdf, tdf = fluence_lib.prepare_sensor_data(fluence_df, temp_df, sensor_name)
    simulated_current = fluence_lib.simulate_current_sensor(fdf, tdf, params)
    
    # Prepare current data
    current_adjusted = fluence_lib.prepare_sensor_current(current_df, temp_df, params, sensor_name)
    
    # Plot results
    fluence_lib.plot_leakage_current(
        simulated_current, current_adjusted, sensor_name,
        start_date=pd.Timestamp('2018-01-01'),
        end_date=pd.Timestamp('2018-12-31')
    )
    
    # Plot simulated vs real on the same plot
    fluence_lib.plot_simulated_vs_real(
        simulated_current, current_adjusted, sensor_name,
        start_date=pd.Timestamp('2018-01-01'),
        end_date=pd.Timestamp('2018-12-31')
    )

if __name__ == "__main__":
    main()
