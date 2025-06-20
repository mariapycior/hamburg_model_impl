import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from params import Parameters
from config import SIMULATION_PERIOD, TEMPERATURE_CORRECTION_ENABLED, TEMPERATURE_CORRECTION_DELTA, CROSS_SECTIONS
from config_plot import (
    CURRENT_TEMP_MODE, REFERENCE_TEMPERATURE,
    USE_LINES_FOR_SIMULATION, SHOW_ERROR_BANDS, ERROR_PERCENTAGE, PLOT_RESAMPLING_PERIOD,
    SCATTER_MARKER_SIZE, LINE_WIDTH, ERROR_BAND_ALPHA, REAL_DATA_COLOR, SIMULATED_DATA_COLOR, ERROR_BAND_COLOR,
    DEFAULT_FIGURE_SIZE, MULTI_SUBPLOT_FIGURE_SIZE, ERROR_BAND_ZORDER, DATA_ZORDER,
    SHOW_RATIO_FOR_SINGLE_SENSOR, RATIO_PLOT_HEIGHT, SENSOR_GROUPING_MODE, GROUP_COLORS
)
from VeloDetectorElement import VeloDetectorElement
import matplotlib.gridspec as gridspec


def plot_group_averages(df_group_averages):
    """
    Plot average simulated and real leakage currents for each group on separate subplots.
    df_group_averages: DataFrame with columns sim_* and real_* (index: time)
    """
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec
    import numpy as np
    from config_plot import (
        SIMULATED_DATA_COLOR, REAL_DATA_COLOR, DEFAULT_FIGURE_SIZE, LINE_WIDTH, 
        SCATTER_MARKER_SIZE, SENSOR_GROUPING_MODE, RATIO_PLOT_HEIGHT, SHOW_RATIO_FOR_SINGLE_SENSOR
    )
    import groups
    # Extract group names
    group_names = []
    # Pobieramy tylko nazwy grup bez kolumn *_std
    for col in df_group_averages.columns:
        if col.startswith('sim_') and not col.endswith('_std'):
            group_names.append(col[4:])
    n_groups = len(group_names)
    if n_groups == 0:
        print("No data to plot group averages.")
        return

    # Get title for the grouping mode
    grouping_mode = SENSOR_GROUPING_MODE if hasattr(groups, 'group_modes') and SENSOR_GROUPING_MODE in groups.group_modes else 'none'
    suptitle = groups.group_modes[grouping_mode]['title'] if grouping_mode in groups.group_modes else 'Average Leakage Current per Group'

    # Create figure with appropriate size
    if n_groups > 2:
        fig_width = DEFAULT_FIGURE_SIZE[0] * 1.5
    else:
        fig_width = DEFAULT_FIGURE_SIZE[0]
    fig_height = DEFAULT_FIGURE_SIZE[1]
    fig = plt.figure(figsize=(fig_width, fig_height))
    
    # Add main title to figure
    fig.suptitle(suptitle, fontsize=12, y=0.98)

    # Find common x/y limits
    x_min, x_max = df_group_averages.index.min(), df_group_averages.index.max()
    y_min = float('inf')
    y_max = float('-inf')
    for group in group_names:
        sim_col = f"sim_{group}"
        real_col = f"real_{group}"
        for col in [sim_col, real_col]:
            if col in df_group_averages:
                vals = df_group_averages[col].dropna()
                if not vals.empty:
                    y_min = min(y_min, vals.min())
                    y_max = max(y_max, vals.max())
    # Fallback if no data
    if y_min == float('inf') or y_max == float('-inf'):
        y_min, y_max = 0, 1
    
    # Use original figure size
    # Fix width for all group counts, avoid making it too wide
    if n_groups > 2:
        fig_width = DEFAULT_FIGURE_SIZE[0] * 1.5
    else:
        fig_width = DEFAULT_FIGURE_SIZE[0]
    fig_height = DEFAULT_FIGURE_SIZE[1]
    fig = plt.figure(figsize=(fig_width, fig_height))
    
    # Create a GridSpec for each group (2 rows if ratio enabled, 1 row otherwise)
    if SHOW_RATIO_FOR_SINGLE_SENSOR:
        fig_gs = gridspec.GridSpec(2, n_groups, height_ratios=[1-RATIO_PLOT_HEIGHT, RATIO_PLOT_HEIGHT])
    else:
        fig_gs = gridspec.GridSpec(1, n_groups)
    
    # Store all axes for later reference
    main_axes = []
    ratio_axes = []
    
    # Calculate global ratio range for all groups
    all_ratio_values = []
    for group in group_names:
        sim_col = f"sim_{group}"
        real_col = f"real_{group}"
        
        if sim_col in df_group_averages and real_col in df_group_averages:
            sim_data = df_group_averages[sim_col]
            real_data = df_group_averages[real_col]
            common_index = sim_data.index.intersection(real_data.index)
            
            for idx in common_index:
                sim_val = sim_data.loc[idx]
                real_val = real_data.loc[idx]
                if not np.isnan(sim_val) and not np.isnan(real_val) and real_val != 0:
                    all_ratio_values.append(sim_val / real_val)
    
    for i, group in enumerate(group_names):
        sim_col = f"sim_{group}"
        real_col = f"real_{group}"
        
        # Create main axis
        ax_main = plt.subplot(fig_gs[0, i])
        main_axes.append(ax_main)
        
        # Add subplot title with group name
        if group == 'all':
            ax_main.set_title('Mean Values from All Sensors', fontsize=10)
            add_parameter_info(ax_main, loc='upper left')
        else:
            ax_main.set_title(f'Group: {group}', fontsize=10)
        
        # Plot data on main axis
        sim_data = None
        real_data = None
        
        if sim_col in df_group_averages:
            sim_data = df_group_averages[sim_col]
            ax_main.plot(df_group_averages.index, sim_data, color=SIMULATED_DATA_COLOR, linewidth=LINE_WIDTH, label='Simulated')
            
            # Dodajemy band dla odchylenia standardowego
            if f'sim_{group}_std' in df_group_averages:
                std_data = df_group_averages[f'sim_{group}_std']
                ax_main.fill_between(
                    df_group_averages.index,
                    sim_data - std_data,
                    sim_data + std_data,
                    color=ERROR_BAND_COLOR,
                    alpha=ERROR_BAND_ALPHA,
                    label='Sim ± std'
                )
        
        if real_col in df_group_averages:
            real_data = df_group_averages[real_col]
            ax_main.scatter(df_group_averages.index, real_data, color=REAL_DATA_COLOR, s=SCATTER_MARKER_SIZE, label='Measured')
        
        # ax_main.set_title(f'Group: {group}')
        ax_main.set_ylabel('Average Leakage Current [mA]')
        ax_main.set_xlim(x_min, x_max)
        ax_main.set_ylim(y_min, y_max)
        ax_main.grid(True)
        
        # Double density grid on y axis
        import matplotlib.ticker as mticker
        ax_main.yaxis.set_minor_locator(mticker.AutoMinorLocator(2))
        ax_main.grid(which='minor', axis='y', linestyle=':', alpha=0.4)
        ax_main.legend(fontsize=7, loc='best')
        
        # Add ratio subplot if enabled and both sim and real data exist
        if SHOW_RATIO_FOR_SINGLE_SENSOR and sim_data is not None and real_data is not None:
            # Hide x-labels on main plot
            plt.setp(ax_main.get_xticklabels(), visible=False)
            
            # Create ratio axis
            ax_ratio = plt.subplot(fig_gs[1, i], sharex=ax_main)
            ratio_axes.append(ax_ratio)
            
            # Calculate ratio where both values exist
            common_index = sim_data.index.intersection(real_data.index)
            ratio_values = []
            x_values = []
            
            for idx in common_index:
                sim_val = sim_data.loc[idx]
                real_val = real_data.loc[idx]
                if not np.isnan(sim_val) and not np.isnan(real_val) and real_val != 0:
                    ratio_values.append(sim_val / real_val)
                    x_values.append(idx)
            
            if x_values:  # Only proceed if we have ratio data
                # Plot ratio
                ax_ratio.scatter(x_values, ratio_values, color='black', s=SCATTER_MARKER_SIZE, alpha=0.7)
                ax_ratio.axhline(y=1.0, color='gray', linestyle='-', alpha=0.7)  # Solid reference line at ratio = 1
                
                # Set ratio plot labels and grid
                ax_ratio.set_ylabel('Sim/Meas')
                ax_ratio.set_xlabel('Year')
                ax_ratio.grid(True)
                
                # Double density grid on y axis for ratio plot - spójnie z głównym wykresem
                ax_ratio.yaxis.set_minor_locator(mticker.AutoMinorLocator(2))
                ax_ratio.grid(which='minor', axis='y', linestyle=':', alpha=0.4)
                
                # Use global ratio limits calculated earlier for consistent y-axis range across all plots
                # The limits will be applied after all plots are created
        else:
            # If no ratio plot, configure x-axis on main plot
            for label in ax_main.get_xticklabels():
                label.set_rotation(45)
                label.set_ha('right')
    
    # Configure x-axis labels on ratio plots
    for ax in ratio_axes:
        for label in ax.get_xticklabels():
            label.set_rotation(45)
            label.set_ha('right')
    
    # Apply consistent y-axis limits to all ratio plots if we have any ratio values
    if all_ratio_values and ratio_axes:
        ratio_array = np.array(all_ratio_values)
        # Calculate global max deviation from 1.0
        max_dev = max(abs(np.nanmin(ratio_array) - 1.0), abs(np.nanmax(ratio_array) - 1.0))
        # Add 20% padding
        max_dev = max_dev * 1.2
        # Calculate limits to make 1.0 exactly in the middle
        ylim_low = 1.0 - max_dev
        ylim_high = 1.0 + max_dev
        
        # Make sure lower limit is not negative
        if ylim_low < 0:
            ylim_low = 0
            # If we had to adjust the lower limit, also adjust the upper limit to keep 1.0 in the middle
            ylim_high = 1.0 + (1.0 - ylim_low)
            
        # Apply the same limits to all ratio plots
        for ax in ratio_axes:
            ax.set_ylim(ylim_low, ylim_high)
    
    # Add overall title - zmniejszony rozmiar i obniżona pozycja
    # fig.suptitle(f'Mean values: {suptitle}', fontsize=12, y=0.98)
    
    # Adjust layout
    if ratio_axes:
        plt.subplots_adjust(hspace=0.1)  # Reduce space between main and ratio plots
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])  # Zmniejszona przestrzeń na górze
    plt.show()

def get_group_averages(df: pd.DataFrame, sensors: list):
    """
    Zwraca DataFrame ze średnimi czasowymi dla każdej grupy sensorów (simulowane i real).
    Grupy pobiera z groups.py jeśli dostępne, inaczej traktuje całość jako jedną grupę.
    """
    try:
        import groups
        grouping_mode = SENSOR_GROUPING_MODE if 'SENSOR_GROUPING_MODE' in globals() else 'none'
        if hasattr(groups, 'group_modes') and grouping_mode in groups.group_modes:
            group_defs = groups.group_modes[grouping_mode]['groups']
        else:
            group_defs = [(sensors, 'all', 0)]
    except ImportError:
        group_defs = [(sensors, 'all', 0)]

    result = {}
    for group_sensors, group_label, _ in group_defs:
        sim_cols = [f"current_{s}" for s in group_sensors if f"current_{s}" in df.columns]
        real_cols = [f"real_current_{s}" for s in group_sensors if f"real_current_{s}" in df.columns]
        if sim_cols:
            result[f"sim_{group_label}"] = df[sim_cols].mean(axis=1)
            result[f"sim_{group_label}_std"] = df[sim_cols].std(axis=1)
        if real_cols:
            result[f"real_{group_label}"] = df[real_cols].mean(axis=1)
    if result:
        out_df = pd.DataFrame(result, index=df.index)
        return out_df
    else:
        return pd.DataFrame(index=df.index)

