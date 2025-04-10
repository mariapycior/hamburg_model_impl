"""
Fluence data analysis script

This script loads fluence and temperature data for further analysis.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

from fluence_lib import (
    load_avg_fluence,
    load_temperature_data,
    prepare_sensor_data,
    simulate_current_sensor,
    plot_leakage_current
)

# Global constants
KB = 8.617333262145e-5  # Boltzmann constant in eV/K
T_REF = 293.15  # Reference temperature in K (20°C)
E_I_STAR = 1.0  # Activation energy in eV

# Default parameters
ALPHA_I = 1.23e-17
ALPHA_0 = 7.07e-17
BETA = 3.29e-18
E_I = 1.30
K_0I = 1.2e13
T_0 = 1.0
V=1

class Parameters:
    """
    Class to store physical parameters used in calculations.
    """
    def __init__(self):
        # Activation energy (eV)
        self.E_I_star = E_I_STAR
        self.T_ref = T_REF
        self.k_0I = K_0I
        self.E_I = E_I
        self.alpha_I = ALPHA_I
        self.alpha_0 = ALPHA_0
        self.beta = BETA
        self.t_0 = T_0
        self.V = V
        
    def set_E_I_star(self, value: float):
        self.E_I_star = value
        
    def set_T_ref(self, value: float):
        self.T_ref = value
        
    def set_k_0I(self, value: float):
        self.k_0I = value
        
    def set_E_I(self, value: float):
        self.E_I = value
        
    def set_alpha_I(self, value: float):
        self.alpha_I = value
        
    def set_alpha_0(self, value: float):
        self.alpha_0 = value
        
    def set_beta(self, value: float):
        self.beta = value
        
    def set_t_0(self, value: float):
        self.t_0 = value
    
    def set_V(self, value: float):
        self.V = value

def load_data():
    """
    Load both fluence and temperature data.
    """
    fluence_file = os.path.join('in_data', 'avgFluenceBinned.csv')
    temp_file = os.path.join('in_data', 'run2_temp_A_60s.csv')
    
    fluence_df = load_avg_fluence(fluence_file)
    print("Fluence data loaded successfully!")
    
    temp_df = load_temperature_data(temp_file)
    print("Temperature data loaded successfully!")
    
    return fluence_df, temp_df

def test_single_sensor(fluence_df: pd.DataFrame, temp_df: pd.DataFrame, params):
    """
    Test current simulation for a single sensor.
    """
    sensor_name = 'VL01_CT'  # Example sensor
    
    # Prepare data for this sensor
    fluence_series, temp_series = prepare_sensor_data(fluence_df, temp_df, sensor_name)
    
    # Print first records
    print("\nFirst record of fluence data:")
    print(fluence_series.head(1))
    print("\nFirst record of temperature data:")
    print(temp_series.head(1))
    
    # Simulate current for this sensor
    current_df = simulate_current_sensor(fluence_series, temp_series, sensor_name, params)
    
    print(f"\nSimulated current for sensor {sensor_name}")
    print(current_df.head())
    
    # Plot the results
    output_path = os.path.join('out_data', f'leakage_current_{sensor_name}.png')
    os.makedirs('out_data', exist_ok=True)
    plot_leakage_current(current_df, sensor_name, output_path)
    print(f"\nPlot saved to {output_path}")
    
    return current_df

if __name__ == "__main__":
    # Create parameter object with default values
    params = Parameters()
    
    # Load data
    fluence_df, temp_df = load_data()
    
    # Test for a single sensor
    current_df = test_single_sensor(fluence_df, temp_df, params)
    
    print("\nData loaded and ready for analysis!")
