# Hamburg Model – Z-Position Groups

Branch extends `main` with sensor grouping by **z-position along the beam axis**. Groups are defined in `groups.py`. When more than 4 z-groups are present, plots use a 2×4 grid layout. Grouping mode is set to `'z_position'` in `config_plot.py`.

## Getting data

Config and input data files are stored in the `data` branch. After cloning, run once:

```bash
git checkout origin/data -- config.py config_plot.py params.py in_data/
```

This places all required files in your working directory without switching branches. Keep them in your local `.gitignore` to avoid committing them.

Set `SENSOR_GROUPING_MODE = 'z_position'` in `config_plot.py`.

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
