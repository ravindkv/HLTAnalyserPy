from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from array import array
import argparse
import sys
import ROOT
import json
import re
import six

from DataFormats.FWLite import Events, Handle
from Analysis.HLTAnalyserPy.EvtData import EvtData, EvtHandles, add_product,get_objs
import Analysis.HLTAnalyserPy.CoreTools as CoreTools
import Analysis.HLTAnalyserPy.TrigTools as TrigTools

if __name__ == "__main__":
    
    CoreTools.load_fwlitelibs()

    parser = argparse.ArgumentParser(description='example e/gamma HLT analyser')
    parser.add_argument('in_filename',nargs="+",help='input filename')
    parser.add_argument('--prefix','-p',default='file:',help='file prefix')

    args = parser.parse_args()
    products = []
    add_product(products,"trig_sum","trigger::TriggerEvent","hltTriggerSummaryAOD")
    add_product(products,"trig_res","edm::TriggerResults","TriggerResults")
    
    evtdata = EvtData(products,verbose=True)
    
    in_filenames_with_prefix = ['{}{}'.format(args.prefix,x) for x in args.in_filename]
    events = Events(in_filenames_with_prefix)
    
    print("number of events",events.size())
    
    path_filters = TrigTools.get_pathfilters(events,"HLT")
    for path,filts in path_filters.items():
        print(f"{path}:")
        for filt in filts:
            print(f"   {filt}")


   # for event in events:
    #    evtdata.get_handles(event)
    #    if not path_filters:
     #       path_filters = get_pathfilters(evtdata,"HLT")
        
            
        
