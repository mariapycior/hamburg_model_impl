# Hamburg Model – Current Growth (Linear Fit)

Branch extends `groups_of_sensors` with **linear fits on group average plots**, showing the current growth rate in mA/fb⁻¹ for defined luminosity ranges. Fit ranges and line styling are configured in `config_plot.py`.

## Getting data

Config and input data files are stored in the `data` branch. After cloning, run once:

```bash
git checkout origin/data -- config.py config_plot.py params.py in_data/
```

This places all required files in your working directory without switching branches. Keep them in your local `.gitignore` to avoid committing them.

Key `config_plot.py` settings for this branch: `SENSOR_GROUPING_MODE`, `FIT_LUMINOSITY_RANGES`, `SIMULATION_LINE_COLOR`, `MEASUREMENT_LINE_COLOR`.

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
