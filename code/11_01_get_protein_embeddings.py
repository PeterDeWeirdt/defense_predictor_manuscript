import os
import torch
from esm import pretrained, FastaBatchedDataset
import numpy as np
import pandas as pd
from tqdm import tqdm

if __name__ == '__main__':
    in_fasta = '../data3/interim/model_neighbor_seqs.faa'
    output_file = '../data3/interim/model_neighbor_representations.pq'
    model_location = 'esm2_t30_150M_UR50D'
    toks_per_batch = 4096
    truncation_seq_length = 1022
    repr_layer = 30
    model, alphabet = pretrained.load_model_and_alphabet(model_location)
    if torch.cuda.is_available():
        model = model.cuda()
        print("Transferred model to GPU")
    assert (-(model.num_layers + 1) <= repr_layer <= model.num_layers)
    repr_layer = (repr_layer + model.num_layers + 1) % (model.num_layers + 1)
    print('repr layer', repr_layer)
    dataset = FastaBatchedDataset.from_file(in_fasta)
    batches = dataset.get_batch_indices(toks_per_batch, extra_toks_per_seq=1)
    data_loader = torch.utils.data.DataLoader(
        dataset, collate_fn=alphabet.get_batch_converter(truncation_seq_length), batch_sampler=batches
    )
    rep_list = list()
    label_list = list()
    with torch.no_grad():
        for batch_idx, (labels, strs, toks) in enumerate(data_loader):
            if torch.cuda.is_available():
                toks = toks.to(device="cuda", non_blocking=True)
            out = model(toks, repr_layers=[repr_layer], return_contacts=False)
            representations = out['representations'][repr_layer]
            for i, label in enumerate(labels):
                truncate_len = min(truncation_seq_length, len(strs[i]))
                mean_rep = representations[i, 1:truncate_len + 1].mean(0).cpu().numpy()
                label_list.append(label)
                rep_list.append(mean_rep)
    rep_df = pd.DataFrame(rep_list)
    rep_df.index = label_list
    rep_df.to_parquet(output_file)
    
