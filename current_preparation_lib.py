import numpy as np
import pandas as pd
from config import CURRENT_TEMP_MODE, SIMULATION_PERIOD, OUTPUT_SIMULATED_DF_PATH, REFERENCE_TEMPERATURE, TARGET_LUMINOSITIES

def load_temperature_data(file_path: str) -> pd.DataFrame:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Temperature file not found: {file_path}")
    df = pd.read_csv(file_path, index_col="TS", parse_dates=["TS"])
    df = df.dropna(how='all')
    return df

def adjust_real_current_with_temperature(df: pd.DataFrame, params, sensors: list) -> pd.DataFrame:
    """Adjust real current with temperature for multiple sensors."""
    out = df.copy()
    out = set_temperature_where_fluence_zero(out, sensors)
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

def adjust_both_with_new_temperature(df: pd.DataFrame, params, sensors: list, T_new: float = None) -> pd.DataFrame:
    """Adjust both real and simulated currents to a new temperature for multiple sensors."""
    out = df.copy()
    out = set_temperature_where_fluence_zero(out, sensors)
    if T_new is None:
        T_new = REFERENCE_TEMPERATURE
        
    for sensor in sensors:
        real_col = f"real_current_{sensor}"
        sim_col = f"current_{sensor}"
        temp_col = f"temperature_{sensor}"
        
        if real_col not in out.columns or sim_col not in out.columns or temp_col not in out.columns:
            continue
            
        T_real = out[temp_col].values
        T_ref = params.T_ref
        E_eff = params.E_eff
        kB = params.kb
        R_Tref_real = (T_new / T_real) ** 2 * np.exp(-(E_eff / (2 * kB)) * (1 / T_new - 1 / T_real))
        R_Tref_sim = (T_new / T_ref) ** 2 * np.exp(-(E_eff / (2 * kB)) * (1/T_new - 1/T_ref))
        
        out[real_col] = out[real_col].values * R_Tref_real
        out[sim_col] = out[sim_col].values * R_Tref_sim
        
    return out

def set_temperature_where_fluence_zero(data: pd.DataFrame, sensors: list, threshold_percent: float =50.0) -> pd.DataFrame:
    """Filter temperature values based on histogram analysis by month.
    
    For each month separately, keeps only values from bins that exceed threshold_percent of the highest bin.
    """
    out = data.copy()
    
    for sensor in sensors:
        temp_col = f"temperature_{sensor}"
        
        if temp_col not in out.columns:
            continue
        
        # Get all data with timestamps    
        temp_series = out[temp_col].copy()
        if temp_series.isna().all():
            continue
            
        # Process each month separately
        # Create a mask that will collect all valid points
        all_valid_mask = pd.Series(False, index=out.index)
        
        # Group by year and month
        for (year, month), month_data in temp_series.groupby([temp_series.index.year, temp_series.index.month]):
            # Skip if we have too few data points
            if len(month_data) < 20:
                continue
                
            # Get data without NaN values
            month_data_clean = month_data.dropna()
            if len(month_data_clean) == 0:
                continue
                
            # Remove extreme values (below 200K and above 300K)
            mask = (month_data_clean > 200) & (month_data_clean < 300)
            filtered_month_data = month_data_clean[mask]
            if len(filtered_month_data) < 10:  # Skip if too few points after filtering
                continue
                
            # Create histogram for this month
            hist, bin_edges = np.histogram(filtered_month_data, bins=100)
            
            # Find maximum bin count and threshold
            max_bin_count = np.max(hist)
            threshold = (threshold_percent / 100) * max_bin_count
            
            # Find bins that exceed the threshold
            valid_bins = np.where(hist >= threshold)[0]
            if len(valid_bins) == 0:
                continue
                
            # Create mask for values that belong to valid bins
            month_mask = pd.Series(False, index=month_data.index)
            
            for bin_idx in valid_bins:
                bin_min = bin_edges[bin_idx]
                bin_max = bin_edges[bin_idx + 1]
                month_mask |= (month_data >= bin_min) & (month_data < bin_max)
            
            # Add this month's valid points to the overall mask
            all_valid_mask.loc[month_mask.index] = month_mask
        
        # Set values outside valid bins to NaN
        out.loc[~all_valid_mask & ~out[temp_col].isna(), temp_col] = float('nan')
    
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
        
    columns_to_keep = ['integrated_luminosity'] if 'integrated_luminosity' in df.columns else []
    for sensor in sensor_names:
        sensor_columns = [col for col in df.columns if col.endswith(f"_{sensor}")]
        columns_to_keep.extend(sensor_columns)
    
    if len(columns_to_keep) > 1:  # Ensure we have more than just luminosity column
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

def prepare_data_for_analysis(df: pd.DataFrame, params, sensors_to_use, start_date=None):
    """Prepare data for analysis by filtering by date and applying temperature adjustments."""
    result_df = df.copy()
    
    if start_date:
        start_date = pd.to_datetime(start_date)
        result_df = result_df[result_df.index >= start_date]

    if CURRENT_TEMP_MODE == 'adjust_real':
        result_df = adjust_real_current_with_temperature(result_df, params, sensors_to_use)
    elif CURRENT_TEMP_MODE == 'adjust_sim':
        result_df = adjust_simulated_current_with_temperature(result_df, params, sensors_to_use)
    elif CURRENT_TEMP_MODE == 'adjust_both':
        result_df = adjust_both_with_new_temperature(result_df, params, sensors_to_use)
    
    result_df = add_delivered_fluence(result_df, params, sensors_to_use)
    
    return result_df

def current_for_lumi(df: pd.DataFrame, target_luminosities: list = None) -> pd.DataFrame:
    from VeloDetectorElement import VeloDetectorElement
    velo = VeloDetectorElement()
    
    if target_luminosities is None:
        target_luminosities = TARGET_LUMINOSITIES
    
    summary = pd.DataFrame()
    sim_sensors = [col.replace('current_', '') for col in df.columns if col.startswith('current_') and not col.startswith('current_real')]
    
    for target_lumi in target_luminosities:
        for sensor in sim_sensors:
            sim_col = f'current_{sensor}'
            real_col = f'real_current_{sensor}'
            
            sensor_data = df[[sim_col, real_col, 'integrated_luminosity']].dropna()
            if not sensor_data.empty and 'integrated_luminosity' in sensor_data.columns:
                closest_idx = (sensor_data['integrated_luminosity'] - target_lumi).abs().idxmin()
                sim_val = sensor_data[sim_col].loc[closest_idx]
                real_val = sensor_data[real_col].loc[closest_idx]
            else:
                sim_val = None
                real_val = None
            
            try:
                sensor_key = (sensor, 'HV')
                position = velo.sensor_name2sensor_z(sensor_key)
            except:
                position = None
                
            if sensor not in summary.index:
                summary.loc[sensor, 'position'] = position
                
            lumi_str = f'_f{target_lumi:.1f}'
            summary.loc[sensor, f'current_sim{lumi_str}'] = sim_val
            summary.loc[sensor, f'current_real{lumi_str}'] = real_val
            
    return summary.sort_values('position')

