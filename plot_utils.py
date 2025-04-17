import os
import matplotlib.pyplot as plt


def plot_leakage_current(result_df, current_sample_df, sensor_name, output_path=None, start_date=None, end_date=None):
    if sensor_name in current_sample_df.columns:
        # Resample real current data to daily averages
        real_current = current_sample_df[sensor_name].resample('1D').mean()
    else:
        raise ValueError(f"Sensor {sensor_name} not found in the current sample file.")
    if start_date is None:
        start_date = min(result_df.index.min(), real_current.index.min())
    if end_date is None:
        end_date = max(result_df.index.max(), real_current.index.max())
    plt.figure(figsize=(12, 16))
    plt.subplot(4, 1, 1)
    plt.scatter(result_df.index, result_df['current'], color='blue', s=10, label='Leakage Current Simulated')
    plt.xlim(start_date, end_date)
    plt.ylim(0, 50)
    plt.ylabel('Current (mA)')
    plt.title(f'Simulated Leakage Current for Sensor {sensor_name}')
    plt.grid(True)
    plt.legend()
    plt.subplot(4, 1, 2)
    plt.scatter(real_current.index, real_current, color='red', s=10, label='Leakage Current (Real Data)')
    plt.xlim(start_date, end_date)
    plt.ylabel('Current (mA)')
    plt.ylim(0, 50)
    plt.title(f'Real Leakage Current for Sensor {sensor_name}')
    plt.grid(True)
    plt.legend()
    plt.subplot(4, 1, 3)
    plt.scatter(result_df.index, result_df['fluence'], color='green', s=10, label='Fluence')
    plt.xlim(start_date, end_date)
    plt.ylabel('Fluence (n/cm²)')
    plt.title('Fluence')
    plt.grid(True)
    plt.legend()
    plt.subplot(4, 1, 4)
    plt.scatter(result_df.index, result_df['temperature'], color='magenta', s=10, label='Temperature')
    plt.xlim(start_date, end_date)
    plt.ylabel('Temperature (K)')
    plt.title('Temperature')
    plt.grid(True)
    plt.legend()
    if output_path:
        plt.savefig(output_path)
    plt.show()

def plot_simulated_vs_real(result_df, current_sample_df, sensor_name, output_path=None, start_date=None, end_date=None):
    if sensor_name in current_sample_df.columns:
        # Resample real current data to daily averages
        real_current = current_sample_df[sensor_name].resample('1D').mean()
    else:
        raise ValueError(f"Sensor {sensor_name} not found in the current sample file.")
    if start_date is None:
        start_date = min(result_df.index.min(), real_current.index.min())
    if end_date is None:
        end_date = max(result_df.index.max(), real_current.index.max())
    plt.figure(figsize=(12, 8))
    plt.scatter(real_current.index, real_current, color='red', s=1, label='Real Current')
    plt.scatter(result_df.index, result_df['current'], color='blue', s=1, label='Simulated Current')
    plt.xlim(start_date, end_date)
    plt.ylim(0, 50)
    plt.ylabel('Current (mA)')
    plt.title(f'Comparison of Real vs Simulated Current for Sensor {sensor_name}')
    plt.grid(True)
    plt.legend()
    if output_path:
        plt.savefig(output_path)
    plt.show()

def plot_all_sensors(simulated_df, real_df, sensors, output_dir="out_data", start_date=None, end_date=None):
    plt.figure(figsize=(12, 12))
    for sensor in sensors:
        plt.scatter(simulated_df.index, simulated_df[sensor], s=1, label=sensor)
    plt.xlim(start_date, end_date)
    plt.ylim(0, 10)
    plt.ylabel('Current (mA)')
    plt.title('Simulated Current for All Sensors')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "all_simulated.png"))
    plt.show()
    plt.close()
    plt.figure(figsize=(12, 12))
    # Resample real data for each sensor
    real_df_daily = real_df.resample('1D').mean()
    for sensor in sensors:
        plt.scatter(real_df_daily.index, real_df_daily[sensor], s=1, label=sensor)
    plt.xlim(start_date, end_date)
    plt.ylim(0, 10)
    plt.ylabel('Current (mA)')
    plt.title('Real Current for All Sensors')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "all_real.png"))
    plt.show()
    plt.close()
