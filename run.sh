#!/bin/bash
sudo python3 scripts/run_cpu_micro.py
# if results dir exists, chown to user
sudo chown -R $USER:$USER results
python3 scripts/draw.py