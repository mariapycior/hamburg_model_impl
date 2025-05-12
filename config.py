"""
Configuration file for path settings
"""

import os

class Paths:
    """Class to store path configurations."""
    def __init__(self):
        self.base_dir = 'in_data'
        self.fluence_dir = os.path.join(self.base_dir, 'fluence')
        self.current_dir = os.path.join(self.base_dir, 'current')
        self.temperature_dir = os.path.join(self.base_dir, 'temperature')

    def get_fluence_file(self, filename: str) -> str:
        """Get full path to a fluence file."""
        return os.path.join(self.fluence_dir, filename)

    def get_current_file(self, filename: str) -> str:
        """Get full path to a current file."""
        return os.path.join(self.current_dir, filename)

    def get_temperature_file(self, filename: str) -> str:
        """Get full path to a temperature file."""
        return os.path.join(self.temperature_dir, filename)

    def get_temperature_files_for_years(self, years: list) -> list:
        """Get temperature files for specified years."""
        return [self.get_temperature_file(f'temperature_1T_{year}.csv') for year in years]

# Mode for current-temperature adjustment: 'adjust_sim', 'adjust_real', or 'none'
CURRENT_TEMP_MODE = 'adjust_sim'  # Możesz zmienić na 'adjust_real' lub 'none'

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

# --- Ustawienia okresów czasowych (resampling/interwały) ---
# Dostępne wartości: '1min', '1H', '10H', '24H', '1W'
SIMULATION_PERIOD = '10H'  # <- Zmień tutaj na: '1min', '1H', '10H', '24H', '1W' wg potrzeb

# --- Ścieżki do plików wyjściowych ---
OUTPUT_SIMULATED_DF_PATH = "out_data/data/simulated_df.csv"

# --- Physical constants ---
KB = 8.617333262145e-5  # Boltzmann constant in eV/K
T_REF = 294.15  # Reference temperature in K
E_I_STAR = 1.30  # Energy in eV
ALPHA_I = 1.23e-17  # Current-related damage rate in A/cm
ALPHA_0_STAR = 6.74e-17  # Current-related damage coefficient in A/cm
BETA = 3.29e-18  # Second order damage coefficient in A/cm
E_I = 1.11  # Activation energy in eV
K_0I = 1.2e13  # Frequency factor in s^-1
T_0 = 1.0  # Reference time in days
V = 0.805  # Bias voltage in V
E_EFF = 1.21  # Effective activation energy in eV

# --- File paths ---
FLUENCE_FILENAME = "avgFluenceBinned_1h.csv"
OUTPUT_SIMULATED_DF_PATH = "out_data/data/simulated_df.csv"

# --- Runtime settings ---
RUN_MODE = "single"  # "single" or "all"
SENSOR_NAME = "VL02_CT"
SELECTED_YEARS = range(2011, 2013)
