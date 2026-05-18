# Hamburg Model – Few Sensors

Branch extends `main` to support **plotting up to 5 sensors simultaneously** on a single figure.

## Input data

Same directory structure as `main`:

```
in_data/
├── fluence/      # avgFluenceBinned_10T_74_80.csv
├── current/      # 2011_current.csv, 2012_current.csv, ls1_current.csv,
│                 # 2016_current.csv, 2017_current.csv, 2018_current.csv
├── temperature/  # temperatureNTC01_10T_YYYY.csv  (one per year, 2011–2018)
└── lumi/         # lumi_binned.csv
```

## Config files (gitignored – create locally)

| File | Purpose |
|------|---------|
| `config.py` | Paths, NTC setting, luminosity type, simulation period |
| `config_plot.py` | Plot display options |
| `params.py` | Hamburg model parameters |

## Usage

```bash
# Run simulation
python simulate_current.py

# Single sensor (default)
python plot_currents.py --sensor VL02_CT

# Multiple sensors on one figure (up to 5)
python plot_currents.py --sensor VL02_CT VL03_CT VL04_CT

# All sensors overview
python plot_currents.py --all-sensors

# List available sensors
python plot_currents.py --list-sensors
```
