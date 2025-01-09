#!/usr/bin/env python
# coding: utf-8
# %%

# %%


import pandas as pd
import os
import urllib
from joblib import Parallel, delayed
from tqdm import tqdm


# ## Download genomes and sequences

# %%

def unzip_file(file):
    os.system('gunzip ' + file)
    
    
def download_genome(row, out_dir):
    path = row['ftp_path']
    prot_stub = path.split('/')[-1]
    genome_file = prot_stub + '_genomic.fna.gz'
    try:
        urllib.request.urlretrieve(path + '/' + genome_file, out_dir + genome_file)
        unzip_file(out_dir + genome_file)
    except:
        print('Excepted for ' + path + '/' + genome_file)

# %%


genome_summary_df = pd.read_table('https://ftp.ncbi.nlm.nih.gov/genomes/refseq/assembly_summary_refseq.txt',
                                  header=1)

# %%


vassallo_strains = pd.read_csv('../data/raw/vassallo_strains.csv', names=['assembly'])

# %%

possible_pathogenic_assemblies = ['GCF_003333865.1', 'GCF_003334065.1']
vassallo_assemblies = [x for x in vassallo_strains['assembly'].to_list() if x not in possible_pathogenic_assemblies]
vassallo_genome_summary_df = (genome_summary_df[genome_summary_df['#assembly_accession']
                                                .isin(vassallo_assemblies)]
                              .reset_index(drop=True))


# %%


assemblies_dir = '../data/interim/ecor_genomic/'


# %%


if 'ecor_genomic' in os.listdir('../data/interim'):
    os.system('rm -r ' + assemblies_dir)
os.mkdir(assemblies_dir)


# %%


print('Downloading data')
_ = Parallel(n_jobs=4)(delayed(download_genome)(row, assemblies_dir) for _, row in tqdm(
    vassallo_genome_summary_df.iterrows(), total=len(vassallo_genome_summary_df)))


# %%




