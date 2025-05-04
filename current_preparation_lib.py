import numpy as np
import pandas as pd
from config import CURRENT_TEMP_MODE, SIMULATION_PERIOD

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

# --- GŁÓWNY PROGRAM ---
if __name__ == "__main__":
    # Załaduj simulated_df z pliku
    simulated_df = pd.read_csv("out_data/simulated_df.csv", index_col=0, parse_dates=True)
    print("Loaded simulated_df:")
    print(simulated_df.head())

    # Przykład użycia: przelicz temperaturę/prąd jeśli potrzebujesz
    # (zakładając, że masz obiekt params i ew. temp_df)
    # from test_area import Parameters
    # params = Parameters()
    # adjusted_df = adjust_simulated_current_with_temperature(simulated_df, params)
    # print(adjusted_df.head())
