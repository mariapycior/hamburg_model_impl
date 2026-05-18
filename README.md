# Hamburg Model – Z-Position Groups

Branch extends `main` with sensor grouping by **z-position along the beam axis**. Groups are defined in `groups.py`. When more than 4 z-groups are present, plots use a 2×4 grid layout. Grouping mode is set to `'z_position'` in `config_plot.py`.

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
| `config_plot.py` | Plot options; set `SENSOR_GROUPING_MODE = 'z_position'` |
| `params.py` | Hamburg model parameters |

## Usage

```bash
# Run simulation
python simulate_current.py

# Plot single sensor
python plot_currents.py --sensor VL02_CT

# Plot all z-position groups
python plot_currents.py --all-sensors

# List available sensors
python plot_currents.py --list-sensors
```
