import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import tqdm
import os
from config import CURRENT_YEAR_LIST, CURRENT_YEAR_RANGES, CURRENT_TEMP_MODE, SIMULATION_PERIOD

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

def load_sensor_current(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path, index_col="TS", parse_dates=["TS"])
    print(f"Loaded sensor current from {file_path}")
    return df

def load_data(fluence_file: str, temp_files: list) -> tuple:
    fluence_df = load_avg_fluence(fluence_file)
    temp_df = pd.concat([load_temperature_data(f) for f in sorted(temp_files, key=lambda x: int(x.split('_')[-1].split('.')[0]))], axis=0, join='outer')
    temp_df = temp_df.groupby(temp_df.index).max().sort_index()
    print("Loaded all fluence and temperature data")
    return fluence_df, temp_df

def calculate_temperature_factor_theta(T_a: float, E_I_star: float, T_ref: float, kB: float) -> float:
    return np.exp(-E_I_star / kB * (1/T_a - 1/T_ref))

def calculate_intrinsic_lifetime_tau(k_0I: float, E_I: float, T_a: float, kB: float) -> float:
    return (k_0I * np.exp(-E_I / (kB * T_a)))/60

def calculate_temperature_factor_theta_vectorized(T_a: np.ndarray, E_I_star: float, T_ref: float, kB: float) -> np.ndarray:
    return np.exp(-E_I_star / kB * (1/T_a - 1/T_ref))

def calculate_intrinsic_lifetime_tau_vectorized(k_0I: float, E_I: float, T_a: np.ndarray, kB: float) -> np.ndarray:
    return np.exp(-E_I / (kB * T_a)) / 60 * k_0I

