import numpy as np
import pandas as pd
from config import CURRENT_TEMP_MODE, SIMULATION_PERIOD, OUTPUT_SIMULATED_DF_PATH

def adjust_real_current_with_temperature(current_data: pd.DataFrame, temperature_data: pd.DataFrame, params, column: str) -> pd.DataFrame:
    if CURRENT_TEMP_MODE == 'none':
        return current_data
    T = temperature_data[column].reindex(current_data.index, method='nearest').values
    T_ref = params.T_ref
    E_eff = params.E_eff
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
        out.loc[(out['temperature'] < 260) | (out['temperature'] > 264), 'temperature'] = float('nan')
        return out
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
    out.loc[(out['temperature'] < 260) | (out['temperature'] > 290), 'temperature'] = float('nan')
    return out

def adjust_simulated_current_with_temperature(data: pd.DataFrame, params) -> pd.DataFrame:
    if CURRENT_TEMP_MODE == 'none':
        return data
    data = set_temperature_where_fluence_zero(data)
    T = data['temperature'].values
    T_ref = params.T_ref
    E_eff = params.E_eff
    kB = params.kb
    R_Tref = (T_ref / T) ** 2 * np.exp(-(E_eff / (2 * kB)) * (1/T - 1/T_ref))
    print('T_REF', T_ref)
    out = data.copy()
    out['current'] = out['current'].values * R_Tref
    return out

def prepare_sensor_current(current_df: pd.DataFrame, temp_df: pd.DataFrame, params, sensor_name: str) -> pd.DataFrame:
    if CURRENT_TEMP_MODE == 'adjust_real':
        return adjust_real_current_with_temperature(current_df, temp_df, params, sensor_name)
    else:
        return current_df

from numba import njit
import numpy as np

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


def load_and_prepare_simulated_df(sensor_names, path=OUTPUT_SIMULATED_DF_PATH):
    """
    Load simulated_df and map columns for the given sensor(s).
    sensor_names: str or list of str
    Returns original DataFrame with all columns for all requested sensors
    """
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    
    from config import SELECTED_YEARS
    if SELECTED_YEARS:
        years_mask = df.index.year.isin(SELECTED_YEARS)
        df = df[years_mask]
    
    if isinstance(sensor_names, str):
        sensor_names = [sensor_names]
        
    # Zbierz wszystkie kolumny powiązane z żądanymi sensorami
    columns_to_keep = []
    for sensor in sensor_names:
        # Dodaj kolumny dla danego sensora (current, temperature, fluence, time)
        sensor_columns = [col for col in df.columns if col.endswith(f"_{sensor}")]
        columns_to_keep.extend(sensor_columns)
    
    # Jeśli znaleziono jakiekolwiek kolumny, zwróć DataFrame tylko z tymi kolumnami
    if columns_to_keep:
        return df[columns_to_keep]
    else:
        return None

