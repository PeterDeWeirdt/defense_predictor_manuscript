#!/bin/bash

#SBATCH --exclusive
#SBATCH -o 07_03_get_model_seq_db.log-%j
#SBATCH -c 40
#SBATCH --gres=gpu:volta:1 
#SBATCH --time=48:00:00

# Loading the required module
source /etc/profile
module load anaconda/2023a

source /state/partition1/llgrid/pkg/anaconda/anaconda3-2023a/etc/profile.d/conda.sh
conda run -n beaker bash -c "echo \"PATH inside environment: \${PATH}\""

# Run the script
export CUDA_VISIBLE_DEVICES=0,1
conda run -n nvcc /home/gridsan/pdeweirdt/Documents/foldseek/build/bin/foldseek \
    createdb ../data3/interim/model_seqs.faa ../data3/interim/foldseek_dbs/model_seqs_prostt5 \
    --prostt5-model /home/gridsan/pdeweirdt/prostt5_weights/ --gpu 1

