import pandas as pd
import os
import subprocess

if __name__ == '__main__':
    blast_results = pd.read_csv('../data3/external/negative_library_blast_out.csv', 
                            names=['query', 'subject', 'identity', 'ali_len', 'mismatches', 
                                   'gaps', 'q_start', 'q_end', 's_start', 's_end', 'evalue', 
                                   'bit_score', 'positives'])
    top_out_dir = '../data3/interim/negative_flags/'
    if not os.path.exists(top_out_dir):
        os.mkdir(top_out_dir)
    with open('../data/external/email.txt', 'r') as f:
        email = f.read().strip()
    for query, query_df in blast_results.groupby('query'):
        if query not in os.listdir(top_out_dir):
            query_dir = top_out_dir + query + '/'
            os.mkdir(query_dir)
            print(query)
            if len(query_df) > 30:
                query_df = query_df.sample(30, random_state=7)
            query_protein_list = '../data/tmp/' + query + '.txt'
            query_df[['subject']].to_csv(query_protein_list, header=False, index=False)
            command = ['conda', 'run', '-n', 'eFlaGs2', 'python', '/home/gridsan/pdeweirdt/FlaGs2/FlaGs2.py', 
               '-p', query_protein_list, '-o', query_dir + query, '-u', email, '-vb']
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            # This loop will read and print the output in real-time
            for line in iter(process.stdout.readline, b''):
                print(line.decode(), end='')
            process.stdout.close()
            return_code = process.wait()
            if return_code:
                raise subprocess.CalledProcessError(return_code, command)
            os.system('rm ' + query_protein_list)
