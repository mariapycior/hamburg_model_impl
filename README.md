# Hamburg Model – Sensor Groups with Ratio

Branch extends `main` with sensor grouping (R/Phi type, A/C side, z-position) and an optional **sim/real ratio subplot**. Groups are defined in `groups.py`. Plots can show current vs time or integrated luminosity.

## Getting data

Config and input data files are stored in the `data` branch. After cloning, run once:

```bash
git checkout origin/data -- config.py config_plot.py params.py in_data/
```

This places all required files in your working directory without switching branches. Keep them in your local `.gitignore` to avoid committing them.

Key `config_plot.py` settings for this branch: `SENSOR_GROUPING_MODE`, `SHOW_RATIO_FOR_SINGLE_SENSOR`, `RATIO_PLOT_HEIGHT`.

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
