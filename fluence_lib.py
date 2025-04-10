"""
Fluence calculation library

This script loads fluence and temperature data for further analysis.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import tqdm

KB = 8.617333262145e-5
T_REF = 293.15
E_I_STAR = 1.0

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

def calculate_temperature_factor(T_a: float, E_I_star: float, T_ref: float) -> float:
    return np.exp(-E_I_star / KB * (1/T_a - 1/T_ref))

def calculate_intrinsic_lifetime(k_0I: float, E_I: float, T_a: float) -> float:
    return 1.0 / (k_0I * np.exp(-E_I / (KB * T_a)))

def align_temperature_to_fluence(fluence_df: pd.DataFrame, temp_df: pd.DataFrame, sensor_name: str) -> pd.DataFrame:
    fluence_series = fluence_df[sensor_name]
    temp_series = temp_df[sensor_name]
    
    print("\nTime ranges before filtering:")
    print(f"Fluence range: {fluence_series.index[0]} to {fluence_series.index[-1]}")
    print(f"Temp range: {temp_series.index[0]} to {temp_series.index[-1]}")
        
    fluence_start = fluence_series.index[0]
    fluence_end = fluence_series.index[-1]
    temp_start = temp_series.index[0]
    temp_end = temp_series.index[-1]
    
    start_time = max(fluence_start, temp_start)
    end_time = min(fluence_end, temp_end)
    
    print(f"\nCalculated overlap: {start_time} to {end_time}")
    
    fluence_series = fluence_series[(fluence_series.index >= start_time) & (fluence_series.index <= end_time)]
    temp_series = temp_series[(temp_series.index >= start_time) & (temp_series.index <= end_time)]
    
    print("\nFluence data for sensor after time selection:")
    print(fluence_series.head())
    
    print("\nTemperature data for sensor after time selection:")
    print(temp_series.head())
    
    temp_series = temp_series.resample('10min').mean()
    
    temp_series = temp_series.bfill()
    temp_series = temp_series.ffill()
    
    temp_first = temp_series.index[0]
    fluence_first = fluence_series.index[0]
    
    print(f"\nBefore alignment:")
    print(f"Fluence first timestamp: {fluence_first}")
    print(f"Temperature first timestamp: {temp_first}")
    
    time_diff = (fluence_first - temp_first).total_seconds() % 600
    if time_diff > 300:
        time_diff = time_diff - 600
    
    shift = timedelta(seconds=time_diff)
    print(f"Calculated shift: {shift} seconds")
    
    fluence_series.index = fluence_series.index - shift
    
    print(f"\nAfter alignment:")
    print(f"Fluence first timestamp: {fluence_series.index[0]}")
    print(f"Temperature first timestamp: {temp_first}")
    
    return fluence_series, temp_series

def prepare_sensor_data(fluence_df: pd.DataFrame, temp_df: pd.DataFrame, sensor_name: str) -> tuple:
    return align_temperature_to_fluence(fluence_df, temp_df, sensor_name)

def simulate_current_sensor(fluence_series: pd.Series, temp_series: pd.Series, sensor_name: str, params) -> pd.DataFrame:
    print("Starting current simulation...")
    
    result = pd.DataFrame(index=fluence_series.index)
    result['current'] = 0.0
    result['fluence'] = fluence_series.values
    
    temp_reindexed = temp_series.reindex(fluence_series.index, method='nearest')
    result['temperature'] = temp_reindexed.values
    
    delta_t_minutes = 10.0  # 10 minutes between samples
    
    irradiation_periods = []
    current_period_start = None
    
    # Find irradiation periods
    for i in range(1, len(result)):
        phi_eq = result.iloc[i]['fluence'] - result.iloc[i-1]['fluence']
        
        if phi_eq > 0 and current_period_start is None:
            current_period_start = i - 1
        elif phi_eq == 0 and current_period_start is not None:
            irradiation_periods.append((current_period_start, i))
            current_period_start = None
    
    if current_period_start is not None:
        irradiation_periods.append((current_period_start, len(result) - 1))
    
    print(f"Found {len(irradiation_periods)} irradiation periods")
    
    # Process each irradiation period separately
    for period_start, period_end in irradiation_periods:
        print(f"Processing period from {result.index[period_start]} to {result.index[period_end]}")
        
        # Reset sums for each period
        sum_t_tau = 0
        sum_theta_t = 0
        
        for i in tqdm.tqdm(range(period_start + 1, period_end + 1)):
            phi_eq = result.iloc[i]['fluence'] - result.iloc[i-1]['fluence']
            
            if phi_eq <= 0:
                continue
                
            T_j = result.iloc[i]['temperature']
            
            tau = calculate_intrinsic_lifetime(params.k_0I, params.E_I, T_j)
            theta = calculate_temperature_factor(T_j, params.E_I_star, params.T_ref)
            
            # Update sums
            sum_t_tau += delta_t_minutes / tau
            sum_theta_t += theta * delta_t_minutes
            
            # Calculate current increment
            delta_I = phi_eq * (
                params.alpha_I * np.exp(-sum_t_tau) + 
                params.alpha_0 - 
                params.beta * np.log(max(1e-10, sum_theta_t / params.t_0))
            )
            
            # Accumulate current
            if i > 0:
                result.iloc[i, result.columns.get_loc('current')] = result.iloc[i-1]['current'] + delta_I
    
    print("Simulation completed!")
    return result

def plot_leakage_current(result_df: pd.DataFrame, sensor_name: str, output_path: str = None):
    plt.figure(figsize=(12, 8))
    
    # Plot leakage current
    plt.subplot(3, 1, 1)
    plt.plot(result_df.index, result_df['current'], 'b-', label='Leakage Current')
    plt.ylabel('Current (A)')
    plt.title(f'Leakage Current for Sensor {sensor_name}')
    plt.grid(True)
    plt.legend()
    
    # Plot fluence
    plt.subplot(3, 1, 2)
    plt.plot(result_df.index, result_df['fluence'], 'r-', label='Fluence')
    plt.ylabel('Fluence (n/cm²)')
    plt.title('Fluence')
    plt.grid(True)
    plt.legend()
    
    # Plot temperature
    plt.subplot(3, 1, 3)
    plt.plot(result_df.index, result_df['temperature'], 'g-', label='Temperature')
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
