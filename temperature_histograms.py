#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from config import Paths

# Wczytaj dane
paths = Paths()
simulated_path = paths.get_output_file('simulated_df.csv')
df = pd.read_csv(simulated_path, index_col=0, parse_dates=True)
df_filtered = df.copy()

# Próg filtrowania (procent najwyższego binu)
THRESHOLD_PERCENT = 30

# Znajdź kolumny temperatury
temp_columns = [col for col in df.columns if col.startswith('temperature_')]

# Liczba sensorów dla wykresu
plot_sensors = min(4, len(temp_columns))
selected_plot_sensors = temp_columns[:plot_sensors]

# Utwórz wykres histogramów dla przykładowych 4 sensorów
plt.figure(figsize=(15, 10))

# Przetwarzaj wszystkie sensory
filtered_counts = {}
valid_bin_ranges = {}

for i, sensor_col in enumerate(temp_columns):
    # Pobierz dane temperatury bez NaN
    temp_data = df[sensor_col].dropna()
    
    # Usuń wartości skrajne (poniżej 200K i powyżej 300K)
    original_temp_data = temp_data.copy()
    temp_data = temp_data[(temp_data > 200) & (temp_data < 300)]
    
    if len(temp_data) == 0:
        continue
        
    sensor_name = sensor_col.replace('temperature_', '')
    
    # Utwórz histogram
    hist, bin_edges = np.histogram(temp_data, bins=100)
    
    # Znajdź maksymalną wartość histogramu
    max_bin_count = np.max(hist)
    threshold = (THRESHOLD_PERCENT / 100) * max_bin_count
    
    # Znajdź biny, które przekraczają próg
    valid_bins = np.where(hist >= threshold)[0]
    
    if len(valid_bins) > 0:
        # Stwórz maskę dla wszystkich wartości, które należą do ważnych binów
        valid_mask = np.zeros_like(temp_data, dtype=bool)
        
        for bin_idx in valid_bins:
            bin_min = bin_edges[bin_idx]
            bin_max = bin_edges[bin_idx + 1]
            valid_mask |= (temp_data >= bin_min) & (temp_data < bin_max)
        
        # Zachowaj tylko wartości z ważnych binów
        valid_data = temp_data[valid_mask]
        
        # Zastosuj filtr do oryginalnych danych
        new_mask = np.ones_like(original_temp_data, dtype=bool)
        
        for bin_idx in valid_bins:
            bin_min = bin_edges[bin_idx]
            bin_max = bin_edges[bin_idx + 1]
            in_bin_mask = (original_temp_data >= bin_min) & (original_temp_data < bin_max)
            new_mask &= ~in_bin_mask  # Odwróć maskę - chcemy indeksy, które NIE są w tych binach
        
        # Indeksy w df do ustawienia na NaN
        indices_to_nan = original_temp_data[new_mask].index
        
        # Zapisz zakres ważnych binów dla wykresu
        valid_bin_mins = [bin_edges[idx] for idx in valid_bins]
        valid_bin_maxs = [bin_edges[idx+1] for idx in valid_bins]
        valid_bin_ranges[sensor_name] = list(zip(valid_bin_mins, valid_bin_maxs))
        
        # Zapisz ile wartości jest poniżej progu
        total_points = len(original_temp_data)
        filtered_points = len(indices_to_nan)
        filtered_counts[sensor_name] = (total_points, filtered_points)
        
        # Ustaw NaN dla wartości poza ważnymi binami
        df_filtered.loc[indices_to_nan, sensor_col] = np.nan
        
        # Rysuj wykresy dla wybranych sensorów
        if sensor_col in selected_plot_sensors:
            idx = selected_plot_sensors.index(sensor_col)
            
            plt.subplot(2, 2, idx + 1)
            
            # Narysuj pełny histogram i zaznacz ważne biny
            counts, bins, patches = plt.hist(temp_data, bins=100, color='skyblue', 
                                     edgecolor='black', alpha=0.3, label='Wszystkie dane')
            
            # Zaznacz ważne biny na histogramie
            for bin_idx in valid_bins:
                patches[bin_idx].set_facecolor('blue')
                patches[bin_idx].set_alpha(0.7)
            
            # Dodaj linię progu
            plt.axhline(threshold, color='red', linestyle='dashed', 
                       linewidth=1, label=f'Próg {THRESHOLD_PERCENT}%: {threshold:.0f} punktów')
            
            # Dodaj informacje o średniej i medianie
            mean_temp = np.mean(valid_data) if len(valid_data) > 0 else np.nan
            median_temp = np.median(valid_data) if len(valid_data) > 0 else np.nan
            if not np.isnan(mean_temp):
                plt.axvline(mean_temp, color='green', linestyle='dashed', 
                          linewidth=1, label=f'Średnia po filtracji: {mean_temp:.2f}K')
            
            plt.title(f'Rozkład temperatur - {sensor_name}\n(niebieskie biny powyżej progu {THRESHOLD_PERCENT}%)')
            plt.xlabel('Temperatura [K]')
            plt.ylabel('Liczba pomiarów')
            plt.grid(True, alpha=0.3)
            plt.legend(fontsize='small')

# Zapisz przefiltrowane dane
plt.tight_layout()
plt.savefig('temperature_histograms_filtered.png', dpi=300)
plt.show()

output_file = 'simulated_df_filtered_temp.csv'
df_filtered.to_csv(paths.get_output_file(output_file))

# Wypisz statystyki filtrowania
print(f"Zapisano przefiltrowane dane do: {output_file}")
print(f"Próg filtrowania: {THRESHOLD_PERCENT}% najwyższego binu")
print("\nStatystyki filtrowania (sensor, wszystkie punkty, odfiltrowane punkty, % odfiltrowanych):")
for sensor, (total, filtered) in filtered_counts.items():
    percent = (filtered / total * 100) if total > 0 else 0
    print(f"{sensor}: {total} punktów, {filtered} odfiltrowanych ({percent:.1f}%)")
    
    # Wypisz zakresy zachowanych binów
    if sensor in valid_bin_ranges and len(valid_bin_ranges[sensor]) < 10:  # Pokazuj tylko jeśli nie ma za dużo binów
        print(f"  Zachowane zakresy: {', '.join([f'{min:.2f}-{max:.2f}K' for min, max in valid_bin_ranges[sensor]])}")
