#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import os
import urllib
from joblib import Parallel, delayed
from tqdm import tqdm


# ## Download genomes and sequences

# In[2]:

def unzip_file(file):
    os.system('gunzip ' + file)
    
    
def download_genome(row, out_dir):
    path = row['ftp_path']
    prot_stub = path.split('/')[-1]
    prot_file = prot_stub + '_protein.faa.gz'
    ft_file = prot_stub + '_feature_table.txt.gz'
    try:
        urllib.request.urlretrieve(path + '/' + prot_file, out_dir + prot_file)
        urllib.request.urlretrieve(path + '/' + ft_file, out_dir + ft_file)
    except:
        print('Excepted for ' + path + '/' + prot_file)

            
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

# In[3]:


vassallo_strains = pd.read_csv('../data/raw/vassallo_strains.csv', names=['assembly'])

# In[4]:

possible_pathogenic_assemblies = ['GCF_003333865.1', 'GCF_003334065.1']
vassallo_assemblies = [x for x in vassallo_strains['assembly'].to_list() if x not in possible_pathogenic_assemblies]
vassallo_genome_summary_df = (genome_summary_df[genome_summary_df['#assembly_accession']
                                                .isin(vassallo_assemblies)]
                              .reset_index(drop=True))


# In[18]:


assemblies_dir = '../data/interim/ecor_assemblies/'


# In[13]:


if 'ecor_assemblies' in os.listdir('../data/interim'):
    os.system('rm -r ' + assemblies_dir)
os.mkdir(assemblies_dir)


# In[22]:


print('Downloading data')
_ = Parallel(n_jobs=4)(delayed(download_genome)(row, assemblies_dir) for _, row in tqdm(
    vassallo_genome_summary_df.iterrows(), total=len(vassallo_genome_summary_df)))


# In[9]:


print('Downloading nucleotide sequences')
_ = Parallel(n_jobs=4)(delayed(download_cds_fna)(row, assemblies_dir) for _, row in tqdm(
    vassallo_genome_summary_df.iterrows(), total=len(vassallo_genome_summary_df)))


# In[ ]:




