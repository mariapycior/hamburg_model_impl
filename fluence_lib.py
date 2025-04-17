import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import tqdm
import os

def load_avg_fluence(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path, skiprows=4)
    df['bin_centre_date'] = pd.to_datetime(df['bin_centre_date'], format='%d-%m-%Y %H:%M:%S')
    df['TS'] = df['bin_centre_date'] - pd.Timedelta(minutes=5)
    df.set_index('TS', inplace=True)
    df.drop('bin_centre_date', axis=1, inplace=True)
    print(f"Loaded fluence data from {file_path}")
    return df

def load_temperature_data(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    df['TS'] = pd.to_datetime(df['TS'])
    df.set_index('TS', inplace=True)
    df = df.dropna(how='all')
    print(f"Loaded temperature data from {file_path}")
    return df

def load_sensor_current(file_path: str) -> pd.DataFrame:
    current_df = pd.read_csv(file_path)
    current_df['TS'] = pd.to_datetime(current_df['TS'])
    current_df.set_index('TS', inplace=True)
    print(f"Loaded sensor current from {file_path}")
    return current_df

def load_data(fluence_file: str, temp_files: list) -> tuple:
    fluence_df = load_avg_fluence(fluence_file)
    temp_files = sorted(temp_files, key=lambda x: int(x.split('_')[-1].split('.')[0]))
    temp_dfs = []
    for temp_file in temp_files:
        temp_df = load_temperature_data(temp_file)
        temp_dfs.append(temp_df)
    temp_df = pd.concat(temp_dfs, axis=0, join='outer')
    temp_df = temp_df.groupby(temp_df.index).max()
    temp_df = temp_df.sort_index()
    print("Loaded all fluence and temperature data")
    return fluence_df, temp_df

def calculate_temperature_factor_theta(T_a: float, E_I_star: float, T_ref: float, kB: float) -> float:
    return np.exp(-E_I_star / kB * (1/T_a - 1/T_ref))

def calculate_intrinsic_lifetime_tau(k_0I: float, E_I: float, T_a: float, kB: float) -> float:
    return (k_0I * np.exp(-E_I / (kB * T_a)))/60

def calculate_temperature_factor_theta_vectorized(T_a: np.ndarray, E_I_star: float, T_ref: float, kB: float) -> np.ndarray:
    return np.exp(-E_I_star / kB * (1/T_a - 1/T_ref))

def calculate_intrinsic_lifetime_tau_vectorized(k_0I: float, E_I: float, T_a: np.ndarray, kB: float) -> np.ndarray:
    return (k_0I * np.exp(-E_I / (kB * T_a))) / 60

def align_temperature_to_fluence(fluence_df: pd.DataFrame, temp_df: pd.DataFrame, sensor_name: str) -> pd.DataFrame:
    fluence_series = fluence_df[sensor_name]
    temp_series = temp_df[sensor_name]
    temp_series = temp_series.resample('10min').mean()
    temp_start = temp_series.index[0]
    temp_end = temp_series.index[-1]
    temp_series = temp_series.bfill().ffill()
    temp_first = temp_series.index[0]
    fluence_first = fluence_series.index[0]
    time_diff = (fluence_first - temp_first).total_seconds() % 600
    if time_diff > 300:
        time_diff -= 600
    shift = timedelta(seconds=time_diff)
    fluence_series.index = fluence_series.index - shift
    full_index = pd.date_range(start=temp_start, end=temp_end, freq='10min')
    fluence_series = fluence_series.reindex(full_index, fill_value=0)
    return fluence_series, temp_series

def prepare_sensor_data(fluence_df: pd.DataFrame, temp_df: pd.DataFrame, sensor_name: str) -> tuple:
    fluence_series, temp_series = align_temperature_to_fluence(fluence_df, temp_df, sensor_name)
    common_index = fluence_series.index.intersection(temp_series.index)
    fluence_series_filtered = fluence_series[common_index]
    temp_series_filtered = temp_series[common_index]
    fluence_df_result = pd.DataFrame({fluence_series.name: fluence_series_filtered})
    temp_df_result = pd.DataFrame({temp_series.name: temp_series_filtered})
    fluence_df_result.index.name = 'ts'
    temp_df_result.index.name = 'ts'
    return fluence_df_result, temp_df_result

from numba import njit

@njit
def calculate_leakage_current(fluence, time_tau, time_theta, alpha_I, alpha_0_star, beta, V):
    I_leak = 0.0
    N = len(fluence)
    sum_1 = 0.0
    sum_2 = 0.0
    for i in range(N - 1, -1, -1):
        sum_1 += time_tau[i]
        sum_2 += time_theta[i]
        alpha = alpha_I * np.exp(-sum_1) + alpha_0_star - beta * np.log(sum_2)
        I_leak += fluence[i] * V * alpha
    return I_leak

def combine_periods(df: pd.DataFrame, temp_tolerance: float = 1, fluence_tolerance: float = 0.01) -> pd.DataFrame:
    combined = []
    i = 0
    while i < len(df):
        current_start = i
        base_temp = df['temperature'].iloc[i]
        base_flu = df['fluence'].iloc[i]
        while i < len(df):
            temp_change = abs(df['temperature'].iloc[i] - base_temp)
            flu_change = abs(df['fluence'].iloc[i] - base_flu)
            if temp_change > temp_tolerance or flu_change > fluence_tolerance:
                break
            i += 1
        period_df = df.iloc[current_start:i]
        avg_temp = period_df['temperature'].mean()
        avg_flu = period_df['fluence'].sum()
        time = (i - current_start) * 10  
        combined.append({
            'start_time': df.index[current_start],  
            'temperature': avg_temp,
            'fluence': avg_flu,
            'time': float(time)
        })
    result = pd.DataFrame(combined).set_index('start_time')
    return result

def simulate_current_sensor(fluence_df: pd.Series, temp_df: pd.Series, params) -> pd.DataFrame:
    result = pd.DataFrame(index=fluence_df.index)
    result['fluence'] = fluence_df.values
    result['temperature'] = temp_df.values
    combined = result.copy() 
    combined = combine_periods(result, temp_tolerance=0.0, fluence_tolerance=0.0)
    combined['current'] = 0.0
    temperatures = combined['temperature'].values
    fluences = combined['fluence'].values
    times = combined['time'].values
    tau_j = calculate_intrinsic_lifetime_tau_vectorized(params.k_0I, params.E_I, temperatures, params.kb)
    theta_j = calculate_temperature_factor_theta_vectorized(temperatures, params.E_I_star, params.T_ref, params.kb)
    time_tau = times / tau_j
    time_theta = theta_j * times / params.t_0
    N = len(combined)
    for n in range(N):
        I_leak = calculate_leakage_current(fluences[:n], time_tau[:n], time_theta[:n], 
                                           params.alpha_I, params.alpha_0_star, params.beta, params.V)
        combined.loc[combined.index[n], 'current'] = I_leak*1000#+ 0.5
    return combined

def prepare_sensor_current(current_df: pd.DataFrame, temp_df: pd.DataFrame, params, sensor_name: str) -> pd.DataFrame:
    current_adjusted = adjust_current_with_temperature(current_df, temp_df, params, sensor_name)
    return current_adjusted

def adjust_current_with_temperature(
    current_data: pd.DataFrame,
    temperature_data: pd.DataFrame,
    params,
    column: str
) -> pd.DataFrame:
    current_data = current_data.sort_index()
    temperature_data = temperature_data.sort_index()
    aligned_temp = temperature_data[column].reindex(current_data.index, method='nearest')
    T = aligned_temp.values
    T_ref = params.T_ref
    E_eff = 1.21 
    kB = params.kb
    R_Tref = (T_ref / T) ** 2 * np.exp(-(E_eff / (2 * kB)) * (1 / T_ref - 1 / T))
    adjusted_current = current_data[column].values * R_Tref
    return pd.DataFrame({f"{column}": adjusted_current}, index=current_data.index)

def find_common_sensors(*dfs: pd.DataFrame) -> list:
    common_sensors = set(dfs[0].columns)
    for df in dfs[1:]:
        common_sensors.intersection_update(df.columns)
    return sorted(list(common_sensors))

def process_single_sensor(fluence_df: pd.DataFrame, temp_df: pd.DataFrame, current_df: pd.DataFrame, params, sensor_name: str) -> tuple:
    fdf, tdf = prepare_sensor_data(fluence_df, temp_df, sensor_name)
    simulated_current = simulate_current_sensor(fdf[sensor_name], tdf[sensor_name], params)
    current_adjusted = prepare_sensor_current(current_df, temp_df, params, sensor_name)
    return simulated_current['current'], current_adjusted[sensor_name]

def process_all_sensors(fluence_df: pd.DataFrame, temp_df: pd.DataFrame, current_df: pd.DataFrame, params):
    common_sensors = find_common_sensors(fluence_df, temp_df, current_df)
    common_sensors = common_sensors[:15]
    all_simulated = {}
    all_real = {}
    
    for sensor_name in tqdm.tqdm(common_sensors):
        sim_current, real_current = process_single_sensor(
            fluence_df,
            temp_df,
            current_df,
            params,
            sensor_name
        )
        all_simulated[sensor_name] = sim_current
        all_real[sensor_name] = real_current
    
    return pd.DataFrame(all_simulated), pd.DataFrame(all_real), common_sensors

def load_and_combine_currents(current_files):
    if len(current_files) == 1:
        return load_sensor_current(current_files[0])
    current_dfs = [load_sensor_current(file) for file in current_files]
    return pd.concat(current_dfs, axis=0).groupby(level=0).last().sort_index()

def run_leakage_current_pipeline(fluence_file, temp_files, current_files, params, paths):
    current_df = load_and_combine_currents(current_files)
    fluence_df, temp_df = load_data(fluence_file, temp_files)
    
    # Get common sensors across all dataframes
    common_sensors = find_common_sensors(fluence_df, temp_df, current_df)
    print(f"Found {len(common_sensors)} common sensors across all datasets")
    #common_sensors = common_sensors[:5]  # Exclude 'TS' column
    # Filter dataframes to only include common sensors
    fluence_df = fluence_df[common_sensors]
    temp_df = temp_df[common_sensors]
    current_df = current_df[common_sensors]
    
    return process_all_sensors(fluence_df, temp_df, current_df, params)

def plot_leakage_current(result_df: pd.DataFrame, current_sample_df: pd.DataFrame, sensor_name: str, 
                         output_path: str = None, start_date: pd.Timestamp = None, end_date: pd.Timestamp = None):
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

def plot_simulated_vs_real(result_df: pd.DataFrame, current_sample_df: pd.DataFrame, sensor_name: str, 
                          output_path: str = None, start_date: pd.Timestamp = None, end_date: pd.Timestamp = None):
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

def plot_all_sensors(simulated_df: pd.DataFrame, real_df: pd.DataFrame, sensors, output_dir: str = "out_data", start_date=None, end_date=None):
    plt.figure(figsize=(12, 12))
    for sensor in sensors:
        plt.scatter(simulated_df.index, simulated_df[sensor], s=1, label=sensor)
    plt.xlim(start_date, end_date)
    plt.ylim(0, 10)
    plt.ylabel('Current (mA)')
    plt.title('Simulated Current for All Sensors')
    plt.grid(True)
    
    
    
    #plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
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
    #plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "all_real.png"))
    plt.show()
    plt.close()

def adjust_real_current_with_temperature(
    current_data: pd.DataFrame,
    temperature_data: pd.DataFrame,
    params,
    column: str
) -> pd.DataFrame:
    current_data = current_data.sort_index()
    temperature_data = temperature_data.sort_index()
    aligned_temp = temperature_data[column].reindex(current_data.index, method='nearest')
    T = aligned_temp.values
    T_ref = params.T_ref
    E_eff = 1.24 # Eg
    kB = params.kb
    
    R_Tref = 1#(T_ref / T) ** 2 * np.exp(-(E_eff / (2 * kB)) * (1 / T_ref - 1 / T))

    adjusted_current = current_data[column].values * R_Tref
    return pd.DataFrame({f"{column}": adjusted_current}, index=current_data.index)

def adjust_simulated_current_with_temperature(
    data: pd.DataFrame,
    params,
) -> pd.DataFrame:
    data = data.sort_index()
    T = data['temperature'].values
    #T = np.zeros_like(data['temperature'].values)+262.15
    T_ref = params.T_ref
    E_eff = 1.24  # Eg
    kB = params.kb
    
    R_Tref = (T_ref / T) ** 2 * np.exp(-(E_eff / (2 * kB)) * (1/T - 1/T_ref))
    
    adjusted_current = data.copy()
    adjusted_current['current'] = adjusted_current['current'].values * R_Tref
    
    # Set current to NaN where fluence is 0
    adjusted_current.loc[adjusted_current['fluence'] == 0, 'current'] = np.nan
    return adjusted_current
