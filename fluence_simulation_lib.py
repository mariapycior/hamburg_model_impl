import numpy as np
import pandas as pd
from datetime import timedelta
import tqdm
from config import CURRENT_YEAR_LIST, CURRENT_YEAR_RANGES, SIMULATION_PERIOD, RUN_MODE

def load_avg_fluence(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path, skiprows=4)
    df['bin_centre_date'] = pd.to_datetime(df['bin_centre_date'], format='%d-%m-%Y %H:%M:%S')
    df.set_index('bin_centre_date', inplace=True)
    df.index = df.index - pd.Timedelta(minutes=5)
    df.index.name = "TS"
    print(f"Loaded fluence data from {file_path}")
    return df

def load_temperature_data(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path, index_col="TS", parse_dates=["TS"])
    df = df.dropna(how='all')
    print(f"Loaded temperature data from {file_path}")
    return df

def load_data(fluence_file: str, temp_files: list) -> tuple:
    fluence_df = load_avg_fluence(fluence_file)
    temp_df = pd.concat([load_temperature_data(f) for f in sorted(temp_files, key=lambda x: int(x.split('_')[-1].split('.')[0]))], axis=0, join='outer')
    temp_df = temp_df.groupby(temp_df.index).max().sort_index()
    print("Loaded all fluence and temperature data")
    return fluence_df, temp_df

def calculate_temperature_factor_theta_vectorized(T_a: np.ndarray, E_I_star: float, T_ref: float, kB: float) -> np.ndarray:
    return np.exp(-E_I_star / kB * (1/T_a - 1/T_ref))

def calculate_intrinsic_lifetime_tau_vectorized(k_0I: float, E_I: float, T_a: np.ndarray, kB: float) -> np.ndarray:
    return np.exp(-E_I / (kB * T_a)) / 60 * k_0I

def align_temperature_to_fluence(fluence_df: pd.DataFrame, temp_df: pd.DataFrame, sensor_name: str) -> pd.DataFrame:
    fluence_series = fluence_df[sensor_name]
    fluence_series = fluence_series.resample(SIMULATION_PERIOD.lower()).sum()
    temp_series_raw = temp_df[sensor_name].resample(SIMULATION_PERIOD.lower()).mean()
    temp_series = temp_series_raw.ffill()
    temp_series = temp_series.bfill()
    freq_seconds = pd.to_timedelta(SIMULATION_PERIOD.lower()).total_seconds()
    shift = timedelta(seconds=((fluence_series.index[0] - temp_series.index[0]).total_seconds() % freq_seconds) - (freq_seconds if (fluence_series.index[0] - temp_series.index[0]).total_seconds() % freq_seconds > freq_seconds/2 else 0))
    print(f"[align_temperature_to_fluence] shift: {shift}, before: {fluence_series.index[0]}, after: {fluence_series.index[0] - shift}")
    fluence_series.index = fluence_series.index - shift
    full_index = pd.date_range(start=temp_series.index[0], end=temp_series.index[-1], freq=SIMULATION_PERIOD.lower())
    fluence_series = fluence_series.reindex(full_index, fill_value=0)

    return fluence_series, temp_series

def prepare_sensor_data(fluence_df: pd.DataFrame, temp_df: pd.DataFrame, sensor_name: str) -> tuple:
    fluence_series, temp_series = align_temperature_to_fluence(fluence_df, temp_df, sensor_name)
    common_index = fluence_series.index.intersection(temp_series.index)
    fluence_df_result = pd.DataFrame({fluence_series.name: fluence_series[common_index]})
    temp_df_result = pd.DataFrame({temp_series.name: temp_series[common_index]})
    fluence_df_result.index.name = 'ts'
    temp_df_result.index.name = 'ts'
    return fluence_df_result, temp_df_result

def find_common_sensors(*dfs) -> list:
    cols = [set(df.columns) for df in dfs]
    return sorted(set.intersection(*cols))

from numba import njit

@njit
def calculate_leakage_current(fluence, time_tau, time_theta, alpha_I, alpha_0_star, beta, V):
    I_leak = 0.0
    n = len(fluence)
    sum_1 = 0.0
    sum_2 = 0.0
    for j in range(n - 1, -1, -1):
        sum_1 += time_tau[j]
        sum_2 += time_theta[j]
        alpha = alpha_I * np.exp(-sum_1) + alpha_0_star - beta * np.log(sum_2)
        I_leak += fluence[j] * V * alpha
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
        freq_minutes = int(pd.to_timedelta(SIMULATION_PERIOD.lower()).total_seconds() // 60)
        time = (i - current_start) * freq_minutes
        combined.append({
            'start_time': df.index[current_start],  
            'temperature': avg_temp,
            'fluence': avg_flu,
            'time': float(time)
        })
    result = pd.DataFrame(combined).set_index('start_time')
    return result

def simulate_current_sensor(fluence_df: pd.Series, temp_df: pd.Series, params, sensor_name: str = None) -> pd.DataFrame:
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
    print('T_REF', params.T_ref)
    time_tau = times / tau_j
    time_theta = theta_j * times / params.t_0
    N = len(combined)
    for n in tqdm.tqdm(range(N), desc='Simulating current', total=N):
        I_leak = calculate_leakage_current(fluences[:n], time_tau[:n], time_theta[:n],
                                           params.alpha_I, params.alpha_0_star, params.beta, params.V)
        combined.loc[combined.index[n], 'current'] = I_leak * 1000
    print("Simulation completed!")
    if sensor_name is not None:
        combined = combined.rename(columns={
            "current": f"current_{sensor_name}",
            "temperature": f"temperature_{sensor_name}",
            "fluence": f"fluence_{sensor_name}",
            "time": f"time_{sensor_name}"
        })
    return combined

def process_single_sensor(fluence_df, temp_df, params, sensor_name):
    fdf, tdf = prepare_sensor_data(fluence_df, temp_df, sensor_name)
    sim_df = simulate_current_sensor(fdf[sensor_name], tdf[sensor_name], params, sensor_name=sensor_name)
    return sim_df

def run_leakage_current_pipeline(fluence_file, temp_files, params, sensor_name=None):
    fluence_df, temp_df = load_data(fluence_file, temp_files)
    if sensor_name is not None:
        common_sensors = [sensor_name]
        fluence_df = fluence_df[[sensor_name]]
        temp_df = temp_df[[sensor_name]]
    else:
        common_sensors = find_common_sensors(fluence_df, temp_df)
        print(f"Found {len(common_sensors)} common sensors across all datasets")
        fluence_df = fluence_df[common_sensors]
        temp_df = temp_df[common_sensors]
    return process_single_sensor(fluence_df, temp_df, params, sensor_name=sensor_name)

def get_current_files(paths, selected_years):
    return [paths.get_current_file(f) for f, years in CURRENT_YEAR_LIST
            if any(year in selected_years for year in years)]

def get_available_sensors(paths, selected_years):
    relevant_files = [f for f, years in CURRENT_YEAR_RANGES.items()
                      if any(year in selected_years for year in years)]
    all_current_dfs = [pd.read_csv(paths.get_current_file(f)) for f in relevant_files]
    common_sensors = set(all_current_dfs[0].columns) - {'TS'}
    for df in all_current_dfs[1:]:
        common_sensors &= (set(df.columns) - {'TS'})
    return sorted(common_sensors)