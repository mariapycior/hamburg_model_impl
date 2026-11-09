"""
Configuration file for plotting options and settings.
This file contains settings related to plot appearance, data averaging, and data processing options.
"""

# --- Data Processing Settings ---
# Mode for current-temperature adjustment: 'adjust_sim', 'adjust_real', or 'adjust_both'
CURRENT_TEMP_MODE = 'adjust_both'

# Reference temperature for adjusting currents (in Kelvin)
REFERENCE_TEMPERATURE = 273.15

# Temperature correction settings
TEMPERATURE_CORRECTION_ENABLED = False # Whether to apply temperature correction
TEMPERATURE_CORRECTION_DELTA = 3.2     # Correction value in Kelvin

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

# --- Color Settings ---
# Paleta kolorów dla 5 sensorów z trzema odcieniami dla każdego
# Format: [light (punkty), medium (symulacja), light_alpha (pasek błędu)]
COLOR_PALETTES = {
    0: ['#32CD32', '#006400', '#CCFFCC'],  # Zielony: jasny, średni, bardzo jasny
    1: ['#1E90FF', '#0066CC', '#CCECFF'],  # Niebieski: jasny, średni, bardzo jasny
    2: ['#9370DB', '#6A359C', '#E6E6FA'],  # Fioletowy: jasny, średni, bardzo jasny
    3: ['#FFA500', '#CC8400', '#FFE5B4'],  # Pomarańczowy: jasny, średni, bardzo jasny
    4: ['#FF4500', '#CC3700', '#FFCCCC'],   # Czerwony: jasny, średni, bardzo jasny
}

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
DEFAULT_FIGURE_SIZE = (3.5, 5)

# Figure size for multi-subplot plots
MULTI_SUBPLOT_FIGURE_SIZE = (3.5, 5)

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
SHOW_RATIO = True  # Global toggle for ratio on multi-sensor plots
SHOW_RATIO_FOR_MULTIPLE_SENSORS = True  # Enable ratio subplot when plotting multiple sensors

# --- Parameter Info Box Settings ---
SHOW_PARAMETER_INFO_BOX = True
SHOW_PLOT_TITLES = False

PARAMETER_INFO_FIELDS = {
    'alpha_I': False,
    'alpha_0_star': False,
    'beta': False,
    'E_I': False,
    'V': False,
    'E_eff': False,
    'cross_sections': False,
    'timestep': False,
    'resampling': False,
    'temperature_adjustment': True,
    'temperature_correction': True,
    'thermistor': False,
    'luminosity_mode': False,
}

# --- Sensor Grouping Settings ---
# Grouping mode: 'none', 'side', 'type', 'z_position', 'tb'
SENSOR_GROUPING_MODE = 'all'

# Colors for different groups
GROUP_COLORS = {
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
TARGET_LUMINOSITIES = [0.8, 2.7, 3.1, 6.5]  # Default target luminosities in fb^-1
