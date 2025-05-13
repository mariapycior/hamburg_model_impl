#!/usr/bin/env python3

import os
import argparse
import pandas as pd
from datetime import datetime

from config import Paths, CURRENT_YEAR_LIST
import current_preparation_lib as cpl

def parse_arguments():
    parser = argparse.ArgumentParser(description='Load and process simulated and real current data')
    parser.add_argument('--sensor', type=str, default='VL02_CT', 
                        help='Sensor name to process (default: VL02_CT)')
    parser.add_argument('--simulated-file', type=str, default='simulated_df.csv',
                        help='Filename of the simulated data')
    parser.add_argument('--start-date', type=str, default=None,
                        help='Start date for data (format: YYYY-MM-DD)')
    parser.add_argument('--all-sensors', action='store_true',
                        help='Process all sensors')
    parser.add_argument('--list-sensors', action='store_true',
                        help='List all available sensors')
    return parser.parse_args()

def list_available_sensors(simulated_path):
    try:
        df = pd.read_csv(simulated_path, index_col=0, parse_dates=True, nrows=1)
        sensors = set()
        for col in df.columns:
            if col.startswith('current_'):
                sensor = col.replace('current_', '')
                sensors.add(sensor)
        return sorted(list(sensors))
    except Exception as e:
        print(f"Error reading data file: {e}")
        return []

def load_simulated_data(simulated_path):
    try:
        # Najpierw pobierz listę wszystkich dostępnych sensorów
        sensors = list_available_sensors(simulated_path)
        if not sensors:
            return None
            
        # Wczytaj dane dla wszystkich sensorów
        all_data = cpl.load_and_prepare_simulated_df(sensors, simulated_path)
        return all_data
    except Exception as e:
        print(f"Error loading simulated data: {e}")
        return None

def load_real_current_data(paths):
    # Załaduj wszystkie pliki z danymi rzeczywistymi
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
    
    # Jeśli nie załadowano żadnych danych, zwróć None
    if real_all_df.empty:
        return None
    
    # Zmień nazwy kolumn na 'real_current_nazwa-sensora'
    new_names = {}
    for col in real_all_df.columns:
        new_names[col] = f"real_current_{col}"
    
    real_all_df = real_all_df.rename(columns=new_names)
    
    # Usuń duplikaty po indeksie (datach)
    real_all_df = real_all_df[~real_all_df.index.duplicated(keep='first')]
    
    return real_all_df

def main():
    args = parse_arguments()
    paths = Paths()
    simulated_path = paths.get_output_file(args.simulated_file)
    
    if args.list_sensors:
        sensors = list_available_sensors(simulated_path)
        if sensors:
            for sensor in sensors:
                print(f"- {sensor}")
        return
    
    # 1. Wczytaj WSZYSTKIE dane symulowane dla WSZYSTKICH sensorów
    all_sensors = list_available_sensors(simulated_path)
    simulated_data = load_simulated_data(simulated_path)
    if simulated_data is None:
        print("Nie udało się wczytać danych symulowanych")
        return
    
    # 2. Wczytaj WSZYSTKIE dane rzeczywiste
    real_data = load_real_current_data(paths)
    if real_data is None:
        print("Nie udało się wczytać danych rzeczywistych")
    
    # 3. Określ, które sensory są potrzebne
    if args.all_sensors:
        sensors_to_use = all_sensors
    else:
        sensors_to_use = [args.sensor]
    
    # 4. Filtruj tylko potrzebne kolumny z danych symulowanych
    filtered_sim_columns = []
    for sensor in sensors_to_use:
        # Wybierz wszystkie kolumny związane z danym sensorem
        sim_sensor_columns = [col for col in simulated_data.columns if col.endswith(f"_{sensor}")]
        filtered_sim_columns.extend(sim_sensor_columns)
    
    # Filtruj tylko potrzebne kolumny z danych rzeczywistych
    if real_data is not None:
        filtered_real_columns = []
        for sensor in sensors_to_use:
            real_sensor_column = f"real_current_{sensor}"
            if real_sensor_column in real_data.columns:
                filtered_real_columns.append(real_sensor_column)
    
    # 5. Utwórz końcowy dataframe
    result_dfs = []
    
    # Dodaj przefiltrowane dane symulowane
    if filtered_sim_columns:
        result_dfs.append(simulated_data[filtered_sim_columns])
    
    # Dodaj przefiltrowane dane rzeczywiste jeśli istnieją
    if real_data is not None and filtered_real_columns:
        result_dfs.append(real_data[filtered_real_columns])
    
    # Połącz wszystkie dane w jeden dataframe
    if result_dfs:
        result_df = pd.concat(result_dfs, axis=1)
    else:
        print("Brak danych do połączenia")
        return
    
    # 6. Zastosuj filtr daty początkowej jeśli podano
    if args.start_date:
        start_date = pd.to_datetime(args.start_date)
        result_df = result_df[result_df.index >= start_date]
    
    # 7. Zapisz wynikowy dataframe
    if args.all_sensors:
        output_filename = 'combined_data.csv'
    else:
        output_filename = f'{args.sensor}_data.csv'
    
    result_df.to_csv(output_filename)
    print(f"Dane zapisane do {output_filename}")


if __name__ == "__main__":
    main()
