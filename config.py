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
        ntc_format = f"temperatureNTC{NTC}_10T_" if NTC == "00" else "temperature_10T_"
        return [self.get_temperature_file(f'{ntc_format}{year}.csv') for year in years]
    
    def get_output_file(self, filename: str) -> str:
        """Get full path to an output file."""
        return os.path.join(self.output_dir, filename)

# --- Input File Configuration ---
# Cross section parameter (kept for compatibility)
CROSS_SECTIONS = "74mb, 80mb"

# Luminosity type: "delivered" or "recorded"
LUMINOSITY = "delivered"

# NTC parameter: "00" or "01"
NTC = "01"

# File selection based on luminosity type
if LUMINOSITY == "recorded":
    FLUENCE_FILENAME = "avgFluenceBinned_10T_74_80_recorded.csv"
    LUMI_FILENAME = "lumi_binned_recorded.csv"
else:  # delivered
    FLUENCE_FILENAME = "avgFluenceBinned_10T_74_80.csv"
    LUMI_FILENAME = "lumi_binned.csv"

# Current file to year mapping
CURRENT_YEAR_RANGES = {
    '2011_current.csv': [2011],
    '2012_current.csv': [2012],
    'ls1_current.csv': [2013, 2014, 2015],
    '2016_current.csv': [2016],
    '2017_current.csv': [2017],
    '2018_current.csv': [2018],
}

CURRENT_YEAR_LIST = [
    ('2011_current.csv', [2011]),
    ('2012_current.csv', [2012]),
    ('ls1_current.csv', [2013, 2014, 2015]),
    ('2016_current.csv', [2016]),
    ('2017_current.csv', [2017]),
    ('2018_current.csv', [2018]),
]

# --- Simulation Configuration ---

# Temperature correction settings
TEMPERATURE_CORRECTION_ENABLED = True # Whether to apply temperature correction
TEMPERATURE_CORRECTION_DELTA = 3.2      # Correction value in Kelvin


# Resampling period for simulation data
# Available values: '1min', '1H', '10H', '24H', '1W'
SIMULATION_PERIOD = '6H'

# --- Output Configuration ---
OUTPUT_SIMULATED_DF_PATH = "simulated_df.csv"

# --- Runtime settings ---
RUN_MODE = "all"  # "single" or "all"
SENSOR_NAME = "VL02_CT"
SELECTED_YEARS = range(2011, 2019)
