import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from params import Parameters
from config import SIMULATION_PERIOD, TEMPERATURE_CORRECTION_ENABLED, TEMPERATURE_CORRECTION_DELTA
from config_plot import (
    CURRENT_TEMP_MODE, REFERENCE_TEMPERATURE,
    USE_LINES_FOR_SIMULATION, SHOW_ERROR_BANDS, ERROR_PERCENTAGE, PLOT_RESAMPLING_PERIOD,
    SCATTER_MARKER_SIZE, LINE_WIDTH, ERROR_BAND_ALPHA, REAL_DATA_COLOR, SIMULATED_DATA_COLOR, ERROR_BAND_COLOR
)

# Stałe dla przejrzystości kodu
DEFAULT_FIGURE_SIZE = (8, 6)
MULTI_SUBPLOT_FIGURE_SIZE = (6, 8)
ERROR_BAND_ZORDER = -10
DATA_ZORDER = 10

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
    
    if CURRENT_TEMP_MODE == 'adjust_real':
        temp_text = "\nAdjusted real to sim. temperature"
    elif CURRENT_TEMP_MODE == 'adjust_sim':
        temp_text = "\nAdjusted sim. to real temperature"
    elif CURRENT_TEMP_MODE == 'adjust_both':
        temp_text = f"\nAdjusted both to {REFERENCE_TEMPERATURE:.2f} K"
    else:
        temp_text = ""
    
    if TEMPERATURE_CORRECTION_ENABLED:
        temp_text += f"\nTemp. correction: +{TEMPERATURE_CORRECTION_DELTA} K"
    
    param_text += temp_text
    
    props = dict(boxstyle='round', facecolor='white', alpha=0.7)
    ax.text(0.02, 0.98, param_text, transform=ax.transAxes, fontsize=8,
            verticalalignment='top', horizontalalignment='left', bbox=props)


def resample_data(data, period):
    """Resample data based on specified period."""
    if period and isinstance(data, pd.Series) and not data.empty:
        return data.resample(period).mean()
    return data

def setup_subplot(ax, x_data, y_data, color, label, title, ylabel, xlim, ylim=None, use_line=None, show_error_band=None, is_current_plot=False, force_no_error=False):
    use_line = USE_LINES_FOR_SIMULATION if use_line is None else use_line
    show_error_band = SHOW_ERROR_BANDS if show_error_band is None else show_error_band
    
    if force_no_error:
        show_error_band = False
    
    if PLOT_RESAMPLING_PERIOD:
        y_data_series = pd.Series(y_data, index=x_data)
        y_data_series = y_data_series.dropna()
        y_data_series = resample_data(y_data_series, PLOT_RESAMPLING_PERIOD)
        x_data = y_data_series.index
        y_data = y_data_series.values
    
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

def plot_leakage_current(df: pd.DataFrame, sensor_name: str, 
                        output_path: str = None, start_date: pd.Timestamp = None, end_date: pd.Timestamp = None,
                        use_lines: bool = None, show_error_band: bool = None, resampling_period: str = None):
    sim_col = f"current_{sensor_name}"
    real_col = f"real_current_{sensor_name}"
    temp_col = f"temperature_{sensor_name}"
    fluence_col = f"fluence_{sensor_name}"
    
    if sim_col not in df.columns:
        raise ValueError(f"Simulated current column not found for sensor {sensor_name}")

    if start_date is None:
        start_date = df.index.min()
    if end_date is None:
        end_date = df.index.max()

    fig, axes = plt.subplots(4, 1, figsize=MULTI_SUBPLOT_FIGURE_SIZE)
    
    setup_subplot(axes[0], df.index, df[sim_col], SIMULATED_DATA_COLOR, 'Leakage Current Simulated', 
                 f'Simulated Leakage Current for Sensor {sensor_name}', 'Leakage Current (mA)', 
                 (start_date, end_date), (0, 0.3), use_line=use_lines, show_error_band=show_error_band,
                 is_current_plot=True)
    
    if real_col in df.columns:
        setup_subplot(axes[1], df.index, df[real_col], REAL_DATA_COLOR, 'Leakage Current (Real Data)', 
                     f'Real Leakage Current for Sensor {sensor_name}', 'Leakage Current (mA)', 
                     (start_date, end_date), (0, 0.3), use_line=False,
                     is_current_plot=True)
    
    if fluence_col in df.columns:
        setup_subplot(axes[2], df.index, df[fluence_col], 'green', 'Fluence', 
                     'Fluence', 'Fluence (n/cm²)', (start_date, end_date))
    
    if temp_col in df.columns:
        setup_subplot(axes[3], df.index, df[temp_col], 'magenta', 'Temperature', 
                     'Temperature', 'Temperature (K)', (start_date, end_date))

    plt.tight_layout()
    if output_path:
        plt.savefig(output_path)
    plt.show()
    plt.close()


