import os
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import re
from params import Parameters
from config import SIMULATION_PERIOD, TEMPERATURE_CORRECTION_ENABLED, TEMPERATURE_CORRECTION_DELTA
from VeloDetectorElement import VeloDetectorElement

def get_sensor_number(sensor_code):
    """Get sensor number from sensor code using VeloDetectorElement."""
    try:
        velo_det = VeloDetectorElement()
        # The sensor code is assumed to be in format like 'VL01_CT' or 'PU02_AB'
        # We need to add 'HV' to match the key format in VeloDetectorElement
        sensor_key = (sensor_code, 'HV')
        if sensor_key in velo_det.__members__['__Velo_Det__']:
            # Sensor number is at index 1
            return str(velo_det.__members__['__Velo_Det__'][sensor_key][1])
        return sensor_code  # Return original code if not found
    except Exception as e:
        print(f"Error getting sensor number for {sensor_code}: {e}")
        return sensor_code  # Return original code on error
from config_plot import (
    CURRENT_TEMP_MODE, REFERENCE_TEMPERATURE,
    USE_LINES_FOR_SIMULATION, SHOW_ERROR_BANDS, ERROR_PERCENTAGE, PLOT_RESAMPLING_PERIOD,
    SCATTER_MARKER_SIZE, LINE_WIDTH, ERROR_BAND_ALPHA, REAL_DATA_COLOR, SIMULATED_DATA_COLOR, ERROR_BAND_COLOR,
    COLOR_PALETTES, DEFAULT_FIGURE_SIZE, MULTI_SUBPLOT_FIGURE_SIZE, ERROR_BAND_ZORDER, DATA_ZORDER,
    SHOW_RATIO, RATIO_PLOT_HEIGHT, SHOW_RATIO_FOR_MULTIPLE_SENSORS
)


def add_parameter_info(ax, loc='upper left'):
    params = Parameters()
    timestep = pd.to_timedelta(SIMULATION_PERIOD.lower()).total_seconds() / 3600
    
    param_text = (
        f"$\\alpha_I$: {params.alpha_I:.2e} A/cm\n"
        f"$\\alpha_0^*$: {params.alpha_0_star:.2e} A/cm\n"
        f"$\\beta$: {params.beta:.2e} A/cm\n"
        f"$E_I$: {params.E_I:.2f} eV\n"
        f"$V$: {params.V:.3f} cm$^3$\n"
        f"$E_{{eff}}$: {params.E_eff:.2f} eV\n"
        f"Timestep: {timestep:.1f} h"
    )
    
    # Add resampling period information
    if PLOT_RESAMPLING_PERIOD:
        # Convert shorthand period to more readable format
        period_display = PLOT_RESAMPLING_PERIOD
        if period_display == '1W':
            period_display = '1 week'
        elif period_display.endswith('W'):
            period_display = period_display.replace('W', ' weeks')
        elif period_display == '1D':
            period_display = '1 day'
        elif period_display.endswith('D'):
            period_display = period_display.replace('D', ' days')
        
        param_text += f"\nData averaged over {period_display}"
    
    temp_info = ""
    if CURRENT_TEMP_MODE == 'adjust_real':
        temp_info = "Adjusted real to sim. temperature"
    elif CURRENT_TEMP_MODE == 'adjust_sim':
        temp_info = "Adjusted sim. to real temperature"
    elif CURRENT_TEMP_MODE == 'adjust_both':
        temp_info = f"Adjusted both to {REFERENCE_TEMPERATURE:.2f} K"
    
    if temp_info:
        # Formatujemy tekst z jawnie dodanymi spacjami w LaTeX
        if CURRENT_TEMP_MODE == 'adjust_both':
            param_text += f"\n$\\mathbf{{Adjusted\\ both\\ to\\ {REFERENCE_TEMPERATURE:.2f}\\ K}}$"
        else:
            param_text += f"\n$\\mathbf{{{temp_info.replace(' ', '\\ ')}}}$"
        
    if TEMPERATURE_CORRECTION_ENABLED:
        param_text += f"\nTemp. correction: +{TEMPERATURE_CORRECTION_DELTA} K"
    
    props = dict(boxstyle='round', facecolor='white', alpha=0.7)
    ax.text(0.02, 0.98, param_text, transform=ax.transAxes, fontsize=8,
            verticalalignment='top', horizontalalignment='left', bbox=props)


def resample_data(data, period):
    """Resample data based on specified period."""
    if period and not data.empty:
        if isinstance(data, pd.Series):
            return data.resample(period).mean()
        elif isinstance(data, pd.DataFrame):
            return data.resample(period).mean()
    return data

def setup_subplot(ax, x_data, y_data, color, label, title, ylabel, xlim, ylim=None, use_line=None, show_error_band=None, is_current_plot=False, force_no_error=False):
    use_line = USE_LINES_FOR_SIMULATION if use_line is None else use_line
    show_error_band = SHOW_ERROR_BANDS if show_error_band is None else show_error_band
    
    if force_no_error:
        show_error_band = False
    
    if PLOT_RESAMPLING_PERIOD:
        y_data_series = pd.Series(y_data, index=x_data)
        y_data_series = y_data_series.dropna()
        y_data_series = resample_data(y_data_series, PLOT_RESAMPLING_PERIOD)
        x_data = y_data_series.index
        y_data = y_data_series.values
    
    y_data_series = pd.Series(y_data, index=x_data)
    y_data_series = y_data_series.sort_index()
    
    if use_line and show_error_band and is_current_plot:
        error_value = y_data_series * (ERROR_PERCENTAGE / 100)
        ax.fill_between(
            y_data_series.index, 
            y_data_series - error_value, 
            y_data_series + error_value, 
            color=ERROR_BAND_COLOR, 
            alpha=ERROR_BAND_ALPHA, 
            label=None,
            zorder=ERROR_BAND_ZORDER
        )
    
    if use_line:
        line = ax.plot(y_data_series.index, y_data_series.values, color=color, linewidth=LINE_WIDTH, label=label, zorder=DATA_ZORDER)
    else:
        ax.scatter(y_data_series.index, y_data_series.values, color=color, s=SCATTER_MARKER_SIZE, label=label, zorder=DATA_ZORDER)
    
    ax.set_xlim(xlim)
    if ylim:
        ax.set_ylim(ylim)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True)
    ax.minorticks_on()
    ax.grid(True, which='minor', alpha=0.15)
    ax.legend(fontsize=7)

def plot_leakage_current(df: pd.DataFrame, sensor_name, 
                        output_path: str = None, start_date: pd.Timestamp = None, end_date: pd.Timestamp = None,
                        use_lines: bool = None, show_error_band: bool = None, resampling_period: str = None):
    # Sprawdź czy sensor_name jest stringiem lub listą
    if isinstance(sensor_name, str):
        sensors = [sensor_name]
    else:
        # Jeśli podano listę, ogranicz do maks. 5 sensorów
        sensors = sensor_name[:5]
    
    # Sprawdź, czy są dostępne dane dla sensorów
    valid_sensors = []
    for sensor in sensors:
        sim_col = f"current_{sensor}"
        if sim_col in df.columns:
            valid_sensors.append(sensor)
    
    if not valid_sensors:
        raise ValueError(f"Simulated current column not found for any of the sensors: {', '.join(sensors)}")

    if start_date is None:
        start_date = df.index.min()
    if end_date is None:
        end_date = df.index.max()

    fig, axes = plt.subplots(4, 1, figsize=MULTI_SUBPLOT_FIGURE_SIZE)
    
    # Ustal kolory dla wykresów
    import matplotlib.cm as cm
    sim_colors = cm.Blues(np.linspace(0.6, 0.9, len(valid_sensors)))
    real_colors = cm.Reds(np.linspace(0.6, 0.9, len(valid_sensors)))
    
    # Pierwszy subplot - symulowane prądy
    ax = axes[0]
    for i, sensor in enumerate(valid_sensors):
        sim_col = f"current_{sensor}"
        if sim_col in df.columns:
            use_line_plot = USE_LINES_FOR_SIMULATION if use_lines is None else use_lines
            show_err = SHOW_ERROR_BANDS if show_error_band is None else show_error_band
            
            if use_line_plot:
                # Pokaż pasmo błędu tylko dla pojedynczego sensora
                if show_err and len(valid_sensors) == 1:
                    error_value = df[sim_col] * (ERROR_PERCENTAGE / 100)
                    ax.fill_between(
                        df.index, 
                        df[sim_col] - error_value, 
                        df[sim_col] + error_value, 
                        color=ERROR_BAND_COLOR, 
                        alpha=ERROR_BAND_ALPHA, 
                        label=None,
                        zorder=ERROR_BAND_ZORDER
                    )
                
                ax.plot(df.index, df[sim_col], 
                        color=sim_colors[i], linewidth=LINE_WIDTH, 
                        label='Simulated', zorder=DATA_ZORDER)
            else:
                ax.scatter(df.index, df[sim_col], 
                          color=sim_colors[i], s=SCATTER_MARKER_SIZE, 
                          label='Simulated', zorder=DATA_ZORDER)
    
    # Formatowanie pierwszego subplotu
    if len(valid_sensors) == 1:
        ax.set_title(f'Simulated Leakage Current for Sensor {valid_sensors[0]}')
    else:
        ax.set_title('Simulated Leakage Current for Multiple Sensors')
    ax.set_ylabel(r'Leakage Current [mA]')
    ax.set_xlim(start_date, end_date)
    add_parameter_info(ax)
    ax.grid(True)
    ax.minorticks_on()
    ax.grid(True, which='minor', alpha=0.15)
    ax.legend(fontsize=7)
    
    # Drugi subplot - rzeczywiste prądy
    ax = axes[1]
    real_plot_created = False
    for i, sensor in enumerate(valid_sensors):
        real_col = f"real_current_{sensor}"
        if real_col in df.columns and df[real_col].notna().any():
            ax.scatter(df.index, df[real_col], 
                      color=real_colors[i], s=SCATTER_MARKER_SIZE, 
                      label='Measured', zorder=DATA_ZORDER)
            real_plot_created = True
    
    # Formatowanie drugiego subplotu
    if real_plot_created:
        if len(valid_sensors) == 1:
            ax.set_title(f'Real Leakage Current for Sensor {valid_sensors[0]}')
        else:
            ax.set_title('Real Leakage Current for Multiple Sensors')
        ax.set_ylabel(r'Leakage Current [mA]')
        ax.set_xlim(start_date, end_date)
        add_parameter_info(ax)
        ax.grid(True)
    ax.minorticks_on()
    ax.grid(True, which='minor', alpha=0.15)
    ax.legend(fontsize=7)
    
    # Trzeci subplot - fluencja (użyj pierwszego sensora jako przykład)
    if valid_sensors:
        fluence_col = f"fluence_{valid_sensors[0]}"
        if fluence_col in df.columns:
            setup_subplot(axes[2], df.index, df[fluence_col], 'green', 'Fluence', 
                        'Fluence', 'Fluence (n/cm²)', (start_date, end_date), use_line=False)
    
    # Czwarty subplot - temperatura (użyj pierwszego sensora jako przykład)
    if valid_sensors:
        temp_col = f"temperature_{valid_sensors[0]}"
        if temp_col in df.columns:
            setup_subplot(axes[3], df.index, df[temp_col], 'magenta', 'Temperature', 
                        'Temperature [K]', r'Temperature [K]', (start_date, end_date), use_line=False)

    plt.tight_layout()
    if output_path:
        plt.savefig(output_path)
    # Wykres gotowy do wyświetlenia


def plot_simulated_vs_real(df: pd.DataFrame, sensor_name, output_path: str = None, 
                         start_date: pd.Timestamp = None, end_date: pd.Timestamp = None, weekly_average: bool = False,
                         use_lines: bool = None, show_error_band: bool = None, resampling_period: str = None):
    # Sprawdź czy sensor_name jest stringiem lub listą
    if isinstance(sensor_name, str):
        sensors = [sensor_name]
    else:
        # Jeśli podano listę, ogranicz do maks. 5 sensorów
        sensors = sensor_name[:5]
    
    # Sprawdzenie czy dane istnieją
    valid_sensors = []
    for sensor in sensors:
        sim_col = f"current_{sensor}"
        real_col = f"real_current_{sensor}"
        if sim_col in df.columns or real_col in df.columns:
            valid_sensors.append(sensor)
    
    if not valid_sensors:
        print(f"No data found for sensor(s) {', '.join(sensors)}")
        return

    temp_df = df.copy()
    custom_period = resampling_period or PLOT_RESAMPLING_PERIOD
    
    if weekly_average:
        temp_df = temp_df.rolling('7d', min_periods=1).mean()
    elif custom_period:
        temp_df = temp_df.resample(custom_period).mean()

    # Przygotuj figure z/bez ratio subplot
    if SHOW_RATIO:
        import matplotlib.gridspec as gridspec
        fig = plt.figure(figsize=DEFAULT_FIGURE_SIZE)
        gs = gridspec.GridSpec(2, 1, height_ratios=[1-RATIO_PLOT_HEIGHT, RATIO_PLOT_HEIGHT])
        ax_main = fig.add_subplot(gs[0])
        ax_ratio = fig.add_subplot(gs[1], sharex=ax_main)
        ax = ax_main  # Dla zgodności z istniejącym kodem
    else:
        fig, ax = plt.subplots(figsize=DEFAULT_FIGURE_SIZE)
    
    if start_date is not None and end_date is not None:
        ax.set_xlim(pd.to_datetime(start_date), pd.to_datetime(end_date))
    else:
        ax.set_xlim(df.index.min(), df.index.max())

    # Rysuj wykresy dla każdego sensora
    for i, sensor in enumerate(valid_sensors):
        # Pobierz kolory z palety dla danego sensora (maksymalnie 5 sensorów)
        sensor_idx = min(i, 4)  # Ograniczamy indeks do 4 (5 dostępnych palet)
        dark_color = COLOR_PALETTES[sensor_idx][0]   # Kolor dla punktów (dane rzeczywiste)
        medium_color = COLOR_PALETTES[sensor_idx][1]  # Kolor dla linii (dane symulowane)
        light_color = COLOR_PALETTES[sensor_idx][2]   # Kolor dla paska błędu
        
        sim_col = f"current_{sensor}"
        real_col = f"real_current_{sensor}"
        
        # Rysuj dane rzeczywiste
        if real_col in temp_df.columns:
            real_data = temp_df[real_col].dropna()
            if not real_data.empty:
                # Użyj numeru sensora zamiast pełnej nazwy
                sensor_num = get_sensor_number(sensor)
                ax.scatter(real_data.index, real_data, 
                           color=dark_color, s=SCATTER_MARKER_SIZE, 
                           label=None, zorder=DATA_ZORDER)
        
        # Rysuj dane symulowane
        if sim_col in temp_df.columns:
            sim_data = temp_df[sim_col].dropna()
            if not sim_data.empty:
                sim_data = sim_data.sort_index()
                use_line_plot = USE_LINES_FOR_SIMULATION if use_lines is None else use_lines
                show_error = SHOW_ERROR_BANDS if show_error_band is None else show_error_band
                
                if use_line_plot and show_error:
                    # Pokaż pasmo błędu dla każdego sensora, ale bez dodawania do legendy
                    error_value = sim_data * (ERROR_PERCENTAGE / 100)
                    ax.fill_between(
                        sim_data.index, 
                        sim_data - error_value, 
                        sim_data + error_value, 
                        color=light_color, 
                        alpha=ERROR_BAND_ALPHA, 
                        label=None, 
                        zorder=ERROR_BAND_ZORDER
                    )
                
                # Numer sensora jest już wyciągnięty wcześniej
                if use_line_plot:
                    ax.plot(sim_data.index, sim_data, 
                       color=medium_color, 
                       linewidth=LINE_WIDTH, 
                       label=f'Sensor {sensor_num}',
                       zorder=DATA_ZORDER)
                else:
                    ax.scatter(sim_data.index, sim_data, 
                              color=medium_color, 
                              s=SCATTER_MARKER_SIZE, 
                              label=f'Sensor {sensor_num}',
                              zorder=DATA_ZORDER)

    add_parameter_info(ax)
    
    ax.set_ylabel(r'Leakage Current [mA]')
    # Opis osi X tylko jeśli nie ma ratio
    if not (SHOW_RATIO and SHOW_RATIO_FOR_MULTIPLE_SENSORS):
        ax.set_xlabel(r'Year')
    
    # Różne ustawienia wykresu
    ax.set_ylabel(r'Leakage Current [mA]')
    title = f'Simulated vs Real Leakage Current'
    if len(valid_sensors) == 1:
        title += f' for Sensor {valid_sensors[0]}'
    ax.set_title(title)
    add_parameter_info(ax)
    ax.grid(True)
    ax.minorticks_on()
    ax.grid(True, which='minor', alpha=0.15)
    
    # Twórz legendę
    from matplotlib.lines import Line2D
    handles, labels = ax.get_legend_handles_labels()
    filtered = [(h, l) for h, l in zip(handles, labels) if l and l.startswith('Sensor')]
    handles = [h for h, l in filtered]
    labels = [l for h, l in filtered]
    black_dot = Line2D([0], [0], marker='o', color='w', markerfacecolor='black', markersize=5, linestyle='')
    handles.append(black_dot)
    labels.append('Measured')
    ax.legend(handles=handles, labels=labels, fontsize=7)
    
    # Dodaj ratio plot
    if SHOW_RATIO and SHOW_RATIO_FOR_MULTIPLE_SENSORS:
        # Ukryj etykiety osi X na głównym wykresie
        if 'ax_main' in locals():
            plt.setp(ax_main.get_xticklabels(), visible=False)
            
        # Lista do przechowywania wszystkich ratio (do późniejszego skalowania osi Y)
        all_ratio_values = []
        
        # Dla każdego sensora przygotuj ratio
        for i, sensor in enumerate(valid_sensors):
            sim_col = f"current_{sensor}"
            real_col = f"real_current_{sensor}"
            
            # Sprawdź czy są dostępne dane symulowane i rzeczywiste dla sensora
            if sim_col in temp_df.columns and real_col in temp_df.columns:
                # Znajdź wspólne indeksy (daty) dla obu zestawów danych
                sim_data = temp_df[sim_col].dropna()
                real_data = temp_df[real_col].dropna()
                common_indices = sim_data.index.intersection(real_data.index)
                
                if len(common_indices) > 0:
                    # Oblicz ratio dla wspólnych indeksów
                    ratio = sim_data.loc[common_indices] / real_data.loc[common_indices]
                    
                    # Użyj koloru zgodnego z kolorem sensora
                    sensor_idx = min(i, 4)  # Ogranicz indeks do 4 (5 dostępnych palet)
                    medium_color = COLOR_PALETTES[sensor_idx][1]  # Używamy koloru z symulacji dla spójności
                    
                    # Rysuj ratio na dolnym subplocie
                    if 'ax_ratio' in locals():
                        ax_ratio.scatter(common_indices, ratio, 
                                      color=medium_color, 
                                      s=SCATTER_MARKER_SIZE, 
                                      alpha=0.7,
                                      label=f'{get_sensor_number(sensor)}')
                        
                        # Dodaj wartości ratio do listy (do skalowania)
                        all_ratio_values.extend(ratio.values)
        
        # Konfiguracja wykresu ratio
        if 'ax_ratio' in locals() and all_ratio_values:            
            # Dodaj linię odniesienia przy ratio=1.0
            ax_ratio.axhline(y=1.0, color='gray', linestyle='-', alpha=0.7)
            ax_ratio.set_ylabel('Sim/Meas')
            ax_ratio.set_xlabel('Year')
            ax_ratio.grid(True, alpha=0.3)
        ax_ratio.minorticks_on()
        ax_ratio.grid(True, which='minor', alpha=0.15)
            
            # Usunięto legendę dla ratio plot, zgodnie z wymaganiem
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path)
    # Wykres gotowy do wyświetlenia


