#!/bin/bash

#SBATCH --exclusive
#SBATCH -o 17_03_query_refseq_1k.log-%j
#SBATCH -c 48
#SBATCH --time=48:00:00

# Loading the required module
source /etc/profile
module load anaconda/2023a

source /state/partition1/llgrid/pkg/anaconda/anaconda3-2023a/etc/profile.d/conda.sh
conda run -n beaker bash -c "echo \"PATH inside environment: \${PATH}\""

# Run the script
conda run -n beaker python 17_01_query_refseq_1k.py
