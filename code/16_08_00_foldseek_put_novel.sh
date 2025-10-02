#!/bin/bash

#SBATCH --exclusive
#SBATCH -o 16_08_01_foldseek_put_novel.log-%j
#SBATCH -c 40
#SBATCH --gres=gpu:volta:1 
#SBATCH --time=48:00:00

# Loading the required module
source /etc/profile
#module load anaconda/2023a

source /state/partition1/llgrid/pkg/anaconda/anaconda3-2023a/etc/profile.d/conda.sh
conda run -n nvcc bash -c "echo \"PATH inside environment: \${PATH}\""

PADDB1=../data3/interim/foldseek_dbs/df_rep_foldseek_db_pad
PDB2=../data3/interim/ecoli3k_put_novel_structures/
DB2=../data3/interim/foldseek_dbs/ecoli3k_put_novel_foldseek_db
PADDB2=../data3/interim/foldseek_dbs/ecoli3k_put_novel_foldseek_db_pad
RESDB=../data3/interim/foldseek_dbs/ecoli3k_put_novel_df_rep_search
RESFILE=../data3/interim/ecoli3k_put_novel_rep_search.txt
# Run the script
conda run -n nvcc /home/gridsan/pdeweirdt/Documents/foldseek/build/bin/foldseek \
    createdb $PDB2 $DB2

conda run -n nvcc /home/gridsan/pdeweirdt/Documents/foldseek/build/bin/foldseek \
    makepaddedseqdb $DB2 $PADDB2

export CUDA_VISIBLE_DEVICES=0,1
conda run -n nvcc /home/gridsan/pdeweirdt/Documents/foldseek/build/bin/foldseek \
    search $PADDB2 $PADDB1 $RESDB $TMPDIR \
    --gpu 1 --alignment-type 1 -a

conda run -n nvcc /home/gridsan/pdeweirdt/Documents/foldseek/build/bin/foldseek \
    convertalis $PADDB2 $PADDB1 $RESDB $RESFILE \
    --format-output "query,target,fident,alnlen,mismatch,gapopen,qstart,qend,tstart,tend,qcov,tcov,evalue,bits,alntmscore,qtmscore,ttmscore,rmsd,lddt,prob"

