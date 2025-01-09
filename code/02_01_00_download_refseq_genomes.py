#!/usr/bin/env python
# coding: utf-8

# In[2]:


import os
import pandas as pd
import urllib.request
from tqdm import tqdm
from joblib import Parallel, delayed
import hashlib
import numpy as np
import dask.dataframe as dd


# In[2]:


def download_genome(row, faa_dir, ft_dir, gff_dir):
    path = row['ftp_path']
    prot_stub = path.split('/')[-1]
    prot_file = prot_stub + '_protein.faa.gz'
    ft_file = prot_stub + '_feature_table.txt.gz'
    gff_file = prot_stub + '_genomic.gff.gz'
    try:
        urllib.request.urlretrieve(path + '/' + prot_file, faa_dir + prot_file)
        urllib.request.urlretrieve(path + '/' + ft_file, ft_dir + ft_file)
        urllib.request.urlretrieve(path + '/' + gff_file, gff_dir + gff_file)
    except:
        print('Excepted for ' + path + '/' + prot_file)


def unzip_file(file):
    os.system('gunzip ' + file)


def encode_protein(p):
    return hashlib.sha224(p.encode('utf-8')).hexdigest()


def process_seq(seq, name, assembly, f):
    seq_id = encode_protein(seq)
    print(','.join([name, seq_id, seq, assembly]), file=f)


def process_faa_file(faa_dir, faa_file, out_dir):
    assembly = faa_file.split('.')[0]
    with open(out_dir + assembly + '.csv', 'w') as f:
        seq = ''
        for line in open(faa_dir + faa_file, 'r'):
            if '>' in line:
                if seq:
                    process_seq(seq, name, assembly, f)
                    seq = ''
                name = line.split(' ')[0][1:]
            else:
                seq += line.strip()
        process_seq(seq, name, assembly, f)


def process_unique_split(out_dir, unique_seq_df, i):
    with open(out_dir + str(i) + '.faa', 'w') as f:
        for _, row in unique_seq_df.iterrows():
            print('>' + row['seq_id'], file=f)
            print(row['seq'], file=f)


# In[4]:


faa_dir = '../data/genome_downloads/faa/'
ft_dir = '../data/genome_downloads/ft/'
gff_dir = '../data/genome_downloads/gff/'
seq_assembly_dir = '../data/interim/seq_assemblies/'
unique_seq_dir = '../data/interim/unqiue_seqs/'
if os.path.exists(faa_dir):
    os.system('rm -r ' + faa_dir)
os.mkdir(faa_dir)
if os.path.exists(ft_dir):
    os.system('rm -r ' + ft_dir)
os.mkdir(ft_dir)
if os.path.exists(gff_dir):
    os.system('rm -r ' + gff_dir)
os.mkdir(gff_dir)
genome_summary_df = pd.read_table('https://ftp.ncbi.nlm.nih.gov/genomes/refseq/assembly_summary_refseq.txt',
                                  header=1)
tax_id_df = pd.read_table('../data/raw/ncbi_tax_categories.txt', names=['domain', 'species_taxid', 'taxid'])
merged_genome_summary_df = (genome_summary_df.merge(tax_id_df, how='inner', on=['taxid', 'species_taxid']))


# In[12]:


filtered_genome_summary_df = (merged_genome_summary_df[merged_genome_summary_df['domain'].isin(['A', 'B', 'V']) &
                                                       (merged_genome_summary_df['refseq_category']
                                                        .isin(['representative genome', 'reference genome']))])
ecor22_assembly = merged_genome_summary_df[merged_genome_summary_df['# assembly_accession'] == 'GCF_003334115.1']
filtered_genome_summary_df = pd.concat([filtered_genome_summary_df, ecor22_assembly], 
                                       axis=0)
filtered_genome_summary_df.shape


# In[13]:


filtered_genome_summary_df['domain'].value_counts()


# In[ ]:


print('Downloading data')
_ = Parallel(n_jobs=32)(delayed(download_genome)(row, faa_dir, ft_dir, gff_dir) for _, row in tqdm(
    filtered_genome_summary_df.iterrows(), total=len(filtered_genome_summary_df)))


# In[15]:


print('Unzipping faa files')
faa_files = [file for file in os.listdir(faa_dir) if '.gz' in file]
_ = Parallel(n_jobs=32)(delayed(unzip_file)(faa_dir + f) for f in tqdm(faa_files))


# In[16]:


print('Unzipping feature table files')
ft_files = [file for file in os.listdir(ft_dir) if '.gz' in file]
_ = Parallel(n_jobs=32)(delayed(unzip_file)(ft_dir + f) for f in tqdm(ft_files))


# In[17]:


print('Unzipping gff files')
gff_files = [file for file in os.listdir(gff_dir) if '.gz' in file]
_ = Parallel(n_jobs=32)(delayed(unzip_file)(gff_dir + f) for f in tqdm(gff_files))


# In[18]:


print('Deduplicating fasta files')
faa_files = [file for file in os.listdir(faa_dir) if '.faa' in file]
os.system('mkdir ' + seq_assembly_dir)
_ = Parallel(n_jobs=32)(delayed(process_faa_file)(faa_dir, faa_file, seq_assembly_dir) for faa_file in tqdm(faa_files))
os.system('cat ' + seq_assembly_dir + '*.csv > ../data/interim/seq_assemblies.csv')
os.system('rm -r ' + seq_assembly_dir)

