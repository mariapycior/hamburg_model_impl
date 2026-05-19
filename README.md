# Hamburg Model – Few Sensors

Branch extends `main` to support **plotting up to 5 sensors simultaneously** on a single figure.

## Getting data

Config and input data files are stored in the `data` branch. After cloning, run once:

```bash
git checkout origin/data -- config.py config_plot.py params.py in_data/
```

This places all required files in your working directory without switching branches. Keep them in your local `.gitignore` to avoid committing them.

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
