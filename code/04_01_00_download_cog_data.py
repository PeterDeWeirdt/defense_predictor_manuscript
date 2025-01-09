import requests
import pandas as pd
import io

print('Reading in COG data')
cog_description_request = requests.get('https://ftp.ncbi.nih.gov/pub/COG/COG2020/data/cog-20.def.tab')
cog_desc_df = pd.read_table(io.StringIO(cog_description_request.text), 
                            names=['cog_id', 'cog_category', 
                                   'cog_name', 'gene_name', 
                                   'pathway', 'pmid', 'pbdid'])

cog_proteins_request = requests.get('https://ftp.ncbi.nih.gov/pub/COG/COG2020/data/cog-20.cog.csv')
cog_protein_df = pd.read_csv(io.StringIO(cog_proteins_request.text), 
                             names=['gene_id', 'assembly_id', 'protein_id',
                                    'protein_len', 'cog_map2_protein', 'cog_match_len',
                                    'cog_id', 'reserved', 'membership_class', 
                                    'bit_score', 'e-value', 'profile_len', 
                                    'protein_map2_cog', 'err'])
print('Writing COG data')
cog_desc_df.to_parquet('../data/interim/cog_descriptions.pq', index=False)
cog_protein_df.to_parquet('../data/interim/cog_proteins.pq', index=False)