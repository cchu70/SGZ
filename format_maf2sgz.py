import pandas as pd
import numpy as np
from multiprocessing import Pool
import tqdm
import argparse
import sys

def format_hapaseg_tonly_merged_maf2sgz(sample_id, maf_fn):
    maf_df = pd.read_csv(maf_fn, sep='\t')
    new_maf_df = pd.DataFrame(index=maf_df.index, columns=['#sample', 'mutation', 'frequency', 'depth', 'pos', 'status', 'strand', 'effect'])
    new_maf_df['#sample'] = sample_id
    new_maf_df['mutation'] = maf_df['Chromosome'].astype(str) + ':' + maf_df['Start_position'].astype(str) + ':' + maf_df['putative_somatic'].astype(str)
    new_maf_df['depth'] = maf_df['t_ref_count'] + maf_df['t_alt_count']
    new_maf_df['frequency'] = maf_df['t_alt_count'] / new_maf_df['depth']
    new_maf_df['pos'] = 'chr' + maf_df['Chromosome'].astype(str) + ':' + maf_df['Start_position'].astype(str)
    
    new_maf_fn = '{}.hapaseg_tonly_merged_maf2sgz.tsv'.format(sample_id)
    new_maf_df.to_csv(new_maf_fn, sep='\t', index=None)
    return new_maf_fn
    
    
def parse_args():
    
    parser = argparse.ArgumentParser(argument_default = argparse.SUPPRESS)
    parser.add_argument('--sample_id', type=str,
                        help='sample id')
    parser.add_argument('--hapaseg_tonly_merged_maf', type=str,
                        help='Path to hapaseg_tonly_merged_maf')
    
    return parser.parse_args()
    
    
def main():
    args = parse_args()
    
    new_maf_fn = format_hapaseg_tonly_merged_maf2sgz(
        sample_id=args.sample_id, 
        maf_fn=args.hapaseg_tonly_merged_maf, 
    )
    
if __name__ == "__main__":
    main()
    
    