import os
from joblib import Parallel, delayed
from tqdm import tqdm
import random

def hmmsearch(tblout, database, input_file, cutoff=1E-2):
    # fixed total targets for comparison with other 
    rand = random.randint(0, 1_000_000_000)
    os.system(' '.join(['conda run -n beaker', 
                        'hmmsearch',
                        '-o', '../data/tmp/tmpfile_' + str(rand) + '.txt',
                        '--domtblout', tblout,
                        '-E', str(cutoff), 
                        '--domE', str(cutoff),
                        '--cpu', '2',
                        database,
                        input_file]))
    os.system('rm ../data/tmp/tmpfile_' + str(rand) + '.txt')
    

if __name__ == '__main__':
    df_uniref_out = '../data/interim/df_uniref_out/'
    split_dir = '../data/interim/uniref50_chunks/uniref50.faa.split/'
    _ = Parallel(n_jobs=24)(delayed(hmmsearch)(df_uniref_out + str(i)  + '.txt', 
                                           '../data/interim/defense_finder.hmm', 
                                           split_dir + f) for (i, f) in tqdm(enumerate(os.listdir(split_dir)), 
                                                                                  position=0, total=610) if '.faa' in f)