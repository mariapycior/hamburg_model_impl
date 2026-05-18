# Hamburg Model – Group Mean Plots

Branch extends `main` with sensor **grouping and mean ± std plots**. Sensors are grouped by type (R/Phi), side (A/C), and z-position as defined in `groups.py`. Plots show the mean current with a shaded standard deviation band for each group.

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
| `config_plot.py` | Plot options; set `SENSOR_GROUPING_MODE` (`'type'`, `'side'`, `'z_position'`) |
| `params.py` | Hamburg model parameters |

## Usage

```bash
# Run simulation
python simulate_current.py

# Plot single sensor
python plot_currents.py --sensor VL02_CT

# Plot group means for all sensors
python plot_currents.py --all-sensors

# Choose x-axis: time / luminosity / fluence
python plot_currents.py --all-sensors --plot-by luminosity

# List available sensors
python plot_currents.py --list-sensors
```
