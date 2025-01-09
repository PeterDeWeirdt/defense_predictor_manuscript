#!/bin/bash

#SBATCH --exclusive
#SBATCH -o 13_01_03_01_query_filt_1_seqs.sh.log-%j
#SBATCH -c 40
#SBATCH --gres=gpu:volta:1
#SBATCH --time=48:00:00

# Loading the required module
source /etc/profile

bash -c "echo \"PATH inside environment: \${PATH}\""

msa_dir='../data/interim/pd_filt_1_msas/'
raw_out_dir='../data/interim/pd_filt_1_msas_self_alignments/'
parsed_out_file='../data/interim/pd_filt_1_msas_self_hhblits_results.csv'

conda run -n hhpred python ~/Documents/hhpred/code/hhpred.py "$raw_out_dir" \
 "$parsed_out_file" --dbs pd_filt_1 --input_a3m_dir "$msa_dir" \
 --n_jobs 40