def plot_sensors_data(df: pd.DataFrame, sensors: list, column_prefix: str, title: str, 
                     output_path: str = None, start_date: pd.Timestamp = None, end_date: pd.Timestamp = None,
                     use_lines: bool = None, show_error_band: bool = None, resampling_period: str = None,
                     force_no_error: bool = False, y_range: tuple = None):
    fig, ax = plt.subplots(figsize=DEFAULT_FIGURE_SIZE)
    columns = []
    
    temp_df = df.copy()
    custom_period = resampling_period or PLOT_RESAMPLING_PERIOD
    
    if custom_period:
        temp_df = temp_df.resample(custom_period).mean()

    # Rysuj wykresy dla każdego sensora
    for i, sensor in enumerate(sensors):
        col_name = f"{column_prefix}_{sensor}"
        if col_name in temp_df.columns:
            columns.append(col_name)
            y = temp_df[col_name]
            y_clean = y.dropna()
            if not y_clean.empty:
                use_line_plot = USE_LINES_FOR_SIMULATION if use_lines is None else use_lines
                show_error = SHOW_ERROR_BANDS if show_error_band is None else show_error_band
                
                if force_no_error:
                    show_error = False
                
                is_current_plot = column_prefix == "current" or column_prefix == "real_current"
                
                if column_prefix != "real_current" and use_line_plot and show_error and is_current_plot:
                    y_sorted = y_clean.sort_index()
                    error_value = y_sorted * (ERROR_PERCENTAGE / 100)
                    ax.fill_between(
                        y_sorted.index, 
                        y_sorted - error_value, 
                        y_sorted + error_value, 
                        color=ERROR_BAND_COLOR, 
                        alpha=ERROR_BAND_ALPHA,
                        zorder=ERROR_BAND_ZORDER
                    )
                
                if column_prefix == "real_current":
                    ax.scatter(y_clean.index, y_clean.values, s=SCATTER_MARKER_SIZE, 
                              label=sensor, zorder=DATA_ZORDER)
                else:
                    y_sorted = y_clean.sort_index()
                    if use_line_plot:
                        ax.plot(y_sorted.index, y_sorted.values, linewidth=LINE_WIDTH, 
                               label=sensor, zorder=DATA_ZORDER)
                    else:
                        ax.scatter(y_sorted.index, y_sorted.values, s=SCATTER_MARKER_SIZE, 
                                  label=sensor, zorder=DATA_ZORDER)
    
    if columns:
        data_df = df[columns]
        valid_count = data_df.notna().sum(axis=1)
        mean_data = data_df.mean(axis=1)
        mean_data[valid_count <= (len(columns) // 2)] = float('nan')
        mean_data = mean_data.sort_index()
        ax.plot(mean_data.index, mean_data.values, color='black', linewidth=3, 
                label='Mean (Measured)' if column_prefix == 'real_current' else 'Mean (Simulated)',
                zorder=DATA_ZORDER+1)  # Mean line should be above individual data
    
    add_parameter_info(ax)
    ax.set_xlim(start_date, end_date)
    if y_range is not None:
        ax.set_ylim(y_range)
    if column_prefix == "current" or column_prefix == "real_current":
        ax.set_ylabel(r'Leakage Current [mA]')
    elif column_prefix == "fluence":
        ax.set_ylabel(r'Fluence [$1\,\mathrm{MeV}\, \mathrm{n}_{\mathrm{eq}}/\mathrm{cm}^2$]')
    elif column_prefix == "temperature":
        ax.set_ylabel(r'Temperature [K]')
    ax.set_title(title)
    ax.grid(True)
    ax.minorticks_on()
    ax.grid(True, which='minor', alpha=0.15)
    plt.tight_layout()
    ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), title='Sensors', fontsize=7)
    
    if output_path:
        plt.savefig(output_path)
    # Wykres gotowy do wyświetlenia

def plot_all_sensors(df: pd.DataFrame, sensors: list, output_dir: str = None, 
                    start_date: pd.Timestamp = None, end_date: pd.Timestamp = None,
                    use_lines: bool = None, show_error_band: bool = None, resampling_period: str = None):
    # Najpierw przygotuj dane i znajdź globalny zakres osi Y dla obu wykresów
    temp_df = df.copy()
    custom_period = resampling_period or PLOT_RESAMPLING_PERIOD
    if custom_period:
        temp_df = temp_df.resample(custom_period).mean()
    
    # Oblicz globalny zakres osi Y
    min_val = float('inf')
    max_val = float('-inf')
    
    # Zbierz wszystkie kolumny z danymi (symulowanymi i rzeczywistymi)
    all_columns = []
    
    for sensor in sensors:
        sim_col = f"current_{sensor}"
        real_col = f"real_current_{sensor}"
        
        if sim_col in temp_df.columns:
            all_columns.append(sim_col)
        if real_col in temp_df.columns:
            all_columns.append(real_col)
    
    # Oblicz min i max dla wszystkich danych
    if all_columns:
        data_subset = temp_df[all_columns].dropna(how='all')
        if not data_subset.empty:
            # Dodaj 10% marginesu
            curr_min = data_subset.min().min()
            curr_max = data_subset.max().max()
            
            if not (pd.isna(curr_min) or pd.isna(curr_max)):
                min_val = min(min_val, curr_min)
                max_val = max(max_val, curr_max)
    
    # Ustaw wspólny zakres osi Y z 10% marginesem
    if min_val != float('inf') and max_val != float('-inf'):
        y_range_margin = (max_val - min_val) * 0.1
        y_range = (max(0, min_val - y_range_margin), max_val + y_range_margin)
    else:
        y_range = None
    
    # Plot simulated current for all sensors (no error bands when plotting all sensors)
    sim_output = None if output_dir is None else os.path.join(output_dir, 'all_sensors_simulated.png')
    plot_sensors_data(df, sensors, 'current', 'Simulated Leakage Current for All Sensors', 
                     sim_output, start_date, end_date, use_lines, show_error_band, resampling_period,
                     force_no_error=True, y_range=y_range)  # Force no error band for all sensors plot
    
    # Plot real current for all sensors (if available)
    real_output = None if output_dir is None else os.path.join(output_dir, 'all_sensors_real.png')
    plot_sensors_data(df, sensors, 'real_current', 'Real Leakage Current for All Sensors', 
                     real_output, start_date, end_date, False, False, resampling_period, y_range=y_range)



