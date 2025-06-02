import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from params import Parameters
from config import SIMULATION_PERIOD, TEMPERATURE_CORRECTION_ENABLED, TEMPERATURE_CORRECTION_DELTA
from config_plot import (
    CURRENT_TEMP_MODE, REFERENCE_TEMPERATURE,
    USE_LINES_FOR_SIMULATION, SHOW_ERROR_BANDS, ERROR_PERCENTAGE, PLOT_RESAMPLING_PERIOD,
    SCATTER_MARKER_SIZE, LINE_WIDTH, ERROR_BAND_ALPHA, REAL_DATA_COLOR, SIMULATED_DATA_COLOR, ERROR_BAND_COLOR,
    DEFAULT_FIGURE_SIZE, MULTI_SUBPLOT_FIGURE_SIZE, ERROR_BAND_ZORDER, DATA_ZORDER,
    SENSOR_GROUPING_MODE, GROUP_COLORS
)
from VeloDetectorElement import VeloDetectorElement


def add_parameter_info(ax, loc='upper left'):
    params = Parameters()
    timestep = pd.to_timedelta(SIMULATION_PERIOD.lower()).total_seconds() / 3600
    
    param_text = (
        f"$\\alpha_I$: {params.alpha_I:.2e} A/cm\n"
        f"$\\alpha_0^*$: {params.alpha_0_star:.2e} A/cm\n"
        f"$\\beta$: {params.beta:.2e} A/cm\n"
        f"$E_I$: {params.E_I:.2f} eV\n"
        f"$V$: {params.V:.3f} cm$^3$\n"
        f"$E_{{eff}}$: {params.E_eff:.2f} eV\n"
        f"Timestep: {timestep:.1f} h"
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
        temp_info = "Adjusted real to sim. temperature"
    elif CURRENT_TEMP_MODE == 'adjust_sim':
        temp_info = "Adjusted sim. to real temperature"
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
        line = ax.plot(y_data_series.index, y_data_series.values, color=color, linewidth=LINE_WIDTH, label=label, zorder=DATA_ZORDER)
    else:
        ax.scatter(y_data_series.index, y_data_series.values, color=color, s=SCATTER_MARKER_SIZE, label=label, zorder=DATA_ZORDER)
    
    ax.set_xlim(xlim)
    if ylim:
        ax.set_ylim(ylim)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
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
                 (start_date, end_date), is_current_plot=True)
    
    if real_col in df.columns:
        setup_subplot(axes[1], df.index, df[real_col], REAL_DATA_COLOR, 'Leakage Current (Real Data)', 
                     f'Real Leakage Current for Sensor {sensor_number}', 'Leakage Current (mA)', 
                     (start_date, end_date), use_line=False,
                     is_current_plot=True)
    
    if fluence_col in df.columns:
        setup_subplot(axes[2], df.index, df[fluence_col], 'green', 'Fluence', 
                     'Fluence', 'Fluence (n/cm²)', (start_date, end_date), use_line=False)
    
    if temp_col in df.columns:
        setup_subplot(axes[3], df.index, df[temp_col], 'magenta', 'Temperature', 
                     'Temperature', 'Temperature (K)', (start_date, end_date), use_line=False)

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

    fig, ax = plt.subplots(figsize=DEFAULT_FIGURE_SIZE)
    ax.set_xlim(df.index.min(), df.index.max())

    if real_col in temp_df.columns:
        real_data = temp_df[real_col].dropna()
        if not real_data.empty:
            ax.scatter(real_data.index, real_data, color=REAL_DATA_COLOR, s=SCATTER_MARKER_SIZE, 
                      label='Real Leakage Current', zorder=DATA_ZORDER)
    
    if sim_col in temp_df.columns:
        sim_data = temp_df[sim_col].dropna()
        if not sim_data.empty:
            sim_data = sim_data.sort_index()
            use_line_plot = USE_LINES_FOR_SIMULATION if use_lines is None else use_lines
            show_error = SHOW_ERROR_BANDS if show_error_band is None else show_error_band
            
            if use_line_plot:
                if show_error:
                    error_value = sim_data * (ERROR_PERCENTAGE / 100)
                    ax.fill_between(
                        sim_data.index, 
                        sim_data - error_value, 
                        sim_data + error_value, 
                        color=ERROR_BAND_COLOR, 
                        alpha=ERROR_BAND_ALPHA, 
                        label=f'{ERROR_PERCENTAGE}% Error Band',
                        zorder=ERROR_BAND_ZORDER
                    )
                
                ax.plot(sim_data.index, sim_data, color=SIMULATED_DATA_COLOR, linewidth=LINE_WIDTH, 
                        label='Simulated Leakage Current', zorder=DATA_ZORDER)
            else:
                ax.scatter(sim_data.index, sim_data, color=SIMULATED_DATA_COLOR, s=SCATTER_MARKER_SIZE, 
                          label='Simulated Leakage Current', zorder=DATA_ZORDER)

    add_parameter_info(ax)
    
    ax.set_ylabel('Leakage Current (mA)')
    ax.set_xlabel('Time')
    ax.set_title(f'Real vs Simulated Leakage Current for Sensor {sensor_number}')
    ax.grid(True)
    ax.legend()
    plt.tight_layout()
    


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
    ax.set_ylabel('Leakage Current (mA)')
    ax.set_title(title)
    ax.grid(True)
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
        legend = ax.legend(unique_handles, unique_labels, loc='best', framealpha=0.7, title=legend_title)
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
    
    # Plot real current for all sensors (if available)
    plot_sensors_data(df, sensors, 'real_current', 'Real Leakage Current for All Sensors', y_range=y_range)



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
    
    use_line_plot = USE_LINES_FOR_SIMULATION if use_lines is None else use_lines
    show_err = SHOW_ERROR_BANDS if show_error_band is None else show_error_band
    
    df_binned = df_binned.sort_values(by=param_col)
    
    if real_col in df_binned.columns and df_binned[real_col].notna().any():
        df_real = df_binned[[real_col, param_col]].dropna()
        ax.scatter(df_real[param_col], df_real[real_col], 
                  color=REAL_DATA_COLOR, s=SCATTER_MARKER_SIZE, 
                  label='Real Data', zorder=DATA_ZORDER)
    
    if sim_col in df_binned.columns and df_binned[sim_col].notna().any():
        df_sim = df_binned[[sim_col, param_col]].dropna()
        
        if show_err and use_line_plot:
            error_value = df_sim[sim_col] * (ERROR_PERCENTAGE / 100)
            ax.fill_between(
                df_sim[param_col], 
                df_sim[sim_col] - error_value, 
                df_sim[sim_col] + error_value, 
                color=ERROR_BAND_COLOR, 
                alpha=ERROR_BAND_ALPHA, 
                label=f'{ERROR_PERCENTAGE}% Error Band',
                zorder=ERROR_BAND_ZORDER
            )
        
        if use_line_plot:
            ax.plot(df_sim[param_col], df_sim[sim_col], 
                   color=SIMULATED_DATA_COLOR, linewidth=LINE_WIDTH, 
                   label='Simulated Data', zorder=DATA_ZORDER)
        else:
            ax.scatter(df_sim[param_col], df_sim[sim_col], 
                      color=SIMULATED_DATA_COLOR, s=SCATTER_MARKER_SIZE, 
                      label='Simulated Data', zorder=DATA_ZORDER)
    
    add_parameter_info(ax)
    ax.set_xlabel(x_label)
    ax.set_ylabel('Leakage Current (mA)')
    ax.set_title(f'Leakage Current vs {title_param} for Sensor {sensor_number}')
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
        ax.set_title('Simulated Leakage Current vs Fluence for All Sensors')
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
        ax.set_title('Real Leakage Current vs Fluence for All Sensors')
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
        ax.set_title('Simulated Leakage Current vs Integrated Luminosity for All Sensors')
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
        ax.set_title('Real Leakage Current vs Integrated Luminosity for All Sensors')
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



def plot_currents_vs_position(summary_df: pd.DataFrame, target_luminosities: list):
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
                      label=f'Real @ {target_lumi} fb$^{{-1}}$', zorder=10)
    
    add_parameter_info(ax, loc='upper right')
    
    ax.set_xlabel('Sensor Z Position (mm)')
    ax.set_ylabel('Leakage Current (mA)')
    ax.set_title('Leakage Current vs Sensor Position at Different Luminosities')
    ax.grid(True)
    ax.legend(fontsize=8, loc='upper left')
    plt.tight_layout()
    
    
        