def plot_simulated_vs_real(df: pd.DataFrame, sensor_name: str, output_path: str = None, 
                         start_date: pd.Timestamp = None, end_date: pd.Timestamp = None, weekly_average: bool = False,
                         use_lines: bool = None, show_error_band: bool = None, resampling_period: str = None):
    sim_col = f"current_{sensor_name}"
    real_col = f"real_current_{sensor_name}"
    
    if sim_col not in df.columns and real_col not in df.columns:
        print(f"No data found for sensor {sensor_name}")
        return

    temp_df = df.copy()
    custom_period = resampling_period or PLOT_RESAMPLING_PERIOD
    
    if weekly_average:
        temp_df = temp_df.rolling('7d', min_periods=1).mean()
    elif custom_period:
        temp_df = temp_df.resample(custom_period).mean()

    fig, ax = plt.subplots(figsize=MULTI_SUBPLOT_FIGURE_SIZE)
    
    if start_date is not None and end_date is not None:
        ax.set_xlim(pd.to_datetime(start_date), pd.to_datetime(end_date))
    else:
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
    ax.set_title(f'Real vs Simulated Leakage Current for {sensor_name}')
    ax.grid(True)
    ax.legend()
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path)
    plt.show()
    plt.close()


def plot_sensors_data(df: pd.DataFrame, sensors: list, column_prefix: str, title: str, 
                     output_path: str = None, start_date: pd.Timestamp = None, end_date: pd.Timestamp = None,
                     use_lines: bool = None, show_error_band: bool = None, resampling_period: str = None,
                     force_no_error: bool = False):
    fig, ax = plt.subplots(figsize=DEFAULT_FIGURE_SIZE)
    columns = []
    
    temp_df = df.copy()
    custom_period = resampling_period or PLOT_RESAMPLING_PERIOD
    if custom_period:
        temp_df = temp_df.resample(custom_period).mean()
    
    for sensor in sensors:
        col_name = f"{column_prefix}_{sensor}"
        if col_name in temp_df.columns:
            columns.append(col_name)
            y = temp_df[col_name]
            y_clean = y.dropna()
            if not y_clean.empty:
                use_line_plot = USE_LINES_FOR_SIMULATION if use_lines is None else use_lines
                show_error = SHOW_ERROR_BANDS if show_error_band is None else show_error_band
                
                if force_no_error:
                    show_error = False
                
                is_current_plot = column_prefix == "current" or column_prefix == "real_current"
                
                if column_prefix != "real_current" and use_line_plot and show_error and is_current_plot:
                    y_sorted = y_clean.sort_index()
                    error_value = y_sorted * (ERROR_PERCENTAGE / 100)
                    ax.fill_between(
                        y_sorted.index, 
                        y_sorted - error_value, 
                        y_sorted + error_value, 
                        color=ERROR_BAND_COLOR, 
                        alpha=ERROR_BAND_ALPHA,
                        zorder=ERROR_BAND_ZORDER
                    )
                
                if column_prefix == "real_current":
                    ax.scatter(y_clean.index, y_clean.values, s=SCATTER_MARKER_SIZE, 
                              label=sensor, zorder=DATA_ZORDER)
                else:
                    y_sorted = y_clean.sort_index()
                    if use_line_plot:
                        ax.plot(y_sorted.index, y_sorted.values, linewidth=LINE_WIDTH, 
                               label=sensor, zorder=DATA_ZORDER)
                    else:
                        ax.scatter(y_sorted.index, y_sorted.values, s=SCATTER_MARKER_SIZE, 
                                  label=sensor, zorder=DATA_ZORDER)
    
    if columns:
        data_df = df[columns]
        valid_count = data_df.notna().sum(axis=1)
        mean_data = data_df.mean(axis=1)
        mean_data[valid_count <= (len(columns) // 2)] = float('nan')
        mean_data = mean_data.sort_index()
        ax.plot(mean_data.index, mean_data.values, color='black', linewidth=3, 
                label=f'Mean ({"real" if column_prefix == "real_current" else "simulated"})', 
                zorder=DATA_ZORDER+1)  # Mean line should be above individual data
    
    add_parameter_info(ax)
    ax.set_xlim(start_date, end_date)
    ax.set_ylabel('Leakage Current (mA)')
    ax.set_title(title)
    ax.grid(True)
    plt.tight_layout()
    ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), title='Sensors', fontsize='small')
    
    if output_path:
        plt.savefig(output_path)
    plt.show()
    plt.close()

def plot_all_sensors(df: pd.DataFrame, sensors: list, output_dir: str = None, 
                    start_date: pd.Timestamp = None, end_date: pd.Timestamp = None,
                    use_lines: bool = None, show_error_band: bool = None, resampling_period: str = None):
    # Plot simulated current for all sensors (no error bands when plotting all sensors)
    sim_output = None if output_dir is None else os.path.join(output_dir, 'all_sensors_simulated.png')
    plot_sensors_data(df, sensors, 'current', 'Simulated Leakage Current for All Sensors', 
                     sim_output, start_date, end_date, use_lines, show_error_band, resampling_period,
                     force_no_error=True)  # Force no error band for all sensors plot
    
    # Plot real current for all sensors (if available)
    real_output = None if output_dir is None else os.path.join(output_dir, 'all_sensors_real.png')
    plot_sensors_data(df, sensors, 'real_current', 'Real Leakage Current for All Sensors', 
                     real_output, start_date, end_date, False, False, resampling_period)



