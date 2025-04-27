import os
import matplotlib.pyplot as plt
import pandas as pd


def plot_leakage_current(result_df: pd.DataFrame, current_sample_df: pd.DataFrame, sensor_name: str, 
                         output_path: str = None, start_date: pd.Timestamp = None, end_date: pd.Timestamp = None):
    if sensor_name in current_sample_df.columns:
        real_current = current_sample_df[sensor_name]
    else:
        raise ValueError(f"Sensor {sensor_name} not found in the current sample file.")

    if start_date is None:
        start_date = min(result_df.index.min(), real_current.index.min())
    if end_date is None:
        end_date = max(result_df.index.max(), real_current.index.max())

    plt.figure(figsize=(12, 16))
    
    plt.subplot(4, 1, 1)
    plt.scatter(result_df.index, result_df['current'], color='blue', s=1, label='Leakage Current Simulated')
    plt.xlim(start_date, end_date)
    plt.ylim(0, 0.4)
    plt.ylabel('Current (mA)')
    plt.title(f'Simulated Leakage Current for Sensor {sensor_name}')
    plt.grid(True)
    plt.legend()
    
    plt.subplot(4, 1, 2)
    plt.scatter(real_current.index, real_current, color='red', s=1, label='Leakage Current (Real Data)')
    plt.xlim(start_date, end_date)
    plt.ylabel('Current (mA)')
    plt.ylim(0, 0.4)
    plt.title(f'Real Leakage Current for Sensor {sensor_name}')
    plt.grid(True)
    plt.legend()
    
    plt.subplot(4, 1, 3)
    plt.scatter(result_df.index, result_df['fluence'], color='green', s=1, label='Fluence')
    plt.xlim(start_date, end_date)
    plt.ylabel('Fluence (n/cm²)')
    plt.title('Fluence')
    plt.grid(True)
    plt.legend()
    
    plt.subplot(4, 1, 4)
    plt.scatter(result_df.index, result_df['temperature'], color='magenta', s=1, label='Temperature')
    plt.xlim(start_date, end_date)
    plt.ylabel('Temperature (K)')
    plt.title('Temperature')
    plt.grid(True)
    plt.legend()

    if output_path:
        plt.savefig(output_path)
    plt.show()


def plot_simulated_vs_real(simulated_df: pd.Series, real_series: pd.Series, sensor_name: str, output_path=None, start_date=None, end_date=None):
    """
    Plot simulated and real current on the same plot (time series overlay).
    Args:
        simulated_df: Series with simulated current, indexed by time (sensor name as Series.name)
        real_series: Series with real current, indexed by time
        sensor_name: Name of the sensor
        output_path: Path to save the plot
        start_date: Start date for plotting
        end_date: End date for plotting
    """
    # Ensure correct index type
    if not isinstance(simulated_df.index, pd.DatetimeIndex):
        try:
            simulated_df.index = pd.to_datetime(simulated_df.index)
        except Exception:
            pass
    if not isinstance(real_series.index, pd.DatetimeIndex):
        try:
            real_series.index = pd.to_datetime(real_series.index)
        except Exception:
            pass
    if start_date is None:
        start_date = min(simulated_df.index.min(), real_series.index.min())
    if end_date is None:
        end_date = max(simulated_df.index.max(), real_series.index.max())
    plt.figure(figsize=(12, 8))
    plt.ylim(0, 0.4)
    plt.scatter(real_series.index, real_series.values, color='red', s=1, label='Real Current')
    plt.scatter(simulated_df.index, simulated_df.values, color='blue', s=1, label='Simulated Current')
    plt.xlim(start_date, end_date)
    plt.ylabel('Current (mA)')
    plt.title(f'Comparison of Real vs Simulated Current for Sensor {sensor_name} 1min step')
    plt.grid(True)
    plt.legend()
    if output_path:
        plt.savefig(output_path)
    plt.show()
    plt.close()


def plot_all_sensors(simulated_df, real_df, sensors, output_dir="out_data", start_date=None, end_date=None):
    # Plot of simulated current for all sensors
    plt.figure(figsize=(12, 12))
    for sensor in sensors:
        plt.scatter(simulated_df.index, simulated_df[sensor], s=1, label=sensor)
    plt.xlim(start_date, end_date)
    #plt.ylim(0, 10)
    plt.ylabel('Current (mA)')
    plt.title('Simulated Current for All Sensors')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "all_simulated.png"))
    plt.show()
    plt.close()
    # Plot of real current for all sensors
    plt.figure(figsize=(12, 12))
    # Resample real data for each sensor
    real_df_daily = real_df.resample('1D').mean()
    for sensor in sensors:
        plt.scatter(real_df_daily.index, real_df_daily[sensor], s=1, label=sensor)
    plt.xlim(start_date, end_date)
    plt.ylabel('Current (mA)')
    plt.title('Real Current for All Sensors')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "all_real.png"))
    plt.show()
    plt.close()


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
