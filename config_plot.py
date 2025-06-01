"""
Configuration file for plotting options and settings.
This file contains settings related to plot appearance, data averaging, and data processing options.
"""

# --- Data Processing Settings ---
# Mode for current-temperature adjustment: 'adjust_sim', 'adjust_real', or 'adjust_both'
CURRENT_TEMP_MODE = 'adjust_sim'

# Reference temperature for adjusting currents (in Kelvin)
REFERENCE_TEMPERATURE = 273.35

# --- Plot Mode Settings ---
# Whether to use lines for simulated data (True) or scatter points (False)
USE_LINES_FOR_SIMULATION = True

# Whether to display error bands for simulated data
SHOW_ERROR_BANDS = True

# Error percentage for simulated data (if SHOW_ERROR_BANDS is True)
ERROR_PERCENTAGE = 10  # 10% error band

# --- Data Aggregation Settings ---
# Resampling period for plots (independent from simulation period in config.py)
# Available values: None (use raw data), '1H', '24H', '1W'
PLOT_RESAMPLING_PERIOD = '1W'

# --- Visual Settings ---
# Marker size for scatter plots
SCATTER_MARKER_SIZE = 1

# Line width for line plots
LINE_WIDTH = 1

# Alpha (transparency) for error bands
ERROR_BAND_ALPHA = 0.6

# Colors
REAL_DATA_COLOR = 'red'
SIMULATED_DATA_COLOR = 'blue'
ERROR_BAND_COLOR = 'lightblue'

# --- Figure Settings ---
# Default figure size for single plots
DEFAULT_FIGURE_SIZE = (8, 6)

# Figure size for multi-subplot plots
MULTI_SUBPLOT_FIGURE_SIZE = (6, 8)

# --- Layer Order (zorder) Settings ---
# Lower zorder values appear behind higher values
ERROR_BAND_ZORDER = -10  # Error bands should be behind data
DATA_ZORDER = 10          # Data points and lines should be in front

# --- Plot Types to Generate ---
# Set to True to enable, False to disable
GENERATE_SINGLE_SENSOR_PLOTS = True
GENERATE_ALL_SENSORS_PLOT = False
GENERATE_TEMPERATURE_PLOTS = True
GENERATE_FLUENCE_PLOTS = True
