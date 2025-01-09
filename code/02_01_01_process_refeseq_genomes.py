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

def process_unique_split(out_dir, unique_seq_df, i):
    with open(out_dir + str(i) + '.faa', 'w') as f:
        for _, row in unique_seq_df.iterrows():
            print('>' + row['seq_id'], file=f)
            print(row['seq'], file=f)

# In[3]:


seq_assembly_df = pd.read_csv('../data/interim/seq_assemblies.csv',
                              names=['name', 'seq_id', 'seq', 'assembly'])
unique_seq_df = seq_assembly_df[['seq_id', 'seq']].drop_duplicates()
rm_rows = len(seq_assembly_df) - len(unique_seq_df)
print('Removed', rm_rows, 'rows (', rm_rows/len(seq_assembly_df)*100, '%)')


# In[4]:
# Removed 1727415 rows ( 2.5306882474651142 %)

del seq_assembly_df


# We'll write out to parquet for fast querying

# In[ ]:


unique_seq_df.to_parquet('../data/interim/refseq_seq_ids.pq', 
                         index=False)


# In[21]:

unique_seq_dir = '../data/interim/unqiue_seqs/'
print('Writing deduplicated sequences')
os.mkdir(unique_seq_dir)
unique_seq_df = np.array_split(unique_seq_df, 1_000)
Parallel(n_jobs=32)(delayed(process_unique_split)(unique_seq_dir, df, i) for i, df in tqdm(enumerate(unique_seq_df), total=1_000))
os.system('cat ' + unique_seq_dir + '*.faa > ../data/interim/unique_seqs.faa')
os.system('rm -r ' + unique_seq_dir)


# In[ ]:




