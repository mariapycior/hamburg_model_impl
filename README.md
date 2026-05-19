# Hamburg Model – Group Mean Plots

Branch extends `main` with sensor **grouping and mean ± std plots**. Sensors are grouped by type (R/Phi), side (A/C), and z-position as defined in `groups.py`. Plots show the mean current with a shaded standard deviation band for each group.

## Getting data

Config and input data files are stored in the `data` branch. After cloning, run once:

```bash
git checkout origin/data -- config.py config_plot.py params.py in_data/
```

This places all required files in your working directory without switching branches. Keep them in your local `.gitignore` to avoid committing them.

Set `SENSOR_GROUPING_MODE` in `config_plot.py` to `'type'`, `'side'`, or `'z_position'`.

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
