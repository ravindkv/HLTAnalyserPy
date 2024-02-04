from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import argparse
import sys
import ROOT
import json
import re


import Analysis.HLTAnalyserPy.CoreTools as CoreTools
import Analysis.HLTAnalyserPy.RateCfgTools as RateCfgTools
import Analysis.HLTAnalyserPy.TrigTools as TrigTools


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='generates a rate ntup config from HLT file')
    parser.add_argument('cfg',help='input config')
    parser.add_argument('--l1seeds',nargs="+",help="l1 seeds to search for")
    parser.add_argument('--out','-o',default="output.json",help="output file")

    args = parser.parse_args()
  
    process = CoreTools.load_cmssw_cfg(args.cfg)


    for name,path in process.paths_().items():
        name_novers = TrigTools.strip_trig_ver(name)
        path_l1seeds = RateCfgTools.get_l1_seeds(process,path)
        datasets = RateCfgTools.get_datasets(process,path)

        matched_seeds = [seed for seed in path_l1seeds if seed in args.l1seeds] if path_l1seeds else None
        if matched_seeds:
            print(f'{name_novers} : {" ".join(matched_seeds)} : {" ".join(datasets)}')

        
     
