import os
import matplotlib.pyplot as plt
import pandas as pd


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

    plt.figure(figsize=(12, 16))
    
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
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt

    sim_col = f"current_{sensor_name}"
    real_col = f"real_current_{sensor_name}"
    
    if sim_col not in df.columns and real_col not in df.columns:
        print(f"No data found for sensor {sensor_name}")
        return

    if weekly_average:
        df = df.rolling('7d', min_periods=1).mean()

    plt.figure(figsize=(12, 8))
   #plt.ylim(0,6)
    
    if start_date is not None and end_date is not None:
        plt.xlim(pd.to_datetime(start_date), pd.to_datetime(end_date))
    else:
        plt.xlim(df.index.min(), df.index.max())

    if real_col in df.columns:
        real_data = df[real_col].dropna()
        if not real_data.empty:
            plt.scatter(real_data.index, real_data, color='red', s=1, label='Real Leakage Current')
    
    if sim_col in df.columns:
        sim_data = df[sim_col].dropna()
        if not sim_data.empty:
            plt.scatter(sim_data.index, sim_data, color='blue', s=1, label='Simulated Leakage Current')

    plt.ylabel('Leakage Current (mA)')
    plt.xlabel('Time')
    plt.title(f'Comparison of Real vs Simulated Leakage Current for Sensor {sensor_name}')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path)
    plt.show()
    plt.close()


def plot_all_sensors(df, sensors, output_dir=None, start_date=None, end_date=None):
    import os
    
    # Plot of simulated current for all sensors
    plt.figure(figsize=(12, 12))
    sim_columns = []
    
    for sensor in sensors:
        sim_col = f"current_{sensor}"
        if sim_col in df.columns:
            sim_columns.append(sim_col)
            y = df[sim_col]
            y_clean = y.dropna()
            x_clean = y_clean.index
            if not y_clean.empty and len(x_clean) == len(y_clean):
                plt.scatter(x_clean, y_clean.values, s=1, label=sensor)
    
    # Calculate mean with condition on number of non-NaN values
    if sim_columns:
        sim_df = df[sim_columns]
        valid_count_sim = sim_df.notna().sum(axis=1)
        mean_sim = sim_df.mean(axis=1)
        mean_sim[valid_count_sim <= (len(sim_columns) // 2)] = float('nan')
        plt.plot(mean_sim.index, mean_sim.values, color='black', linewidth=3, label='Mean (simulated)')
        
    plt.xlim(start_date, end_date)
    plt.ylabel('Leakage Current (mA)')
    plt.title('Simulated Leakage Current for All Sensors')
    plt.grid(True)
    plt.tight_layout()
    plt.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), title='Sensors', fontsize='small')
    if output_dir is not None:
        plt.savefig(os.path.join(output_dir, "all_simulated.png"), bbox_inches='tight')
    plt.show()
    plt.close()
    
    # Plot of real currents
    plt.figure(figsize=(12, 12))
    real_columns = []
    
    for sensor in sensors:
        real_col = f"real_current_{sensor}"
        if real_col in df.columns:
            real_columns.append(real_col)
            y = df[real_col]
            y_clean = y.dropna()
            x_clean = y_clean.index
            if not y_clean.empty and len(x_clean) == len(y_clean):
                plt.scatter(x_clean, y_clean.values, s=1, label=sensor)
    
    # Calculate mean with condition on number of non-NaN values
    if real_columns:
        real_df = df[real_columns]
        valid_count_real = real_df.notna().sum(axis=1)
        mean_real = real_df.mean(axis=1)
        mean_real[valid_count_real <= (len(real_columns) // 2)] = float('nan')
        plt.plot(mean_real.index, mean_real.values, color='black', linewidth=3, label='Mean (real)')
    plt.xlim(start_date, end_date)
    plt.ylabel('Leakage Current (mA)')
    plt.title('Real Leakage Current for All Sensors')
    plt.grid(True)
    plt.tight_layout()
    plt.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), title='Sensors', fontsize='small')
    if output_dir is not None:
        plt.savefig(os.path.join(output_dir, "all_real.png"), bbox_inches='tight')
    plt.show()
    plt.close()
    
    # Add call to plot currents vs delivered fluence
    plot_all_currents_vs_delivered_fluence(df, sensors, output_dir)


def plot_temperature_only(result_df: pd.DataFrame, output_path: str = None, start_date: pd.Timestamp = None, end_date: pd.Timestamp = None):
    if start_date is None:
        start_date = result_df.index.min()
    if end_date is None:
        end_date = result_df.index.max()
    plt.figure(figsize=(12, 8))
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


