from predict import defense_predictor
import pandas as pd
from tqdm import tqdm
import os
from warnings import warn


if __name__ == '__main__':
    out_dir = '../data3/interim/refseq1k_preds/'
    n_feats = 640
    feat_names = ['ft' + str(i + 1) for i in range(n_feats)]
    ft_dir = '../data/genome_downloads/ft/'
    fna_dir = '../data/genome_downloads/fna/'
    faa_dir = '../data/genome_downloads/faa/'
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
        x_file_dict = None
    else:
        X_files = [x for x in os.listdir(out_dir) if x.endswith('_X.pq')]
        x_file_dict = {x.split('_X')[0]: out_dir + x for x in X_files}
    for sel_assembly_f, rep_file in [('../data/interim/refseq_500_selected_assemblies.csv', 
                                      '../data/interim/refseq_500_reps.csv'),
                                     ('../data/interim/refseq_1k_selected_assemblies.csv', 
                                      '../data/interim/refseq_1k_reps.csv')]:
        selected_assemblies = (pd.read_csv(sel_assembly_f)
                               ['assembly'].to_list())
        rep_df = pd.read_csv(rep_file, index_col=0, names=feat_names)
        feature_file_dict = {x.split('.')[0]: ft_dir + x for x in os.listdir(ft_dir)
                             if x.split('.')[0] in selected_assemblies}
        fna_file_dict = {x.split('.')[0]: fna_dir + x for x in os.listdir(fna_dir)
                         if x.split('.')[0] in selected_assemblies}
        faa_file_dict = {x.split('.')[0]: faa_dir + x for x in os.listdir(faa_dir)
                         if (x.split('.')[0] in selected_assemblies) and (x.endswith('.faa'))}
        for assembly in tqdm(selected_assemblies, position=0):
            try:
                feature_file = feature_file_dict[assembly]
                fna_file = fna_file_dict[assembly]
                faa_file = faa_file_dict[assembly]
                if x_file_dict is not None:
                    X = pd.read_parquet(x_file_dict[assembly])
                else:
                    X = None
                out_df, model_ft_df = defense_predictor(feature_file, fna_file, faa_file, rep_df=rep_df, model_feature_df=X)
                out_df.to_parquet(os.path.join(out_dir, assembly + '_predictions.pq'), index=False)
                model_ft_df.to_parquet(os.path.join(out_dir, assembly + '_X.pq'), index=True)
            except:
                warn("Failed for " + assembly)
    
    