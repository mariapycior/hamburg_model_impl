import numpy as np
import pandas as pd
from datetime import timedelta
import tqdm
import os
from config import CURRENT_YEAR_LIST, CURRENT_YEAR_RANGES, SIMULATION_PERIOD, RUN_MODE, SENSOR_NAME, CURRENT_TEMP_MODE, OUTPUT_SIMULATED_DF_PATH
from numba import njit

def load_avg_fluence(file_path: str) -> pd.DataFrame:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Fluence file not found: {file_path}")
    with open(file_path, 'r') as f:
        lines = [next(f) for _ in range(3)]
    try:
        bin_seconds = float(lines[2].split(',')[0])
    except Exception:
        bin_seconds = 300.0
    shift_seconds = bin_seconds / 2.0
    df = pd.read_csv(file_path, skiprows=4)
    df['bin_centre_date'] = pd.to_datetime(df['bin_centre_date'], format='%d-%m-%Y %H:%M:%S')
    df.set_index('bin_centre_date', inplace=True)
    df.index = df.index - pd.Timedelta(seconds=shift_seconds)
    return df

def load_temperature_data(file_path: str) -> pd.DataFrame:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Temperature file not found: {file_path}")
    df = pd.read_csv(file_path, index_col="TS", parse_dates=["TS"])
    df = df.dropna(how='all')
    return df

def load_data(fluence_file: str, temp_files: list) -> tuple:
    if not temp_files:
        raise ValueError("No temperature files provided")
    fluence_df = load_avg_fluence(fluence_file)
    sorted_temp_files = sorted(temp_files, key=lambda x: int(x.split('_')[-1].split('.')[0]))
    
    temp_dfs = []
    for temp_file in sorted_temp_files:
        try:
            temp_dfs.append(load_temperature_data(temp_file))
        except Exception as e:
            print(f"Skipping temperature file {temp_file} due to error: {str(e)}")
            
    if not temp_dfs:
        raise ValueError("No valid temperature data could be loaded")
        
    return fluence_df, pd.concat(temp_dfs).groupby(level=0).max().sort_index()

def calculate_temperature_factor_theta_vectorized(T_a: np.ndarray, E_I_star: float, T_ref: float, kB: float) -> np.ndarray:
    return np.exp(-E_I_star / kB * (1/T_a - 1/T_ref))

def calculate_intrinsic_lifetime_tau_vectorized(k_0I: float, E_I: float, T_a: np.ndarray, kB: float) -> np.ndarray:
    return np.exp(-E_I / (kB * T_a)) / 60 * k_0I

def align_temperature_to_fluence(fluence_df: pd.DataFrame, temp_df: pd.DataFrame, sensor_name: str) -> tuple:
    if sensor_name not in fluence_df.columns:
        raise KeyError(f"Sensor {sensor_name} not found in fluence data")
    if sensor_name not in temp_df.columns:
        raise KeyError(f"Sensor {sensor_name} not found in temperature data")
    fluence_series = fluence_df[sensor_name]
    temp_series = temp_df[sensor_name]
    # pobrane dane
    freq_seconds = pd.to_timedelta(SIMULATION_PERIOD.lower()).total_seconds()
    time_diff_seconds = (fluence_series.index[0] - temp_series.index[0]).total_seconds()
    modulo = time_diff_seconds % freq_seconds
    # tu bedzie modulo ok
    print(f"SIMULATION_PERIOD: {SIMULATION_PERIOD}")
    print(f"First fluence record: {fluence_series.index[0]}")
    print(f"First temperature record: {temp_series.index[0]}")
    print(f"Time difference: {time_diff_seconds} seconds")
    print(f"Modulo with simulation period: {modulo} seconds")
    
    min_modulo = modulo
    records_to_remove = 0
    
    max_temp_check = min(len(temp_series), int(freq_seconds / 60))
    
    for i in range(1, max_temp_check):
        new_time_diff = (fluence_series.index[0] - temp_series.index[i]).total_seconds()
        new_modulo = new_time_diff % freq_seconds
        if new_modulo < min_modulo:
            min_modulo = new_modulo
            records_to_remove = i
    
    print(f"Minimum modulo possible: {min_modulo} seconds")
    print(f"Records to remove from temperature: {records_to_remove}")
    
    # Usunięcie początkowych rekordów, aby zminimalizować modulo
    if records_to_remove > 0:
        temp_series = temp_series.iloc[records_to_remove:]
        print(f"Removed {records_to_remove} records from temperature series")
        print(f"New first temperature record: {temp_series.index[0]}")
    
    print(f"Fluence series length: {len(fluence_series)}")
    # dotąd jest dobrze
    # Obliczenie modulo po usunięciu rekordów
    new_time_diff = (fluence_series.index[0] - temp_series.index[0]).total_seconds()
    remaining_modulo = new_time_diff % freq_seconds
    print(f"Modulo after removing records: {remaining_modulo} seconds")
    
    # Przesunięcie TYLKO pierwszej wartości o wartość modulo
    if remaining_modulo != 0:

        old_index = temp_series.index.tolist()
        old_index[0] = old_index[0] + timedelta(seconds=remaining_modulo)
        temp_series.index = old_index
        print(f"Adjusted first temperature record by {remaining_modulo} seconds")
        print(f"New first temperature record: {temp_series.index[0]}")
        print(f"New first temperature record: {temp_series.index[1]}")
    
    # Obliczanie modulo po przesunięciu pierwszej wartości
    final_diff = (fluence_series.index[0] - temp_series.index[0]).total_seconds()
    final_modulo_before_resample = final_diff % freq_seconds
    print(f"Modulo after adjusting first record: {final_modulo_before_resample} seconds")
    
    # Zapamiętaj dokładny czas pierwszego rekordu fluencji przed resamplingiem
    first_fluence_time = fluence_series.index[0]
    
    # Teraz wykonujemy resampling
    fluence_series = fluence_series.resample(SIMULATION_PERIOD.lower()).sum()
    temp_series = temp_series.resample(SIMULATION_PERIOD.lower()).mean()
    temp_series = temp_series.ffill().bfill()
    
    # Sprawdź modulo po resamplingu
    resampled_modulo = (fluence_series.index[0] - temp_series.index[0]).total_seconds() % freq_seconds
    print(f"Modulo after resampling: {resampled_modulo} seconds")
    
    # Jeśli modulo nie jest zerowe, dostosuj TYLKO pierwsze indeksy czasowe po resamplingu
    if resampled_modulo != 0:
        target_start_time = pd.Timestamp(first_fluence_time).floor(SIMULATION_PERIOD.lower())
        first_fluence_idx = fluence_series.index[0]
        first_temp_idx = temp_series.index[0]
        
        # Przesuwamy tylko pierwsze indeksy
        fluence_series.index = fluence_series.index.map(lambda x: target_start_time if x == first_fluence_idx else x)
        temp_series.index = temp_series.index.map(lambda x: target_start_time if x == first_temp_idx else x)
        print(f"Adjusted first index of resampled series to align with: {target_start_time}")
    
    # Sprawdź, czy indeksy są zrównane po resamplingu
    final_modulo = (fluence_series.index[0] - temp_series.index[0]).total_seconds() % freq_seconds
    print(f"Final modulo: {final_modulo} seconds")
    return fluence_series, temp_series



