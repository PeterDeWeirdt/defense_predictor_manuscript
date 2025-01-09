from tqdm import tqdm
from predict import get_representations
import warnings
import os
from esm import pretrained, FastaBatchedDataset
import torch

if __name__ == '__main__':
    unique_seqs_fa = '../data/ecoli/interim/unique_seqs.faa'
    rep_output_dir = '../data/ecoli/interim/'
    if 'ecoli_reps.csv' not in os.listdir('../data/ecoli/interim'):
        print('Calculating assembly representations')
        model_location = 'esm2_t30_150M_UR50D'
        toks_per_batch = 4096
        truncation_seq_length = 1022
        repr_layer = 30
        model, alphabet = pretrained.load_model_and_alphabet(model_location)
        device = torch.device('cuda')
        print('Model device:', device)
        model = model.to(device)
        repr_layer = (repr_layer + model.num_layers + 1) % (model.num_layers + 1)
        print('Repr layer', repr_layer)
        get_representations(unique_seqs_fa, 'ecoli', 
                            rep_output_dir, toks_per_batch, alphabet,
                            truncation_seq_length, model, repr_layer, 'cuda')
    else:
        warnings.warn('Representation directory already exists')
