# Hamburg Model – Leakage Current Simulation

Hamburg model implementation for VELO silicon strip detector sensors (LHCb experiment, 2011–2018). Simulates leakage current from fluence, temperature, and luminosity data, and compares with measured values per sensor.

## Getting data

Config and input data files are stored in the `data` branch. After cloning, run once:

```bash
git checkout origin/data -- config.py config_plot.py params.py in_data/
```

This places all required files in your working directory without switching branches. Keep them in your local `.gitignore` to avoid committing them.

Output is written to `out_data/data/simulated_df.csv`.

## Usage

```bash
# 1. Run simulation
python simulate_current.py

# 2. Plot one sensor
python plot_currents.py --sensor VL02_CT

# 3. Overview plot for all sensors
python plot_currents.py --all-sensors

# List available sensors
python plot_currents.py --list-sensors
```
