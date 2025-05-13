import numpy as np
import pandas as pd
from datetime import timedelta
import tqdm
import os
from config import CURRENT_YEAR_LIST, CURRENT_YEAR_RANGES, SIMULATION_PERIOD, RUN_MODE, SENSOR_NAME
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
    df.index.name = "TS"
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
            temp_df = load_temperature_data(temp_file)
            temp_dfs.append(temp_df)
        except Exception as e:
            print(f"Skipping temperature file {temp_file} due to error: {str(e)}")
    if not temp_dfs:
        raise ValueError("No valid temperature data could be loaded")
    temp_df = pd.concat(temp_dfs, axis=0, join='outer')
    temp_df = temp_df.groupby(temp_df.index).max().sort_index()
    return fluence_df, temp_df

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
    fluence_series = fluence_series.resample(SIMULATION_PERIOD.lower()).sum()
    temp_series_raw = temp_df[sensor_name].resample(SIMULATION_PERIOD.lower()).mean()
    temp_series = temp_series_raw.ffill().bfill()
    freq_seconds = pd.to_timedelta(SIMULATION_PERIOD.lower()).total_seconds()
    time_diff_seconds = (fluence_series.index[0] - temp_series.index[0]).total_seconds() % freq_seconds
    if time_diff_seconds > 0:
        shift_seconds = time_diff_seconds
        if time_diff_seconds > freq_seconds/2:
            shift_seconds = time_diff_seconds - freq_seconds
        shift = timedelta(seconds=shift_seconds)
        fluence_series.index = fluence_series.index - shift
    full_index = pd.date_range(start=temp_series.index[0], end=temp_series.index[-1], freq=SIMULATION_PERIOD.lower())
    fluence_series = fluence_series.reindex(full_index, fill_value=0)
    return fluence_series, temp_series

def prepare_sensor_data(fluence_df: pd.DataFrame, temp_df: pd.DataFrame, sensor_name: str) -> tuple:
    fluence_series, temp_series = align_temperature_to_fluence(fluence_df, temp_df, sensor_name)
    common_index = fluence_series.index.intersection(temp_series.index)
    fluence_df_result = pd.DataFrame({sensor_name: fluence_series[common_index]})
    temp_df_result = pd.DataFrame({sensor_name: temp_series[common_index]})
    fluence_df_result.index.name = 'ts'
    temp_df_result.index.name = 'ts'
    return fluence_df_result, temp_df_result

def find_common_sensors(*dfs) -> list:
    if not dfs:
        raise ValueError("No DataFrames provided to find common sensors")
    cols = [set(df.columns) for df in dfs]
    common_cols = set.intersection(*cols)
    if not common_cols:
        print("Warning: No common sensors found across all DataFrames")
    return sorted(common_cols)

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

def simulate_current_sensor(fluence_df: pd.Series, temp_df: pd.Series, params, sensor_name: str = None) -> pd.DataFrame:
    result = pd.DataFrame(index=fluence_df.index)
    result['fluence'] = fluence_df.values
    result['temperature'] = temp_df.values
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

def process_single_sensor(fluence_df, temp_df, params, sensor_name):
    fdf, tdf = prepare_sensor_data(fluence_df, temp_df, sensor_name)
    sim_df = simulate_current_sensor(fdf[sensor_name], tdf[sensor_name], params, sensor_name=sensor_name)
    return sim_df

def process_all_sensors(fluence_df, temp_df, params, sensor_name=None, common_sensors=None):
    if sensor_name is not None:
        common_sensors = [sensor_name]
    if common_sensors is None:
        raise ValueError("common_sensors must be provided!")
    if not common_sensors:
        print("No sensors to process. Empty list provided.")
        return None
    all_simulated = {}
    failed_sensors = []
    for sensor in tqdm.tqdm(common_sensors, desc="Processing sensors"):
        try:
            if sensor not in fluence_df.columns:
                print(f"Sensor {sensor} not found in fluence data, skipping")
                failed_sensors.append(sensor)
                continue
            if sensor not in temp_df.columns:
                print(f"Sensor {sensor} not found in temperature data, skipping")
                failed_sensors.append(sensor)
                continue
            sensor_fluence_df = fluence_df[[sensor]]
            sensor_temp_df = temp_df[[sensor]]
            sim_df = process_single_sensor(sensor_fluence_df, sensor_temp_df, params, sensor)
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

# ----- Funkcje do przetwarzania danych rzeczywistych -----

def load_real_current_data(paths):
    """Wczytaj dane rzeczywiste dla wszystkich sensorów z plików zdefiniowanych w konfiguracji."""
    real_all_df = pd.DataFrame()
    current_files = [file_name for file_name, _ in CURRENT_YEAR_LIST]
    
    for file_name in current_files:
        file_path = paths.get_current_file(file_name)
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path, index_col=0, parse_dates=True)
                # Jeśli to pierwszy plik lub dataframe jest pusty, użyj go jako bazowy
                if real_all_df.empty:
                    real_all_df = df
                else:
                    # Połącz z istniejącym dataframe, ignorując powtórzenia indeksów
                    real_all_df = pd.concat([real_all_df, df], axis=0)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
    
    if real_all_df.empty:
        return None

    # Dodaj prefiks 'real_current_' do nazw kolumn
    new_names = {}
    for col in real_all_df.columns:
        new_names[col] = f"real_current_{col}"
    
    real_all_df = real_all_df.rename(columns=new_names)
    real_all_df = real_all_df[~real_all_df.index.duplicated(keep='first')]
    
    return real_all_df

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
        # Jeśli szerokość okna jest NaN lub <= 0, pomijamy
        if np.isnan(time_windows[i]) or time_windows[i] <= 0:
            continue
        
        # Oblicz koniec przedziału czasowego
        start_time = sim_timestamps[i]
        end_time = start_time + time_windows[i]
        
        # Wyszukaj wartości w tym przedziale
        sum_values = 0.0
        count = 0
        for j in range(len(real_timestamps)):
            if real_timestamps[j] >= start_time and real_timestamps[j] < end_time:
                if not np.isnan(real_values[j]):
                    sum_values += real_values[j]
                    count += 1
        
        # Oblicz średnią jeśli znaleziono wartości
        if count > 0:
            result[i] = sum_values / count
    
    return result

