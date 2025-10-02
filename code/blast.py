import os
import pandas as pd

def run_blast(query_fasta, target_fasta, output_file, 
              dbtype='prot', threads=48, outfmt=10):
    tmp_target = os.path.join('$TMPDIR', 'target.faa')
    os.system(' '.join(['cp', target_fasta, tmp_target]))
    tmp_target_db = os.path.join('$TMPDIR', 'target_db')
    os.system(' '.join(['conda run -n blast',
                        'makeblastdb',
                        '-in', tmp_target, 
                        '-dbtype', dbtype, 
                        '-out', tmp_target_db]))
    tmp_query = os.path.join('$TMPDIR', 'query.faa')
    os.system(' '.join(['cp', query_fasta, tmp_query]))
    tmp_out = '$TMPDIR/tmp_out.csv'
    os.system(' '.join(['conda run -n blast blastp',
                    '-db', tmp_target_db, 
                    '-query', tmp_query, 
                    '-out', tmp_out, 
                    '-outfmt', str(outfmt),
                    '-num_threads', str(threads)]))
    os.system(' '.join(['cp', tmp_out, output_file]))
    
    
def read_blast_fmt10(file):
    search_df = pd.read_csv(file, 
                        names=['query', 'target', 'fident', 'alnlen', 'mismatch', 
                               'gapopen', 'qstart', 'qend', 'tstart', 'tend', 
                               'evalue', 'bits'])
    return search_df