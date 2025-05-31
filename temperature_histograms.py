#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from config import Paths

# Wczytaj dane
paths = Paths()
simulated_path = paths.get_output_file('simulated_df.csv')
df = pd.read_csv(simulated_path, index_col=0, parse_dates=True)

# Wybierz 4 sensory do analizy
all_sensors = set()
for col in df.columns:
    if col.startswith('temperature_'):
        sensor = col.replace('temperature_', '')
        all_sensors.add(sensor)

selected_sensors = list(all_sensors)[:4] if len(all_sensors) >= 4 else list(all_sensors)
print(f"Wybrane sensory do analizy: {selected_sensors}")

# Przygotuj trzy wersje danych
df_all = df.copy()  # Wszystkie dane
df_nonzero_fluence = df.copy()  # Tylko dane z niezerową fluencją
df_zero_fluence = df.copy()  # Tylko dane z zerową fluencją

# Przygotuj dane dla każdego sensora
for sensor in selected_sensors:
    temp_col = f"temperature_{sensor}"
    fluence_col = f"fluence_{sensor}"
    
    if temp_col not in df.columns or fluence_col not in df.columns:
        continue
    
    # Ustaw NaN dla zerowej fluencji w df_nonzero_fluence
    zero_fluence_mask = (df[fluence_col] == 0)
    df_nonzero_fluence.loc[zero_fluence_mask, temp_col] = np.nan
    
    # Ustaw NaN dla niezerowej fluencji w df_zero_fluence
    nonzero_fluence_mask = (df[fluence_col] != 0) & ~df[fluence_col].isna()
    df_zero_fluence.loc[nonzero_fluence_mask, temp_col] = np.nan

# Utwórz histogramy dla każdego sensora
for sensor in selected_sensors:
    # Pobierz dane temperaturowe dla sensora
    temp_col = f"temperature_{sensor}"
    if temp_col not in df.columns:
        continue
    
    fluence_col = f"fluence_{sensor}"
    if fluence_col not in df.columns:
        continue
    
    # Przygotuj dane do histogramów
    temperature_data = df[temp_col].dropna().copy()
    
    # Wersja z niezerową fluencją
    nonzero_fluence = df.loc[df[fluence_col] > 0, temp_col].dropna()
    
    # Wersja z zerową fluencją
    zero_fluence = df.loc[df[fluence_col] == 0, temp_col].dropna()
    
    # Znajdź bin z najwyższą liczbą wystąpień dla danych z zerową fluencją
    if len(zero_fluence) > 0:
        hist, bin_edges = np.histogram(zero_fluence, bins=100)
        if hist.max() > 0:
            max_bin_idx = np.argmax(hist)
            max_bin_min = bin_edges[max_bin_idx]
            max_bin_max = bin_edges[max_bin_idx + 1]
            # Oblicz średnią wartość w najwyższym binie
            bin_values = zero_fluence[(zero_fluence >= max_bin_min) & (zero_fluence < max_bin_max)]
            if len(bin_values) > 0:
                bin_mean = bin_values.mean()
                print(f"{sensor}: Najwyższy bin dla zerowej fluencji w przedziale {max_bin_min:.2f}-{max_bin_max:.2f}K, średnia: {bin_mean:.4f}K")

# Twórz wykresy dla każdego sensora
for sensor in selected_sensors:
    temp_col = f"temperature_{sensor}"
    fluence_col = f"fluence_{sensor}"
    
    if temp_col not in df.columns or fluence_col not in df.columns:
        continue
    
    # Utwórz 3 rodzaje histogramów na jednym wykresie
    plt.figure(figsize=(15, 8))
    
    # 1. Wszystkie dane
    plt.subplot(1, 3, 1)
    all_temp_data = df_all[temp_col].dropna()
    all_temp_filtered = all_temp_data[(all_temp_data > 200) & (all_temp_data < 300)]
    if len(all_temp_filtered) > 0:
        plt.hist(all_temp_filtered, bins=100, color='blue', alpha=0.7, edgecolor='black')
        plt.axvline(all_temp_filtered.mean(), color='red', linestyle='dashed', 
                    linewidth=2, label=f'Śr: {all_temp_filtered.mean():.2f}K')
        plt.title(f"{sensor} - Wszystkie dane\n({len(all_temp_filtered)} punktów)")
        plt.xlabel("Temperatura [K]")
        plt.ylabel("Liczba pomiarów")
        plt.grid(alpha=0.3)
        plt.legend()
    
    # 2. Tylko niezerowa fluencja
    plt.subplot(1, 3, 2)
    nonzero_temp_data = df_nonzero_fluence[temp_col].dropna()
    nonzero_temp_filtered = nonzero_temp_data[(nonzero_temp_data > 200) & (nonzero_temp_data < 300)]
    if len(nonzero_temp_filtered) > 0:
        plt.hist(nonzero_temp_filtered, bins=100, color='green', alpha=0.7, edgecolor='black')
        plt.axvline(nonzero_temp_filtered.mean(), color='red', linestyle='dashed', 
                    linewidth=2, label=f'Śr: {nonzero_temp_filtered.mean():.2f}K')
        plt.title(f"{sensor} - Tylko niezerowa fluencja\n({len(nonzero_temp_filtered)} punktów)")
        plt.xlabel("Temperatura [K]")
        plt.ylabel("Liczba pomiarów")
        plt.grid(alpha=0.3)
        plt.legend()
    
    # 3. Tylko zerowa fluencja
    plt.subplot(1, 3, 3)
    zero_temp_data = df_zero_fluence[temp_col].dropna()
    zero_temp_filtered = zero_temp_data[(zero_temp_data > 200) & (zero_temp_data < 300)]
    if len(zero_temp_filtered) > 0:
        plt.hist(zero_temp_filtered, bins=100, color='orange', alpha=0.7, edgecolor='black')
        plt.axvline(zero_temp_filtered.mean(), color='red', linestyle='dashed', 
                    linewidth=2, label=f'Śr: {zero_temp_filtered.mean():.2f}K')
        plt.title(f"{sensor} - Tylko zerowa fluencja\n({len(zero_temp_filtered)} punktów)")
        plt.xlabel("Temperatura [K]")
        plt.ylabel("Liczba pomiarów")
        plt.grid(alpha=0.3)
        plt.legend()
    
    # Dodaj statystyki porównawcze
    plt.tight_layout()
    plt.show()

# Komunikat podsumowujący
print("Wyświetlono histogramy temperatur w trzech wariantach:")
print("1. Dla wszystkich danych")
print("2. Tylko dla danych z niezerową fluencją")
print("3. Tylko dla danych z zerową fluencją")

