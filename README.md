# Hamburg Model – Leakage Current Simulation

Hamburg model implementation for VELO silicon strip detector sensors (LHCb experiment, 2011–2018). Simulates leakage current from fluence, temperature, and luminosity data, and compares with measured values per sensor.

## Input data

Create the directory structure below and place input files accordingly:

```
in_data/
├── fluence/      # avgFluenceBinned_10T_74_80.csv
├── current/      # 2011_current.csv, 2012_current.csv, ls1_current.csv,
│                 # 2016_current.csv, 2017_current.csv, 2018_current.csv
├── temperature/  # temperatureNTC01_10T_YYYY.csv  (one per year, 2011–2018)
└── lumi/         # lumi_binned.csv
```

Output is written to `out_data/data/simulated_df.csv`.

## Config files (gitignored – create locally)

| File | Purpose |
|------|---------|
| `config.py` | Paths, NTC setting, luminosity type, simulation period |
| `config_plot.py` | Plot display options (colors, font sizes, etc.) |
| `params.py` | Hamburg model parameters (α, k, etc.) |

## Usage

```bash
# 1. Run simulation
python simulate_current.py

# 2. Plot one sensor
python plot_currents.py --sensor VL02_CT

# 3. Overview plot for all sensors
python plot_currents.py --all-sensors

# List available sensors
python plot_currents.py --list-sensors
```
