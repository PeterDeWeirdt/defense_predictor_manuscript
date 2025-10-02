#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import os


# In[3]:


model_seq_info = pd.read_parquet('../data3/interim/candidate_model_seq_info.pq')


# In[8]:


model_seq_info['short_seq_id'] = model_seq_info['seq_id'].str[:50]


# In[9]:


short_model_seq_f = '../data3/interim/short_id_candidate_model_seqs.faa'


# In[10]:


with open(short_model_seq_f, 'w') as f:
    for _, row in model_seq_info.iterrows():
        print('>' + row['short_seq_id'], file=f)
        print(row['seq'], file=f)


# In[11]:


tmp_model_seq_f = '$TMPDIR/short_id_model_seqs.faa'


# In[12]:


os.system(' '.join(['cp', short_model_seq_f, tmp_model_seq_f]))


# In[13]:


tmp_model_seq_db = '$TMPDIR/model_seqs'


# In[14]:


os.system(' '.join(['conda run -n blast', 
                    'makeblastdb', 
                    '-in', tmp_model_seq_f, 
                    '-dbtype prot', 
                    '-out', tmp_model_seq_db]))


# In[15]:


tmp_blast_search_out = '$TMPDIR/model_seq_blast_search.csv'


# In[17]:


os.system(' '.join(['conda run -n blast blastp',
                    '-db', tmp_model_seq_db, 
                    '-query', tmp_model_seq_f, 
                    '-out', tmp_blast_search_out, 
                    '-outfmt 10',
                    '-num_threads 48']))


# In[ ]:


os.system(' '.join(['cp', tmp_blast_search_out, '../data3/interim/']))

