import os
import torch
from esm import pretrained, FastaBatchedDataset
from joblib import Parallel, delayed
import csv
import numpy as np
from tqdm import tqdm
import argparse


def get_representations(fasta_file, output_dir, 
                        fasta_file_dir, toks_per_batch, 
                        alphabet, truncation_seq_length, 
                        model, repr_layer):
    out_file = fasta_file.split('.')[0] + '.csv'
    with open(output_dir + out_file, 'w') as f:
        dataset = FastaBatchedDataset.from_file(fasta_file_dir + fasta_file)
        batches = dataset.get_batch_indices(toks_per_batch, extra_toks_per_seq=1)
        data_loader = torch.utils.data.DataLoader(
            dataset, collate_fn=alphabet.get_batch_converter(truncation_seq_length), batch_sampler=batches
        )
        with torch.no_grad():
            for batch_idx, (labels, strs, toks) in enumerate(data_loader):
                if torch.cuda.is_available():
                    toks = toks.to(device="cuda", non_blocking=True)
                out = model(toks, repr_layers=[repr_layer], return_contacts=False)
                representations = out['representations'][repr_layer]
                for i, label in enumerate(labels):
                    truncate_len = min(truncation_seq_length, len(strs[i]))
                    mean_rep = representations[i, 1:truncate_len + 1].mean(0).cpu().numpy()
                    print(','.join([label] + [str(x) for x in mean_rep]), file=f)
                    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('fasta_file_dir')
    args = parser.parse_args()
    fasta_file_dir = args.fasta_file_dir
    fasta_files = [x for x in os.listdir(fasta_file_dir) if '.faa' in x]
    model_location = 'esm2_t30_150M_UR50D'
    toks_per_batch = 4096
    truncation_seq_length = 1022
    output_dir = '../data/interim/representations/'
    repr_layer = 30
    model, alphabet = pretrained.load_model_and_alphabet(model_location)
    if torch.cuda.is_available():
        model = model.cuda()
        print("Transferred model to GPU")
    assert (-(model.num_layers + 1) <= repr_layer <= model.num_layers)
    repr_layer = (repr_layer + model.num_layers + 1) % (model.num_layers + 1)
    print('repr layer', repr_layer)
    for fasta_file in tqdm(fasta_files):
        get_representations(fasta_file, output_dir, 
                            fasta_file_dir, toks_per_batch, 
                            alphabet, truncation_seq_length, 
                            model, repr_layer)