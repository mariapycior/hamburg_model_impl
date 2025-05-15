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
    plt.ylim(0, 0.3)
    plt.ylabel('Current (mA)')
    plt.title(f'Simulated Leakage Current for Sensor {sensor_name}')
    plt.grid(True)
    plt.legend()
    
    plt.subplot(4, 1, 2)
    plt.scatter(real_current.index, real_current, color='red', s=1, label='Leakage Current (Real Data)')
    plt.xlim(start_date, end_date)
    plt.ylabel('Current (mA)')
    plt.ylim(0, 0.3)
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


def plot_simulated_vs_real(simulated_series, real_series, sensor_name, output_path=None, start_date=None, end_date=None, weekly_average=False):
    """
    Plot simulated and real current on the same plot (time series overlay).
    Handles missing data (NaN, pd.NA) robustly.
    Args:
        simulated_series: Series or DataFrame with simulated current, indexed by time
        real_series: Series or DataFrame with real current, indexed by time
        sensor_name: Name of the sensor
        output_path: Path to save the plot
        start_date: Start date for plotting
        end_date: End date for plotting
        weekly_average: If True, plot 7-day rolling mean
    """
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt

    # Obsługa przypadków, gdy któryś z serii jest None
    if simulated_series is None:
        simulated_series = pd.Series()
    if real_series is None:
        real_series = pd.Series()
        
    # Extract series if DataFrame
    if isinstance(simulated_series, pd.DataFrame):
        if simulated_series.shape[1] == 1:
            simulated_series = simulated_series.iloc[:, 0]
        else:
            simulated_series = simulated_series.squeeze()
    if isinstance(real_series, pd.DataFrame):
        if real_series.shape[1] == 1:
            real_series = real_series.iloc[:, 0]
        else:
            real_series = real_series.squeeze()

    # Ensure correct type and handle NA
    sim = pd.to_numeric(simulated_series, errors='coerce')
    real = pd.to_numeric(real_series, errors='coerce')
    df = pd.DataFrame({'simulated': sim, 'real': real})
    df = df.dropna(how='all')

    # Filter by date
    if start_date is not None:
        df = df[df.index >= pd.to_datetime(start_date)]
    if end_date is not None:
        df = df[df.index <= pd.to_datetime(end_date)]

    if weekly_average:
        df = df.rolling('7d', min_periods=1).mean()

    plt.figure(figsize=(12, 8))
    plt.ylim(0,6)
    # Zakres osi X
    if start_date is not None and end_date is not None and not df.empty:
        plt.xlim(pd.to_datetime(start_date), pd.to_datetime(end_date))
    elif not df.empty:
        plt.xlim(df.index.min(), df.index.max())
    if not df['real'].isna().all():
        plt.scatter(df.index, df['real'], color='red', s=1, label='Real Current')
    if not df['simulated'].isna().all():
        plt.scatter(df.index, df['simulated'], color='blue', s=1, label='Simulated Current')
    plt.ylabel('Current (mA)')
    plt.xlabel('Time')
    plt.title(f'Comparison of Real vs Simulated Current for Sensor {sensor_name}')
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
    plt.ylabel('Current (mA)')
    plt.title('Simulated Current for All Sensors')
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
    plt.ylabel('Current (mA)')
    plt.title('Real Current for All Sensors')
    plt.grid(True)
    plt.tight_layout()
    plt.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), title='Sensors', fontsize='small')
    if output_dir is not None:
        plt.savefig(os.path.join(output_dir, "all_real.png"), bbox_inches='tight')
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
    plt.ylabel('Simulated current (mA)')
    plt.title('Simulated current for all sensors (simple overlay)')
    plt.grid(True)
    plt.tight_layout()
    if output_path:
        plt.savefig(output_path)
    plt.close()


def plot_simulated_pandas(simulated_df, output_path=None):
    import matplotlib.pyplot as plt
    plt.figure(figsize=(12, 8))
    simulated_df.plot(ax=plt.gca(), legend=False, alpha=0.7)
    plt.ylabel("Simulated current (mA)")
    plt.title("Simulated current for all sensors (pandas plot)")
    plt.tight_layout()
    if output_path:
        plt.savefig(output_path)
    plt.close()
