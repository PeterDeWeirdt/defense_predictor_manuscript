#!/bin/bash

#SBATCH --exclusive
#SBATCH -o 07_03_05_query_foldseek.log-%j
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
    search ../data3/interim/foldseek_dbs/padded_model_seqs_prostt5 ../data3/interim/foldseek_dbs/padded_model_seqs_prostt5 \
    ../data3/interim/foldseek_dbs/model_model_search $TMPDIR --gpu 1 --max-seqs 5000

conda run -n nvcc /home/gridsan/pdeweirdt/Documents/foldseek/build/bin/foldseek \
    convertalis ../data3/interim/foldseek_dbs/padded_model_seqs_prostt5 \ 
    ../data3/interim/foldseek_dbs/padded_model_seqs_prostt5 \ 
    ../data3/interim/foldseek_dbs/model_model_search \
    ../data3/interim/foldseek_model_search.txt