def prepare_sensor_data(fluence_df: pd.DataFrame, temp_df: pd.DataFrame, sensor_name: str) -> tuple:
    fluence_series, temp_series = align_temperature_to_fluence(fluence_df, temp_df, sensor_name)
    common_index = fluence_series.index.intersection(temp_series.index)
    return fluence_series[common_index], temp_series[common_index]

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
    if 'temperature' not in df.columns or 'fluence' not in df.columns:
        raise KeyError("Input DataFrame must contain 'temperature' and 'fluence' columns")
    if len(df) == 0:
        return pd.DataFrame(columns=['temperature', 'fluence', 'time'])
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

def simulate_current_sensor(fluence_series: pd.Series, temp_series: pd.Series, params, sensor_name: str = None) -> pd.DataFrame:
    combined = pd.DataFrame({
        'fluence': fluence_series.values,
        'temperature': temp_series.values
    }, index=fluence_series.index)
    combined = combine_periods(combined, temp_tolerance=0.0, fluence_tolerance=0.0)
    combined['current'] = 0.0
    temperatures = combined['temperature'].values
    fluences = combined['fluence'].values
    times = combined['time'].values
    
    tau_j = calculate_intrinsic_lifetime_tau_vectorized(params.k_0I, params.E_I, temperatures, params.kb)
    theta_j = calculate_temperature_factor_theta_vectorized(temperatures, params.E_I_star, params.T_ref, params.kb)
    time_tau = times / tau_j
    time_theta = theta_j * times / params.t_0
    
    for n in range(len(combined)):
        I_leak = calculate_leakage_current(fluences[:n], time_tau[:n], time_theta[:n], params.alpha_I, params.alpha_0_star, params.beta, params.V)
        combined.loc[combined.index[n], 'current'] = I_leak * 1000
    
    if sensor_name is not None:
        combined = combined.rename(columns={
            "current": f"current_{sensor_name}",
            "temperature": f"temperature_{sensor_name}",
            "fluence": f"fluence_{sensor_name}",
            "time": f"time_{sensor_name}"
        })
    return combined