def plot_currents_vs_parameter(df: pd.DataFrame, sensor_name: str, param_type: str = 'luminosity', 
                               output_path: str = None, use_lines: bool = None, show_error_band: bool = None):
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
    if PLOT_RESAMPLING_PERIOD:
        temp_df = resample_data(temp_df, period=PLOT_RESAMPLING_PERIOD)
    
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
    ax.set_title(f'Leakage Current vs {title_param} for Sensor {sensor_name}')
    ax.grid(True)
    ax.legend()
    
    if output_path:
        plt.savefig(output_path)
    
    plt.show()
    plt.close()


def plot_currents_vs_cumulative_fluence(df: pd.DataFrame, sensor_name: str, output_path: str = None,
                                  use_lines: bool = None, show_error_band: bool = None):
    """
    Plot both simulated and real currents against delivered fluence.
    """
    return plot_currents_vs_parameter(df, sensor_name, param_type='fluence', output_path=output_path,
                                     use_lines=use_lines, show_error_band=show_error_band)


def plot_all_currents_vs_luminosity(df: pd.DataFrame, sensors: list, output_dir: str = None):
    """Plot all sensors currents against integrated luminosity in two separate plots."""
    if 'integrated_luminosity' not in df.columns:
        print("No integrated luminosity data found")
        return
        
    fig, ax = plt.subplots(figsize=DEFAULT_FIGURE_SIZE)
    sim_columns = []
    
    for sensor in sensors:
        sim_col = f"current_{sensor}"
        
        if sim_col in df.columns:
            sim_columns.append(sim_col)
            sim_data = df[[sim_col, 'integrated_luminosity']].dropna()
            if not sim_data.empty:
                ax.scatter(sim_data['integrated_luminosity'], sim_data[sim_col], 
                          s=SCATTER_MARKER_SIZE, label=sensor, zorder=DATA_ZORDER)
    
    add_parameter_info(ax)
    
    ax.set_xlabel('Integrated Luminosity (fb$^{-1}$)')
    ax.set_ylabel('Leakage Current (mA)')
    ax.set_title('Simulated Leakage Current vs Integrated Luminosity for All Sensors')
    ax.grid(True)
    plt.tight_layout()
    ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), title='Sensors', fontsize='small')
    if output_dir is not None:
        plt.savefig(os.path.join(output_dir, "all_simulated_vs_luminosity.png"), bbox_inches='tight')
    plt.show()
    plt.close()
    
    fig, ax = plt.subplots(figsize=DEFAULT_FIGURE_SIZE)
    real_columns = []
    
    for sensor in sensors:
        real_col = f"real_current_{sensor}"
        
        if real_col in df.columns:
            real_columns.append(real_col)
            real_data = df[[real_col, 'integrated_luminosity']].dropna()
            if not real_data.empty:
                ax.scatter(real_data['integrated_luminosity'], real_data[real_col], 
                          s=SCATTER_MARKER_SIZE, label=sensor, zorder=DATA_ZORDER)
    
    add_parameter_info(ax)
    
    ax.set_xlabel('Integrated Luminosity (fb$^{-1}$)')
    ax.set_ylabel('Leakage Current (mA)')
    ax.set_title('Real Leakage Current vs Integrated Luminosity for All Sensors')
    ax.grid(True)
    plt.tight_layout()
    ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), title='Sensors', fontsize='small')
    if output_dir is not None:
        plt.savefig(os.path.join(output_dir, "all_real_vs_luminosity.png"), bbox_inches='tight')
    plt.show()
    plt.close()


def plot_integrated_luminosity(df: pd.DataFrame, output_path: str = None):
    """Plot integrated luminosity over time."""
    try:
        plt.figure(figsize=DEFAULT_FIGURE_SIZE)
        df['integrated_luminosity'].plot(zorder=DATA_ZORDER)
        plt.title('Integrated Luminosity vs Time')
        plt.xlabel('Time')
        plt.ylabel('Integrated Luminosity (fb$^{-1}$)')
        plt.grid(True)
        if output_path:
            plt.savefig(output_path)
        plt.show()
        plt.close()
        print("Created integrated luminosity plot")
    except Exception as e:
        print(f"Error creating integrated luminosity plot: {e}")


def plot_currents_vs_integrated_luminosity(df: pd.DataFrame, sensor_name: str, output_path: str = None,
                                    use_lines: bool = None, show_error_band: bool = None):
    """
    Plot both simulated and real currents against integrated luminosity.
    """
    return plot_currents_vs_parameter(df, sensor_name, param_type='luminosity', output_path=output_path,
                                     use_lines=use_lines, show_error_band=show_error_band)


def plot_currents_vs_position(summary_df: pd.DataFrame, target_luminosities: list, output_path: str = None):
    """
    Plot simulated and real currents against sensor position.
    Args:
        summary_df: DataFrame from create_sensor_summary with columns [current_sim, current_real, position, luminosity]
        target_luminosities: List of target luminosity values used for the plot
        output_path: Optional path to save the plot
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
    ax.legend(fontsize=8)
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path)
    plt.show()
    plt.close()
