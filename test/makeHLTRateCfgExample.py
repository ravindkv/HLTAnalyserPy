from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import argparse
import sys
import ROOT
import json
import re
from collections import OrderedDict

import Analysis.HLTAnalyserPy.CoreTools as CoreTools
import Analysis.HLTAnalyserPy.TrigTools as TrigTools
import Analysis.HLTAnalyserPy.RateCfgTools as RateCfgTools


def adjust_ps_cols(pathname,input_ps):
    """
    
    it sets column 0 as unprescaled all paths (usually for running if the prescales are already applied)
    it then makes copy of the column 1 (which we assume is the 2E34 column, adjust as needed) which you can then run
    
    you can add it a second time (remember to make a seperate copy via list(prescale) and apply other modifications

    """
    
    prescales = [1]
    prescale = input_ps[1]
    prescales.append(prescale)


    return prescales
    

if __name__ == "__main__":
    

    parser = argparse.ArgumentParser(description='generates a rate ntup config from HLT file')
    parser.add_argument('cfg',help='input config')
    parser.add_argument('--out','-o',default="output.json",help="output file")
    args = parser.parse_args()
  
    process = CoreTools.load_cmssw_cfg(args.cfg)
    cfg_dict = OrderedDict()
    group_data = {}

    #physics datasets are to determine if the physics flag is set in the config, the physics flag is needed to be included in rate overlaps
    physics_streams = {"PhysicsMuons","PhysicsHadronsTaus","PhysicsEGamma","PhysicsCommissioning"}
    physics_datasets = RateCfgTools.get_physics_datasets(process,physics_streams)

    print(physics_datasets)

    for name,path in process.paths_().items():
        name_novers = TrigTools.strip_trig_ver(name)
        cfg_dict[name_novers] = RateCfgTools.get_path_data(process,path,group_data,physics_datasets)
        cfg_dict[name_novers]['prescales'] =  adjust_ps_cols(name_novers,cfg_dict[name_novers]['prescales'])
        
        

    with open(args.out,'w') as f:
        json.dump(cfg_dict,f,indent=0)
