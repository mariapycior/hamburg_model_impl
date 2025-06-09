"""
Configuration file for plotting options and settings.
This file contains settings related to plot appearance, data averaging, and data processing options.
"""

# --- Data Processing Settings ---
# Mode for current-temperature adjustment: 'adjust_sim', 'adjust_real', or 'adjust_both'
CURRENT_TEMP_MODE = 'adjust_both'

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
PLOT_RESAMPLING_PERIOD = '24H'

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
DEFAULT_FIGURE_SIZE = (7, 5)

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


# --- Ratio Plot Settings ---
# Show ratio between simulated and real data for single sensor plots
SHOW_RATIO_FOR_SINGLE_SENSOR = True  # Set to True to enable ratio subplot
RATIO_PLOT_HEIGHT = 0.2  # Height ratio of the ratio subplot (relative to main plot)

# --- Sensor Grouping Settings ---
# Grouping mode: 'all', 'none', 'side', 'type', 'z_position', 'tb'
SENSOR_GROUPING_MODE = 'all'

# Colors for different groups
GROUP_COLORS = {
    'all': ['#1E90FF'],              # Dodgerblue - kolor dla wszystkich sensorów
    'side': ['#0000FF', '#FF0000'],  # A (blue), C (red)
    'type': ['#00FF00', '#FF00FF'],  # R (green), Phi (magenta)
    'tb': ['#00FFFF', '#FF8000'],    # T (cyan), B (orange)
    'z_position': ['#FF0000', '#00FF00', '#0000FF', '#FF00FF', '#00FFFF', '#FF8000', 
                 '#800080', '#008080', '#808000']
}



# --- Fit Quality Metrics ---
# Available metrics: 'mse', 'rmse', 'mae', 'r2', 'pearson', 'spearman', 'all'
# Use 'all' to calculate all metrics, or list specific metrics to calculate
FIT_QUALITY_METRICS = 'all'  # Can be a string ('all') or a list of specific metrics, e.g. ['mse', 'pearson']

# --- Target Luminosity Values ---
# Target luminosity points for which currents vs position plots are generated
TARGET_LUMINOSITIES = [0.8, 3.1, 6.5]  # Default target luminosities in fb^-1
