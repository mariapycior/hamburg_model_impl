import pandas as pd
from config import Paths, SENSOR_NAME, SELECTED_YEARS

def main():
    paths = Paths()
    temp_files = paths.get_temperature_files_for_years(SELECTED_YEARS)
    temp_df = pd.concat([
        pd.read_csv(f, index_col="TS", parse_dates=["TS"]) for f in temp_files
    ], axis=0, join='outer')
    temp_df = temp_df.groupby(temp_df.index).max().sort_index()

    # Resample and select sensor
    sensor_temp = temp_df[SENSOR_NAME].resample('10min').mean()

    # Find NaN gaps
    is_nan = sensor_temp.isna()
    nan_periods = []
    start = None
    for idx, val in is_nan.items():
        if val and start is None:
            start = idx
        elif not val and start is not None:
            nan_periods.append((start, idx))
            start = None
    if start is not None:
        nan_periods.append((start, sensor_temp.index[-1]))

    # Calculate durations and sort
    nan_periods = [ (s, e, (e-s).total_seconds()/60) for s, e in nan_periods ]
    nan_periods.sort(key=lambda x: x[2], reverse=True)

    total = len(sensor_temp)
    n_nan = sensor_temp.isna().sum()
    n_val = total - n_nan
    print(f"\nDane temperatury dla sensora {SENSOR_NAME}:")
    print(f"  Wartości: {n_val} / {total} ({100*n_val/total:.2f}%)")
    print(f"  Braki   : {n_nan} / {total} ({100*n_nan/total:.2f}%)\n")

    # Przerwy powyżej 5 godzin
    long_gaps = [p for p in nan_periods if p[2] > 5*60]
    long_gaps_minutes = sum(p[2] for p in long_gaps)
    total_minutes = total * 10
    print(f"Liczba przerw >5h: {len(long_gaps)}")
    print(f"Łączny czas tych przerw: {long_gaps_minutes:.0f} min ({long_gaps_minutes/60:.1f} h)")
    print(f"Stanowią {100*long_gaps_minutes/total_minutes:.2f}% całego czasu\n")

    print(f"Najdłuższe okresy z NaN dla sensora {SENSOR_NAME} (start, end, minuty):")
    for s, e, mins in nan_periods[:100]:
        print(f"{s} - {e} : {mins:.1f} min")

if __name__ == "__main__":
    main()
