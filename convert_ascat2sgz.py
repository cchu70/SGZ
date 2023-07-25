import pandas as pd
import numpy as np
from multiprocessing import Pool
import tqdm
import argparse
import sys

def convert_seg_to_sgz(seg_df, tumor_log_r, tumor_baf, ascat_qc):
    seg_df['chr'] = seg_df['chr'].astype(str)
    tumor_log_r['chrs'] = tumor_log_r['chrs'].astype(str)
    tumor_baf['chrs'] = tumor_baf['chrs'].astype(str)
    
    seg_df['startpos'] = seg_df['startpos'].astype(int)
    seg_df['endpos'] = seg_df['endpos'].astype(int)
    tumor_log_r['pos'] = tumor_log_r['pos'].astype(int)
    tumor_baf['pos'] = tumor_baf['pos'].astype(int)
    
    sgz_seg_df = seg_df.copy()
    sgz_seg_df['CN'] = sgz_seg_df['nMajor'] + sgz_seg_df['nMinor']
    
    purity = float(ascat_qc.iloc[0]['purity'])
    ploidy = float(ascat_qc.iloc[0]['ploidy'])
    sgz_seg_df['purity'] = purity
    sgz_seg_df['baseLevel'] = (purity * ploidy) + (2 * (1-purity))
    
    sgz_seg_df['mafPred'] = ((purity * sgz_seg_df['nMinor']) + (1 - purity)) / (sgz_seg_df['CN'] * purity + 2 * (1 - purity)) #? expected vaf of germline het given purity and ploidy?
    
    sgz_seg_df = sgz_seg_df.rename(columns={'chr': 'CHR', 'startpos': 'segStart', 'endpos': 'segEnd', 'nMinor': 'numMAtumorPred'})
    
    for i, r in tqdm.tqdm(sgz_seg_df.iterrows()):
        chrom = r['CHR']
        start = int(r['segStart'])
        end = int(r['segEnd'])
        
        seg_tumor_log_r = tumor_log_r.loc[
            (tumor_log_r['chrs'] == chrom) & (tumor_log_r['pos'].between(start, end, inclusive='both')),
            tumor_log_r.columns.tolist()[-1]
        ]
        
        sgz_seg_df.loc[i, 'segLR'] = seg_tumor_log_r.median()
        sgz_seg_df.loc[i, 'numLRProbes'] = seg_tumor_log_r.shape[0]
        
        seg_tumor_baf = tumor_baf.loc[
            (tumor_baf['chrs'] == chrom) & (tumor_baf['pos'].between(start, end, inclusive='both')),
            tumor_baf.columns.tolist()[-1]
        ]
        
        # Minor SNP allelic imbalance
        seg_tumor_baf.loc[seg_tumor_baf > 0.5] = 1 - seg_tumor_baf.loc[seg_tumor_baf > 0.5]
        
        # Remove homozygous
        seg_tumor_baf = seg_tumor_baf[seg_tumor_baf > 0.1]
        
        sgz_seg_df.loc[i, 'segMAF'] = seg_tumor_baf.median()
        sgz_seg_df.loc[i, 'numAFProbes'] = seg_tumor_baf.shape[0]
        
    sgz_seg_df = sgz_seg_df.drop(columns=['sample', 'nMajor'])
    sgz_seg_df = sgz_seg_df[sgz_seg_df['segMAF'].notna()]
    return sgz_seg_df
    
def parse_args():
    
    parser = argparse.ArgumentParser(argument_default = argparse.SUPPRESS)
    parser.add_argument('--sample_id', type=str,
                        help='sample id')
    parser.add_argument('--ascat_segments', type=str,
                        help='Path to segmentation from ASCAT (non-raw)')
    parser.add_argument('--tumor_log_r', type=str,
                        help='Path to tumor LogR file')
    parser.add_argument('--tumor_baf', type=str,
                        help='Path to tumor BAF file')
    parser.add_argument('--ascat_qc', type=str,
                        help='Path to ASCAT qc file with purity information')
    
    return parser.parse_args()
    
    
def main():
    args = parse_args()
    
    seg_df = pd.read_csv(args.ascat_segments, sep='\t')
    
    ascat_segments_df = pd.read_csv(args.ascat_segments, sep='\t')
    tumor_LogR_df = pd.read_csv(args.tumor_log_r, sep='\t')
    tumor_BAF_df = pd.read_csv(args.tumor_baf, sep='\t')
    ascat_qc_df = pd.read_csv(args.ascat_qc, sep=' ')
    
    sgz_seg_df = convert_seg_to_sgz(
        seg_df=ascat_segments_df, 
        tumor_log_r=tumor_LogR_df, 
        tumor_baf=tumor_BAF_df, 
        ascat_qc=ascat_qc_df
    )
    
    sgz_seg_fn = f='{}.ascat2SGZ.tsv'.format(args.sample_id)
    sgz_seg_df.to_csv(sgz_seg_fn, sep='\t', index=None)
    
if __name__ == "__main__":
    main()
    