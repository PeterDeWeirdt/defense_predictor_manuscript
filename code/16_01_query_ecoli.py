#!/usr/bin/env python
# coding: utf-8
# %%

# %%


import pandas as pd
import os
import tqdm
from predict import defense_predictor
from tqdm import tqdm


# %%


selected_assemblies = [x.split('.')[0] for x in 
                       (pd.read_csv('../data/ecoli/interim/ecoli_3000_refseq_assemblies.csv')
                       ['#assembly_accession'].to_list())]


# %%


n_feats = 640
feat_names = ['ft' + str(i + 1) for i in range(n_feats)]
rep_file = '../data/ecoli/interim/ecoli_reps.csv'
rep_df = pd.read_csv(rep_file, index_col=0, names=feat_names)


# %%


prediction_out_dir = '../data3/interim/ecoli_predictions/'


# %%


if not os.path.exists(prediction_out_dir):
    os.mkdir(prediction_out_dir)
    x_file_dict = None
else:
    X_files = [x for x in os.listdir(prediction_out_dir) if x.endswith('_X.pq')]
    x_file_dict = {x.split('_X')[0]: prediction_out_dir + x for x in X_files}


# %%


ft_dir = '../data/ecoli/raw/ft/'
feature_file_dict = {x.split('.')[0]: ft_dir + x for x in os.listdir(ft_dir)
                     if x.split('.')[0] in selected_assemblies}


# %%


fna_dir = '../data/ecoli/raw/fna/'
fna_file_dict = {x.split('.')[0]: fna_dir + x for x in os.listdir(fna_dir)
                 if x.split('.')[0] in selected_assemblies}

# %%


faa_dir = '../data/ecoli/raw/faa/'
faa_file_dict = {x.split('.')[0]: faa_dir + x for x in os.listdir(faa_dir)
                 if (x.split('.')[0] in selected_assemblies) and (x.endswith('.faa'))}


# %%


for assembly in tqdm(selected_assemblies, position=0):
    feature_file = feature_file_dict[assembly]
    fna_file = fna_file_dict[assembly]
    faa_file = faa_file_dict[assembly]
    if x_file_dict is not None:
        X = pd.read_parquet(x_file_dict[assembly])
        pred_df = pd.read_parquet(os.path.join(prediction_out_dir, assembly + '_predictions.pq'))
        X.index = pred_df['protein_context_id']
    else:
        X = None
    out_df, model_ft_df = defense_predictor(feature_file, fna_file, faa_file, rep_df=rep_df, model_feature_df=X)
    out_df.to_parquet(os.path.join(prediction_out_dir, assembly + '_predictions.pq'), index=False)
    model_ft_df.to_parquet(os.path.join(prediction_out_dir, assembly + '_X.pq'), index=True)