def plot_currents_vs_parameter(df: pd.DataFrame, sensor_name, param_type: str = 'luminosity', 
                                output_path: str = None, use_lines: bool = None, show_error_band: bool = None, show_ratio: bool = None):
    """
    Plot both simulated and real currents against a chosen parameter (integrated luminosity or cumulative fluence).
    Supports single sensor (string) or multiple sensors (list, max 5).
    """
    # Sprawdź czy sensor_name jest stringiem lub listą
    if isinstance(sensor_name, str):
        sensors = [sensor_name]
    else:
        # Jeśli podano listę, ogranicz do maks. 5 sensorów
        sensors = sensor_name[:5]
    
    # Sprawdzanie parametru dla wykresów
    if param_type == 'luminosity':
        param_col = "integrated_luminosity"
        x_label = r'Integrated Luminosity [fb$^{-1}$]'
        title_param = 'Integrated Luminosity'
    else:  # fluence
        # Dla wielu sensorów musimy sprawdzić, które mają dane fluence
        valid_sensors = []
        for sensor in sensors:
            delivered_fluence_col = f"delivered_fluence_{sensor}"
            if delivered_fluence_col in df.columns:
                valid_sensors.append(sensor)
        
        if not valid_sensors:
            print(f"No fluence data found for sensors: {', '.join(sensors)}")
            return
        
        # Dla fluence będziemy używać tylko sensorów z dostępnymi danymi fluence
        sensors = valid_sensors
        param_col = f"delivered_fluence_{sensors[0]}"  # Użyj pierwszego sensora jako bazowego dla osi X
        x_label = r'Fluence [$1\,\mathrm{MeV}\, \mathrm{n}_{\mathrm{eq}}/\mathrm{cm}^2$]'
        title_param = 'Cumulative Fluence'
    
    if param_col not in df.columns:
        print(f"Parameter column {param_col} not found in DataFrame")
        return
    
    # Sprawdź czy są dostępne jakiekolwiek dane dla wybranych sensorów
    valid_sim_cols = []
    valid_real_cols = []
    for sensor in sensors:
        sim_col = f"current_{sensor}"
        real_col = f"real_current_{sensor}"
        
        if sim_col in df.columns and df[sim_col].notna().any():
            valid_sim_cols.append(sim_col)
        if real_col in df.columns and df[real_col].notna().any():
            valid_real_cols.append(real_col)
    
    if not valid_sim_cols and not valid_real_cols:
        print(f"No data found for sensors: {', '.join(sensors)}")
        return
    
    # Przygotuj dane
    temp_df = df.copy()
    if PLOT_RESAMPLING_PERIOD:
        temp_df = resample_data(temp_df, period=PLOT_RESAMPLING_PERIOD)
    
    df_binned = temp_df.sort_values(by=param_col)
    
    # Ustawienia wykresu
    # Przygotuj figure z/bez ratio subplot
    show_ratio_plot = SHOW_RATIO if show_ratio is None else show_ratio
    
    if show_ratio_plot:
        import matplotlib.gridspec as gridspec
        fig = plt.figure(figsize=DEFAULT_FIGURE_SIZE)
        gs = gridspec.GridSpec(2, 1, height_ratios=[1-RATIO_PLOT_HEIGHT, RATIO_PLOT_HEIGHT])
        ax_main = fig.add_subplot(gs[0])
        ax_ratio = fig.add_subplot(gs[1], sharex=ax_main)
        ax = ax_main  # Dla zgodności z istniejącym kodem
    else:
        fig, ax = plt.subplots(figsize=DEFAULT_FIGURE_SIZE)

    # Opis osi X tylko na dolnym wykresie (ratio) jeśli jest ratio, a na głównym tylko jeśli nie ma ratio
    if show_ratio_plot:
        ax_ratio.set_xlabel(x_label)
    else:
        ax.set_xlabel(x_label)

    use_line_plot = USE_LINES_FOR_SIMULATION if use_lines is None else use_lines
    show_err = SHOW_ERROR_BANDS if show_error_band is None else show_error_band
    
    # Słowniki do przechowywania danych dla ratio
    sim_data_by_sensor = {}
    real_data_by_sensor = {}
    
    # Kolory są pobierane z COLOR_PALETTES dla każdego sensora
    
    # Rysowanie danych rzeczywistych
    for i, sensor in enumerate(sensors):
        # Pobierz kolory z palety dla danego sensora (maksymalnie 5 sensorów)
        sensor_idx = min(i, 4)  # Ograniczamy indeks do 4 (5 dostępnych palet)
        dark_color = COLOR_PALETTES[sensor_idx][0]   # Kolor dla punktów (dane rzeczywiste)
        
        real_col = f"real_current_{sensor}"
        if real_col in df_binned.columns and df_binned[real_col].notna().any():
            # Jeśli to wykres fluence, używamy fluence dla danego sensora
            if param_type == 'fluence':
                sensor_param_col = f"delivered_fluence_{sensor}"
            else:
                sensor_param_col = param_col
                
            if sensor_param_col in df_binned.columns:
                df_real = df_binned[[real_col, sensor_param_col]].dropna()
                if not df_real.empty:
                    # Zapisz dane do późniejszego obliczenia ratio
                    real_data_by_sensor[sensor] = {'param': df_real[sensor_param_col].values, 'current': df_real[real_col].values}
                    
                    # Użyj numeru sensora zamiast pełnej nazwy
                    sensor_num = get_sensor_number(sensor)
                    ax.scatter(df_real[sensor_param_col], df_real[real_col], 
                              color=dark_color, s=SCATTER_MARKER_SIZE, 
                              label=None, zorder=DATA_ZORDER)

    # Po wszystkich danych: jeśli jest ratio, ustaw opis osi X tylko na ax_ratio
    if show_ratio_plot:
        ax_ratio.set_xlabel(x_label)

    # Rysowanie danych symulowanych
    for i, sensor in enumerate(sensors):
        # Pobierz kolory z palety dla danego sensora (maksymalnie 5 sensorów)
        sensor_idx = min(i, 4)  # Ograniczamy indeks do 4 (5 dostępnych palet)
        medium_color = COLOR_PALETTES[sensor_idx][1]  # Kolor dla linii (dane symulowane)
        light_color = COLOR_PALETTES[sensor_idx][2]   # Kolor dla paska błędu
        
        sim_col = f"current_{sensor}"
        if sim_col in df_binned.columns and df_binned[sim_col].notna().any():
            # Jeśli to wykres fluence, używamy fluence dla danego sensora
            if param_type == 'fluence':
                sensor_param_col = f"delivered_fluence_{sensor}"
            else:
                sensor_param_col = param_col
                
            if sensor_param_col in df_binned.columns:
                df_sim = df_binned[[sim_col, sensor_param_col]].dropna()
                if not df_sim.empty:
                    # Zapisz dane do późniejszego obliczenia ratio
                    sim_data_by_sensor[sensor] = {'param': df_sim[sensor_param_col].values, 'current': df_sim[sim_col].values}
                    
                    # Pokaż pasmo błędu dla każdego sensora
                    if show_err and use_line_plot:
                        error_value = df_sim[sim_col] * (ERROR_PERCENTAGE / 100)
                        ax.fill_between(
                            df_sim[sensor_param_col], 
                            df_sim[sim_col] - error_value, 
                            df_sim[sim_col] + error_value, 
                            color=light_color, 
                            alpha=ERROR_BAND_ALPHA, 
                            label=None,
                            zorder=ERROR_BAND_ZORDER
                        )
                    
                    # Użyj numeru sensora zamiast pełnej nazwy
                    sensor_num = get_sensor_number(sensor)
                    if use_line_plot:
                        ax.plot(df_sim[sensor_param_col], df_sim[sim_col], 
                               color=medium_color, linewidth=LINE_WIDTH, 
                               label=f'Sensor {sensor_num}', zorder=DATA_ZORDER)
                    else:
                        ax.scatter(df_sim[sensor_param_col], df_sim[sim_col], 
                                  color=medium_color, s=SCATTER_MARKER_SIZE, 
                                  label=f'Sensor {sensor_num}', zorder=DATA_ZORDER)
    
    add_parameter_info(ax)
    ax.set_ylabel(r'Leakage Current [mA]')
    # Tytuł z numerami sensorów
    if isinstance(sensor_name, list):
        # Użyj numerów sensorów w tytule dla wielu sensorów
        sensor_numbers = [get_sensor_number(s) for s in sensor_name]
        sensor_numbers_str = ', '.join(sensor_numbers)
        ax.set_title(f'Leakage Current vs {title_param} for Sensors {sensor_numbers_str}')
    else:
        # Dla pojedynczego sensora
        sensor_num = get_sensor_number(sensor_name)
        ax.set_title(f'Leakage Current vs {title_param} for Sensor {sensor_num}')
    ax.grid(True)
    ax.minorticks_on()
    ax.grid(True, which='minor', alpha=0.15)
    
    # Dodaj czarny punkt dla Real Data tylko w legendzie
    from matplotlib.lines import Line2D
    # Twórz legendę z oryginalnych elementów plus czarny punkt
    handles, labels = ax.get_legend_handles_labels()
    black_dot = Line2D([0], [0], marker='o', color='w', markerfacecolor='black', markersize=5, linestyle='')
    handles.append(black_dot)
    labels.append('Measured')
    
    ax.legend(handles=handles, labels=labels, fontsize=7)
    
    # Rysuj wykres ratio jeśli potrzebny
    if show_ratio_plot:
        import numpy as np
        from scipy import interpolate
        
        # Ukryj etykiety osi X na głównym wykresie
        plt.setp(ax_main.get_xticklabels(), visible=False)
        
        # Dla każdego sensora oblicz ratio symulacja/rzeczywiste
        for i, sensor in enumerate(sensors):
            if sensor in sim_data_by_sensor and sensor in real_data_by_sensor:
                sim_data = sim_data_by_sensor[sensor]
                real_data = real_data_by_sensor[sensor]
                
                # Uzyskaj kolor z tej samej palety co wyżej
                sensor_idx = min(i, 4)
                color = COLOR_PALETTES[sensor_idx][1]  # Używamy koloru z symulacji dla spójności
                
                # Aby obliczyć ratio potrzebujemy wspólnych wartości parametru (np. fluencji)
                # Używamy interpolacji, aby obliczyć wartości prądu symulowanego w punktach rzeczywistych
                try:
                    # Interpolacja danych symulowanych do punktów rzeczywistych
                    sim_interp = interpolate.interp1d(sim_data['param'], sim_data['current'], 
                                                     bounds_error=False, fill_value=np.nan)
                    
                    # Oblicz interpolowane wartości symulowane w punktach rzeczywistych
                    interp_sim_currents = sim_interp(real_data['param'])
                    
                    # Oblicz ratio tylko dla punktów, gdzie interpolacja zwróciła poprawne wartości
                    valid_indices = ~np.isnan(interp_sim_currents)
                    if np.any(valid_indices):
                        ratio = interp_sim_currents[valid_indices] / real_data['current'][valid_indices]
                        
                        # Rysuj ratio na dolnym subplocie
                        ax_ratio.scatter(real_data['param'][valid_indices], ratio, 
                                       color=color, s=SCATTER_MARKER_SIZE, alpha=0.7,
                                       label=f'{get_sensor_number(sensor)}')
                except Exception as e:
                    print(f"Error calculating ratio for sensor {sensor}: {e}")
        
        # Dodaj linię odniesienia przy ratio=1.0
        ax_ratio.axhline(y=1.0, color='gray', linestyle='-', alpha=0.7)
        
        # Konfiguracja wykresu ratio
        ax_ratio.set_xlabel(x_label)
        ax_ratio.set_ylabel('Sim/Meas')
        ax_ratio.grid(True, alpha=0.3)
        ax_ratio.minorticks_on()
        ax_ratio.grid(True, which='minor', alpha=0.15)
        
        # Usunięto legendę dla ratio plot, zgodnie z wymaganiem
        
        # Automatyczne dopasowanie zakresu osi Y
        # Ten kod będzie działał, jeśli mamy jakieś dane ratio
        if hasattr(ax_ratio, '_children') and any(isinstance(child, mpl.collections.PathCollection) for child in ax_ratio.get_children()):
            # Pobierz wszystkie punkty ratio
            ratio_points = []
            for collection in [c for c in ax_ratio.get_children() if isinstance(c, mpl.collections.PathCollection)]:
                if hasattr(collection, '_offsets') and len(collection._offsets) > 0:
                    offsets = collection.get_offsets()
                    if len(offsets) > 0 and offsets.shape[1] >= 2:
                        ratio_points.extend(offsets[:, 1])
            
            if ratio_points:
                ratios = np.array(ratio_points)
                # Ustal zakres osi Y na podstawie maksymalnego odchylenia od 1.0
                if len(ratios) > 0:
                    max_dev = max(abs(np.nanmin(ratios) - 1.0), abs(np.nanmax(ratios) - 1.0))
                    max_dev = max_dev * 1.2  # Dodaj trochę marginesu
                    ylim_low = max(0, 1.0 - max_dev)  # Nie schodź poniżej 0
                    ylim_high = 1.0 + max_dev
                    ax_ratio.set_ylim(ylim_low, ylim_high)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path)
    
    # Wykres gotowy do wyświetlenia


