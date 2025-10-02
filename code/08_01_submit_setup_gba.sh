#!/bin/bash

#SBATCH --exclusive
#SBATCH -o 08_02_setup_gba.log-%j
#SBATCH -c 48
#SBATCH --time=48:00:00

# Loading the required module
source /etc/profile
module load anaconda/2023a

source /state/partition1/llgrid/pkg/anaconda/anaconda3-2023a/etc/profile.d/conda.sh
conda run -n beaker bash -c "echo \"PATH inside environment: \${PATH}\""

# Run the script
conda run -n beaker python 08_00_setup_gba.py
