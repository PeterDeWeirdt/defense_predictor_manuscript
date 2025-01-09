#!/bin/bash
#SBATCH -o submit.sh.log-%j
# Loading Modules
source /etc/profile
conda activate beaker
python 03_00_defensefinder_search.py
