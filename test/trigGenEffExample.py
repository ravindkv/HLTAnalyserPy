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
from Analysis.HLTAnalyserPy.EvtData import EvtData, EvtHandles,std_products, add_product,get_objs

import Analysis.HLTAnalyserPy.CoreTools as CoreTools
import Analysis.HLTAnalyserPy.GenTools as GenTools
import Analysis.HLTAnalyserPy.TrigTools as TrigTools

if __name__ == "__main__":
    
    CoreTools.load_fwlitelibs()

    parser = argparse.ArgumentParser(description='example e/gamma HLT analyser')
    parser.add_argument('in_filename',nargs="+",help='input filename')
    parser.add_argument('--report','-r',default=10,type=int,help="report every N events")
    parser.add_argument('--prefix','-p',default='file:',help='file prefix')
    parser.add_argument('--out','-o',default="output.root",help='output filename')
    args = parser.parse_args()

    products = []
    add_product(products,"genparts","std::vector<reco::GenParticle>","genParticles")
    add_product(products,"geninfo","GenEventInfoProduct","generator")
    add_product(products,"pu_sum","std::vector<PileupSummaryInfo>","addPileupInfo")
    add_product(products,"trig_sum","trigger::TriggerEvent","hltTriggerSummaryAOD")
    add_product(products,"trig_res","edm::TriggerResults","TriggerResults")
    evtdata = EvtData(products,verbose=True)
    
    in_filenames_with_prefix = ['{}{}'.format(args.prefix,x) for x in args.in_filename]
    events = Events(in_filenames_with_prefix)
    
    print("number of events",events.size())

    out_file = ROOT.TFile.Open(args.out,"RECREATE")
    etHistAll = ROOT.TH1D("etHistAll","",100,0,100)
    etHistPass = ROOT.TH1D("etHistPass","",100,0,100)

    for event_nr,event in enumerate(events):
        if event_nr%args.report==0:
            print("processing event {} / {}".format(event_nr,events.size()))
            
        evtdata.get_handles(event)
        gen_eles = GenTools.get_genparts(evtdata.get("genparts"),pid=11,antipart=True)
        objs_pass_ele32 = TrigTools.get_objs_passing_filter_aod(evtdata,"hltEle32WPTightGsfTrackIsoFilter")
        for ele in gen_eles:
            if abs(ele.eta())<2.5:
                etHistAll.Fill(ele.et())
                if(TrigTools.match_trig_objs(ele.eta(),ele.phi(),objs_pass_ele32)):
                    etHistPass.Fill(ele.et())
        
    out_file.Write()
