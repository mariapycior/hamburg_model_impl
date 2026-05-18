# Hamburg Model – Sensor Groups with Ratio

Branch extends `main` with sensor grouping (R/Phi type, A/C side, z-position) and an optional **sim/real ratio subplot**. Groups are defined in `groups.py`. Plots can show current vs time or integrated luminosity.

## Input data

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
| `config_plot.py` | Plot options; key settings: `SENSOR_GROUPING_MODE`, `SHOW_RATIO_FOR_SINGLE_SENSOR`, `RATIO_PLOT_HEIGHT` |
| `params.py` | Hamburg model parameters |

## Usage

```bash
# Run simulation
python simulate_current.py

# Plot single sensor
python plot_currents.py --sensor VL02_CT

# Plot sensor groups (with ratio subplot if enabled in config_plot.py)
python plot_currents.py --all-sensors

# Plot vs luminosity
python plot_currents.py --all-sensors --plot-by luminosity

# List available sensors
python plot_currents.py --list-sensors
```
