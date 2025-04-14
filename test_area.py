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
T_REF = 294.15  # Reference temperature in K (20°C)
E_I_STAR = 1.30  # Activation energy in eV

# Default parameters for leakage current calculation
ALPHA_I = 1.23e-17  # A/cm
ALPHA_0_STAR = 7.07e-17  # A/cm
BETA = 3.29e-18  # A/cm
E_I = 1.11  # eV
K_0I = 1.2e13  # 1/s
T_0 = 1.0  # min
V = 4.0  # cm3

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
    fluence_file = paths.get_fluence_file('avgFluenceBinned.csv')  # Using avgFluenceBinned.csv for run1
    temp_file = paths.get_temperature_file('run1_temp_C_60s.csv')
    current_file = paths.get_current_file('run1_current_sample.csv')
    
    # Load data
    fluence_df, temp_df = fluence_lib.load_data(fluence_file, temp_file)
    current_df = fluence_lib.load_sensor_current(current_file)
    
    # Sensor configuration
    sensor_name = 'VL02_CT'  # Change this to select different sensor
    
    # Simulate current for sensor
    fdf, tdf = fluence_lib.prepare_sensor_data(fluence_df, temp_df, sensor_name)
    simulated_current = fluence_lib.simulate_current_sensor(fdf, tdf, params)
    
    # Prepare current data
    current_adjusted = fluence_lib.prepare_sensor_current(current_df, temp_df, params, sensor_name)
    
    # Plot results
    fluence_lib.plot_leakage_current(
        simulated_current, current_adjusted, sensor_name
    )

if __name__ == "__main__":
    main()
