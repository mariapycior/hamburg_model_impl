"""
Fluence calculation library

This script loads fluence and temperature data for further analysis.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import tqdm


def load_avg_fluence(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path, skiprows=4)
    df['bin_centre_date'] = pd.to_datetime(df['bin_centre_date'], format='%d-%m-%Y %H:%M:%S')
    df['TS'] = df['bin_centre_date'] - pd.Timedelta(minutes=5)
    df.set_index('TS', inplace=True)
    df.drop('bin_centre_date', axis=1, inplace=True)
    return df

def load_temperature_data(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    df['TS'] = pd.to_datetime(df['TS'])
    df.set_index('TS', inplace=True)
    df = df.dropna(how='all')
    return df

def calculate_temperature_factor_theta(T_a: float, E_I_star: float, T_ref: float, kB: float) -> float:
    return np.exp(-E_I_star / kB * (1/T_a - 1/T_ref))

def calculate_intrinsic_lifetime_tau(k_0I: float, E_I: float, T_a: float, kB: float) -> float:
    return 1.0 / (k_0I * np.exp(-E_I / (kB * T_a)))

def calculate_temperature_factor_theta_vectorized(T_a: np.ndarray, E_I_star: float, T_ref: float, kB: float) -> np.ndarray:
    return np.exp(-E_I_star / kB * (1/T_a - 1/T_ref))

def calculate_intrinsic_lifetime_tau_vectorized(k_0I: float, E_I: float, T_a: np.ndarray, kB: float) -> np.ndarray:
    return 1.0 / (k_0I * np.exp(-E_I / (kB * T_a)))

def align_temperature_to_fluence(fluence_df: pd.DataFrame, temp_df: pd.DataFrame, sensor_name: str) -> pd.DataFrame:
    fluence_series = fluence_df[sensor_name]
    temp_series = temp_df[sensor_name]
        
    fluence_start = fluence_series.index[0]
    fluence_end = fluence_series.index[-1]
    temp_start = temp_series.index[0]
    temp_end = temp_series.index[-1]
    
    start_time = max(fluence_start, temp_start)
    end_time = min(fluence_end, temp_end)
    
    
    fluence_series = fluence_series[(fluence_series.index >= start_time) & (fluence_series.index <= end_time)]
    temp_series = temp_series[(temp_series.index >= start_time) & (temp_series.index <= end_time)]
    
    temp_series = temp_series.resample('10min').mean()
    
    temp_series = temp_series.bfill()
    temp_series = temp_series.ffill()
    
    temp_first = temp_series.index[0]
    fluence_first = fluence_series.index[0]

    
    time_diff = (fluence_first - temp_first).total_seconds() % 600
    if time_diff > 300:
        time_diff = time_diff - 600
    
    shift = timedelta(seconds=time_diff)
    
    fluence_series.index = fluence_series.index - shift
    fluence_series = fluence_series.reindex(pd.date_range(fluence_series.index.min(), fluence_series.index.max(), freq='10T'), fill_value=0)
        
    return fluence_series, temp_series

import pandas as pd

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


def simulate_current_sensor(fluence_df: pd.Series, temp_df: pd.Series, sensor_name: str, params) -> pd.DataFrame:
    print("Starting current simulation...")
    time = 600  # s

    if not fluence_df.index.equals(temp_df.index):
        raise ValueError("Indexes of fluence_df and temp_df must match!")

    result = pd.DataFrame(index=fluence_df.index)
    result['current'] = 0.0
    result['fluence'] = fluence_df.values
    result['temperature'] = temp_df.values

    # Vectorized calculation of tau_j and Theta_j
    temperatures = result['temperature'].values
    tau_j = calculate_intrinsic_lifetime_tau_vectorized(params.k_0I, params.E_I, temperatures, params.kb)
    theta_j = calculate_temperature_factor_theta_vectorized(temperatures, params.E_I_star, params.T_ref, params.kb)
    
    print("Calculating time factors...")
    # Pre-calculate time factors
    time_tau = time / tau_j
    time_theta = theta_j * time / params.t_0
    
    print("Starting main calculation loop...")
    n = len(result)
    for i in tqdm.tqdm(range(n)):
        # Use numpy slicing for faster sum calculation
        sum_1 = np.sum(time_tau[:i-1])
        sum_2 = np.sum(time_theta[:i-1])
        
        # Calculate alpha and current
        alpha = params.alpha_I * np.exp(-sum_1) + params.alpha_0_star - params.beta * np.log(sum_2)
        result.loc[result.index[i], 'current'] = result['fluence'].iloc[i] * params.V * alpha
        
        # Print progress info every 10% of total
        if i % (n//10) == 0:
            print(f"Progress: {i/n*100:.1f}%, Current sum_1: {sum_1:.2e}, sum_2: {sum_2:.2e}")

    print("Simulation completed!")
    return result


def plot_leakage_current(result_df: pd.DataFrame, sensor_name: str, output_path: str = None):
    plt.figure(figsize=(12, 8))
    
    # Plot leakage current
    plt.subplot(3, 1, 1)
    plt.plot(result_df.index, result_df['current'], 'bo', label='Leakage Current')
    plt.ylabel('Current (A)')
    plt.title(f'Leakage Current for Sensor {sensor_name}')
    plt.grid(True)
    plt.legend()
    
    # Plot fluence
    plt.subplot(3, 1, 2)
    plt.plot(result_df.index, result_df['fluence'], 'ro', label='Fluence')
    plt.ylabel('Fluence (n/cm²)')
    plt.title('Fluence')
    plt.grid(True)
    plt.legend()
    
    # Plot temperature
    plt.subplot(3, 1, 3)
    plt.plot(result_df.index, result_df['temperature'], 'go', label='Temperature')
    plt.ylabel('Temperature (K)')
    plt.xlabel('Time')
    plt.title('Temperature')
    plt.grid(True)
    plt.legend()
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path)
    else:
        plt.show()
    
    plt.close()
