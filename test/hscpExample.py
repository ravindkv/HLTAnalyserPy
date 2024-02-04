import ROOT
import json
import re
import argparse
from DataFormats.FWLite import Events, Handle
from Analysis.HLTAnalyserPy.EvtData import EvtData, EvtHandles, add_product,get_objs

import Analysis.HLTAnalyserPy.CoreTools as CoreTools
import Analysis.HLTAnalyserPy.GenTools as GenTools
import Analysis.HLTAnalyserPy.HistTools as HistTools
import Analysis.HLTAnalyserPy.TrigTools as TrigTools


    
if __name__ == "__main__":
    
    CoreTools.load_fwlitelibs()

    parser = argparse.ArgumentParser(description='example e/gamma HLT analyser')
    parser.add_argument('in_filenames',nargs="+",help='input filename')
    parser.add_argument('--prefix','-p',default='file:',help='file prefix')
    parser.add_argument('--l1menufile',required=True,help='l1menu file')
    parser.add_argument('--out','-o',default="output.root",help='output filename')
    args = parser.parse_args()
    

    #we use a helper class EvtData which allows us to more easily access the products
    #products tells it what to read
    #note its a lazy evaulation, it only get the product on demand so other than startup, no
    #performance loss to having products registered you dont use
    #std_products is just a list with each entry having
    #    name : name to access it with
    #    type : c++ type, eg std::vector<reco::GenParticle>
    #    tag : InputTag but as a string so ":" seperates name:instance:process 
    
    hlt_process = "HLTX" #replace this with the HLT process name you want

    std_products = []
    #hlt products
    add_product(std_products,"trig_sum","trigger::TriggerEvent",f"hltTriggerSummaryAOD::{hlt_process}")
    add_product(std_products,"trig_res","edm::TriggerResults",f"TriggerResults::{hlt_process}")
    
    #l1 menu results
    add_product(std_products,"l1algblk","BXVector<GlobalAlgBlk>","hltGtStage2Digis")
    add_product(std_products,"l1extblk","BXVector<GlobalExtBlk>","hltGtStage2Digis")
    #l1 objects 
    add_product(std_products,"l1eg","BXVector<l1t::EGamma>","hltGtStage2Digis:EGamma")
    add_product(std_products,"l1etsum","BXVector<l1t::EtSum>","hltGtStage2Digis:EtSum")
    add_product(std_products,"l1jet","BXVector<l1t::Jet>","hltGtStage2Digis:Jet")
    add_product(std_products,"l1muon","BXVector<l1t::Muon>","hltGtStage2Digis:Muon")
    add_product(std_products,"l1tau","BXVector<l1t::Tau>","hltGtStage2Digis:Tau")
    # additional HLT products saved
    add_product(std_products,"ecalpfclus","std::vector<reco::PFCluster>","hltParticleFlowClusterECALUnseeded")
    add_product(std_products,"hcalpfclus","std::vector<reco::PFCluster>","hltParticleFlowClusterHCAL")
    add_product(std_products,"tracks","std::vector<reco::Track>","hltMergedTracks")
    add_product(std_products,"dedx","edm::ValueMap<reco::DeDxData>","hltDeDxEstimatorProducer")
    
    evtdata = EvtData(std_products,verbose=True)

    events = Events(CoreTools.get_filenames(args.in_filenames,args.prefix))
    print("number of events",events.size())

    #we need to map the L1 bits to seed names
    #we do this with the l1 menu file which we can generate from the 
    #following commmand
    #  cmsRun Analysis/HLTAnalyserPy/test/dumpConditions_cfg.py outputFile=l1MenuMC.root globalTag=121X_mcRun3_2021_realistic_v15 startRunNr=1 endRunNr=1
    #this dumps the menu into the file. As its MC, there is only one tree entry 
    #so we can just access the first entry
    l1menu_tree_file = ROOT.TFile.Open(args.l1menufile)
    l1menu_tree = ROOT.L1TUtmTriggerMenuRcd
    l1menu_tree.GetEntry(0)
    l1menu = l1menu_tree.L1TUtmTriggerMenu__
    #https://cmssdt.cern.ch/lxr/source/CondFormats/L1TObjects/interface/L1TUtmAlgorithm.h

    l1name_to_indx = {x.second.getName() :x.second.getIndex() for x in l1menu.getAlgorithmMap()}
    l1bitnr = l1name_to_indx["L1_SingleMu22"]
    
    for eventnr,event in enumerate(events):
        #we need to initialise the handles, must be called first for every event
        evtdata.get_handles(events)
        
        #lets access the L1 information
        l1algblk = evtdata.get("l1algblk")
        #we retrieve the bits after masks and prescales 
        #you can see it before masks and prescales via getAlgoDecisionInitial()
        #this is a BXVector which means the first number is the bx (-2 -> 2) and
        #the second number is object number (and for a menu is there is exactly 1
        #so its always 0)
        #normally you select bx 0 which is the bx that caused the trigger
        l1dec_final = l1algblk.at(0,0).getAlgoDecisionFinal()
        #we can also get the results of the next bx
        l1dec_final_bxp1 = l1algblk.at(1,0).getAlgoDecisionFinal() if l1algblk.getLastBX()>=1 else None
        

        #the l1 menu is simply 512 bits saying if a bit passed or failed
        #we translate the bit numbers to seed names via the L1 menu record
        print(f"l1 pass {l1dec_final[l1bitnr]}")

        #now we can also look at given L1 objects. Note, these are all L1 objects
        #and may not pass the quality requirements of a given seed 
        #lets the get l1muons
        l1muons_allbx = evtdata.get("l1muon")
        
        l1muons_bx0 = [l1muons_allbx.at(0,munr) for munr in range(0,l1muons_allbx.size(0))]       
        #now getting bx1 muons (however this is not in the MC by default. Only data
        #hence why we check the bx is stored)
        l1muons_bx1 = [l1muons_allbx.at(1,munr) for munr in range(0,l1muons_allbx.size(1))] if l1muons_allbx.getLastBX()>=1 else []
        print(f"nr muons bx 0 {len(l1muons_bx0)}")
        for mu in l1muons_bx0:
            print(f" pt/eta/phi {mu.hwPt()} {mu.hwEta()} {mu.hwPhi()}")

        print(f"nr muons bx 1 {len(l1muons_bx1)}")
        for mu in l1muons_bx1:
            print(f" pt/eta/phi {mu.hwPt()} {mu.hwEta()} {mu.hwPhi()}")
        
        #now lets get some HLT quantities
        #the hlt stores all the 4 vectors of objects passing filters in 
        #TriggerEvent 
        #we can access the objects via filter
        
        #all objects passing a given filter:
        hltpfmet_objs = TrigTools.get_objs_passing_filter_aod(evtdata,"hltPFMET10")
        print(f"hlt met {len(hltpfmet_objs)}")
        for metobj in hltpfmet_objs:
            print(f" met {metobj.pt()} {metobj.phi()}")
        
        #we can also do this for l1obj which the HLT filters write
        #these filters always begin with hltL1s
        l1met_objs = TrigTools.get_objs_passing_filter_aod(evtdata,"hltL1sAllETMHFSeeds")
        #tracks
        hlt_trk_p4s = TrigTools.get_objs_passing_filter_aod(evtdata,"hltTrk50Filter")
        #now the above is the basic HLT info you can expect to exist in AOD
        
        #however we can also save additional products in the HLT
        #here we would need to do seomthing like
        """
        outputMod.outputCommands.append("keep *_particleFlowClusterECALUnseeded_*_*")
        """
        
        #lets get the pf clusters (which we registered above)
        ecalpfclus = evtdata.get("ecalpfclus")
        hcalpfclus = evtdata.get("hcalpfclus")
        
        #do what you want with them
        print(f"nr ecal clus {ecalpfclus.size()} hcal clus {hcalpfclus.size()}")
        
                
