import os
from joblib import Parallel, delayed
import subprocess
from tqdm import tqdm
import warnings


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
                
        
def run_defense_finder(assembly_file, out_dir):
    assembly_stub = assembly_file.split('.')[0]
    assembly_out_dir = out_dir + assembly_stub
    if 'GCF' in assembly_file:
        os.mkdir(assembly_out_dir)
        subprocess.run(['defense-finder', 'run', 
                        '-w', '1',
                        '-o', assembly_out_dir,
                        '../data/genome_downloads/faa/' + assembly_file], 
                       stdout=subprocess.DEVNULL)
    else:
        warnings.warn(' '.join([assembly_file, 'failed']))
        
    

if __name__ == '__main__':
    faa_files = os.listdir('../data/genome_downloads/faa/')
    chunked_filtered_faa_files = chunks(faa_files, 1_000)
    for i, faa_chunk in enumerate(chunked_filtered_faa_files):
        if i == 11: # need to do 11
            print(i)
            out_dir = '../data/interim/defense_finder_results_' + str(i) + '/'
            os.mkdir(out_dir)
            _ = Parallel(n_jobs=48)(delayed(run_defense_finder)(assembly_file, out_dir) for assembly_file in tqdm(faa_chunk))