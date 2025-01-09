#!/bin/bash

# SBATCH --exclusive
# SBATCH -o 13_01_02_01_query_prefilt_seqs.sh.log-%j
# SBATCH -c 40
# SBATCH --gres=gpu:volta:1
# SBATCH --time=48:00:00

# Loading the required module
source /etc/profile

bash -c "echo \"PATH inside environment: \${PATH}\""

out_prefilt_pd_seqs='../data/interim/ecor_pd_seqs_prefilt.faa'
msa_out_dir='../data/interim/pd_prefilt_msas/'
raw_out_dir='../data/interim/pd_prefilt_pfam_innate_df_alignments/'
parsed_out_file='../data/interim/pd_prefilt_pfam_innate_df_domains.csv'

conda run -n hhpred python ~/Documents/hhpred/code/hhpred.py "$raw_out_dir" \
 "$parsed_out_file" --dbs pfam innate df --in_fasta "$out_prefilt_pd_seqs" \
 --n_iter 2 --alignment_dir "$msa_out_dir" --n_jobs 40 --reuse_msas