def process_all_sensors(fluence_df, temp_df, params, common_sensors):
    if not common_sensors:
        print("No sensors to process. Empty list provided.")
        return None
        
    all_simulated = {}
    failed_sensors = []
    
    for sensor in tqdm.tqdm(common_sensors, desc="Processing sensors"):
        try:
            if sensor not in fluence_df.columns:
                failed_sensors.append(sensor)
                continue
            if sensor not in temp_df.columns:
                failed_sensors.append(sensor)
                continue

            fluence_series, temp_series = prepare_sensor_data(fluence_df, temp_df, sensor)
            sim_df = simulate_current_sensor(fluence_series, temp_series, params, sensor_name=sensor)
            all_simulated[sensor] = sim_df
        except Exception as e:
            print(f"Error processing sensor {sensor}: {str(e)}")
            failed_sensors.append(sensor)
    if failed_sensors:
        print(f"Failed to process {len(failed_sensors)} sensors: {', '.join(failed_sensors[:5])}" + (f" and {len(failed_sensors)-5} more" if len(failed_sensors) > 5 else ""))
    if len(all_simulated) == 0:
        print("No sensors were successfully processed")
        return None
    if len(all_simulated) == 1:
        return list(all_simulated.values())[0]
    return pd.concat(all_simulated.values(), axis=1, join='outer')



@njit
def _aggregate_window_means(sim_timestamps, real_timestamps, real_values, time_windows):
    """
    Optymalizowana przez numba funkcja do obliczania średnich wartości dla okien czasowych.
    
    Args:
        sim_timestamps: numpy array z timestampami symulacji (w nanosekundach)
        real_timestamps: numpy array z timestampami rzeczywistych danych (w nanosekundach)
        real_values: numpy array z wartościami rzeczywistych prądów
        time_windows: numpy array z szerokościami okien czasowych (w nanosekundach)
    
    Returns:
        numpy array z zagregowanymi średnimi (NaN dla pustych okien)
    """
    result = np.full(len(sim_timestamps), np.nan)
    
    for i in range(len(sim_timestamps)):
        if np.isnan(time_windows[i]) or time_windows[i] <= 0:
            continue
        
        start_time = sim_timestamps[i]
        end_time = start_time + time_windows[i]
        
        sum_values = 0.0
        count = 0
        for j in range(len(real_timestamps)):
            if real_timestamps[j] >= start_time and real_timestamps[j] < end_time:
                if not np.isnan(real_values[j]):
                    sum_values += real_values[j]
                    count += 1
        if count > 0:
            result[i] = sum_values / count
    
    return result

def aggregate_real_current_data(simulated_df, real_df, sensors):

    if real_df is None or simulated_df is None:
        return None
    
    result_data = {}
    
    for sensor in sensors:
        time_col = f"time_{sensor}"
        real_col = f"real_current_{sensor}"
        
        if time_col not in simulated_df.columns or real_col not in real_df.columns:
            continue
        
        sim_timestamps = np.array(simulated_df.index.astype(np.int64).values)
        real_timestamps = np.array(real_df.index.astype(np.int64).values)
        real_values = np.array(real_df[real_col].values, dtype=np.float64)
        
        time_windows = np.array(simulated_df[time_col].values * 1e9, dtype=np.float64)

        aggregated_values = _aggregate_window_means(sim_timestamps, real_timestamps, real_values, time_windows)
        result_data[real_col] = pd.Series(aggregated_values, index=simulated_df.index)

    return pd.DataFrame(result_data)


def load_real_current_data(paths):
    real_all_df = pd.DataFrame()
    current_files = [file_name for file_name, _ in CURRENT_YEAR_LIST]
    
    for file_name in current_files:
        file_path = paths.get_current_file(file_name)
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path, index_col=0, parse_dates=True)
                if real_all_df.empty:
                    real_all_df = df
                else:
                    real_all_df = pd.concat([real_all_df, df], axis=0)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
    
    if real_all_df.empty:
        return None

    new_names = {}
    for col in real_all_df.columns:
        new_names[col] = f"real_current_{col}"
    
    real_all_df = real_all_df.rename(columns=new_names)
    real_all_df = real_all_df[~real_all_df.index.duplicated(keep='first')]
    
    return real_all_df


### checked

def run_leakage_current_pipeline(fluence_file, temp_files, params, sensor_name=None, available_sensors=None, real_df=None):
    fluence_df, temp_df = load_data(fluence_file, temp_files)
    
    # Select sensors based on mode
    sensors_to_process = [sensor_name] if sensor_name else available_sensors
    
    if not sensors_to_process:
        print("No sensors available for processing")
        return None, []
    
    # Process all sensors
    simulated_df = process_all_sensors(fluence_df, temp_df, params, sensors_to_process)
    if simulated_df is None:
        return None, []
    
    # Get processed sensors from column names
    processed_sensors = [col.replace('current_', '') for col in simulated_df.columns if col.startswith('current_')]
    
    if real_df is not None:
        aggregated_real_df = aggregate_real_current_data(simulated_df, real_df, processed_sensors)
        if aggregated_real_df is not None and not aggregated_real_df.empty:
            print(f"Simulation completed with real current data for {len(processed_sensors)} sensors.")
            return pd.concat([simulated_df, aggregated_real_df], axis=1), processed_sensors
        else:
            print(f"Warning: Real current data was provided but could not be aggregated.")
    
    print(f"Simulation completed for {len(processed_sensors)} sensors. No real current data added.")
    return simulated_df, processed_sensors
