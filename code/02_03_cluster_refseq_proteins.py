#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os


# In[2]:


target = '../data/interim/unique_seqs.faa'
target_db = '../data/interim/mmseqs_working_dir/unique_seqs_db'
out_db = '../data/interim/mmseqs_working_dir/unique_seqs_db_clust'
out_tsv = '../data/interim/refseqs_clusters.tsv'
threads = str(48)


# In[ ]:


print('Creating Target Database')
os.system('mmseqs createdb ' + target + ' ' + target_db + ' --dbtype 1')


# In[ ]:


print('Creating Index for Target Database')
os.system('mmseqs createindex ' + target_db + ' ../data/tmp')


# In[3]:


os.system('mmseqs linclust ' + target_db + ' ' +
          out_db + ' ' +
          '../data/tmp ' +
          '-c 0.8 '
          '--min-seq-id 0.3 '
          '--threads ' + threads + ' ' +
          '--cluster-mode 0')  # greedy set-cover


# In[4]:


os.system('mmseqs createtsv ' + target_db + ' ' +
          target_db + ' ' +
          out_db + ' ' +
          out_tsv)