def add_parameter_info(ax, loc='upper left'):
    params = Parameters()
    timestep = pd.to_timedelta(SIMULATION_PERIOD.lower()).total_seconds() / 3600
    
    param_text = (
        f"$\sigma$ (7 TeV), $\sigma$ (13 TeV) = {CROSS_SECTIONS}\n"
        f"$\\alpha_I$: {params.alpha_I:.2e} A/cm\n"
        f"$\\alpha_0^*$: {params.alpha_0_star:.2e} A/cm\n"
        f"$\\beta$: {params.beta:.2e} A/cm\n"
        f"$E_I$: {params.E_I:.2f} eV\n"
        f"$V$: {params.V:.3f} cm$^3$\n"
        f"$E_{{eff}}$: {params.E_eff:.2f} eV\n"
        f"Simulation timestep: {timestep:.1f} h"
    )
    
    # Add resampling period information
    if PLOT_RESAMPLING_PERIOD:
        # Convert shorthand period to more readable format
        period_display = PLOT_RESAMPLING_PERIOD
        if period_display == '1W':
            period_display = '1 week'
        elif period_display.endswith('W'):
            period_display = period_display.replace('W', ' weeks')
        elif period_display == '1D':
            period_display = '1 day'
        elif period_display.endswith('D'):
            period_display = period_display.replace('D', ' days')
        
        param_text += f"\nData averaged over {period_display}"
    
    temp_info = ""
    if CURRENT_TEMP_MODE == 'adjust_real':
        temp_info = "Adjusted meas. to ref. temperature"
    elif CURRENT_TEMP_MODE == 'adjust_sim':
        temp_info = "Adjusted ref. to meas. temperature"
    elif CURRENT_TEMP_MODE == 'adjust_both':
        temp_info = f"Adjusted both to {REFERENCE_TEMPERATURE:.2f} K"
    
    if temp_info:
        # Formatujemy tekst z jawnie dodanymi spacjami w LaTeX
        if CURRENT_TEMP_MODE == 'adjust_both':
            param_text += f"\n$\\mathbf{{Adjusted\\ both\\ to\\ {REFERENCE_TEMPERATURE:.2f}\\ K}}$"
        else:
            param_text += f"\n$\\mathbf{{{temp_info.replace(' ', '\\ ')}}}$"
        
    if TEMPERATURE_CORRECTION_ENABLED:
        param_text += f"\nTemp. correction: +{TEMPERATURE_CORRECTION_DELTA} K"
    
    props = dict(boxstyle='round', facecolor='white', alpha=0.7)
    
    # Ustaw pozycję na podstawie parametru loc
    x, y = 0.02, 0.98  # domyślnie upper left
    halign, valign = 'left', 'top'
    
    if loc == 'upper right':
        x, y = 0.98, 0.98
        halign = 'right'
    elif loc == 'lower left':
        x, y = 0.02, 0.02
        valign = 'bottom'
    elif loc == 'lower right':
        x, y = 0.98, 0.02
        halign, valign = 'right', 'bottom'
    
    ax.text(x, y, param_text, transform=ax.transAxes, fontsize=8,
            verticalalignment=valign, horizontalalignment=halign, bbox=props)



def get_sensor_number(sensor_code):
    """Get sensor number from sensor code using VeloDetectorElement."""
    try:
        velo_det = VeloDetectorElement()
        # The sensor code is assumed to be in format like 'VL01_CT' or 'PU02_AB'
        # We need to add 'HV' to match the key format in VeloDetectorElement
        sensor_key = (sensor_code, 'HV')
        if sensor_key in velo_det.__members__['__Velo_Det__']:
            # Sensor number is at index 1
            return velo_det.__members__['__Velo_Det__'][sensor_key][1]
        return sensor_code  # Return original code if not found
    except Exception as e:
        print(f"Error getting sensor number for {sensor_code}: {e}")
        return sensor_code  # Return original code on error


def setup_subplot(ax, x_data, y_data, color, label, title, ylabel, xlim, ylim=None, use_line=None, show_error_band=None, is_current_plot=False, force_no_error=False):
    use_line = USE_LINES_FOR_SIMULATION if use_line is None else use_line
    show_error_band = SHOW_ERROR_BANDS if show_error_band is None else show_error_band
    if force_no_error:
        show_error_band = False
    y_data_series = pd.Series(y_data, index=x_data)
    y_data_series = y_data_series.sort_index()
    if use_line and show_error_band and is_current_plot:
        error_value = y_data_series * (ERROR_PERCENTAGE / 100)
        ax.fill_between(
            y_data_series.index, 
            y_data_series - error_value, 
            y_data_series + error_value, 
            color=ERROR_BAND_COLOR, 
            alpha=ERROR_BAND_ALPHA, 
            label=f'{ERROR_PERCENTAGE}% Error Band',
            zorder=ERROR_BAND_ZORDER
        )
    if use_line:
        ax.plot(y_data_series.index, y_data_series.values, color=color, linewidth=LINE_WIDTH, label=label, zorder=DATA_ZORDER)
    else:
        ax.scatter(y_data_series.index, y_data_series.values, color=color, s=SCATTER_MARKER_SIZE, label=label, zorder=DATA_ZORDER)
    ax.set_xlim(xlim)
    if ylim:
        ax.set_ylim(ylim)
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=10)
    ax.grid(True)
    ax.legend()


def plot_leakage_current(df: pd.DataFrame, sensor_name: str):
    sim_col = f"current_{sensor_name}"
    real_col = f"real_current_{sensor_name}"
    temp_col = f"temperature_{sensor_name}"
    fluence_col = f"fluence_{sensor_name}"
    
    if sim_col not in df.columns:
        raise ValueError(f"Simulated current column not found for sensor {sensor_name}")

    # Zakres czasu: cały zakres dostępny w df
    start_date = df.index.min()
    end_date = df.index.max()

    fig, axes = plt.subplots(4, 1, figsize=MULTI_SUBPLOT_FIGURE_SIZE)
    
    sensor_number = get_sensor_number(sensor_name)
    
    setup_subplot(axes[0], df.index, df[sim_col], SIMULATED_DATA_COLOR, 'Leakage Current Simulated', 
                 f'Simulated Leakage Current for Sensor {sensor_number}', 'Leakage Current (mA)', 
                 (start_date, end_date), use_line=True, show_error_band=True, is_current_plot=True, force_no_error=False)
    
    if real_col in df.columns:
        setup_subplot(axes[1], df.index, df[real_col], REAL_DATA_COLOR, 'Leakage Current (Measured Data)', 
                     f'Measured Leakage Current for Sensor {sensor_number}', 'Leakage Current [mA]', 
                     (start_date, end_date), use_line=False, show_error_band=False, is_current_plot=True, force_no_error=False)
    
    if fluence_col in df.columns:
        setup_subplot(axes[2], df.index, df[fluence_col], 'green', 'Fluence', 
                     'Fluence', 'Fluence (n/cm²)', (start_date, end_date), use_line=False, show_error_band=False, is_current_plot=False, force_no_error=False)
    
    if temp_col in df.columns:
        setup_subplot(axes[3], df.index, df[temp_col], 'magenta', 'Temperature', 
                     'Temperature', 'Temperature (K)', (start_date, end_date), use_line=False, show_error_band=False, is_current_plot=False, force_no_error=False)

    plt.tight_layout()
    # Wykres gotowy do wyświetlenia


def plot_simulated_vs_real(df: pd.DataFrame, sensor_name: str):

    sim_col = f"current_{sensor_name}"
    real_col = f"real_current_{sensor_name}"
    
    if sim_col not in df.columns and real_col not in df.columns:
        print(f"No data found for sensor {sensor_name}")
        return
        
    sensor_number = get_sensor_number(sensor_name)

    temp_df = df.copy()


    # Check if ratio plot should be shown
    show_ratio = SHOW_RATIO_FOR_SINGLE_SENSOR and sim_col in temp_df.columns and real_col in temp_df.columns
    
    # Create appropriate figure layout
    if show_ratio:
        # Create figure with GridSpec for main plot and ratio subplot
        fig = plt.figure(figsize=DEFAULT_FIGURE_SIZE)
        gs = gridspec.GridSpec(2, 1, height_ratios=[1-RATIO_PLOT_HEIGHT, RATIO_PLOT_HEIGHT])
        ax_main = fig.add_subplot(gs[0])
        ax_ratio = fig.add_subplot(gs[1], sharex=ax_main)
        ax = ax_main  # For compatibility with existing code
    else:
        # Standard figure with a single plot
        fig, ax = plt.subplots(figsize=DEFAULT_FIGURE_SIZE)
    
    # Używamy danych z ramki danych do ustawienia zakresu osi x
    ax.set_xlim(df.index.min(), df.index.max())


    real_data = None
    if real_col in temp_df.columns:
        real_data = temp_df[real_col].dropna()
        if not real_data.empty:
            ax.scatter(real_data.index, real_data, color=REAL_DATA_COLOR, s=SCATTER_MARKER_SIZE, 
                      label='Measured Leakage Current', zorder=DATA_ZORDER)
    
    sim_data = None
    if sim_col in temp_df.columns:
        sim_data = temp_df[sim_col].dropna()
        if not sim_data.empty:
            sim_data = sim_data.sort_index()
            ax.plot(sim_data.index, sim_data, color=SIMULATED_DATA_COLOR, linewidth=LINE_WIDTH, 
                    label='Simulated Leakage Current', zorder=DATA_ZORDER)

    add_parameter_info(ax)
    
    ax.set_ylabel('Leakage Current (mA)')
    
    # Dodaj etykietę Year tylko jeśli nie ma ratio
    if not show_ratio:
        ax.set_xlabel('Year')
    ax.grid(True)
    ax.legend()
    
    # Add ratio plot if enabled
    if show_ratio and real_data is not None and sim_data is not None:
        # Find common timestamps where both sim and real data exist
        common_indices = real_data.index.intersection(sim_data.index)
        if len(common_indices) > 0:
            # Calculate ratio for common timestamps
            ratio = sim_data.loc[common_indices] / real_data.loc[common_indices]
            
            # Plot ratio data
            ax_ratio.scatter(common_indices, ratio, color='black', s=SCATTER_MARKER_SIZE, alpha=0.7)
            ax_ratio.axhline(y=1.0, color='gray', linestyle='-', alpha=0.7)  # Reference line at ratio = 1
            
            # Set ratio plot labels and grid
            ax_ratio.set_ylabel('Sim/Meas')
            ax_ratio.set_xlabel('Year')
            ax_ratio.grid(True, alpha=0.3)
            
            # Save reference to ratio axes for later checks
            fig.ratio_axes = True
            
            # Hide x-labels on main plot
            plt.setp(ax_main.get_xticklabels(), visible=False)
            
            # Set y-axis limits so that 1.0 is in the middle
            max_dev = max(abs(np.nanmin(ratio) - 1.0), abs(np.nanmax(ratio) - 1.0))
            # Add 20% padding
            max_dev = max_dev * 1.2
            ylim_low = max(0, 1.0 - max_dev)
            ylim_high = 1.0 + max_dev
            ax_ratio.set_ylim(ylim_low, ylim_high)
    
    plt.tight_layout()
    if show_ratio:
        plt.subplots_adjust(hspace=0.05)  # Reduce space between plots


