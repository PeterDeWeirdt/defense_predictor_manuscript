import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm import tqdm

if __name__ == '__main__':
    fna_base_dir = '../data/interim/ecor_genomic/'
    fna_files = [x for x in os.listdir(fna_base_dir) if '.fna' in x]
    genomad_working_dir = '../data/interim/ecor_genomad/'
    if 'ecor_genomad' not in os.listdir('../data/interim/'):
        os.mkdir(genomad_working_dir)
    for f in tqdm(fna_files, position=0):
        assembly = f.split('.')[0]
        os.system(' '.join(['conda run -n genomad', 
                            'genomad end-to-end --cleanup', 
                            fna_base_dir + f, 
                            genomad_working_dir + assembly, 
                            '~/Documents/genomad/genomad_db/']))
