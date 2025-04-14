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
        return [self.get_temperature_file(f'temperature_10T_{year}.csv') for year in years]
