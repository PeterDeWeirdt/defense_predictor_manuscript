#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import os
from tqdm import tqdm

if __name__ == '__main__':
    cluster_merged_preds = pd.read_csv('../data3/interim/ecor_predictions.csv')
    putative_novel_ids = cluster_merged_preds.loc[~cluster_merged_preds['defense_homolog'] & 
                                                  (cluster_merged_preds['mean_log_odds'] > 0), 
                                                  'product_accession'].drop_duplicates()
    print(len(putative_novel_ids))
    putative_novel_id_f = '../data3/interim/ecor_putative_novel_ids.txt'
    putative_novel_ids.to_csv(putative_novel_id_f, index=False)
    putative_novel_seq_f = '../data3/interim/ecor_putative_novel_seqs.faa'
    os.system(' '.join(['conda run -n beaker', 
                        'seqtk subseq',
                        '../data/interim/ecor_unique_seqs.faa', 
                        putative_novel_id_f, '>',
                        putative_novel_seq_f]))
    msa_out_dir = '../data3/interim/ecor_putative_novel_msas/'
    if not os.path.exists(msa_out_dir):
        os.mkdir(msa_out_dir)
    old_msa_dir = '../data/interim/ecor_putative_novel_msas2/'
    old_msas = [x for x in os.listdir(old_msa_dir) if '.a3m' in x]
    novel_id_stubs = putative_novel_ids.str.split('\.', expand=True)[0].to_list()
    for f in tqdm(old_msas):
        if f.split('.')[0] in novel_id_stubs:
            os.system(' '.join(['cp', old_msa_dir + f, msa_out_dir]))
    raw_out_dir ='../data3/interim/ecor_putative_novel_pfam_df_alignments/'
    parsed_out_file='../data3/interim/ecor_putative_novel_pfam_df_domains.csv'
    os.system(' '.join(['conda run -n hhpred python', 
                        '~/Documents/hhpred/code/hhpred.py', 
                        '--raw_out_dir', raw_out_dir,  
                        '--parsed_out_file', parsed_out_file, 
                        '--dbs pfam df2', 
                        '--in_fasta', putative_novel_seq_f,  
                        '--n_iter 3', 
                        '--alignment_dir', msa_out_dir, 
                        '--n_jobs 40']))