def plot_sensors_data(df: pd.DataFrame, sensors: list, column_prefix: str, title: str, y_range: tuple = None):
    fig, ax = plt.subplots(figsize=DEFAULT_FIGURE_SIZE)
    columns = []
    
    temp_df = df.copy()
    # Zakres X ustawiany na podstawie danych, nie na podstawie argumentów
    start_date = df.index.min()
    end_date = df.index.max()
    
    for sensor in sensors:
        col_name = f"{column_prefix}_{sensor}"
        if col_name in temp_df.columns:
            columns.append(col_name)
            y = temp_df[col_name]
            y_clean = y.dropna()
            if not y_clean.empty:
                # Use the group_modes structure from groups.py for sensor grouping
                from groups import group_modes
                
                # Determine color and group based on the selected grouping mode
                sensor_color = None
                sensor_group = f"Sensor {get_sensor_number(sensor)}"  # Default group name
                
                if SENSOR_GROUPING_MODE != 'none' and SENSOR_GROUPING_MODE in group_modes:
                    # Get the groups for the selected mode
                    mode_info = group_modes[SENSOR_GROUPING_MODE]
                    found = False
                    
                    # Check each group in the selected mode
                    for sensor_list, group_label, color_idx in mode_info['groups']:
                        if sensor in sensor_list:
                            # Use color from GROUP_COLORS and label from group_modes
                            sensor_color = GROUP_COLORS[SENSOR_GROUPING_MODE][color_idx % len(GROUP_COLORS[SENSOR_GROUPING_MODE])]
                            sensor_group = group_label
                            found = True
                            break
                    
                    # If sensor doesn't belong to any group
                    if not found:
                        sensor_color = 'gray'
                        sensor_group = 'Other'
                
                # Save sensor information for later use when calculating means
                if not hasattr(plot_sensors_data, 'sensor_groups'):
                    plot_sensors_data.sensor_groups = {}
                    
                # Store the legend title for the current grouping mode
                if SENSOR_GROUPING_MODE in group_modes:
                    plot_sensors_data.legend_title = group_modes[SENSOR_GROUPING_MODE]['title']
                else:
                    plot_sensors_data.legend_title = "Sensor Groups"
                
                if sensor_group not in plot_sensors_data.sensor_groups:
                    plot_sensors_data.sensor_groups[sensor_group] = {
                        'sensors': [],
                        'color': sensor_color,
                        'label': sensor_group,
                        'columns': []
                    }
                
                if sensor not in plot_sensors_data.sensor_groups[sensor_group]['sensors']:
                    plot_sensors_data.sensor_groups[sensor_group]['sensors'].append(sensor)
                
                col_name = f"{column_prefix}_{sensor}"
                if col_name not in plot_sensors_data.sensor_groups[sensor_group]['columns']:
                    plot_sensors_data.sensor_groups[sensor_group]['columns'].append(col_name)
                
                # Rysuj sensor z odpowiednim kolorem i etykietą grupy
                if column_prefix == "current":
                    y_sorted = y_clean.sort_index()
                    if sensor_color is None:
                        ax.plot(y_sorted.index, y_sorted.values, linewidth=LINE_WIDTH, label=sensor_group, zorder=DATA_ZORDER)
                    else:
                        ax.plot(y_sorted.index, y_sorted.values, linewidth=LINE_WIDTH, color=sensor_color, label=sensor_group, zorder=DATA_ZORDER)
                elif column_prefix == "real_current":
                    if sensor_color is None:
                        ax.scatter(y_clean.index, y_clean.values, s=SCATTER_MARKER_SIZE, label=sensor_group, zorder=DATA_ZORDER)
                    else:
                        ax.scatter(y_clean.index, y_clean.values, s=SCATTER_MARKER_SIZE, color=sensor_color, label=sensor_group, zorder=DATA_ZORDER)
    
    # Calculate average for each sensor group instead of one global average
    if hasattr(plot_sensors_data, 'sensor_groups'):
        # Calculate and draw average for each group separately
        for group_name, group_info in plot_sensors_data.sensor_groups.items():
            group_columns = group_info['columns']
            if not group_columns:
                continue  # Skip groups without data
                
            # Calculate average for the group
            data_df = df[group_columns]
            valid_count = data_df.notna().sum(axis=1)
            mean_data = data_df.mean(axis=1)
            
            # Ignore points where we have too few data
            mean_data[valid_count <= (len(group_columns) // 2)] = float('nan')
            mean_data = mean_data.sort_index()
            # Set color - darker shade of the group color
            base_color = group_info['color']
            if base_color == 'gray' or base_color is None:
                mean_color = 'black'  # Default color for groups without a specified color
            else:
                # Convert color to RGB and darken
                from matplotlib.colors import to_rgb, to_hex
                r, g, b = to_rgb(base_color)
                # Darken the color by multiplying by 0.6
                mean_color = to_hex((r*0.6, g*0.6, b*0.6))
            
            # Draw the group average (without label - we'll add a single common info about averages later)
            ax.plot(mean_data.index, mean_data.values, color=mean_color, linewidth=3, 
                    label=None,  # No separate label for each average
                    zorder=DATA_ZORDER+1)  # Average line should be above individual data
        
        # Clear the group dictionary at the end of the function
        # We'll keep the legend title for use in the legend
        legend_title = getattr(plot_sensors_data, 'legend_title', "Sensor Groups")
        plot_sensors_data.sensor_groups = {}
    
    # If there are no groups, calculate global average
    elif columns:
        data_df = df[columns]
        valid_count = data_df.notna().sum(axis=1)
        mean_data = data_df.mean(axis=1)
        mean_data[valid_count <= (len(columns) // 2)] = float('nan')
        mean_data = mean_data.sort_index()
        ax.plot(mean_data.index, mean_data.values, color='black', linewidth=3, 
                label=f'Mean ({"real" if column_prefix == "real_current" else "simulated"})', 
                zorder=DATA_ZORDER+1)  # Average line should be above individual data
    
    add_parameter_info(ax)
    ax.set_xlim(start_date, end_date)
    if y_range is not None:
        ax.set_ylim(y_range)
    ax.set_ylabel('Leakage Current [mA]')
    
    # Dodaj etykietę Year tylko jeśli nie ma ratio
    if not hasattr(plt.gcf(), 'ratio_axes') or not plt.gcf().ratio_axes:
        ax.set_xlabel('Year')
    ax.set_title(title, fontsize=10)
    
    ax.grid(True)
    
    # Double density grid on y axis - spójnie z innymi wykresami
    import matplotlib.ticker as mticker
    ax.yaxis.set_minor_locator(mticker.AutoMinorLocator(2))
    ax.grid(which='minor', axis='y', linestyle=':', alpha=0.4)
    plt.tight_layout()
    # Show legend with unique entries and appropriate title based on grouping mode
    from collections import OrderedDict
    
    # Get legend elements (handles and labels)
    handles, labels = ax.get_legend_handles_labels()
    
    # Remove duplicates while preserving order
    by_label = OrderedDict(zip(labels, handles))
    unique_handles = list(by_label.values())
    unique_labels = list(by_label.keys())
    
    # Add information about averages to the legend
    if SENSOR_GROUPING_MODE != 'none':
        # If grouping is enabled, add a single entry for all mean lines
        from matplotlib.lines import Line2D
        mean_line = Line2D([0], [0], color='black', linewidth=3)
        unique_handles.append(mean_line)
        unique_labels.append("Bold lines: Group averages")
    
    # Get the legend title based on the current grouping mode
    legend_title = getattr(plot_sensors_data, 'legend_title', "Sensor Groups")
    
    # Add legend only if we have unique labels
    if unique_labels:
        legend = ax.legend(unique_handles, unique_labels, loc='best', framealpha=0.7, title=legend_title, fontsize=7)
        # Make the legend title bold
        plt.setp(legend.get_title(), fontweight='bold')
    
    
        
    # Wykres gotowy do wyświetlenia

def plot_all_sensors(df: pd.DataFrame, sensors: list):
    # Najpierw przygotuj dane i znajdź globalny zakres osi Y dla obu wykresów
    temp_df = df.copy()
    
    # Oblicz globalny zakres osi Y
    min_val = float('inf')
    max_val = float('-inf')
    
    # Zbierz wszystkie kolumny z danymi (symulowanymi i rzeczywistymi)
    all_columns = []
    
    for sensor in sensors:
        sim_col = f"current_{sensor}"
        real_col = f"real_current_{sensor}"
        
        if sim_col in temp_df.columns:
            all_columns.append(sim_col)
        if real_col in temp_df.columns:
            all_columns.append(real_col)
    
    # Oblicz min i max dla wszystkich danych
    if all_columns:
        data_subset = temp_df[all_columns].dropna(how='all')
        if not data_subset.empty:
            # Dodaj 10% marginesu
            curr_min = data_subset.min().min()
            curr_max = data_subset.max().max()
            
            if not (pd.isna(curr_min) or pd.isna(curr_max)):
                min_val = min(min_val, curr_min)
                max_val = max(max_val, curr_max)
    
    # Ustaw wspólny zakres osi Y z 10% marginesem
    if min_val != float('inf') and max_val != float('-inf'):
        y_range_margin = (max_val - min_val) * 0.1
        y_range = (max(0, min_val - y_range_margin), max_val + y_range_margin)
    else:
        y_range = None
    
    # Plot simulated current for all sensors (no error bands when plotting all sensors)
    plot_sensors_data(df, sensors, 'current', 'Simulated Leakage Current for All Sensors', y_range=y_range)
    
    # Plot measured current for all sensors (if available)
    plot_sensors_data(df, sensors, 'real_current', 'Measured Leakage Current for All Sensors', y_range=y_range)
    
    # Zwróć średnie grupowe (sim i real) jako DataFrame
    return get_group_averages(df, sensors)




def plot_currents_vs_parameter(df: pd.DataFrame, sensor_name: str, param_type: str = 'luminosity'):
    sensor_number = get_sensor_number(sensor_name)
    """
    Plot both simulated and real currents against a chosen parameter (integrated luminosity or cumulative fluence).
    """
    sim_col = f"current_{sensor_name}"
    real_col = f"real_current_{sensor_name}"
    
    if param_type == 'luminosity':
        param_col = "integrated_luminosity"
        x_label = 'Integrated Luminosity (fb$^{-1}$)'
        title_param = 'Integrated Luminosity'
    else:  # fluence
        delivered_fluence_col = f"delivered_fluence_{sensor_name}"
        if delivered_fluence_col not in df.columns:
            return
        param_col = delivered_fluence_col
        x_label = 'Fluence (n/cm²)'
        title_param = 'Cumulative Fluence'
    
    if param_col not in df.columns or (sim_col not in df.columns and real_col not in df.columns):
        return
    
    temp_df = df.copy()
    
    df_binned = temp_df
    
    fig, ax = plt.subplots(figsize=DEFAULT_FIGURE_SIZE)
    
    df_binned = df_binned.sort_values(by=param_col)
    
    if real_col in df_binned.columns and df_binned[real_col].notna().any():
        df_real = df_binned[[real_col, param_col]].dropna()
        ax.scatter(df_real[param_col], df_real[real_col], 
                  color=REAL_DATA_COLOR, s=SCATTER_MARKER_SIZE, 
                  label='Measured Data', zorder=DATA_ZORDER)
    
    if sim_col in df_binned.columns and df_binned[sim_col].notna().any():
        df_sim = df_binned[[sim_col, param_col]].dropna()
        ax.plot(df_sim[param_col], df_sim[sim_col], 
               color=SIMULATED_DATA_COLOR, linewidth=LINE_WIDTH, 
               label='Simulated Data', zorder=DATA_ZORDER)
    
    add_parameter_info(ax)
    ax.set_xlabel(x_label)
    ax.set_ylabel('Leakage Current (mA)')
    ax.grid(True)
    ax.legend()
    

def plot_all_currents_vs_fluence(df: pd.DataFrame, sensors: list, output_dir: str = None):
    """Plot all sensors currents against fluence in two separate plots using continuous lines.
    Both plots use the same axis scales for better comparison."""
    # Check if any sensors have fluence data
    has_fluence_data = False
    for sensor in sensors:
        fluence_col = f"delivered_fluence_{sensor}"
        if fluence_col in df.columns:
            has_fluence_data = True
            break
            
    if not has_fluence_data:
        print("No fluence data found for any sensors")
        return
    
    
    temp_df = df.copy()
    
    # First, collect all data to determine common axis limits
    all_fluence_values = []
    all_current_values = []
    sim_data_by_sensor = {}
    real_data_by_sensor = {}
    
    # Collect simulated data
    for sensor in sensors:
        sim_col = f"current_{sensor}"
        fluence_col = f"delivered_fluence_{sensor}"
        if sim_col in temp_df.columns and fluence_col in temp_df.columns:
            sim_data = temp_df[[sim_col, fluence_col]].dropna()
            if not sim_data.empty:
                sim_data = sim_data.sort_values(fluence_col)
                sim_data_by_sensor[sensor] = sim_data
                all_fluence_values.extend(sim_data[fluence_col].values)
                all_current_values.extend(sim_data[sim_col].values)
    
    # Collect real data
    for sensor in sensors:
        real_col = f"real_current_{sensor}"
        fluence_col = f"delivered_fluence_{sensor}"
        if real_col in temp_df.columns and fluence_col in temp_df.columns:
            real_data = temp_df[[real_col, fluence_col]].dropna()
            if not real_data.empty:
                real_data = real_data.sort_values(fluence_col)
                real_data_by_sensor[sensor] = real_data
                all_fluence_values.extend(real_data[fluence_col].values)
                all_current_values.extend(real_data[real_col].values)
    
    # Determine common axis limits
    if all_fluence_values and all_current_values:
        x_min = min(all_fluence_values)
        x_max = max(all_fluence_values)
        y_min = 0  # Start from 0 for currents
        y_max = max(all_current_values) * 1.1  # Add 10% margin
        
        # Plot for simulated data
        fig, ax = plt.subplots(figsize=DEFAULT_FIGURE_SIZE)
        
        for sensor, sim_data in sim_data_by_sensor.items():
            sensor_number = get_sensor_number(sensor)
            fluence_col = f"delivered_fluence_{sensor}"
            sim_col = f"current_{sensor}"
            ax.plot(sim_data[fluence_col], sim_data[sim_col], linewidth=LINE_WIDTH, label=f"Sensor {sensor_number}", zorder=DATA_ZORDER)
        
        add_parameter_info(ax)
        
        ax.set_xlabel('Fluence (n/cm²)')
        ax.set_ylabel('Leakage Current (mA)')
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.grid(True)
        plt.tight_layout()
        ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), title='Sensors', fontsize='small')
        if output_dir is not None:
            plt.savefig(os.path.join(output_dir, "all_simulated_vs_fluence.png"), bbox_inches='tight')
        
        # Plot for real data
        fig, ax = plt.subplots(figsize=DEFAULT_FIGURE_SIZE)
        
        for sensor, real_data in real_data_by_sensor.items():
            sensor_number = get_sensor_number(sensor)
            fluence_col = f"delivered_fluence_{sensor}"
            real_col = f"real_current_{sensor}"
            ax.plot(real_data[fluence_col], real_data[real_col], linewidth=LINE_WIDTH, label=f"Sensor {sensor_number}", zorder=DATA_ZORDER)
        
        add_parameter_info(ax)
        
        ax.set_xlabel('Fluence (n/cm²)')
        ax.set_ylabel('Leakage Current (mA)')
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.grid(True)
        plt.tight_layout()
        ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), title='Sensors', fontsize='small')
        if output_dir is not None:
            plt.savefig(os.path.join(output_dir, "all_real_vs_fluence.png"), bbox_inches='tight')
    else:
        print("No data available for plotting currents vs fluence")


