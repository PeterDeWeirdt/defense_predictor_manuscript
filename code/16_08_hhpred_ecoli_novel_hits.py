#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import os
from tqdm import tqdm

if __name__ == '__main__':
    putative_novel_seq_f = '../data/ecoli/interim/selected_novel_seqs.faa'
    msa_out_dir = '../data/ecoli/interim/ecoli_putative_novel_msas/'
    if 'ecoli_putative_novel_msas' not in os.listdir('../data/ecoli/interim/'):
        os.mkdir(msa_out_dir)
    raw_out_dir ='../data/ecoli/interim/ecoli_putative_novel_hhdb_alignments/'
    parsed_out_file='../data/ecoli/interim/ecoli_putative_novel_hhdb_domains.csv'
    os.system(' '.join(['conda run -n hhpred python', 
                        '~/Documents/hhpred/code/hhpred.py', 
                        '--raw_out_dir', raw_out_dir,  
                        '--parsed_out_file', parsed_out_file, 
                        '--dbs pfam df innate', 
                        '--in_fasta', putative_novel_seq_f,  
                        '--n_iter 2', 
                        '--alignment_dir', msa_out_dir, 
                        '--n_jobs 40']))

