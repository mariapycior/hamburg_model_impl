#!/bin/bash
cd /home/maria/magisterka/hamburg_new
if [ ! -f config.py ]; then
    git show fa2e846^:config.py > config.py 2>/dev/null || true
fi
if [ ! -f config_plot.py ]; then
    git show fa2e846^:config_plot.py > config_plot.py 2>/dev/null || true
fi
if [ ! -f params.py ]; then
    git show fa2e846^:params.py > params.py 2>/dev/null || true
fi