def aggregate_real_current_data(simulated_df, real_df, sensors):
    """
    Agreguje dane rzeczywiste na podstawie przedziałów czasowych z danych symulowanych.
    Zoptymalizowana wersja używająca numba JIT do przyspieszenia obliczeń.
    
    Args:
        simulated_df (pd.DataFrame): DataFrame z danymi symulowanymi dla wszystkich sensorów
        real_df (pd.DataFrame): DataFrame z danymi rzeczywistymi dla wszystkich sensorów (kolumny: real_current_sensor)
        sensors (list): Lista sensorów, dla których chcemy zagregować dane
    
    Returns:
        pd.DataFrame: DataFrame z zagregowanymi danymi rzeczywistymi dla wybranych sensorów
    """
    if real_df is None or simulated_df is None:
        return None
    
    result_data = {}
    
    # Dla każdego sensora
    for sensor in sensors:
        time_col = f"time_{sensor}"
        real_col = f"real_current_{sensor}"
        
        # Sprawdź czy dane rzeczywiste i symulowane zawierają potrzebne kolumny
        if time_col not in simulated_df.columns or real_col not in real_df.columns:
            continue
        
        # Konwersja indeksów czasu na nanosekundy (inty) dla numby
        sim_timestamps = np.array(simulated_df.index.astype(np.int64).values)
        real_timestamps = np.array(real_df.index.astype(np.int64).values)
        real_values = np.array(real_df[real_col].values, dtype=np.float64)
        
        # Konwersja okien czasowych z sekund na nanosekundy
        time_windows = np.array(simulated_df[time_col].values * 1e9, dtype=np.float64)
        
        # Wywołaj zoptymalizowaną funkcję numba
        aggregated_values = _aggregate_window_means(sim_timestamps, real_timestamps, real_values, time_windows)
        
        # Konwersja wyników z powrotem na pandas Series z właściwym indeksem
        result_data[real_col] = pd.Series(aggregated_values, index=simulated_df.index)
    
    # Utwórz DataFrame z zagregowanymi danymi
    return pd.DataFrame(result_data)

# ----- Zmodyfikowany main pipeline -----

def run_leakage_current_pipeline(fluence_file, temp_files, params, sensor_name=None, available_sensors=None):
    """Główny pipeline do symulacji i łączenia danych rzeczywistych."""
    # 1. Wczytaj dane fluencji i temperatury
    fluence_df, temp_df = load_data(fluence_file, temp_files)
    
    # 2. Przeprowadź symulację
    if RUN_MODE == "single":
        sensor_to_use = SENSOR_NAME if sensor_name is None else sensor_name
        if sensor_to_use in fluence_df.columns and sensor_to_use in temp_df.columns:
            fluence_df_filtered = fluence_df[[sensor_to_use]]
            temp_df_filtered = temp_df[[sensor_to_use]]
            simulated_df = process_single_sensor(fluence_df_filtered, temp_df_filtered, params, sensor_name=sensor_to_use)
            processed_sensors = [sensor_to_use]
        else:
            missing_in = []
            if sensor_to_use not in fluence_df.columns:
                missing_in.append("fluence data")
            if sensor_to_use not in temp_df.columns:
                missing_in.append("temperature data")
            print(f"Error: Sensor {sensor_to_use} not found in {' and '.join(missing_in)}")
            return None, []
    else:
        if not available_sensors:
            available_sensors = find_common_sensors(fluence_df, temp_df)
            if not available_sensors:
                print("No common sensors found between fluence and temperature data")
                return None, []
        
        simulated_df = process_all_sensors(fluence_df, temp_df, params, common_sensors=available_sensors)
        if simulated_df is not None:
            processed_sensors = [col.replace('current_', '') for col in simulated_df.columns if col.startswith('current_')]
            if not processed_sensors:
                processed_sensors = available_sensors
                print("Warning: Could not determine which sensors were actually processed")
        else:
            return None, []
    
    # 3. Wczytaj dane rzeczywiste
    from config import Paths
    paths = Paths()
    real_df = load_real_current_data(paths)
    
    # 4. Połącz dane symulowane z rzeczywistymi
    if real_df is not None:
        # Agreguj dane rzeczywiste na podstawie przedziałów czasowych z symulacji
        aggregated_real_df = aggregate_real_current_data(simulated_df, real_df, processed_sensors)
        
        # Połącz dane symulowane i rzeczywiste
        if aggregated_real_df is not None and not aggregated_real_df.empty:
            final_df = pd.concat([simulated_df, aggregated_real_df], axis=1)
            print(f"Simulation completed with real current data for {len(processed_sensors)} sensors.")
            return final_df, processed_sensors
    
    # Jeśli nie ma danych rzeczywistych, zwróć tylko dane symulowane
    print(f"Simulation completed for {len(processed_sensors)} sensors. No real current data added.")
    return simulated_df, processed_sensors
