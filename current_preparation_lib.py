import numpy as np
import pandas as pd
from config import CURRENT_TEMP_MODE, SIMULATION_PERIOD, OUTPUT_SIMULATED_DF_PATH

def adjust_real_current_with_temperature(df: pd.DataFrame, params, sensors: list) -> pd.DataFrame:
    """Adjust real current with temperature for multiple sensors."""
    out = df.copy()
    for sensor in sensors:
        real_col = f"real_current_{sensor}"
        temp_col = f"temperature_{sensor}"
        
        if real_col not in out.columns or temp_col not in out.columns:
            continue
            
        T = out[temp_col].values
        T_ref = params.T_ref
        E_eff = params.E_eff
        kB = params.kb
        R_Tref = (T_ref / T) ** 2 * np.exp(-(E_eff / (2 * kB)) * (1 / T_ref - 1 / T))
        out[real_col] = out[real_col].values * R_Tref
    return out



def set_temperature_where_fluence_zero(data: pd.DataFrame, sensors: list, value: float = 261.15, min_duration_days: int = 30) -> pd.DataFrame:
    """Set temperature values where fluence is zero, handling multiple sensors."""
    out = data.copy()
    
    for sensor in sensors:
        fluence_col = f"fluence_{sensor}"
        temp_col = f"temperature_{sensor}"
        
        if fluence_col not in out.columns or temp_col not in out.columns:
            continue
            
        zero_mask = (out[fluence_col] == 0)
        if zero_mask.sum() == 0:
            out.loc[(out[temp_col] < 260) | (out[temp_col] > 264), temp_col] = float('nan')
            continue
            
        zero_groups = (zero_mask != zero_mask.shift()).cumsum()
        group_ids = zero_groups[zero_mask].unique()
        freq_minutes = int(pd.to_timedelta(SIMULATION_PERIOD.lower()).total_seconds() // 60)
        min_points = (min_duration_days * 24 * 60) // freq_minutes
        
        for gid in group_ids:
            idx = zero_groups[zero_groups == gid].index
            if len(idx) >= min_points:
                out.loc[idx, temp_col] = value
            else:
                out.loc[idx, temp_col] = float('nan')
                
        out.loc[(out[temp_col] < 260) | (out[temp_col] > 290), temp_col] = float('nan')
    
    return out

def adjust_simulated_current_with_temperature(df: pd.DataFrame, params, sensors: list) -> pd.DataFrame:
    """Adjust simulated current with temperature for multiple sensors."""
    out = df.copy()
    out = set_temperature_where_fluence_zero(out, sensors)
    for sensor in sensors:
        sim_col = f"current_{sensor}"
        temp_col = f"temperature_{sensor}"
        
        if sim_col not in out.columns or temp_col not in out.columns:
            continue
            
        T = out[temp_col].values
        T_ref = params.T_ref
        E_eff = params.E_eff
        kB = params.kb
        R_Tref = (T / T_ref) ** 2 * np.exp(-(E_eff / (2 * kB)) * (1/T - 1/T_ref))
        out[sim_col] = out[sim_col].values * R_Tref
    return out


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
        
    columns_to_keep = []
    for sensor in sensor_names:
        sensor_columns = [col for col in df.columns if col.endswith(f"_{sensor}")]
        columns_to_keep.extend(sensor_columns)
    
    if columns_to_keep:
        return df[columns_to_keep]
    else:
        return None
    
def add_delivered_fluence(df: pd.DataFrame, params, sensors: list) -> pd.DataFrame:
    """Add delivered fluence columns for each sensor."""
    out = df.copy()
    
    for sensor in sensors:
        fluence_col = f"fluence_{sensor}"
        if fluence_col not in out.columns:
            continue
            
        deliv_fluence_col = f"delivered_fluence_{sensor}"
        out[deliv_fluence_col] = out[fluence_col].cumsum()
    
    return out

def create_sensor_summary(df: pd.DataFrame, date=None) -> pd.DataFrame:
    """
    Create a summary DataFrame with sensor currents and positions.
    Args:
        df: DataFrame with sensor data
        date: Optional date for which to get the currents (if None, uses last date)
    Returns:
        DataFrame with sensor names as index and columns: current_sim, current_real, position
    """
    print("Creating sensor summary...")
    
    from VeloDetectorElement import VeloDetectorElement
    velo = VeloDetectorElement()
    
    # Get data for specified date
    if date is None:
        date = df.index[-1]
    print(f"Using date: {date}")
    
    # Prepare empty DataFrame
    summary = pd.DataFrame(columns=['current_sim', 'current_real', 'position'])
    
    # Find all unique sensors
    sim_sensors = [col.replace('current_', '') for col in df.columns if col.startswith('current_') and not col.startswith('current_real')]
    print(f"Found {len(sim_sensors)} sensors")
    
    # Fill data for each sensor
    for sensor in sim_sensors:
        sim_col = f'current_{sensor}'
        real_col = f'real_current_{sensor}'
        
        # Get last non-NaN value for each column
        sim_val = df[sim_col].dropna().iloc[-1] if sim_col in df.columns else None
        real_val = df[real_col].dropna().iloc[-1] if real_col in df.columns else None
        
        try:
            # Add 'HV' to sensor name for position lookup
            sensor_key = (sensor, 'HV')
            position = velo.sensor_name2sensor_z(sensor_key)
            summary.loc[sensor] = [sim_val, real_val, position]
        except Exception as e:
            print(f"Warning: Could not get position for sensor {sensor}: {e}")
            summary.loc[sensor] = [sim_val, real_val, None]
    
    print("Summary created successfully")
    return summary.sort_values('position')

