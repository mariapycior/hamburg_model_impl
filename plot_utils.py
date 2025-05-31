import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from params import Parameters
from config import CURRENT_TEMP_MODE, SIMULATION_PERIOD, REFERENCE_TEMPERATURE, TEMPERATURE_CORRECTION_ENABLED, TEMPERATURE_CORRECTION_DELTA

def add_parameter_info(ax, loc='upper left'):
    """Add a text box with key model parameters to the plot."""
    params = Parameters()
    
    # Calculate simulation timestep in hours
    timestep = pd.to_timedelta(SIMULATION_PERIOD.lower()).total_seconds() / 3600
    
    # Create parameter text
    param_text = (
        f"$\\alpha_I$: {params.alpha_I:.2e} A/cm\n"
        f"$\\alpha_0^*$: {params.alpha_0_star:.2e} A/cm\n"
        f"$\\beta$: {params.beta:.2e} A/cm\n"
        f"$E_I$: {params.E_I:.2f} eV\n"
        f"$V$: {params.V:.3f} cm$^3$\n"
        f"$E_{{eff}}$: {params.E_eff:.2f} eV\n"
        f"Timestep: {timestep:.1f} h"
    )
    
    # Add temperature adjustment info
    if CURRENT_TEMP_MODE == 'adjust_real':
        temp_text = "\nAdjusted real to sim. temperature"
    elif CURRENT_TEMP_MODE == 'adjust_sim':
        temp_text = "\nAdjusted sim. to real temperature"
    elif CURRENT_TEMP_MODE == 'adjust_both':
        temp_text = f"\nAdjusted both to {REFERENCE_TEMPERATURE:.2f} K"
    else:
        temp_text = ""
    
    # Add temperature correction info if enabled
    if TEMPERATURE_CORRECTION_ENABLED:
        temp_corr_text = f"\nTemp. correction: +{TEMPERATURE_CORRECTION_DELTA} K"
        temp_text += temp_corr_text
    
    param_text += temp_text
    
    # Add text box to plot
    props = dict(boxstyle='round', facecolor='white', alpha=0.7)
    ax.text(0.02, 0.98, param_text, transform=ax.transAxes, fontsize=8,
            verticalalignment='top', horizontalalignment='left', bbox=props)


def plot_leakage_current(df: pd.DataFrame, sensor_name: str, 
                         output_path: str = None, start_date: pd.Timestamp = None, end_date: pd.Timestamp = None):
    """Plot detailed view of currents, fluence and temperature for a sensor."""
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

    plt.figure(figsize=(6, 8))
    
    plt.subplot(4, 1, 1)
    plt.scatter(df.index, df[sim_col], color='blue', s=1, label='Leakage Current Simulated')
    plt.xlim(start_date, end_date)
    plt.ylim(0, 0.3)
    plt.ylabel('Leakage Current (mA)')
    plt.title(f'Simulated Leakage Current for Sensor {sensor_name}')
    plt.grid(True)
    plt.legend()
    
    if real_col in df.columns:
        plt.subplot(4, 1, 2)
        plt.scatter(df.index, df[real_col], color='red', s=1, label='Leakage Current (Real Data)')
        plt.xlim(start_date, end_date)
        plt.ylabel('Leakage Current (mA)')
        plt.ylim(0, 0.3)
        plt.title(f'Real Leakage Current for Sensor {sensor_name}')
        plt.grid(True)
        plt.legend()
    
    if fluence_col in df.columns:
        plt.subplot(4, 1, 3)
        plt.scatter(df.index, df[fluence_col], color='green', s=1, label='Fluence')
        plt.xlim(start_date, end_date)
        plt.ylabel('Fluence (n/cm²)')
        plt.title('Fluence')
        plt.grid(True)
        plt.legend()
    
    if temp_col in df.columns:
        plt.subplot(4, 1, 4)
        plt.scatter(df.index, df[temp_col], color='magenta', s=1, label='Temperature')
        plt.xlim(start_date, end_date)
        plt.ylabel('Temperature (K)')
        plt.title('Temperature')
        plt.grid(True)
        plt.legend()

    plt.tight_layout()
    if output_path:
        plt.savefig(output_path)
    plt.show()
    plt.close()


