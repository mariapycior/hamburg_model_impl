# Hamburg Model – Current Growth (Linear Fit)

Branch extends `groups_of_sensors` with **linear fits on group average plots**, showing the current growth rate in mA/fb⁻¹ for defined luminosity ranges. Fit ranges and line styling are configured in `config_plot.py`.

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
| `config_plot.py` | Plot options; key settings: `SENSOR_GROUPING_MODE`, `FIT_LUMINOSITY_RANGES`, `SIMULATION_LINE_COLOR`, `MEASUREMENT_LINE_COLOR` |
| `params.py` | Hamburg model parameters |

## Usage

```bash
# Run simulation
python simulate_current.py

# Plot single sensor
python plot_currents.py --sensor VL02_CT

# Plot groups with linear growth fits (x = time)
python plot_currents.py --all-sensors

# Plot vs luminosity
python plot_currents.py --all-sensors --plot-by luminosity

# List available sensors
python plot_currents.py --list-sensors
```