def plot_simulated_simple(simulated_df, sensors, output_path=None, start_date=None, end_date=None):
    plt.figure(figsize=(12, 8))
    for sensor in sensors:
        if sensor not in simulated_df.columns:
            continue
        y = simulated_df[sensor]
        if hasattr(y, 'columns'):
            y = y.iloc[:, 0]
        y_clean = y.dropna()
        x_clean = y_clean.index
        if y_clean.empty or len(x_clean) != len(y_clean):
            continue
        plt.plot(x_clean, y_clean.values, label=sensor, alpha=0.7, linewidth=1)
    plt.xlim(start_date, end_date)
    plt.ylabel('Simulated Leakage Current (mA)')
    plt.title('Simulated Leakage Current for all sensors (simple overlay)')
    plt.grid(True)
    plt.tight_layout()
    if output_path:
        plt.savefig(output_path)
    plt.close()


def plot_simulated_pandas(simulated_df, output_path=None):
    import matplotlib.pyplot as plt
    plt.figure(figsize=(12, 8))
    simulated_df.plot(ax=plt.gca(), legend=False, alpha=0.7)
    plt.ylabel("Simulated Leakage Current (mA)")
    plt.title("Simulated Leakage Current for all sensors (pandas plot)")
    plt.tight_layout()
    if output_path:
        plt.savefig(output_path)
    plt.close()


def plot_currents_vs_cumulative_fluence(df: pd.DataFrame, sensor_name: str, output_path: str = None):
    """Plot both simulated and real currents against delivered fluence."""
    sim_col = f"current_{sensor_name}"
    real_col = f"real_current_{sensor_name}"
    deliv_fluence_col = f"delivered_fluence_{sensor_name}"
    
    if deliv_fluence_col not in df.columns:
        print(f"No delivered fluence data found for sensor {sensor_name}")
        return
        
    plt.figure(figsize=(12, 8))
    
    if real_col in df.columns:
        real_data = df[[real_col, deliv_fluence_col]].dropna()
        if not real_data.empty:
            plt.scatter(real_data[deliv_fluence_col], real_data[real_col], 
                       color='red', s=1, label='Real Leakage Current')
    
    if sim_col in df.columns:
        sim_data = df[[sim_col, deliv_fluence_col]].dropna()
        if not sim_data.empty:
            plt.scatter(sim_data[deliv_fluence_col], sim_data[sim_col], 
                       color='blue', s=1, label='Simulated Leakage Current')
    
    plt.xlabel('Delivered Fluence (n/cm²)')
    plt.ylabel('Leakage Current (mA)')
    plt.title(f'Leakage Current vs Delivered Fluence for Sensor {sensor_name}')
    plt.grid(True)
    plt.legend()
    
    if output_path:
        plt.savefig(output_path)
    plt.show()
    plt.close()


def plot_all_currents_vs_delivered_fluence(df, sensors, output_dir=None):
    """Plot all sensors currents against delivered fluence in two separate plots."""
    # Plot of simulated currents vs delivered fluence
    plt.figure(figsize=(12, 12))
    sim_columns = []
    
    for sensor in sensors:
        sim_col = f"current_{sensor}"
        deliv_fluence_col = f"delivered_fluence_{sensor}"
        
        if sim_col in df.columns and deliv_fluence_col in df.columns:
            sim_columns.append(sim_col)
            sim_data = df[[sim_col, deliv_fluence_col]].dropna()
            if not sim_data.empty:
                plt.scatter(sim_data[deliv_fluence_col], sim_data[sim_col], 
                          s=1, label=sensor)
    
    plt.xlabel('Delivered Fluence (n/cm²)')
    plt.ylabel('Leakage Current (mA)')
    plt.title('Simulated Leakage Current vs Delivered Fluence')
    plt.grid(True)
    plt.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), 
              title='Sensors', fontsize='small')
    plt.tight_layout()
    
    if output_dir is not None:
        plt.savefig(os.path.join(output_dir, "sim_vs_fluence.png"), 
                   bbox_inches='tight')
    
    # Plot of real currents vs delivered fluence
    plt.figure(figsize=(12, 12))
    real_columns = []
    
    for sensor in sensors:
        real_col = f"real_current_{sensor}"
        deliv_fluence_col = f"delivered_fluence_{sensor}"
        
        if real_col in df.columns and deliv_fluence_col in df.columns:
            real_columns.append(real_col)
            real_data = df[[real_col, deliv_fluence_col]].dropna()
            if not real_data.empty:
                plt.scatter(real_data[deliv_fluence_col], real_data[real_col], 
                          s=1, label=sensor)
    
    plt.xlabel('Delivered Fluence (n/cm²)')
    plt.ylabel('Leakage Current (mA)')
    plt.title('Real Leakage Current vs Delivered Fluence')
    plt.grid(True)
    plt.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), 
              title='Sensors', fontsize='small')
    plt.tight_layout()
    
    if output_dir is not None:
        plt.savefig(os.path.join(output_dir, "real_vs_fluence.png"), 
                   bbox_inches='tight')
    
    plt.show()
    plt.close('all')