def plot_simulated_vs_real(df, sensor_name, output_path=None, start_date=None, end_date=None, weekly_average=False):
    """
    Plot simulated and real current on the same plot (time series overlay).
    Args:
        df: DataFrame with both simulated and real current data
        sensor_name: Name of the sensor
        output_path: Path to save the plot
        start_date: Start date for plotting
        end_date: End date for plotting
        weekly_average: If True, plot 7-day rolling mean
    """
    sim_col = f"current_{sensor_name}"
    real_col = f"real_current_{sensor_name}"
    
    if sim_col not in df.columns and real_col not in df.columns:
        print(f"No data found for sensor {sensor_name}")
        return

    if weekly_average:
        df = df.rolling('7d', min_periods=1).mean()

    fig, ax = plt.subplots(figsize=(6, 8))
    
    if start_date is not None and end_date is not None:
        plt.xlim(pd.to_datetime(start_date), pd.to_datetime(end_date))
    else:
        plt.xlim(df.index.min(), df.index.max())

    if real_col in df.columns:
        real_data = df[real_col].dropna()
        if not real_data.empty:
            ax.scatter(real_data.index, real_data, color='red', s=1, label='Real Leakage Current')
    
    if sim_col in df.columns:
        sim_data = df[sim_col].dropna()
        if not sim_data.empty:
            ax.scatter(sim_data.index, sim_data, color='blue', s=1, label='Simulated Leakage Current')

    # Add parameter info box
    add_parameter_info(ax)
    
    ax.set_ylabel('Leakage Current (mA)')
    ax.set_xlabel('Time')
    ax.set_title(f'Real vs Simulated Leakage Current for {sensor_name}')

    #ax.set_title(f'Comparison of Real vs Simulated Leakage Current for Sensor {sensor_name}')
    ax.grid(True)
    ax.legend()
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path)
    plt.show()
    plt.close()


def plot_all_sensors(df, sensors, output_dir=None, start_date=None, end_date=None):
    import os
    
    # Plot of simulated current for all sensors
    fig, ax = plt.subplots(figsize=(8,6))
    sim_columns = []
    
    for sensor in sensors:
        sim_col = f"current_{sensor}"
        if sim_col in df.columns:
            sim_columns.append(sim_col)
            y = df[sim_col]
            y_clean = y.dropna()
            x_clean = y_clean.index
            if not y_clean.empty and len(x_clean) == len(y_clean):
                ax.scatter(x_clean, y_clean.values, s=1, label=sensor)
    
    # Calculate mean with condition on number of non-NaN values
    if sim_columns:
        sim_df = df[sim_columns]
        valid_count_sim = sim_df.notna().sum(axis=1)
        mean_sim = sim_df.mean(axis=1)
        mean_sim[valid_count_sim <= (len(sim_columns) // 2)] = float('nan')
        ax.plot(mean_sim.index, mean_sim.values, color='black', linewidth=3, label='Mean (simulated)')
    
    # Add parameter info box
    add_parameter_info(ax)
        
    ax.set_xlim(start_date, end_date)
    ax.set_ylabel('Leakage Current (mA)')
    ax.set_title('Simulated Leakage Current for All Sensors')
    ax.grid(True)
    plt.tight_layout()
    ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), title='Sensors', fontsize='small')
    if output_dir is not None:
        plt.savefig(os.path.join(output_dir, "all_simulated.png"), bbox_inches='tight')
    plt.show()
    plt.close()
    
    # Plot of real currents
    fig, ax = plt.subplots(figsize=(8,6))
    real_columns = []
    
    for sensor in sensors:
        real_col = f"real_current_{sensor}"
        if real_col in df.columns:
            real_columns.append(real_col)
            y = df[real_col]
            y_clean = y.dropna()
            x_clean = y_clean.index
            if not y_clean.empty and len(x_clean) == len(y_clean):
                ax.scatter(x_clean, y_clean.values, s=1, label=sensor)
    
    # Calculate mean with condition on number of non-NaN values
    if real_columns:
        real_df = df[real_columns]
        valid_count_real = real_df.notna().sum(axis=1)
        mean_real = real_df.mean(axis=1)
        mean_real[valid_count_real <= (len(real_columns) // 2)] = float('nan')
        ax.plot(mean_real.index, mean_real.values, color='black', linewidth=3, label='Mean (real)')
    
    # Add parameter info box
    add_parameter_info(ax)
    
    ax.set_xlim(start_date, end_date)
    ax.set_ylabel('Leakage Current (mA)')
    ax.set_title('Real Leakage Current for All Sensors')
    ax.grid(True)
    plt.tight_layout()
    ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), title='Sensors', fontsize='small')
    if output_dir is not None:
        plt.savefig(os.path.join(output_dir, "all_real.png"), bbox_inches='tight')
    plt.show()
    plt.close()


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
