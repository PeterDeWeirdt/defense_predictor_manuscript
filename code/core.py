import pandas as pd
from Bio import SeqIO
import warnings
import seaborn as sns
import hashlib


bw_color_palette = sns.color_palette(['#e69f00', '#56b4e9', '#009e73', '#f0e442', '#0072b2', '#d55e00', '#cc79a7'])
# Check 13_02_01 for cutoffs
med_log_odds_cutoff = 4 # greater than this, but less than high is in the medium category

def get_record_metadata(r):
    r_dict = vars(r)
    record_dict = dict()
    for k in ['id', 'name', 'description', 'comment']:
        if k in r_dict.keys():
            record_dict[k] = r_dict[k]
    if record_dict['id'] == 'unknown':
        record_dict['id'] = record_dict['name']
    if 'dbxrefs' in r_dict.keys():
        for ref in r_dict['dbxrefs']:
            source, source_id = ref.split(':')
            record_dict[source] = source_id
    if 'annotations' in r_dict.keys():
        annot = r_dict['annotations']
        if 'taxonomy' in annot.keys():
            for i, tax in enumerate(annot['taxonomy']):
                record_dict['tax_' + str(i)] = tax
        if 'source' in annot.keys():
            record_dict['source'] = annot['source']
        if 'organism' in annot.keys():
            record_dict['organism'] = annot['organism']
    return record_dict


def get_feature_info(f, r):
    feature_dict = {}
    if r.id == 'unknown':
        feature_dict['parent_id'] = r.name
    else:
        feature_dict['parent_id'] = r.id
    feature_dict['type'] = f.type
    feature_dict['strand'] = f.strand
    loc = f.location
    feature_dict['start'] = int(loc.start)
    feature_dict['end'] = int(loc.end)
    feature_dict['start_type'] = loc.start.__class__.__name__
    feature_dict['end_type'] = loc.end.__class__.__name__
    try:
        feature_dict['nt_seq'] = str(f.extract(r.seq))
    except:
        feature_dict['nt_seq'] = None
    feature_dict['id'] = f.id
    quals = f.qualifiers
    for k, v in quals.items():
        if isinstance(v, list):
            feature_dict[k] = ', '.join(v)
        else:
            feature_dict[k] = v
    return feature_dict


def get_gbff_contents(file, base_dir='../data/raw/assemblies/'):
    """Get features from file in genbank file format

    file: str, name of assembly
    base_dir: str, path to assembly files
    returns:
        record_df: DataFrame, record information (taxonomy, source, organism)
        source_df: DataFrame, contig-level nucleotide sequences
        feature_df: DataFrame, genomic features
        merged_feature_df: DataFrame, genomic features merged with record information
    """
    record_meta_list = []
    feature_dict_list = []
    source_list = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for r in SeqIO.parse(base_dir + file, 'gb'):
            record_dict = get_record_metadata(r)
            record_dict['file'] = file
            record_meta_list.append(record_dict)
            features = r.features
            for f in features:
                if f.type != 'gene':
                    feature_dict = get_feature_info(f, r)
                    if f.type == 'source':
                        source_list.append(feature_dict)
                    else:
                        feature_dict_list.append(feature_dict)
    record_df = pd.DataFrame(record_meta_list)
    source_df = pd.DataFrame(source_list)
    feature_df = pd.DataFrame(feature_dict_list)
    merged_feature_df = feature_df.merge(record_df, left_on='parent_id', right_on='id', suffixes=('', '_parent'))
    return record_df, source_df, feature_df, merged_feature_df


def get_hmm_search_hits(file):
    """Read file from hmm search query

    file: str, filepath to hmmsearch result
    returns:
        hit_dict_df: DataFrame
    """
    hit_dict_df = pd.read_table(file,
                                names=['target_name', 'target_accession', 'query_name', 'query_accession',
                                       'sequence_e-value', 'sequence_score', 'sequence_bias',
                                       'best_domain_e-value', 'best_domain_score', 'best_domain_bias',
                                       'exp', 'reg', 'clu', 'ov', 'env', 'dom', 'rep', 'inc', 'target_description'],
                                skiprows=3, sep='\s+', skipfooter=10)
    return hit_dict_df


def encode_protein(p):
    return hashlib.sha224(p.encode('utf-8')).hexdigest()


def read_dom_table(file):
    lines = []
    with open(file, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            parts = line.strip().split(None, 22)  # 22 columns before 'targ_description'
            lines.append(parts)
    columns = ['target', 'target_accession', 'tlen', 
               'query', 'query_accession', 'qlen', 
               'seq_evalue', 'seq_score', 'seq_bias', 
               'dom_n', 'dom_of', 'dom_c_evalue', 'dom_i_evalue', 
               'dom_score', 'dom_bias', 'hmm_from', 'hmm_to', 
               'ali_from', 'ali_to', 'env_from', 'env_to', 'acc',
               'targ_description']
    dom_table = pd.DataFrame(lines, columns=columns)
    numerical_columns = ['tlen', 'qlen', 'seq_evalue', 'seq_score', 'seq_bias',
                         'dom_n', 'dom_of', 'dom_c_evalue', 'dom_i_evalue', 
                         'dom_score', 'dom_bias', 'hmm_from', 'hmm_to', 
                         'ali_from', 'ali_to', 'env_from', 'env_to', 'acc']
    for col in numerical_columns:
        dom_table[col] = dom_table[col].astype(float)
    return dom_table


def read_hmmsearch_seq_table(file, no_description=True):
    if no_description:
        seq_table = pd.read_table(file, 
                                  names = ['target', 'target_accession', 
                                           'query', 'query_accession', 
                                           'seq_evalue', 'seq_score', 'seq_bias',
                                           'dom_evalue', 'dom_score', 'dom_bias', 
                                           'exp', 'reg', 'clu', 'ov', 'env',  'dom', 
                                           'rep', 'inc', 'targ_description'],
                                  comment='#', sep='\s+')
    else:
        raise NotImplementedError()
    return seq_table


def read_mmseqs_results(file):
    gao_blast_results = pd.read_table(file, 
                                  names=['query','target','fident','alnlen','mismatch',
                                              'gapopen','qstart','qend','tstart','tend',
                                              'evalue','bits','qcov','tcov'])
    return gao_blast_results


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

