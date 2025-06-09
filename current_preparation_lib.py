import numpy as np
import pandas as pd
from scipy import stats
from config import SIMULATION_PERIOD, OUTPUT_SIMULATED_DF_PATH, TARGET_LUMINOSITIES
from config_plot import CURRENT_TEMP_MODE, REFERENCE_TEMPERATURE, FIT_QUALITY_METRICS, ERROR_PERCENTAGE, TEMPERATURE_CORRECTION_ENABLED, TEMPERATURE_CORRECTION_DELTA

import os

def load_temperature_data(file_path: str) -> pd.DataFrame:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Temperature file not found: {file_path}")
    df = pd.read_csv(file_path, index_col="TS", parse_dates=["TS"])
    return df.dropna(how='all')

def adjust_real_current_with_temperature(df: pd.DataFrame, params, sensors: list) -> pd.DataFrame:
    out = df.copy()
    out = set_temperature_where_fluence_zero(out, sensors)
    for sensor in sensors:
        real_col = f"real_current_{sensor}"
        temp_col = f"temperature_{sensor}"
        
        if real_col not in out.columns or temp_col not in out.columns:
            continue
            
        R_Tref = _calculate_temperature_adjustment(
            out[temp_col].values, params.T_ref, params.E_eff, params.kb, reverse=True)
        out[real_col] = out[real_col].values * R_Tref
    return out

def adjust_both_with_new_temperature(df: pd.DataFrame, params, sensors: list, T_new: float = None) -> pd.DataFrame:
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
            
        R_Tref_real = _calculate_temperature_adjustment(
            T_new, out[temp_col].values, params.E_eff, params.kb)
        R_Tref_sim = _calculate_temperature_adjustment(
            T_new, params.T_ref, params.E_eff, params.kb)
        
        out[real_col] = out[real_col].values * R_Tref_real
        out[sim_col] = out[sim_col].values * R_Tref_sim
        
    return out

def get_temperature_bin_mean(temp_data):
    if len(temp_data) == 0:
        return None
    
    filtered_temp = temp_data[(temp_data > 200) & (temp_data < 300)]
    if len(filtered_temp) == 0:
        return None
        
    hist, bin_edges = np.histogram(filtered_temp, bins=100)
    max_bin_idx = np.argmax(hist)
    bin_min = bin_edges[max_bin_idx]
    bin_max = bin_edges[max_bin_idx + 1]
    return (bin_min + bin_max) / 2

def set_temperature_where_fluence_zero(data: pd.DataFrame, sensors: list, threshold_percent: float =50.0) -> pd.DataFrame:
    out = data.copy()
    
    for sensor in sensors:
        temp_col = f"temperature_{sensor}"
        fluence_col = f"fluence_{sensor}"
        
        if temp_col not in out.columns:
            continue
            
        if fluence_col not in out.columns:
            out = _apply_histogram_filtering(out, sensor, temp_col, None, threshold_percent)
            continue
            
        zero_fluence_mask = (out[fluence_col] == 0)
        nonzero_fluence_mask = ~zero_fluence_mask & ~out[fluence_col].isna()
        
        if nonzero_fluence_mask.any():
            out = _apply_histogram_filtering(out, sensor, temp_col, nonzero_fluence_mask, threshold_percent)
        
        if zero_fluence_mask.any() and nonzero_fluence_mask.any():
            nonzero_temp_data = out.loc[nonzero_fluence_mask, temp_col].dropna()
            bin_mean = get_temperature_bin_mean(nonzero_temp_data)
            
            if bin_mean is not None:
                out.loc[zero_fluence_mask, temp_col] = bin_mean
    
    return out


def _apply_histogram_filtering(data: pd.DataFrame, sensor: str, temp_col: str, mask=None, threshold_percent: float=50.0) -> pd.DataFrame:
    out = data.copy()
    
    temp_series = out.loc[mask, temp_col].copy() if mask is not None else out[temp_col].copy()
    if temp_series.isna().all():
        return out
        
    all_valid_mask = pd.Series(False, index=temp_series.index)
    
    for (year, month), month_data in temp_series.groupby([temp_series.index.year, temp_series.index.month]):
        if len(month_data) < 20:
            continue
            
        month_data_clean = month_data.dropna()
        if len(month_data_clean) == 0:
            continue
            
        filter_mask = (month_data_clean > 200) & (month_data_clean < 300)
        filtered_month_data = month_data_clean[filter_mask]
        if len(filtered_month_data) < 10:
            continue
            
        hist, bin_edges = np.histogram(filtered_month_data, bins=100)
        max_bin_count = np.max(hist)
        threshold = (threshold_percent / 100) * max_bin_count
        valid_bins = np.where(hist >= threshold)[0]
        
        if len(valid_bins) == 0:
            continue
            
        month_mask = pd.Series(False, index=month_data.index)
        for bin_idx in valid_bins:
            bin_min = bin_edges[bin_idx]
            bin_max = bin_edges[bin_idx + 1]
            month_mask |= (month_data >= bin_min) & (month_data < bin_max)
        
        all_valid_mask.loc[month_mask.index] = month_mask
    
    if mask is not None:
        full_mask = mask.copy()
        invalid_points = mask.index[mask & ~all_valid_mask]
        full_mask.loc[invalid_points] = False
        out.loc[mask & ~full_mask & ~out[temp_col].isna(), temp_col] = float('nan')
    else:
        out.loc[~all_valid_mask & ~out[temp_col].isna(), temp_col] = float('nan')
    
    return out

def _calculate_temperature_adjustment(T, T_ref, E_eff, kB, reverse=False):
    if reverse:
        return (T_ref / T) ** 2 * np.exp(-(E_eff / (2 * kB)) * (1 / T_ref - 1 / T))
    else:
        return (T / T_ref) ** 2 * np.exp(-(E_eff / (2 * kB)) * (1 / T - 1 / T_ref))

def adjust_simulated_current_with_temperature(df: pd.DataFrame, params, sensors: list) -> pd.DataFrame:
    out = df.copy()
    out = set_temperature_where_fluence_zero(out, sensors)
    for sensor in sensors:
        sim_col = f"current_{sensor}"
        temp_col = f"temperature_{sensor}"
        
        if sim_col not in out.columns or temp_col not in out.columns:
            continue
            
        R_Tref = _calculate_temperature_adjustment(
            out[temp_col].values, params.T_ref, params.E_eff, params.kb)
        out[sim_col] = out[sim_col].values * R_Tref
    return out


def load_and_prepare_simulated_df(sensor_names, path=OUTPUT_SIMULATED_DF_PATH):
    if isinstance(sensor_names, str):
        sensor_names = [sensor_names]
        
    try:
        df = pd.read_csv(path, index_col=0, parse_dates=True)
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        
        available_sensors = set()
        for col in df.columns:
            if col.startswith('current_'):
                available_sensors.add(col.replace('current_', ''))
        
        missing_sensors = set(sensor_names) - available_sensors
        if missing_sensors:
            print(f"Warning: Sensors not found in simulated data: {', '.join(missing_sensors)}")
        
        return df
    except Exception as e:
        print(f"Error loading simulated data: {e}")
        return None

def scale_real_current_with_temp_correction(df: pd.DataFrame, params, sensors: list) -> pd.DataFrame:
    """Apply temperature correction to real current values to simulate values as if they were measured at a temperature
    lower by TEMPERATURE_CORRECTION_DELTA degrees."""
    if not TEMPERATURE_CORRECTION_ENABLED:
        return df
        
    out = df.copy()
    for sensor in sensors:
        real_col = f"real_current_{sensor}"
        temp_col = f"temperature_{sensor}"
        
        if real_col not in out.columns or temp_col not in out.columns:
            continue
            
        # Calculate scaling factor for temperature correction
        T_corrected = out[temp_col].values - TEMPERATURE_CORRECTION_DELTA
        R_Tcorr = _calculate_temperature_adjustment(
            T_corrected, out[temp_col].values, params.E_eff, params.kb)
        
        # Apply correction to real current values
        out[real_col] = out[real_col].values * R_Tcorr
    return out

def add_delivered_fluence(df: pd.DataFrame, params, sensors: list) -> pd.DataFrame:
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
    
    # Najpierw zastosuj korekcję temperaturową dla realnych danych (skalowanie w dół o 3K)
    result_df = scale_real_current_with_temp_correction(result_df, params, sensors_to_use)
    
    # Następnie zastosuj standardową korektę temperaturową według wybranego trybu
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


def calculate_fit_quality(df: pd.DataFrame, sensors: list, metric: str = None) -> dict:
    """
    Calculate the quality of fit between simulated and real current data.
    
    Args:
        df: DataFrame containing the processed current data
        sensors: List of sensor names to calculate metrics for
        metric: The metric to use for fit quality assessment
               If None, uses the FIT_QUALITY_METRICS from config_plot.py
               Supported metrics: 'mse' (Mean Squared Error),
                                 'rmse' (Root Mean Squared Error),
                                 'mae' (Mean Absolute Error),
                                 'r2' (R-squared),
                                 'pearson' (Pearson correlation coefficient),
                                 'spearman' (Spearman rank correlation coefficient),
                                 'points_within_error' (Percentage of points within ERROR_PERCENTAGE% of simulated value),
                                 'all' (Returns all metrics in a dictionary)
    
    Returns:
        Dictionary with sensor names as keys and fit quality metrics as values
    """
    # Use configured metrics if none specified
    if metric is None:
        metric = FIT_QUALITY_METRICS
    results = {}
    
    for sensor in sensors:
        sim_col = f"current_{sensor}"
        real_col = f"real_current_{sensor}"
        
        # Skip if either column is missing
        if sim_col not in df.columns or real_col not in df.columns:
            continue
        
        # Get aligned data points (where both sim and real values exist)
        valid_data = df[[sim_col, real_col]].dropna()
        
        # Skip if not enough data points
        if len(valid_data) < 3:  # Need at least a few points for meaningful metrics
            if metric.lower() == 'all':
                results[sensor] = {
                    'mse': None, 'rmse': None, 'mae': None, 'r2': None,
                    'pearson': None, 'spearman': None,
                    'data_points': 0
                }
            else:
                results[sensor] = {'metric': metric, 'value': None, 'data_points': 0}
            continue
        
        sim_values = valid_data[sim_col].values
        real_values = valid_data[real_col].values
        
        # Calculate all metrics if requested
        if metric.lower() == 'all':
            # Calculate all metrics
            mse_value = np.mean((real_values - sim_values) ** 2)
            rmse_value = np.sqrt(mse_value)
            mae_value = np.mean(np.abs(real_values - sim_values))
            
            # R-squared
            if np.var(real_values) == 0:
                r2_value = None
            else:
                ss_res = np.sum((real_values - sim_values) ** 2)
                ss_tot = np.sum((real_values - np.mean(real_values)) ** 2)
                r2_value = 1 - (ss_res / ss_tot)
            
            # Pearson correlation
            pearson_corr, pearson_p = stats.pearsonr(real_values, sim_values)
            
            # Spearman correlation
            spearman_corr, spearman_p = stats.spearmanr(real_values, sim_values)
            
            # Points within error percentage threshold
            relative_error = np.abs(real_values - sim_values) / np.abs(sim_values) * 100
            points_within = np.sum(relative_error <= ERROR_PERCENTAGE)
            points_within_pct = (points_within / len(valid_data)) * 100
            
            results[sensor] = {
                'mse': mse_value,
                'rmse': rmse_value,
                'mae': mae_value,
                'r2': r2_value,
                'pearson': pearson_corr,
                'pearson_p': pearson_p,
                'spearman': spearman_corr,
                'spearman_p': spearman_p,
                'points_within_error': points_within_pct,
                'error_threshold': ERROR_PERCENTAGE,
                'data_points': len(valid_data)
            }
            continue
        
        # Calculate selected metric
        if metric.lower() == 'mse':
            # Mean Squared Error
            value = np.mean((real_values - sim_values) ** 2)
        elif metric.lower() == 'rmse':
            # Root Mean Squared Error
            value = np.sqrt(np.mean((real_values - sim_values) ** 2))
        elif metric.lower() == 'mae':
            # Mean Absolute Error
            value = np.mean(np.abs(real_values - sim_values))
        elif metric.lower() == 'r2':
            # R-squared (coefficient of determination)
            if np.var(real_values) == 0:
                value = None  # Cannot calculate R² when variance is zero
            else:
                ss_res = np.sum((real_values - sim_values) ** 2)
                ss_tot = np.sum((real_values - np.mean(real_values)) ** 2)
                value = 1 - (ss_res / ss_tot)
        elif metric.lower() == 'pearson':
            # Pearson correlation coefficient
            value, p_value = stats.pearsonr(real_values, sim_values)
            results[sensor] = {
                'metric': metric,
                'value': value,
                'p_value': p_value,
                'data_points': len(valid_data)
            }
            continue
        elif metric.lower() == 'spearman':
            # Spearman rank correlation coefficient
            value, p_value = stats.spearmanr(real_values, sim_values)
            results[sensor] = {
                'metric': metric,
                'value': value,
                'p_value': p_value,
                'data_points': len(valid_data)
            }
            continue
        elif metric.lower() == 'points_within_error':
            # Percentage of points within ERROR_PERCENTAGE% of simulated value
            # Calculate relative error percentage for each point
            relative_error = np.abs(real_values - sim_values) / np.abs(sim_values) * 100
            # Count points within the error threshold
            points_within = np.sum(relative_error <= ERROR_PERCENTAGE)
            # Calculate percentage
            value = (points_within / len(valid_data)) * 100
            results[sensor] = {
                'metric': metric,
                'value': value,
                'threshold': ERROR_PERCENTAGE,
                'data_points': len(valid_data)
            }
            continue
        else:
            raise ValueError(f"Unsupported metric: {metric}. Supported: 'mse', 'rmse', 'mae', 'r2', 'pearson', 'spearman', 'points_within_error', 'all'")
        
        results[sensor] = {
            'metric': metric,
            'value': value,
            'data_points': len(valid_data)
        }
    
    return results
