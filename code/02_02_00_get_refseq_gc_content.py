#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import os
import urllib
import re
from joblib import Parallel, delayed
from tqdm import tqdm


# In[19]:


def unzip_file(file):
    os.system('gunzip ' + file)


# In[20]:


def download_cds_fna(row, out_dir):
    path = row['ftp_path']
    prot_stub = path.split('/')[-1]
    fna_file = prot_stub + '_cds_from_genomic.fna.gz'
    try:
        urllib.request.urlretrieve(path + '/' + fna_file, out_dir + fna_file)
        unzip_file(out_dir + fna_file)
    except:
        print('Excepted for ' + path + '/' + fna_file)


# In[2]:


genome_summary_df = pd.read_table('https://ftp.ncbi.nlm.nih.gov/genomes/refseq/assembly_summary_refseq.txt',
                                  header=1)
tax_id_df = pd.read_table('../data/raw/ncbi_tax_categories.txt', names=['domain', 'species_taxid', 'taxid'])
merged_genome_summary_df = (genome_summary_df.merge(tax_id_df, how='inner', on=['taxid', 'species_taxid']))


# We're missing a few genomes in the month or so between we ran notebook 01. Will have to take this into consideration when building model data

# In[3]:


filtered_genome_summary_df = (merged_genome_summary_df[merged_genome_summary_df['domain'].isin(['A', 'B', 'V']) &
                                                       (merged_genome_summary_df['refseq_category']
                                                        .isin(['representative genome', 'reference genome']))])
ecor22_assembly = merged_genome_summary_df[merged_genome_summary_df['# assembly_accession'] == 'GCF_003334115.1']
filtered_genome_summary_df = pd.concat([filtered_genome_summary_df, ecor22_assembly], 
                                       axis=0)
filtered_genome_summary_df.shape


# In[2]:


assemblies_dir = '../data/genome_downloads/fna/'


# In[ ]:


os.mkdir(assemblies_dir)


# In[24]:


print('Downloading nucleotide sequences')
_ = Parallel(n_jobs=32)(delayed(download_cds_fna)(row, assemblies_dir) for _, row in tqdm(
    filtered_genome_summary_df.iterrows(), total=len(filtered_genome_summary_df), position=0))

