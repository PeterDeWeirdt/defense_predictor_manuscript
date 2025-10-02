import os

def run_mmseqs_profile(query_fasta, target_fasta, out_file, threads=40, n_iter=3):
    print("Creating databases")
    query_db = '$TMPDIR/query_db'
    os.system(' '.join(['conda run -n beaker mmseqs createdb',
                        query_fasta, query_db]))
    target_db = '$TMPDIR/target_db'
    os.system(' '.join(['conda run -n beaker mmseqs createdb',
                        target_fasta, target_db]))
    print("Making query profiles")
    query_profile_res = '$TMPDIR/query_profile'
    target_profile_db = '../data3/interim/mmseqs_dbs/minimal_seqs'
    os.system(' '.join(['conda run -n beaker mmseqs',
                        'search', query_db, 
                        target_profile_db,
                        query_profile_res,
                        '$TMPDIR',
                        '-s 6',
                        '--threads', str(threads),
                        '--num-iterations', str(n_iter)]))
    query_profile = '$TMPDIR/query_profile'
    os.system(' '.join(['conda run -n beaker mmseqs',
                        'result2profile', query_db, 
                        target_profile_db,
                        query_profile_res,
                        query_profile]))
    print('Querying target database')
    query_target_search_res = '$TMPDIR/query_target'
    os.system(' '.join(['conda run -n beaker mmseqs',
                        'search', query_profile, 
                        target_db, 
                        query_target_search_res,
                        '$TMPDIR',
                        '-s 7.5',
                        '--threads', str(threads)]))
    print('Writing output')
    os.system(' '.join(['conda run -n beaker mmseqs',
                        'convertalis', query_profile, 
                        target_db, 
                        query_target_search_res,
                        out_file, 
                        '--format-output', 
                        'query,target,fident,alnlen,mismatch,gapopen,qstart,qend,tstart,tend,evalue,bits,qcov,tcov']))

if __name__ == '__main__':
    query = '../data3/interim/candidate_seqs.faa'
    target = '../data3/interim/candidate_seqs.faa'
    out = '../data3/interim/candidate_mmseqs_profile_out.txt'
    run_mmseqs_profile(query, target, out)