#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os


# In[2]:


target_db = '../data/interim/mmseqs_working_dir/unique_seqs_db'
out_db = '../data/interim/mmseqs_working_dir/unique_seqs_db_clust_mode1'
out_tsv = '../data/interim/refseqs_clusters_mode1.tsv'
threads = str(48)


# In[3]:


os.system('mmseqs linclust ' + target_db + ' ' +
          out_db + ' ' +
          '../data/tmp ' +
          '-c 0.8 '
          '--min-seq-id 0.3 '
          '--threads ' + threads + ' ' +
          '--cluster-mode 1')  # connected component (BLAST)


# In[4]:


os.system('mmseqs createtsv ' + target_db + ' ' +
          target_db + ' ' +
          out_db + ' ' +
          out_tsv)

