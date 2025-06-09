"""
Configuration file for plotting options and settings.
This file contains settings related to plot appearance, data averaging, and data processing options.
"""
import os
import importlib.util

# Default configuration values
# These may be overridden by local_config.py if it exists

# --- Data Processing Settings ---
# Mode for current-temperature adjustment: 'adjust_sim', 'adjust_real', or 'adjust_both'
CURRENT_TEMP_MODE = 'adjust_sim'

# Reference temperature for adjusting currents (in Kelvin)
REFERENCE_TEMPERATURE = 273.35

# Temperature correction settings
TEMPERATURE_CORRECTION_ENABLED = True  # Whether to apply temperature correction
TEMPERATURE_CORRECTION_DELTA = 3     # Correction value in Kelvin

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

# Try to import local_config.py if it exists
LOCAL_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'local_config.py')
if os.path.exists(LOCAL_CONFIG_PATH):
    spec = importlib.util.spec_from_file_location('local_config', LOCAL_CONFIG_PATH)
    local_config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(local_config)
    
    # Override settings from local_config.py
    for attr in dir(local_config):
        if not attr.startswith('_'):  # Skip private attributes
            globals()[attr] = getattr(local_config, attr)
    print(f"Loaded local configuration from {LOCAL_CONFIG_PATH}")

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

# --- Ratio Plot Settings ---
# Whether to show ratio (Simulated/Real) subplot
SHOW_RATIO = True
# Whether to show ratio for multiple sensors plots
SHOW_RATIO_FOR_MULTIPLE_SENSORS = True
# Height ratio of the ratio subplot (relative to main plot)
RATIO_PLOT_HEIGHT = 0.2

# --- Fit Quality Metrics ---
# Available metrics: 'mse', 'rmse', 'mae', 'r2', 'pearson', 'spearman', 'all'
# Use 'all' to calculate all metrics, or list specific metrics to calculate
FIT_QUALITY_METRICS = 'all'  # Can be a string ('all') or a list of specific metrics, e.g. ['mse', 'pearson']
