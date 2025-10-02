#!/usr/bin/env python
# coding: utf-8
# %%

# %%


import os


# %%


target_db = '../data/interim/mmseqs_working_dir/unique_seqs_db'
out_db = '../data3/interim/unique_seqs_db_cover'
out_tsv = '../data3/interim/refseq_cover_clusters.tsv'


# %%

os.system(' '.join(['mmseqs cluster', 
                    target_db,
                    out_db, 
                    '../data/tmp',
                    '-c 0.8', 
                    '--cov-mode 0',
                    '--min-seq-id 0.3', 
                    '--threads 48',
                    '--cluster-mode 0', 
                    '-s 6']))


# %%


os.system(' '.join(['mmseqs createtsv',
                    target_db,
                    target_db, 
                    out_db,
                    out_tsv]))

