import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from params import Parameters
from config import CURRENT_TEMP_MODE, SIMULATION_PERIOD, REFERENCE_TEMPERATURE, TEMPERATURE_CORRECTION_ENABLED, TEMPERATURE_CORRECTION_DELTA

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


def setup_subplot(ax, x_data, y_data, color, label, title, ylabel, xlim, ylim=None):
    ax.scatter(x_data, y_data, color=color, s=1, label=label)
    ax.set_xlim(xlim)
    if ylim:
        ax.set_ylim(ylim)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True)
    ax.legend()

def plot_leakage_current(df: pd.DataFrame, sensor_name: str, 
                       output_path: str = None, start_date: pd.Timestamp = None, end_date: pd.Timestamp = None):
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

    fig, axes = plt.subplots(4, 1, figsize=(6, 8))
    
    # Plot simulated current
    setup_subplot(axes[0], df.index, df[sim_col], 'blue', 'Leakage Current Simulated', 
                 f'Simulated Leakage Current for Sensor {sensor_name}', 'Leakage Current (mA)', 
                 (start_date, end_date), (0, 0.3))
    
    # Plot real current if available
    if real_col in df.columns:
        setup_subplot(axes[1], df.index, df[real_col], 'red', 'Leakage Current (Real Data)', 
                     f'Real Leakage Current for Sensor {sensor_name}', 'Leakage Current (mA)', 
                     (start_date, end_date), (0, 0.3))
    
    # Plot fluence if available
    if fluence_col in df.columns:
        setup_subplot(axes[2], df.index, df[fluence_col], 'green', 'Fluence', 
                     'Fluence', 'Fluence (n/cm²)', (start_date, end_date))
    
    # Plot temperature if available
    if temp_col in df.columns:
        setup_subplot(axes[3], df.index, df[temp_col], 'magenta', 'Temperature', 
                     'Temperature', 'Temperature (K)', (start_date, end_date))

    plt.tight_layout()
    if output_path:
        plt.savefig(output_path)
    plt.show()
    plt.close()


