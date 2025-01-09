#!/bin/bash

#SBATCH --exclusive
#SBATCH -o 11_03_00_submit_build_beaker.sh.log-%j
#SBATCH -c 48
#SBATCH --time=48:00:00

# Loading the required module
source /etc/profile
module load anaconda/2023a

source /state/partition1/llgrid/pkg/anaconda/anaconda3-2023a/etc/profile.d/conda.sh
conda run -n beaker bash -c "echo \"PATH inside environment: \${PATH}\""

# Run the script
conda run -n beaker python 11_03_00_build_beaker.py
