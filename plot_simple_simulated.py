import os
import pandas as pd
import matplotlib.pyplot as plt

sim = pd.read_pickle("out_data/simulated_df.pkl") if os.path.exists("out_data/simulated_df.pkl") else None
if sim is None:
    print("Brak pliku simulated_df.pkl. Najpierw wygeneruj simulated_df i zapisz jako pickle.")
    exit(1)

# Wybierz tylko kolumny current (drugi poziom MultiIndex == 'current')
current_cols = [col for col in sim.columns if col[1] == 'current']
sim_current = sim[current_cols]

plt.figure(figsize=(12, 8))
sim_current.plot(ax=plt.gca(), legend=False, alpha=0.7)
plt.ylabel("Simulated current (mA)")
plt.title("Simulated current for all sensors (only current, from pickle)")
plt.tight_layout()
plt.savefig("out_data/simple_simulated_all_current_from_pkl.png")
plt.close()
print("Wykres zapisany jako out_data/simple_simulated_all_current_from_pkl.png")