def plot_simulated_vs_real(df: pd.DataFrame, sensor_name: str, output_path: str = None, 
                        start_date: pd.Timestamp = None, end_date: pd.Timestamp = None, weekly_average: bool = False):
    sim_col = f"current_{sensor_name}"
    real_col = f"real_current_{sensor_name}"
    
    if sim_col not in df.columns and real_col not in df.columns:
        print(f"No data found for sensor {sensor_name}")
        return

    if weekly_average:
        df = df.rolling('7d', min_periods=1).mean()

    fig, ax = plt.subplots(figsize=(6, 8))
    
    if start_date is not None and end_date is not None:
        ax.set_xlim(pd.to_datetime(start_date), pd.to_datetime(end_date))
    else:
        ax.set_xlim(df.index.min(), df.index.max())

    if real_col in df.columns:
        real_data = df[real_col].dropna()
        if not real_data.empty:
            ax.scatter(real_data.index, real_data, color='red', s=1, label='Real Leakage Current')
    
    if sim_col in df.columns:
        sim_data = df[sim_col].dropna()
        if not sim_data.empty:
            ax.scatter(sim_data.index, sim_data, color='blue', s=1, label='Simulated Leakage Current')

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
                     output_path: str = None, start_date: pd.Timestamp = None, end_date: pd.Timestamp = None):
    fig, ax = plt.subplots(figsize=(8,6))
    columns = []
    
    for sensor in sensors:
        col_name = f"{column_prefix}_{sensor}"
        if col_name in df.columns:
            columns.append(col_name)
            y = df[col_name]
            y_clean = y.dropna()
            if not y_clean.empty:
                ax.scatter(y_clean.index, y_clean.values, s=1, label=sensor)
    
    # Calculate mean with condition on number of non-NaN values
    if columns:
        data_df = df[columns]
        valid_count = data_df.notna().sum(axis=1)
        mean_data = data_df.mean(axis=1)
        mean_data[valid_count <= (len(columns) // 2)] = float('nan')
        ax.plot(mean_data.index, mean_data.values, color='black', linewidth=3, 
                label=f'Mean ({"real" if column_prefix == "real_current" else "simulated"})')
    
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
                    start_date: pd.Timestamp = None, end_date: pd.Timestamp = None):
    # Plot simulated current for all sensors
    sim_output = None if output_dir is None else os.path.join(output_dir, 'all_sensors_simulated.png')
    plot_sensors_data(df, sensors, 'current', 'Simulated Leakage Current for All Sensors', 
                     sim_output, start_date, end_date)
    
    # Plot real current for all sensors
    real_output = None if output_dir is None else os.path.join(output_dir, 'all_sensors_real.png')
    plot_sensors_data(df, sensors, 'real_current', 'Real Leakage Current for All Sensors', 
                     real_output, start_date, end_date)


def plot_temperature_only(result_df: pd.DataFrame, output_path: str = None, start_date: pd.Timestamp = None, end_date: pd.Timestamp = None):
    if start_date is None:
        start_date = result_df.index.min()
    if end_date is None:
        end_date = result_df.index.max()
    plt.figure(figsize=(8,6))
    plt.scatter(result_df.index, result_df['temperature'], color='magenta', s=1, label='Temperature')
    plt.xlim(start_date, end_date)
    plt.ylabel('Temperature (K)')
    plt.title('Temperature')
    plt.grid(True, which='both', linestyle=':', linewidth=0.5)
    plt.minorticks_on()
    plt.legend()
    if output_path:
        plt.savefig(output_path)
    plt.show()


def plot_currents_vs_cumulative_fluence(df: pd.DataFrame, sensor_name: str, output_path: str = None):
    """Plot both simulated and real currents against delivered fluence."""
    sim_col = f"current_{sensor_name}"
    real_col = f"real_current_{sensor_name}"
    deliv_fluence_col = f"delivered_fluence_{sensor_name}"
    
    if deliv_fluence_col not in df.columns:
        print(f"No delivered fluence data found for sensor {sensor_name}")
        return
        
    fig, ax = plt.subplots(figsize=(8,6))
    
    if real_col in df.columns:
        real_data = df[[real_col, deliv_fluence_col]].dropna()
        if not real_data.empty:
            ax.scatter(real_data[deliv_fluence_col], real_data[real_col], 
                       color='red', s=1, label='Real Leakage Current')
    
    if sim_col in df.columns:
        sim_data = df[[sim_col, deliv_fluence_col]].dropna()
        if not sim_data.empty:
            ax.scatter(sim_data[deliv_fluence_col], sim_data[sim_col], 
                       color='blue', s=1, label='Simulated Leakage Current')
    
    # Add parameter info box
    add_parameter_info(ax)
    
    ax.set_xlabel('Delivered Fluence (n/cm²)')
    ax.set_ylabel('Leakage Current (mA)')
    ax.set_title(f'Leakage Current vs Delivered Fluence for Sensor {sensor_name}')
    ax.grid(True)
    ax.legend()
    
    if output_path:
        plt.savefig(output_path)
    plt.show()
    plt.close()


def plot_all_currents_vs_luminosity(df, sensors, output_dir=None):
    """Plot all sensors currents against integrated luminosity in two separate plots."""
    if 'integrated_luminosity' not in df.columns:
        print("No integrated luminosity data found")
        return
        
    # Plot of simulated currents vs luminosity
    fig, ax = plt.subplots(figsize=(8,6))
    sim_columns = []
    
    for sensor in sensors:
        sim_col = f"current_{sensor}"
        
        if sim_col in df.columns:
            sim_columns.append(sim_col)
            sim_data = df[[sim_col, 'integrated_luminosity']].dropna()
            if not sim_data.empty:
                ax.scatter(sim_data['integrated_luminosity'], sim_data[sim_col], 
                          s=1, label=sensor)
    
    # Add parameter info box
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
    
    # Plot of real currents vs luminosity
    fig, ax = plt.subplots(figsize=(8,6))
    real_columns = []
    
    for sensor in sensors:
        real_col = f"real_current_{sensor}"
        
        if real_col in df.columns:
            real_columns.append(real_col)
            real_data = df[[real_col, 'integrated_luminosity']].dropna()
            if not real_data.empty:
                ax.scatter(real_data['integrated_luminosity'], real_data[real_col], 
                          s=1, label=sensor)
    
    # Add parameter info box
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
        plt.figure(figsize=(8,6))
        df['integrated_luminosity'].plot()
        plt.title('Integrated Luminosity vs Time')
        plt.xlabel('Time')
        plt.ylabel('Integrated Luminosity')
        plt.grid(True)
        if output_path:
            plt.savefig(output_path)
        plt.show()
        plt.close()
        print("Created integrated luminosity plot")
    except Exception as e:
        print(f"Error creating integrated luminosity plot: {e}")


def plot_currents_vs_integrated_luminosity(df: pd.DataFrame, sensor_name: str, output_path: str = None):
    """Plot both simulated and real currents against integrated luminosity."""
    sim_col = f"current_{sensor_name}"
    real_col = f"real_current_{sensor_name}"
    lumi_col = "integrated_luminosity"
    
    if lumi_col not in df.columns:
        print("No integrated luminosity data found")
        return
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    if sim_col in df.columns:
        sim_data = df[[sim_col, lumi_col]].dropna()
        if not sim_data.empty:
            ax.scatter(sim_data[lumi_col], sim_data[sim_col], 
                      color='blue', s=2, alpha=0.7, label='Simulated')
    
    if real_col in df.columns:
        real_data = df[[real_col, lumi_col]].dropna()
        if not real_data.empty:
            ax.scatter(real_data[lumi_col], real_data[real_col], 
                      color='red', s=2, alpha=0.7, label='Real')
    
    # Add parameter info box
    add_parameter_info(ax)
    
    ax.set_xlabel('Integrated Luminosity (fb$^{-1}$)')
    ax.set_ylabel('Leakage Current (mA)')
    ax.set_title(f'Leakage Current vs Integrated Luminosity for Sensor {sensor_name}')
    ax.grid(True)
    ax.legend()
    
    if output_path:
        plt.savefig(output_path)
    plt.show()
    plt.close()


def plot_currents_vs_position(summary_df: pd.DataFrame, target_luminosities: list, output_path: str = None):
    """
    Plot simulated and real currents against sensor position.
    Args:
        summary_df: DataFrame from create_sensor_summary with columns [current_sim, current_real, position, luminosity]
        target_luminosities: List of target luminosity values used for the plot
        output_path: Optional path to save the plot
    """
    fig, ax = plt.subplots(figsize=(8,6))
    
    markers = ['o', '^', 's', 'D']
    colors = ['blue', 'red', 'green', 'purple']
    
    for i, target_lumi in enumerate(target_luminosities):
        lumi_str = f'_f{target_lumi:.1f}'
        sim_col = f'current_sim{lumi_str}'
        real_col = f'current_real{lumi_str}'
        
        # Extract values for this luminosity target
        positions = summary_df['position'].values
        sim_values = summary_df[sim_col].values if sim_col in summary_df.columns else None
        real_values = summary_df[real_col].values if real_col in summary_df.columns else None
        
        # Skip if no data
        if sim_values is None and real_values is None:
            continue
            
        # Simulated current vs position
        color_idx = i % len(colors)
        marker_idx = i % len(markers)
        
        if sim_values is not None:
            ax.scatter(positions, sim_values, 
                      color=colors[color_idx], marker=markers[marker_idx],
                      s=50, label=f'Sim @ {target_lumi} fb$^{{-1}}$')
            
        # Real current vs position - use same color but hollow markers
        if real_values is not None:
            ax.scatter(positions, real_values, 
                      edgecolor=colors[color_idx], marker=markers[marker_idx],
                      facecolor='none', s=50, label=f'Real @ {target_lumi} fb$^{{-1}}$')
    
    # Add parameter info box
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
