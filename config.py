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
SIMULATION_PERIOD = '24H'  # <- Zmień tutaj na: '1min', '1H', '10H', '24H', '1W' wg potrzeb

# --- Ścieżki do plików wyjściowych ---
OUTPUT_SIMULATED_DF_PATH = "out_data/simulated_df.csv"

# --- Ustawienia uruchamiania ---
RUN_MODE = "all"  # "single" albo "all"
SENSOR_NAME = "VL07_CB"
SELECTED_YEARS = range(2011, 2019)
