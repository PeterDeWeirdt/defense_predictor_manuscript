#!/bin/bash

#SBATCH --exclusive
#SBATCH -o 15_06_01_esmfold_known.log-%j
#SBATCH -c 40
#SBATCH --gres=gpu:volta:1 
#SBATCH --time=48:00:00

# Loading the required module
source /etc/profile
module load cuda/11.8

source /state/partition1/llgrid/pkg/anaconda/anaconda3-2023a/etc/profile.d/conda.sh
conda run -n esmfold3 bash -c "echo \"PATH inside environment: \${PATH}\""


OUTDIR=../data3/interim/df_rep_structures/
if [ ! -d $OUTDIR ]; then
    mkdir -p $OUTDIR
fi

INFASTA=../data3/interim/long_rep_df_full.faa
# Run the script
#source activate esmfold2
# python fold.py -i $INFASTA -o $OUTDIR
nvcc --version
conda run -n esmfold3 python fold.py -i $INFASTA -o $OUTDIR
