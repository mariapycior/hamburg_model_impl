import os
import matplotlib.pyplot as plt


def plot_leakage_current(simulated, real, sensor_name, output_dir=None):
    # Plot leakage current for a single sensor: simulated vs real
    plt.figure(figsize=(10, 5))
    plt.plot(simulated.index, simulated.values, label='Simulated', lw=2)
    plt.plot(real.index, real.values, label='Real', lw=2)
    plt.title(f'Leakage Current - {sensor_name}')
    plt.xlabel('Time')
    plt.ylabel('Current [nA]')
    plt.legend()
    plt.tight_layout()
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        plt.savefig(os.path.join(output_dir, f'leakage_current_{sensor_name}.png'))
    plt.show()
    plt.close()


def plot_simulated_vs_real(result_df, current_sample_df, sensor_name, output_path=None, start_date=None, end_date=None):
    """
    Plot simulated and real current on the same plot (time series overlay).
    Args:
        result_df: DataFrame with simulation results (must contain 'current' column)
        current_sample_df: DataFrame with real current data
        sensor_name: Name of the sensor
        output_path: Path to save the plot
        start_date: Start date for plotting
        end_date: End date for plotting
    """
    if sensor_name in current_sample_df.columns:
        real_current = current_sample_df[sensor_name]
    else:
        raise ValueError(f"Sensor {sensor_name} not found in the current sample file.")

    if start_date is None:
        start_date = min(result_df.index.min(), real_current.index.min())
    if end_date is None:
        end_date = max(result_df.index.max(), real_current.index.max())

    plt.figure(figsize=(12, 8))
    # Plot both real and simulated current on the same plot
    plt.scatter(real_current.index, real_current, color='red', s=1, label='Real Current')
    plt.scatter(result_df.index, result_df['current'], color='blue', s=1, label='Simulated Current')
    plt.xlim(start_date, end_date)
    #plt.ylim(0, 0.25)
    plt.ylabel('Current (mA)')
    plt.title(f'Comparison of Real vs Simulated Current for Sensor {sensor_name}')
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
