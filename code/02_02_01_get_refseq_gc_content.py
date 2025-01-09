#!/usr/bin/env python
# coding: utf-8
# %%

# %%


import pandas as pd
import os
import urllib
import re
from joblib import Parallel, delayed
from tqdm import tqdm


# %%

def get_motifs(fna_file, assemblies_dir, out_dir, motifs):
    assembly = fna_file.split('.')[0]
    seq = ''
    seq_list = []
    seq_info = dict()
    for line in open(assemblies_dir + fna_file):
        line = line.strip()
        if '>' in line:
            if seq:
                seq_info['seq'] = seq
                seq_list.append(seq_info)
                seq_info = dict()
                seq = ''
            seq_info['id'] = line.split(' ')[0][1:]
            regex = '\[([^=]+)=([^=]+)\]'
            attributes = re.findall(regex, line)
            for key, value in attributes:
                seq_info[key] = value
        else:
            seq += line
    seq_info['seq'] = seq
    seq_list.append(seq_info)
    seq_df = pd.DataFrame(seq_list)
    if 'pseudo' in seq_df.columns:
        filtered_seq_df = seq_df[seq_df['pseudo'].isna()].copy()
    else:
        filtered_seq_df = seq_df
    filtered_seq_df['strand'] = ['-' if x else '+' for x in filtered_seq_df['location'].str.contains('complement')]
    filtered_seq_df['start'] = filtered_seq_df['location'].str.extract('([0-9]+)\.\.').astype(int)
    filtered_seq_df['end'] = filtered_seq_df['location'].str.extract('[\.\.|\>]([0-9]+)').astype(int)
    filtered_seq_df['genomic_locus'] = filtered_seq_df['id'].str.extract('lcl\|(.+)_cds')
    filtered_seq_df['gc_frac'] = filtered_seq_df['seq'].str.count('G|C')/filtered_seq_df['seq'].str.len()
    filtered_seq_df['scaled_gc_frac'] = ((filtered_seq_df['gc_frac'] - filtered_seq_df['gc_frac'].mean())/
                                         filtered_seq_df['gc_frac'].std())
    filtered_seq_df['assembly'] = assembly
    out_cols = ['assembly', 'genomic_locus', 'protein_id', 'start', 'end', 'strand', 'gc_frac', 'scaled_gc_frac']
    for motif in motifs:
        col = motif + '_frac'
        filtered_seq_df[col] = filtered_seq_df['seq'].str.count(motif)/filtered_seq_df['seq'].str.len()
        out_cols.append(col)
    for motif in motifs:
        col = 'scaled_' + motif + '_frac'
        unscaled_col = motif + '_frac'
        filtered_seq_df[col] = ((filtered_seq_df[unscaled_col] - filtered_seq_df[unscaled_col].mean())/
                                         filtered_seq_df[unscaled_col].std())
        out_cols.append(col)
    filtered_seq_df = filtered_seq_df[out_cols]
    filtered_seq_df.to_csv(out_dir + assembly + '.csv', index=False, header=False)

# %%

assemblies_dir = '../data/genome_downloads/fna/'
gc_dir = '../data/interim/refseq_gc_frac/'


# %%


os.mkdir(gc_dir)

# %%

nts = ['A', 'C', 'T', 'G']
di_nts = []
for n1 in nts:
    for n2 in nts:
        di_nts.append(n1 + n2)
motifs = nts + di_nts

# %%


print('calculating GC content')
_ = Parallel(n_jobs=48)(delayed(get_motifs)(fna_file, assemblies_dir, gc_dir, motifs) 
                        for fna_file in tqdm([x for x in os.listdir(assemblies_dir) if '.fna' in x], 
                                             position=0))


# %%


out_gc = '../data/interim/refseq_gc_content.csv'


# %%


os.system(' '.join(['cat', gc_dir + '/*.csv', '>', out_gc]))


# %%


os.system('rm -r '+ gc_dir)


# %%




