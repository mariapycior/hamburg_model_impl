"""
Fluence calculation library

This script loads fluence and temperature data for further analysis.
"""

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
    return (k_0I * np.exp(-E_I / (kB * T_a)))/60  # Convert to minutes

def calculate_temperature_factor_theta_vectorized(T_a: np.ndarray, E_I_star: float, T_ref: float, kB: float) -> np.ndarray:
    return np.exp(-E_I_star / kB * (1/T_a - 1/T_ref))

def calculate_intrinsic_lifetime_tau_vectorized(k_0I: float, E_I: float, T_a: np.ndarray, kB: float) -> np.ndarray:
    return  (k_0I * np.exp(-E_I / (kB * T_a))) / 60  # Convert to minutes

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

from numba import njit
import numpy as np

@njit
def calculate_leakage_current(fluence, time_tau, time_theta, alpha_I, alpha_0_star, beta, V):
    I_leak = 0.0
    N = len(fluence)
    sum_1 = 0.0
    sum_2 = 0.0

    # Precompute cumulative sums in reverse order
    for i in range(N - 1, -1, -1):
        sum_1 += time_tau[i]
        sum_2 += time_theta[i]

        # Calculate alpha
        alpha = alpha_I * np.exp(-sum_1) + alpha_0_star - beta * np.log(sum_2)

        # Calculate leakage current
        #R_Tref = (T / T_ref) ** 2 * np.exp(-(E_eff / (2 * kB)) * (1 / T - 1 / T_ref))

        I_leak += fluence[i] * V * alpha


    return I_leak


def simulate_current_sensor(fluence_df: pd.Series, temp_df: pd.Series, params) -> pd.DataFrame:
    print("Starting current simulation...")
    time = 10  # s

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
    N = len(result)
    for n in tqdm.tqdm(range(N)):
        I_leak = 0.0
        if n == 100000:
            print(n)
            #break
        # Call the Numba-optimized leakage current function
        I_leak = calculate_leakage_current(result['fluence'].iloc[:n].values, time_tau[:n], time_theta[:n], 
                                           params.alpha_I, params.alpha_0_star, params.beta, params.V)
        # Store the result in the dataframe
        result.loc[result.index[n], 'current'] = I_leak*1000 # Convert to mA

    print("Simulation completed!")
    return result


def plot_leakage_current(result_df: pd.DataFrame, current_sample_df: pd.DataFrame, sensor_name: str, output_path: str = None):

    if sensor_name in current_sample_df.columns:
        real_current = current_sample_df[sensor_name]
    else:
        raise ValueError(f"Sensor {sensor_name} not found in the current sample file.")

    start_date = pd.Timestamp("2016-04-01")
    end_date = pd.Timestamp("2018-12-01")

    plt.figure(figsize=(12, 16))
    
    # Plot simulated leakage current
    plt.subplot(4, 1, 1)
    plt.scatter(result_df.index, result_df['current'], color='blue', s=10, label='Leakage Current Simulated')
    plt.xlim(start_date, end_date)
    plt.ylabel('Current (mA)')
    plt.title(f'Simulated Leakage Current for Sensor {sensor_name}')
    plt.grid(True)
    plt.legend()
    
    # Plot real leakage current
    plt.subplot(4, 1, 2)
    plt.scatter(real_current.index, real_current, color='red', s=10, label='Leakage Current (Real Data)')
    plt.xlim(start_date, end_date)
    plt.ylabel('Current (mA)')
    plt.title(f'Real Leakage Current for Sensor {sensor_name}')
    plt.grid(True)
    plt.legend()
    
    # Plot fluence
    plt.subplot(4, 1, 3)
    plt.scatter(result_df.index, result_df['fluence'], color='green', s=10, label='Fluence')
    plt.xlim(start_date, end_date)
    plt.ylabel('Fluence (n/cm²)')
    plt.title('Fluence')
    plt.grid(True)
    plt.legend()
    
    # Plot temperature
    plt.subplot(4, 1, 4)
    plt.scatter(result_df.index, result_df['temperature'], color='magenta', s=10, label='Temperature')
    plt.xlim(start_date, end_date)
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


def adjust_current_with_temperature(
    current_data: pd.DataFrame,
    temperature_data: pd.DataFrame,
    params,
    column: str
) -> pd.DataFrame:
    """
    Adjust the current data based on the nearest temperature and the R(T) factor using parameters from the params object.
    Adjust only when fluence is non-zero; otherwise, set current to NaN.
    
    Parameters:
        current_data (pd.DataFrame): DataFrame containing the current data with 'current' and 'fluence' columns.
        temperature_data (pd.DataFrame): DataFrame containing the temperature data.
        params: Parameters object containing physical constants and settings.
        column (str): The column name in temperature_data to use for temperature values.
    
    Returns:
        pd.DataFrame: The same DataFrame as current_data with the 'current' column adjusted.
    """
    # Ensure data is sorted by index
    current_data = current_data.sort_index()
    temperature_data = temperature_data.sort_index()

    # Align temperature data to current data timestamps
    aligned_temp = temperature_data[column].reindex(current_data.index, method='nearest')
    T = aligned_temp.values
    T_ref = params.T_ref
    E_eff = params.E_I_star
    kB = params.kb

    # Calculate R(T) factor
    R_Tref = (T / T_ref) ** 2 * np.exp(-(E_eff / (2 * kB)) * (1 / T - 1 / T_ref))

    # Adjust the 'current' column only where fluence is non-zero
    adjusted_current = current_data['current'].copy()
    adjusted_current[current_data['fluence'] > 0] *= R_Tref[current_data['fluence'] > 0]
    adjusted_current[current_data['fluence'] == 0] = np.nan

    # Update the current column in the DataFrame
    current_data['current'] = adjusted_current

    return current_data
