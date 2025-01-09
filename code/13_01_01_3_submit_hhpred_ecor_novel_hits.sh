#!/bin/bash

#SBATCH --exclusive
#SBATCH -o 13_01_01_3_submit_hhpred_ecor_novel_hits.sh.log-%j
#SBATCH -c 40
#SBATCH --gres=gpu:volta:1
#SBATCH --time=48:00:00

# Loading the required module
source /etc/profile
module load anaconda/2023a

source /state/partition1/llgrid/pkg/anaconda/anaconda3-2023a/etc/profile.d/conda.sh
conda run -n beaker bash -c "echo \"PATH inside environment: \${PATH}\""

# Run the script
conda run -n beaker python 13_01_01_3_hhpred_ecor_novel_hits.py