def plot_all_currents_vs_luminosity(df: pd.DataFrame, sensors: list, output_dir: str = None):
    """Plot all sensors currents against integrated luminosity in two separate plots using continuous lines.
    Both plots use the same axis scales for better comparison."""
    if 'integrated_luminosity' not in df.columns:
        print("No integrated luminosity data found")
        return
    
    
    temp_df = df.copy()
    
    # First, collect all data to determine common axis limits
    all_lumi_values = []
    all_current_values = []
    sim_data_by_sensor = {}
    real_data_by_sensor = {}
    
    # Collect simulated data
    for sensor in sensors:
        sim_col = f"current_{sensor}"
        if sim_col in temp_df.columns:
            sim_data = temp_df[[sim_col, 'integrated_luminosity']].dropna()
            if not sim_data.empty:
                sim_data = sim_data.sort_values('integrated_luminosity')
                sim_data_by_sensor[sensor] = sim_data
                all_lumi_values.extend(sim_data['integrated_luminosity'].values)
                all_current_values.extend(sim_data[sim_col].values)
    
    # Collect real data
    for sensor in sensors:
        real_col = f"real_current_{sensor}"
        if real_col in temp_df.columns:
            real_data = temp_df[[real_col, 'integrated_luminosity']].dropna()
            if not real_data.empty:
                real_data = real_data.sort_values('integrated_luminosity')
                real_data_by_sensor[sensor] = real_data
                all_lumi_values.extend(real_data['integrated_luminosity'].values)
                all_current_values.extend(real_data[real_col].values)
    
    # Determine common axis limits
    if all_lumi_values and all_current_values:
        x_min = min(all_lumi_values)
        x_max = max(all_lumi_values)
        y_min = 0  # Start from 0 for currents
        y_max = max(all_current_values) * 1.1  # Add 10% margin
        
        # Plot for simulated data
        fig, ax = plt.subplots(figsize=DEFAULT_FIGURE_SIZE)
        
        for sensor, sim_data in sim_data_by_sensor.items():
            sensor_number = get_sensor_number(sensor)
            sim_col = f"current_{sensor}"
            ax.plot(sim_data['integrated_luminosity'], sim_data[sim_col], linewidth=LINE_WIDTH, label=f"Sensor {sensor_number}", zorder=DATA_ZORDER)
        
        add_parameter_info(ax)
        
        ax.set_xlabel('Integrated Luminosity (fb$^{-1}$)')
        ax.set_ylabel('Leakage Current (mA)')
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.grid(True)
        plt.tight_layout()
        ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), title='Sensors', fontsize='small')
        if output_dir is not None:
            plt.savefig(os.path.join(output_dir, "all_simulated_vs_luminosity.png"), bbox_inches='tight')
        
        # Plot for real data
        fig, ax = plt.subplots(figsize=DEFAULT_FIGURE_SIZE)
        
        for sensor, real_data in real_data_by_sensor.items():
            sensor_number = get_sensor_number(sensor)
            real_col = f"real_current_{sensor}"
            ax.plot(real_data['integrated_luminosity'], real_data[real_col], linewidth=LINE_WIDTH, label=f"Sensor {sensor_number}", zorder=DATA_ZORDER)
        
        add_parameter_info(ax)
        
        ax.set_xlabel('Integrated Luminosity (fb$^{-1}$)')
        ax.set_ylabel('Leakage Current (mA)')
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.grid(True)
        plt.tight_layout()
        ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), title='Sensors', fontsize='small')
        if output_dir is not None:
            plt.savefig(os.path.join(output_dir, "all_real_vs_luminosity.png"), bbox_inches='tight')
    else:
        print("No data available for plotting currents vs luminosity")


