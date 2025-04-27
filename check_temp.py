import pandas as pd
import matplotlib.pyplot as plt

# Wczytaj plik z temperaturą dla 2017
file_path = 'in_data/temperature/temperature_10T_2017.csv'
df = pd.read_csv(file_path, index_col="TS", parse_dates=["TS"])

# Wyświetl podstawowe informacje o DataFrame
df.info()
print(df.head())

df = df[df.index.year == 2017]

full_index = pd.date_range(start=df.index.min(), end=df.index.max(), freq='10min')
df = df.reindex(full_index).bfill()

for sensor in df.columns:
    temp = df[sensor].values
    idx = df.index
    color_both = []
    color_prev = []
    color_next = []
    color_none = []
    for i in range(len(temp)):
        prev_ok = i > 0 and abs(temp[i] - temp[i-1]) < 2
        next_ok = i < len(temp)-1 and abs(temp[i] - temp[i+1]) < 2
        if prev_ok and next_ok:
            color_both.append(i)
        elif prev_ok:
            color_prev.append(i)
        elif next_ok:
            color_next.append(i)
        else:
            color_none.append(i)
    plt.figure(figsize=(16, 6))
    plt.scatter(idx[color_both], temp[color_both], c='green', s=2, label='oba <2K')
    plt.scatter(idx[color_prev], temp[color_prev], c='blue', s=2, label='tylko z tyłu <2K')
    plt.scatter(idx[color_next], temp[color_next], c='orange', s=2, label='tylko z przodu <2K')
    plt.scatter(idx[color_none], temp[color_none], c='red', s=2, label='brak <2K')
    plt.xlabel('Czas')
    plt.ylabel('Temperatura (K)')
    plt.title(f'Temperatura w czasie dla sensora {sensor} (2017)')
    plt.legend()
    plt.tight_layout()
    plt.show()
