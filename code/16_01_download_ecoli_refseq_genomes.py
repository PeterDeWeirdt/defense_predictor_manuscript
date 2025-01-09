#!/usr/bin/env python
# coding: utf-8
# %%

# %%


import pandas as pd
import urllib.request
from tqdm import tqdm
from joblib import Parallel, delayed
import os

# %%


def download_genome(row, faa_dir, ft_dir, fna_dir):
    path = row['ftp_path']
    prot_stub = path.split('/')[-1]
    prot_file = prot_stub + '_protein.faa.gz'
    ft_file = prot_stub + '_feature_table.txt.gz'
    fna_file = prot_stub + '_cds_from_genomic.fna.gz'
    try:
        urllib.request.urlretrieve(path + '/' + prot_file, faa_dir + prot_file)
        urllib.request.urlretrieve(path + '/' + ft_file, ft_dir + ft_file)
        urllib.request.urlretrieve(path + '/' + fna_file, fna_dir + fna_file)
    except:
        print('Excepted for ' + path)
        

# %%


faa_dir = '../data/ecoli/raw/faa/'
if os.path.exists(faa_dir):
    os.system('rm -r ' + faa_dir)
os.mkdir(faa_dir)

ft_dir = '../data/ecoli/raw/ft/'
if os.path.exists(ft_dir):
    os.system('rm -r ' + ft_dir)
os.mkdir(ft_dir)

fna_dir = '../data/ecoli/raw/fna/'
if os.path.exists(fna_dir):
    os.system('rm -r ' + fna_dir)
os.mkdir(fna_dir)

genome_summary_df = pd.read_csv('../data/ecoli/interim/ecoli_1000_refseq_assemblies.csv')
print(genome_summary_df.shape)

print('Downloading data')
_ = Parallel(n_jobs=32)(delayed(download_genome)(row, faa_dir, ft_dir, fna_dir) for _, row in tqdm(
    genome_summary_df.iterrows(), total=len(genome_summary_df)))