def plot_integrated_luminosity(df: pd.DataFrame):
    """Plot integrated luminosity over time."""
    try:
        plt.figure(figsize=DEFAULT_FIGURE_SIZE)
        df['integrated_luminosity'].plot(zorder=DATA_ZORDER)
        plt.title('Integrated Luminosity vs Time')
        plt.xlabel('Time')
        plt.ylabel('Integrated Luminosity (fb$^{-1}$)')
        plt.grid(True)
        
            
        # Wykres gotowy do wyświetlenia
        print("Created integrated luminosity plot")
    except Exception as e:
        print(f"Error creating integrated luminosity plot: {e}")



def plot_currents_vs_position(summary_df: pd.DataFrame, target_luminosities: list, output_path: str = None):
    """
    Plot simulated and real currents against sensor position.
    Args:
        summary_df: DataFrame from create_sensor_summary with columns [current_sim, current_real, position, luminosity]
        target_luminosities: List of target luminosity values used for the plot
        
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    
    markers = ['o', '^', 's', 'D']
    colors = ['blue', 'red', 'green', 'purple']
    
    for i, target_lumi in enumerate(target_luminosities):
        lumi_str = f'_f{target_lumi:.1f}'
        sim_col = f'current_sim{lumi_str}'
        real_col = f'current_real{lumi_str}'
        
        positions = summary_df['position'].values
        sim_values = summary_df[sim_col].values if sim_col in summary_df.columns else None
        real_values = summary_df[real_col].values if real_col in summary_df.columns else None
        
        if sim_values is None and real_values is None:
            continue
            
        color_idx = i % len(colors)
        marker_idx = i % len(markers)
        
        if sim_values is not None:
            ax.scatter(positions, sim_values, 
                      color=colors[color_idx], marker=markers[marker_idx],
                      s=20, label=f'Sim @ {target_lumi} fb$^{{-1}}$', 
                      zorder=10)
            
        if real_values is not None:
            ax.scatter(positions, real_values, 
                      edgecolor=colors[color_idx], marker=markers[marker_idx],
                      facecolor='none', s=20, 
                      label=f'Meas @ {target_lumi} fb$^{{-1}}$', zorder=10)
    
    add_parameter_info(ax, loc='upper right')
    
    ax.set_xlabel('Sensor Z Position (mm)')
    ax.set_ylabel('Leakage Current [mA]')
    ax.grid(True)
    ax.legend(fontsize=7, loc='upper left')
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path)
