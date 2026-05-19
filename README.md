# data branch

This branch contains input data and configuration files for the Hamburg model simulation. It has no code — checkout individual files from here into your working branch.

## Contents

```
config.py                              # paths, NTC, luminosity type, simulation period
config_plot.py                         # plot display options
params.py                              # Hamburg model parameters
in_data/
├── fluence/avgFluenceBinned_10T_74_80.csv
├── lumi/lumi_binned.csv
├── current/  2011_current.csv, 2012_current.csv, ls1_current.csv,
│             2016_current.csv, 2017_current.csv, 2018_current.csv
└── temperature/  temperature_10T_2011.csv … temperature_10T_2018.csv
```

## Usage

After cloning the repository, run this once to get the files:

```bash
git checkout origin/data -- config.py config_plot.py params.py in_data/
```

Files will appear in your working directory without switching branches. Add them to your local `.gitignore` to avoid committing them.
