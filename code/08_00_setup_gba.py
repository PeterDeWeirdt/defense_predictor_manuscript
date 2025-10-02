#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
from joblib import Parallel, delayed
import os
from tqdm import tqdm


# In[57]:


def get_defense_neighbors(assembly, ft_f, curr_defense, curr_cluster):
    try:
        feature_table = pd.read_table(ft_f)
        feature_table['attributes'] = feature_table['attributes'].astype(str)
        filtered_feature_table = (feature_table[(feature_table['# feature'] == 'CDS') &
                                                ~(feature_table['attributes'].str.contains('pseudo', na=False))]
                                  .reset_index(drop=True))
        filtered_feature_table['genome'] = filtered_feature_table['assembly'].str.split('.', expand=True)[0]
        filtered_feature_table['protein_context_id'] = (filtered_feature_table['product_accession'] + '|' +
                                                        filtered_feature_table['genomic_accession'] + '|' +
                                                        filtered_feature_table['start'].astype(str) + '|' +
                                                        filtered_feature_table['strand'])
        defense_feature_table = (filtered_feature_table.reset_index()
                             .merge(curr_defense, how='inner', 
                                    on='product_accession')
                                    .set_index('index'))
        cluster_feature_table = (filtered_feature_table
                             .reset_index()
                             .merge(curr_cluster, how='inner', 
                                    on='product_accession')
                             .set_index('index'))
        hit_list = list()
        for system, system_df in defense_feature_table.groupby('sys_id'):
            for i, defense_row in system_df.iterrows():
                near_cluster = cluster_feature_table.loc[cluster_feature_table
                                                         .index
                                                         .to_series()
                                                         .between(i-max_dist, i+max_dist), :]
                near_cluster = near_cluster.loc[~near_cluster.index.isin(system_df.index), :] # remove self system
                for _, cluster_row in near_cluster.iterrows():
                    hit_list.append({'seq_id': cluster_row['seq_id'], 
                                     'cluster_id': cluster_row['cluster_id'], 
                                     'assembly': assembly, 
                                     'defense_neighbor': defense_row['gene_name']})
        hit_df = pd.DataFrame(hit_list)    
        return hit_df
    except:
        print('Excepted for ' + assembly)


# In[3]:


model_seq_info = pd.read_parquet('../data3/interim/model_seq_info.pq')
clusters = pd.read_parquet('../data3/interim/refseq_cover_clusters.pq')
defense_finder_genes_genomes = (pd.read_parquet('../data/interim/defense_finder_genes_genomes.pq')
                                .rename(columns={'protein_accession': 'product_accession'})
                                .set_index('genome'))


# In[8]:


seq_assemblies = (pd.read_csv('../data/interim/seq_assemblies.csv', 
                             names=['product_accession', 'seq_id', 'seq', 'assembly_stub'])
                  .drop(columns=['seq']))


# In[10]:


model_cluster_df = clusters[clusters['cluster_id'].isin(model_seq_info['seq_id'])]


# In[12]:


assert model_cluster_df['cluster_id'].nunique() == len(model_seq_info)


# In[13]:


model_cluster_seq_assemblies = (seq_assemblies.merge(model_cluster_df, how='inner', 
                                                     on='seq_id')
                                .set_index('assembly_stub'))


# In[ ]:


del seq_assemblies


# In[21]:


cluster_relevant_genomes = set(model_cluster_seq_assemblies.index.unique())


# In[20]:


defense_relevant_genomes = set(defense_finder_genes_genomes.index.unique())


# In[17]:


ft_dir = '../data/genome_downloads/ft/'
max_dist = 10


# In[22]:


ft_files = {x.split('.')[0]: os.path.join(ft_dir, x) for x in tqdm(os.listdir(ft_dir), position=0) 
            if ('.txt' in x) & (x.split('.')[0] in cluster_relevant_genomes) & 
            (x.split('.')[0] in defense_relevant_genomes)}


# In[23]:


print(len(ft_files))


# In[61]:


defense_neighbor_list = Parallel(n_jobs=48)(delayed(get_defense_neighbors)
                                            (assembly, ft_f, 
                                             defense_finder_genes_genomes.loc[[assembly], :], 
                                             model_cluster_seq_assemblies.loc[[assembly], :]) 
                                            for assembly, ft_f in tqdm(ft_files.items(), position=0))


# In[62]:


defense_neighbor_df = pd.concat(defense_neighbor_list)


# In[63]:


defense_neighbor_df.to_parquet('../data3/interim/model_cluster_defense_neighbors.pq', index=False)
model_cluster_seq_assemblies.to_parquet('../data3/interim/model_cluster_assemblies.pq')


# In[ ]:




