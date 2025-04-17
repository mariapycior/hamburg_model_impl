import os
import pandas as pd
from datetime import datetime
import fluence_lib
from config import Paths

KB = 8.617333262145e-5
T_REF = 294.15
E_I_STAR = 1.30
ALPHA_I = 1.23e-17
ALPHA_0_STAR = 7.07e-17
BETA = 3.29e-18
E_I = 1.11
K_0I = 1.2e13
T_0 = 1.0
V = 0.805

class Parameters:
    def __init__(self):
        self.E_I_star = E_I_STAR
        self.kb = KB
        self.T_ref = T_REF
        self.k_0I = K_0I
        self.E_I = E_I
        self.alpha_I = ALPHA_I
        self.alpha_0_star = ALPHA_0_STAR
        self.beta = BETA
        self.t_0 = T_0
        self.V = V

def get_available_sensors(paths, selected_years):
    year_ranges = {
        'run1_current_all.csv': [2011, 2012],
        'ls1_current_all.csv': [2013, 2014, 2015],
        'run2_current_all.csv': [2016, 2017, 2018]
    }
    
    # Only load current files for selected years
    relevant_files = [
        file for file, years in year_ranges.items()
        if any(year in selected_years for year in years)
    ]
    
    all_current_dfs = [
        pd.read_csv(paths.get_current_file(file))
        for file in relevant_files
    ]
    
    # Get common columns excluding 'TS'
    common_sensors = set(all_current_dfs[0].columns) - {'TS'}
    for df in all_current_dfs[1:]:
        common_sensors &= (set(df.columns) - {'TS'})
    
    return sorted(list(common_sensors))

def get_current_files(paths, selected_years):
    year_ranges = [
        ('run1_current_all.csv', [2011, 2012]),
        ('ls1_current_all.csv', [2013, 2014, 2015]),
        ('run2_current_all.csv', [2016, 2017, 2018])
    ]
    return [paths.get_current_file(f) for f, years in year_ranges 
            if any(year in selected_years for year in years)]

def main():
    params = Parameters()
    paths = Paths()
    selected_years = range(2011, 2019)
    
    # Get available sensors first
    available_sensors = get_available_sensors(paths, selected_years)
    print(f"Found {len(available_sensors)} sensors available across all runs")
    
    fluence_file = paths.get_fluence_file('avgFluenceBinned.csv')
    temp_files = paths.get_temperature_files_for_years(selected_years)
    current_files = get_current_files(paths, selected_years)

    simulated_df, real_df, sensors = fluence_lib.run_leakage_current_pipeline(
        fluence_file, temp_files, current_files, params, paths
    )
    
    if len(sensors) < len(available_sensors):
        print(f"Warning: Only {len(sensors)} out of {len(available_sensors)} sensors have complete data")
    
    fluence_lib.plot_all_sensors(simulated_df, real_df, sensors, output_dir="out_data")

if __name__ == "__main__":
    main()
