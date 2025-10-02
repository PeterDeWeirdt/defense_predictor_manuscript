#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import os
from tqdm import tqdm

if __name__ == '__main__':
    putative_novel_seq_f = '../data3/interim/refseq_1k_putative_novel_seqs.faa'
    msa_out_dir = '../data3/interim/refseq_1k_putative_novel_msas/'
    if not os.path.exists(msa_out_dir):
        os.mkdir(msa_out_dir)
    raw_out_dir ='../data3/interim/refseq_1k_putative_novel_pfam_df_alignments/'
    parsed_out_file='../data3/interim/refseq_1k_putative_novel_pfam_df_domains.csv'
    os.system(' '.join(['conda run -n hhpred python', 
                        '~/Documents/hhpred/code/hhpred.py', 
                        '--raw_out_dir', raw_out_dir,  
                        '--parsed_out_file', parsed_out_file, 
                        '--dbs pfam df2', 
                        '--in_fasta', putative_novel_seq_f,  
                        '--n_iter 3', 
                        '--alignment_dir', msa_out_dir, 
                        '--n_jobs 40']))