def align_temperature_to_fluence(fluence_df: pd.DataFrame, temp_df: pd.DataFrame, sensor_name: str) -> pd.DataFrame:
    fluence_series = fluence_df[sensor_name]
    # Agregacja fluencji do wybranego kroku czasowego
    fluence_series = fluence_series.resample(SIMULATION_PERIOD.lower()).sum()
    temp_series_raw = temp_df[sensor_name].resample(SIMULATION_PERIOD.lower()).mean()
    is_nan = temp_series_raw.isna()
    nan_periods = []
    start = None
    '''for idx, val in is_nan.items():
        if val and start is None:
            start = idx
        elif not val and start is not None:
            nan_periods.append((start, idx))
            start = None
    if start is not None:
        nan_periods.append((start, temp_series_raw.index[-1]))
    mask_265 = pd.Series(False, index=temp_series_raw.index)
    for s, e in nan_periods:
        duration_min = (e - s).total_seconds() / 60
        if duration_min > 5*60:
            mask_265[(mask_265.index >= s) & (mask_265.index < e)] = True
    temp_series[mask_265] = 261.15'''
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
        freq_minutes = int(pd.to_timedelta(SIMULATION_PERIOD.lower()).total_seconds() // 60)
        time = (i - current_start) * freq_minutes  # czas trwania okresu w minutach
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
    print('T_REF',params.T_ref)
    time_tau = times / tau_j
    time_theta = theta_j * times / params.t_0
    N = len(combined)
    for n in tqdm.tqdm(range(N), desc='Simulating current', total=N):
        I_leak = calculate_leakage_current(fluences[:n], time_tau[:n], time_theta[:n], 
                                           params.alpha_I, params.alpha_0_star, params.beta, params.V)
        combined.loc[combined.index[n], 'current'] = I_leak*1000#+ 0.5
    if CURRENT_TEMP_MODE == 'adjust_sim':
        combined = adjust_simulated_current_with_temperature(
            data = combined,
            params=params,
        )
    print("Simulation completed!")
    return combined

def prepare_sensor_current(current_df: pd.DataFrame, temp_df: pd.DataFrame, params, sensor_name: str) -> pd.DataFrame:
    if CURRENT_TEMP_MODE == 'adjust_real':
        return adjust_real_current_with_temperature(current_df, temp_df, params, sensor_name)
    else:
        return current_df

def process_single_sensor(fluence_df, temp_df, current_df, params, sensor_name):
    fdf, tdf = prepare_sensor_data(fluence_df, temp_df, sensor_name)
    sim_df = simulate_current_sensor(fdf[sensor_name], tdf[sensor_name], params)
    real_current = prepare_sensor_current(current_df, temp_df, params, sensor_name)[sensor_name]
    return sim_df, real_current

def process_all_sensors(fluence_df, temp_df, current_df, params, sensor_name=None):
    if sensor_name is not None:
        common_sensors = [sensor_name]
    else:
        common_sensors = find_common_sensors(fluence_df, temp_df, current_df)
    all_simulated = {}
    all_real = {}
    for sensor in tqdm.tqdm(common_sensors):
        sim_df, real_current = process_single_sensor(fluence_df, temp_df, current_df, params, sensor)
        # Dodaj tylko kolumnę 'current', z nazwą sensora
        all_simulated[sensor] = sim_df['current'].rename(sensor)
        all_real[sensor] = real_current
    if len(common_sensors) == 1:
        return all_simulated[common_sensors[0]], pd.DataFrame({common_sensors[0]: all_real[common_sensors[0]]}), common_sensors
    return pd.concat(all_simulated, axis=1), pd.DataFrame(all_real), common_sensors

def load_and_combine_currents(current_files):
    dfs = [load_sensor_current(f) for f in current_files]
    return dfs[0] if len(dfs) == 1 else pd.concat(dfs, axis=0).groupby(level=0).last().sort_index()

def run_leakage_current_pipeline(fluence_file, temp_files, current_files, params, paths, sensor_name=None):
    current_df = load_and_combine_currents(current_files)
    fluence_df, temp_df = load_data(fluence_file, temp_files)
    if sensor_name is not None:
        common_sensors = [sensor_name]
        fluence_df = fluence_df[[sensor_name]]
        temp_df = temp_df[[sensor_name]]
        current_df = current_df[[sensor_name]]
    else:
        common_sensors = find_common_sensors(fluence_df, temp_df, current_df)
        print(f"Found {len(common_sensors)} common sensors across all datasets")
        fluence_df = fluence_df[common_sensors]
        temp_df = temp_df[common_sensors]
        current_df = current_df[common_sensors]
    return process_all_sensors(fluence_df, temp_df, current_df, params, sensor_name=sensor_name)

def adjust_real_current_with_temperature(current_data: pd.DataFrame, temperature_data: pd.DataFrame, params, column: str) -> pd.DataFrame:
    if CURRENT_TEMP_MODE == 'none':
        return current_data
    T = temperature_data[column].reindex(current_data.index, method='nearest').values
    T_ref = params.T_ref
    E_eff = getattr(params, 'E_eff', 1.24)
    kB = params.kb
    R_Tref = (T_ref / T) ** 2 * np.exp(-(E_eff / (2 * kB)) * (1 / T_ref - 1 / T))
    out = current_data.copy()
    out[column] = out[column].values * R_Tref
    return out

def set_temperature_where_fluence_zero(data: pd.DataFrame, value: float = 261.15, min_duration_days: int = 30) -> pd.DataFrame:
    out = data.copy()
    if 'fluence' not in out.columns or 'temperature' not in out.columns:
        return out
    zero_mask = (out['fluence'] == 0)
    if zero_mask.sum() == 0:
        # Usuń wszystkie temperatury poniżej 260 i powyżej 264 (ustaw na NaN)
        out.loc[(out['temperature'] < 260) | (out['temperature'] > 264), 'temperature'] = float('nan')
        return out
    # Find consecutive zero-fluence intervals
    zero_groups = (zero_mask != zero_mask.shift()).cumsum()
    group_ids = zero_groups[zero_mask].unique()
    freq_minutes = int(pd.to_timedelta(SIMULATION_PERIOD.lower()).total_seconds() // 60)
    min_points = (min_duration_days * 24 * 60) // freq_minutes
    for gid in group_ids:
        idx = zero_groups[zero_groups == gid].index
        if len(idx) >= min_points:
            out.loc[idx, 'temperature'] = value
        else:
            out.loc[idx, 'temperature'] = float('nan')
    # Usuń wszystkie temperatury poniżej 260 i powyżej 264 (ustaw na NaN)
    out.loc[(out['temperature'] < 260) | (out['temperature'] > 290), 'temperature'] = float('nan')
    return out

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

def adjust_simulated_current_with_temperature(data: pd.DataFrame, params) -> pd.DataFrame:
    if CURRENT_TEMP_MODE == 'none':
        return data
    # Najpierw ustaw temperaturę tam gdzie fluencja == 0
    data = set_temperature_where_fluence_zero(data)
    T = data['temperature'].values
    T_ref = params.T_ref
    E_eff = getattr(params, 'E_eff', 1.24)
    kB = params.kb
    R_Tref = (T_ref / T) ** 2 * np.exp(-(E_eff / (2 * kB)) * (1/T - 1/T_ref))
    print('T_REF',T_ref)
    out = data.copy()
    out['current'] = out['current'].values * R_Tref
    return out
