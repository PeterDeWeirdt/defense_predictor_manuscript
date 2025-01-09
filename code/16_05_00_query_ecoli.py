#!/usr/bin/env python
# coding: utf-8

# In[12]:


import pandas as pd
import os
import tqdm
from predict import predict_beaker
from tqdm import tqdm


# In[20]:


selected_assemblies = [x.split('.')[0] for x in 
                       (pd.read_csv('../data/ecoli/interim/ecoli_3000_refseq_assemblies.csv')
                       ['#assembly_accession'].to_list())]


# In[32]:


n_feats = 640
feat_names = ['ft' + str(i + 1) for i in range(n_feats)]
rep_file = '../data/ecoli/interim/ecoli_reps.csv'
rep_df = pd.read_csv(rep_file, index_col=0, names=feat_names)


# In[10]:


prediction_out_dir = '../data/ecoli/processed/ecoli_predictions/'


# In[11]:


if 'ecoli_predictions' not in os.listdir('../data/ecoli/processed'):
    os.mkdir(prediction_out_dir)


# In[26]:


ft_dir = '../data/ecoli/raw/ft/'
feature_file_dict = {x.split('.')[0]: ft_dir + x for x in os.listdir(ft_dir)
                     if x.split('.')[0] in selected_assemblies}


# In[27]:


fna_dir = '../data/ecoli/raw/fna/'
fna_file_dict = {x.split('.')[0]: fna_dir + x for x in os.listdir(fna_dir)
                 if x.split('.')[0] in selected_assemblies}


# In[33]:


for assembly in tqdm(selected_assemblies, position=0):
    feature_file = feature_file_dict[assembly]
    fna_file = fna_file_dict[assembly]
    predict_beaker(feature_file, fna_file, 
                   model_representations=rep_df,
                   n_jobs=48, 
                   output_dir=prediction_out_dir)
    

