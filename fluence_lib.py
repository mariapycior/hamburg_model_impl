"""
Fluence calculation library
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

def load_sensor_current(file_path: str) -> pd.DataFrame:
    current_df = pd.read_csv(file_path)
    current_df['TS'] = pd.to_datetime(current_df['TS'])
    current_df.set_index('TS', inplace=True)
    return current_df

def load_data(fluence_file: str, temp_files: list) -> tuple:
    """
    Load fluence and temperature data from CSV files.
    
    Args:
        fluence_file: Path to the fluence file
        temp_files: List of paths to temperature files
        
    Returns:
        Tuple of (fluence_df, temp_df)
    """
    fluence_df = load_avg_fluence(fluence_file)
    
    # Sort files by year (assuming they are named with year in the filename)
    temp_files = sorted(temp_files, key=lambda x: int(x.split('_')[-1].split('.')[0]))
    
    # Load and concatenate temperature files
    temp_dfs = []
    for temp_file in temp_files:
        temp_df = load_temperature_data(temp_file)
        temp_dfs.append(temp_df)
    
    temp_df = pd.concat(temp_dfs, axis=0, join='outer')
    
    temp_df = temp_df.groupby(temp_df.index).max()
    
    # Sort by index to ensure proper order
    temp_df = temp_df.sort_index()
    
    return fluence_df, temp_df

def calculate_temperature_factor_theta(T_a: float, E_I_star: float, T_ref: float, kB: float) -> float:
    return np.exp(-E_I_star / kB * (1/T_a - 1/T_ref))

def calculate_intrinsic_lifetime_tau(k_0I: float, E_I: float, T_a: float, kB: float) -> float:
    return (k_0I * np.exp(-E_I / (kB * T_a)))/60  # Convert to minutes

def calculate_temperature_factor_theta_vectorized(T_a: np.ndarray, E_I_star: float, T_ref: float, kB: float) -> np.ndarray:
    return np.exp(-E_I_star / kB * (1/T_a - 1/T_ref))

def calculate_intrinsic_lifetime_tau_vectorized(k_0I: float, E_I: float, T_a: np.ndarray, kB: float) -> np.ndarray:
    return (k_0I * np.exp(-E_I / (kB * T_a))) / 60  # Convert to minutes

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

    # Przesuń indeks fluencji
    fluence_series.index = fluence_series.index - shift

    # Uzupełnij zerami brakujące okresy na pełnym zakresie temperatury
    full_index = pd.date_range(start=temp_start, end=temp_end, freq='10T')
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
        
        # Idziemy do przodu aż coś przekroczy tolerancję
        while i < len(df):
            temp_change = abs(df['temperature'].iloc[i] - base_temp)
            flu_change = abs(df['fluence'].iloc[i] - base_flu)
            
            if temp_change > temp_tolerance or flu_change > fluence_tolerance:
                break
            i += 1

        # Tworzymy okres
        period_df = df.iloc[current_start:i]
        avg_temp = period_df['temperature'].mean()
        avg_flu = period_df['fluence'].sum()
        time = (i - current_start) * 10  # zakładamy krok co 10 minut

        combined.append({
            'start_time': df.index[current_start],  # zapamiętujemy czas początku
            'temperature': avg_temp,
            'fluence': avg_flu,
            'time': float(time)
        })

    # Tworzymy wynikowy DataFrame z czasem jako indeksem
    result = pd.DataFrame(combined).set_index('start_time')
    return result




def simulate_current_sensor(fluence_df: pd.Series, temp_df: pd.Series, params) -> pd.DataFrame:
    print("Starting current simulation...")
    
    # Create initial result DataFrame
    result = pd.DataFrame(index=fluence_df.index)
    result['fluence'] = fluence_df.values
    result['temperature'] = temp_df.values

    # Combine periods with small changes
    combined = result.copy() 
    combined = combine_periods(result, temp_tolerance=0.0, fluence_tolerance=0.0)
    combined['current'] = 0.0

    # Calculate reduction percentage
    original_periods = len(result)
    combined_periods = len(combined)
    reduction_percentage = ((original_periods - combined_periods) / original_periods) * 100
    print(f"Combined periods: {combined_periods} (reduced by {reduction_percentage:.1f}%)")
    
    # Calculate time-dependent values for combined periods
    temperatures = combined['temperature'].values
    fluences = combined['fluence'].values
    times = combined['time'].values
    
    tau_j = calculate_intrinsic_lifetime_tau_vectorized(params.k_0I, params.E_I, temperatures, params.kb)
    theta_j = calculate_temperature_factor_theta_vectorized(temperatures, params.E_I_star, params.T_ref, params.kb)
    
    #times = 10
    print("Calculating time factors...")
    time_tau = times / tau_j
    time_theta = theta_j * times / params.t_0

    #time_tau.to_csv('time_tau_old.csv')
    
    print("Starting main calculation loop...")
    N = len(combined)
    for n in tqdm.tqdm(range(N)):
        I_leak = 0.0
        if n == 30000:
            print(n)
            #break
        I_leak = calculate_leakage_current(fluences[:n], time_tau[:n], time_theta[:n], 
                                           params.alpha_I, params.alpha_0_star, params.beta, params.V)
        combined.loc[combined.index[n], 'current'] = I_leak*1000 + 0.5

    combined = adjust_simulated_current_with_temperature(
        data = combined,
        params=params,
    )

    print("Simulation completed!")
    return combined



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
    plt.scatter(result_df.index, result_df['current'], color='blue', s=10, label='Leakage Current Simulated')
    plt.xlim(start_date, end_date)
    plt.ylim(0, 1)
    plt.ylabel('Current (mA)')
    plt.title(f'Simulated Leakage Current for Sensor {sensor_name}')
    plt.grid(True)
    plt.legend()
    
    plt.subplot(4, 1, 2)
    plt.scatter(real_current.index, real_current, color='red', s=10, label='Leakage Current (Real Data)')
    plt.xlim(start_date, end_date)
    plt.ylabel('Current (mA)')
    plt.ylim(0, 1)
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

def prepare_sensor_current(current_df: pd.DataFrame, temp_df: pd.DataFrame, params, sensor_name: str) -> pd.DataFrame:
    current_adjusted = adjust_real_current_with_temperature(current_df, temp_df, params, sensor_name)
    return current_adjusted

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
    T_ref = params.T_ref
    E_eff = 1.24  # Eg
    kB = params.kb
    print(len(T))
    R_Tref = (T_ref / T) ** 2 * np.exp(-(E_eff / (2 * kB)) * (1/T - 1/T_ref))
    
    adjusted_current = data.copy()
    adjusted_current['current'] = adjusted_current['current'].values * R_Tref
    return adjusted_current

def plot_simulated_vs_real(result_df: pd.DataFrame, current_sample_df: pd.DataFrame, sensor_name: str, 
                          output_path: str = None, start_date: pd.Timestamp = None, end_date: pd.Timestamp = None):
    """
    Plot simulated and real current on the same plot.
    
    Args:
        result_df: DataFrame with simulation results
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
    plt.ylim(0,0.25)
    plt.ylabel('Current (mA)')
    plt.title(f'Comparison of Real vs Simulated Current for Sensor {sensor_name}')
    plt.grid(True)
    plt.legend()

    if output_path:
        plt.savefig(output_path)
    plt.show()

