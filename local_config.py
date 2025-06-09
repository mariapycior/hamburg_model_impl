"""
Local configuration file that is not tracked by git.
This file contains settings that should be consistent across all branches.
"""

# --- Temperature Correction Settings ---
# Whether to apply temperature correction to real current values
TEMPERATURE_CORRECTION_ENABLED = True

# Correction value in Kelvin (real currents will be scaled as if measured at temperature lower by this value)
TEMPERATURE_CORRECTION_DELTA = 3

# For compatibility with different branches - other common parameters can be added here
# All values from this file will override values from config.py and config_plot.py when imported