def plot_currents_vs_cumulative_fluence(df: pd.DataFrame, sensor_name: str, output_path: str = None,
                                   use_lines: bool = None, show_error_band: bool = None, show_ratio: bool = None):
    """
    Plot both simulated and real currents against delivered fluence.
    """
    return plot_currents_vs_parameter(df, sensor_name, param_type='fluence', output_path=output_path,
                                     use_lines=use_lines, show_error_band=show_error_band, show_ratio=show_ratio)


def plot_all_currents_vs_fluence(df: pd.DataFrame, sensors: list, output_dir: str = None):
    """Plot all sensors currents against fluence in two separate plots using continuous lines.
    Both plots use the same axis scales for better comparison."""
    # Check if any sensors have fluence data
    has_fluence_data = False
    for sensor in sensors:
        fluence_col = f"delivered_fluence_{sensor}"
        if fluence_col in df.columns:
            has_fluence_data = True
            break
            
    if not has_fluence_data:
        print("No fluence data found for any sensors")
        return
    
    # Resample data if configured
    temp_df = df.copy()
    if PLOT_RESAMPLING_PERIOD:
        temp_df = resample_data(temp_df, period=PLOT_RESAMPLING_PERIOD)
    
    # First, collect all data to determine common axis limits
    all_fluence_values = []
    all_current_values = []
    sim_data_by_sensor = {}
    real_data_by_sensor = {}
    
    # Collect simulated data
    for sensor in sensors:
        sim_col = f"current_{sensor}"
        fluence_col = f"delivered_fluence_{sensor}"
        if sim_col in temp_df.columns and fluence_col in temp_df.columns:
            sim_data = temp_df[[sim_col, fluence_col]].dropna()
            if not sim_data.empty:
                sim_data = sim_data.sort_values(fluence_col)
                sim_data_by_sensor[sensor] = sim_data
                all_fluence_values.extend(sim_data[fluence_col].values)
                all_current_values.extend(sim_data[sim_col].values)
    
    # Collect real data
    for sensor in sensors:
        real_col = f"real_current_{sensor}"
        fluence_col = f"delivered_fluence_{sensor}"
        if real_col in temp_df.columns and fluence_col in temp_df.columns:
            real_data = temp_df[[real_col, fluence_col]].dropna()
            if not real_data.empty:
                real_data = real_data.sort_values(fluence_col)
                real_data_by_sensor[sensor] = real_data
                all_fluence_values.extend(real_data[fluence_col].values)
                all_current_values.extend(real_data[real_col].values)
    
    # Determine common axis limits
    if all_fluence_values and all_current_values:
        x_min = min(all_fluence_values)
        x_max = max(all_fluence_values)
        y_min = 0  # Start from 0 for currents
        y_max = max(all_current_values) * 1.1  # Add 10% margin
        
        # Plot for simulated data
        fig, ax = plt.subplots(figsize=DEFAULT_FIGURE_SIZE)
        
        for i, (sensor, sim_data) in enumerate(sim_data_by_sensor.items()):
            fluence_col = f"delivered_fluence_{sensor}"
            color_idx = i % len(COLOR_PALETTES)
            # Używamy średniego koloru z palety (indeks 1) dla linii symulacji
            color = COLOR_PALETTES[color_idx][1]
            ax.plot(sim_data[fluence_col], sim_data[f'current_{sensor}'], 
                   linewidth=LINE_WIDTH, label=sensor, color=color, zorder=DATA_ZORDER)
        
        add_parameter_info(ax)
        
        ax.set_xlabel(r'Fluence [$1\,\mathrm{MeV}\, \mathrm{n}_{\mathrm{eq}}/\mathrm{cm}^2$]')
        ax.set_ylabel(r'Leakage Current [mA]')
        ax.set_title('Simulated Leakage Current vs Fluence for All Sensors')
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.grid(True)
        ax.minorticks_on()
        ax.grid(True, which='minor', alpha=0.15)
        plt.tight_layout()
        ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), title='Sensors', fontsize=7)
        if output_dir is not None:
            plt.savefig(os.path.join(output_dir, "all_simulated_vs_fluence.png"), bbox_inches='tight')
        
        # Plot for real data
        fig, ax = plt.subplots(figsize=DEFAULT_FIGURE_SIZE)
        
        for i, (sensor, real_data) in enumerate(real_data_by_sensor.items()):
            fluence_col = f"delivered_fluence_{sensor}"
            color_idx = i % len(COLOR_PALETTES)
            # Używamy jasnego koloru z palety (indeks 0) dla danych rzeczywistych
            color = COLOR_PALETTES[color_idx][0]
            ax.plot(real_data[fluence_col], real_data[f'real_current_{sensor}'], 
                   linewidth=LINE_WIDTH, label=sensor, color=color, zorder=DATA_ZORDER)
        
        add_parameter_info(ax)
        
        ax.set_xlabel(r'Fluence [$1\,\mathrm{MeV}\, \mathrm{n}_{\mathrm{eq}}/\mathrm{cm}^2$]')
        ax.set_ylabel(r'Leakage Current [mA]')
        ax.set_title('Measured Leakage Current vs Fluence for All Sensors')
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.grid(True)
        ax.minorticks_on()
        ax.grid(True, which='minor', alpha=0.15)
        plt.tight_layout()
        ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), title='Sensors', fontsize=7)
        if output_dir is not None:
            plt.savefig(os.path.join(output_dir, "all_real_vs_fluence.png"), bbox_inches='tight')
    else:
        print("No data available for plotting currents vs fluence")


def plot_all_currents_vs_luminosity(df: pd.DataFrame, sensors: list, output_dir: str = None):
    """Plot all sensors currents against integrated luminosity in two separate plots using continuous lines.
    Both plots use the same axis scales for better comparison."""
    if 'integrated_luminosity' not in df.columns:
        print("No integrated luminosity data found")
        return
    
    # Resample data if configured
    temp_df = df.copy()
    if PLOT_RESAMPLING_PERIOD:
        temp_df = resample_data(temp_df, period=PLOT_RESAMPLING_PERIOD)
    
    # First, collect all data to determine common axis limits
    all_lumi_values = []
    all_current_values = []
    sim_data_by_sensor = {}
    real_data_by_sensor = {}
    
    # Collect simulated data
    for sensor in sensors:
        sim_col = f"current_{sensor}"
        if sim_col in temp_df.columns:
            sim_data = temp_df[[sim_col, 'integrated_luminosity']].dropna()
            if not sim_data.empty:
                sim_data = sim_data.sort_values('integrated_luminosity')
                sim_data_by_sensor[sensor] = sim_data
                all_lumi_values.extend(sim_data['integrated_luminosity'].values)
                all_current_values.extend(sim_data[sim_col].values)
    
    # Collect real data
    for sensor in sensors:
        real_col = f"real_current_{sensor}"
        if real_col in temp_df.columns:
            real_data = temp_df[[real_col, 'integrated_luminosity']].dropna()
            if not real_data.empty:
                real_data = real_data.sort_values('integrated_luminosity')
                real_data_by_sensor[sensor] = real_data
                all_lumi_values.extend(real_data['integrated_luminosity'].values)
                all_current_values.extend(real_data[real_col].values)
    
    # Determine common axis limits
    if all_lumi_values and all_current_values:
        x_min = min(all_lumi_values)
        x_max = max(all_lumi_values)
        y_min = 0  # Start from 0 for currents
        y_max = max(all_current_values) * 1.1  # Add 10% margin
        
        # Plot for simulated data
        fig, ax = plt.subplots(figsize=DEFAULT_FIGURE_SIZE)
        for i, (sensor, sim_data) in enumerate(sim_data_by_sensor.items()):
            color_idx = i % len(COLOR_PALETTES)
            # Używamy średniego koloru z palety (indeks 1) dla linii symulacji
            color = COLOR_PALETTES[color_idx][1]
            ax.plot(sim_data['integrated_luminosity'], sim_data[f'current_{sensor}'], 
                   linewidth=LINE_WIDTH, label=sensor, color=color, zorder=DATA_ZORDER)
        add_parameter_info(ax)
        ax.set_xlabel(r'Integrated Luminosity [fb$^{-1}$]')
        ax.set_ylabel(r'Leakage Current [mA]')
        ax.set_title('Simulated Leakage Current vs Integrated Luminosity for All Sensors')
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.grid(True)
        ax.minorticks_on()
        ax.grid(True, which='minor', alpha=0.15)
        plt.tight_layout()
        ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), title='Sensors', fontsize=7)
        if output_dir is not None:
            plt.savefig(os.path.join(output_dir, "all_simulated_vs_luminosity.png"), bbox_inches='tight')

        # Plot for real data
        fig, ax = plt.subplots(figsize=DEFAULT_FIGURE_SIZE)
        for i, (sensor, real_data) in enumerate(real_data_by_sensor.items()):
            color_idx = i % len(COLOR_PALETTES)
            # Używamy jasnego koloru z palety (indeks 0) dla danych rzeczywistych
            color = COLOR_PALETTES[color_idx][0]
            ax.plot(real_data['integrated_luminosity'], real_data[f'real_current_{sensor}'], 
                   linewidth=LINE_WIDTH, label=sensor, color=color, zorder=DATA_ZORDER)
        add_parameter_info(ax)
        ax.set_xlabel(r'Integrated Luminosity [fb$^{-1}$]')
        ax.set_ylabel(r'Leakage Current [mA]')
        ax.set_title('Measured Leakage Current vs Integrated Luminosity for All Sensors')
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.grid(True)
        ax.minorticks_on()
        ax.grid(True, which='minor', alpha=0.15)
        plt.tight_layout()
        ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), title='Sensors', fontsize=7)
        if output_dir is not None:
            plt.savefig(os.path.join(output_dir, "all_real_vs_luminosity.png"), bbox_inches='tight')


def plot_integrated_luminosity(df: pd.DataFrame, output_path: str = None):
    """Plot integrated luminosity over time."""
    try:
        plt.figure(figsize=DEFAULT_FIGURE_SIZE)
        df['integrated_luminosity'].plot(zorder=DATA_ZORDER)
        plt.title('Integrated Luminosity vs Year')
        plt.xlabel('Year')
        plt.ylabel(r'Integrated Luminosity [fb$^{-1}$]')
        plt.grid(True)
        if output_path:
            plt.savefig(output_path)
        # Wykres gotowy do wyświetlenia
        print("Created integrated luminosity plot")
    except Exception as e:
        print(f"Error creating integrated luminosity plot: {e}")



def plot_currents_vs_position(summary_df: pd.DataFrame, target_luminosities: list, output_path: str = None):
    """
    Plot simulated and real currents against sensor position.
    Args:
        summary_df: DataFrame from create_sensor_summary with columns [current_sim, current_real, position, luminosity]
        target_luminosities: List of target luminosity values used for the plot
        output_path: Optional path to save the plot
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    
    markers = ['o', '^', 's', 'D']
    colors = ['blue', 'red', 'green', 'purple']
    
    for i, target_lumi in enumerate(target_luminosities):
        lumi_str = f'_f{target_lumi:.1f}'
        sim_col = f'current_sim{lumi_str}'
        real_col = f'current_real{lumi_str}'
        
        positions = summary_df['position'].values
        sim_values = summary_df[sim_col].values if sim_col in summary_df.columns else None
        real_values = summary_df[real_col].values if real_col in summary_df.columns else None
        
        if sim_values is None and real_values is None:
            continue
            
        color_idx = i % len(colors)
        marker_idx = i % len(markers)
        
        if sim_values is not None:
            ax.scatter(positions, sim_values, 
                      color=colors[color_idx], marker=markers[marker_idx],
                      s=20, label=f'Sim @ {target_lumi} fb$^{{-1}}$', 
                      zorder=10)
            
        if real_values is not None:
            ax.scatter(positions, real_values, 
                      edgecolor=colors[color_idx], marker=markers[marker_idx],
                      facecolor='none', s=20, 
                      label=f'Real @ {target_lumi} fb$^{{-1}}$', zorder=10)
    
    add_parameter_info(ax, loc='upper right')
    
    ax.set_xlabel(r'Sensor Z Position [mm]')
    ax.set_ylabel(r'Leakage Current [mA]')
    ax.set_title('Leakage Current vs Sensor Position at Different Luminosities')
    ax.grid(True)
    ax.minorticks_on()
    ax.grid(True, which='minor', alpha=0.15)
    ax.legend(fontsize=7)
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path)
