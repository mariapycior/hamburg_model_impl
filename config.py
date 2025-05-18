"""
Configuration file for the Hamburg model leakage current simulation.
"""

import os

# --- Path Configuration ---
class Paths:
    """Class to manage file paths for the simulation."""
    def __init__(self):
        # Base directories
        self.base_dir = 'in_data'
        self.output_dir = 'out_data/data'
        
        # Input data directories
        self.fluence_dir = os.path.join(self.base_dir, 'fluence')
        self.current_dir = os.path.join(self.base_dir, 'current')
        self.temperature_dir = os.path.join(self.base_dir, 'temperature')
        self.lumi_dir = os.path.join(self.base_dir, 'lumi')  # new directory for luminosity files
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

    def get_fluence_file(self, filename: str) -> str:
        """Get full path to a fluence file."""
        return os.path.join(self.fluence_dir, filename)

    def get_current_file(self, filename: str) -> str:
        """Get full path to a current file."""
        return os.path.join(self.current_dir, filename)

    def get_temperature_file(self, filename: str) -> str:
        """Get full path to a temperature file."""
        return os.path.join(self.temperature_dir, filename)

    def get_lumi_file(self, filename: str) -> str:
        """Get full path to a luminosity file."""
        return os.path.join(self.lumi_dir, filename)

    def get_temperature_files_for_years(self, years: list) -> list:
        """Get temperature files for specified years."""
        return [self.get_temperature_file(f'temperature_1T_{year}.csv') for year in years]
    
    def get_output_file(self, filename: str) -> str:
        """Get full path to an output file."""
        return os.path.join(self.output_dir, filename)

# --- Input File Configuration ---
FLUENCE_FILENAME = "avgFluenceBinned.csv"
LUMI_FILENAME = "lumi_binned.csv"

# Current file to year mapping
CURRENT_YEAR_RANGES = {
    'run1_current_all.csv': [2011, 2012],
    'ls1_current_all.csv': [2013, 2014, 2015],
    'run2_current_all.csv': [2016, 2017, 2018]
}

CURRENT_YEAR_LIST = [
    ('run1_current_all.csv', [2011, 2012]),
    ('ls1_current_all.csv', [2013, 2014, 2015]),
    ('run2_current_all.csv', [2016, 2017, 2018])
]

# --- Simulation Configuration ---
# Mode for current-temperature adjustment: 'adjust_sim', 'adjust_real', or 'none'
CURRENT_TEMP_MODE = 'adjust_real'

# Resampling period for simulation data
# Available values: '1min', '1H', '10H', '24H', '1W'
SIMULATION_PERIOD = '24H'

# --- Output Configuration ---
OUTPUT_SIMULATED_DF_PATH = "simulated_df.csv"

# --- Runtime settings ---
RUN_MODE = "all"  # "single" or "all"
SENSOR_NAME = "VL02_CT"
SELECTED_YEARS = range(2011, 2019)
