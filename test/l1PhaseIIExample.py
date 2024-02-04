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

def get_pathfilters(evtdata,procname):
    
    if not hasattr(ROOT,"getPathsNames"):
            ROOT.gInterpreter.Declare("""
#include "FWCore/ParameterSet/interface/ParameterSet.h"
std::vector<std::string> getPathNames(edm::ParameterSet& pset){
   const auto& pathPSet = pset.getParameterSet("@trigger_paths");
   if(pathPSet.exists("@trigger_paths")){
     return pathPSet.getParameter<std::vector<std::string>>("@trigger_paths");
   }else{
     return std::vector<std::string>();
   }
}
                """)

    if not hasattr(ROOT,"getFiltModules"):
            ROOT.gInterpreter.Declare("""
#include "FWCore/ParameterSet/interface/ParameterSet.h"
std::vector<std::string> getFiltModules(edm::ParameterSet& pset,const std::string& pathName){
   std::vector<std::string> filtMods;
   const auto& pathPSet = pset.getParameterSet("@trigger_paths");
   if(pset.existsAs<std::vector<std::string> >(pathName,true)){
     const auto& modules = pset.getParameter<std::vector<std::string>>(pathName);
     for(const auto& mod : modules){
        //ignored modules will start with - and this needs to be removed if present            
        if(pset.exists(mod.front()!=std::string("-") ? mod : mod.substr(1))){
           const auto& modPSet = pset.getParameterSet(mod.front()!=std::string("-") ? mod : mod.substr(1));
           if(modPSet.getParameter<std::string>("@module_edm_type")=="EDFilter" &&
              modPSet.existsAs<bool>("saveTags",true) && modPSet.getParameter<bool>("saveTags")){
              filtMods.push_back(mod);
           }
        }
     }
   }
   return filtMods;
}
                """)

            

    cfg = ROOT.edm.ProcessConfiguration()  
    proc_hist = evtdata.event.object().processHistory() 
    proc_hist.getConfigurationForProcess(procname,cfg) 
    cfg_pset = evtdata.event.object().parameterSet(cfg.parameterSetID())  
    pathnames = ROOT.getPathNames(cfg_pset)
    path_filters = {}
    for path in pathnames:
        path_filters[path] = [filt for filt in ROOT.getFiltModules(cfg_pset,path)]
        
    return path_filters


def print_l1(evtdata,l1_res,l1_name,l1_filtname):
    """
    our example print function which shows if the seed passes 
    and the objects which pass it
    """
    
    l1_objs = TrigTools.get_objs_passing_filter_aod(evtdata,l1_filtname)
    print("{} : {}, nr objs pass {}".format(l1_name,l1_res.result(l1_name),len(l1_objs)))
    for objnr,obj in enumerate(l1_objs):
        print(" {} pt {:3.1f} eta {:3.2f} phi {:3.2f}".format(objnr,obj.pt(),obj.eta(),obj.phi()))

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
    
    l1_res = None
    for event in events:
        evtdata.get_handles(event)

       
        #so the trig res basically a big vector of trigger status, to know what index 
        #corresponds to which path requests the trigger names
        #trig_names = evtdata.event.object().triggerNames(trig_res).triggerNames()
        #as its a bit awkward to look this up each time, we can use TrigTools.TrigResults to do this
        #we just need to pass in a list of path names we want to use
        #we can generate this by filtering trigger names for L1 path names
        if l1_res==None:
            trig_res = evtdata.get("trig_res") 
            l1_names = [x for x in evtdata.event.object().triggerNames(trig_res).triggerNames() if x.startswith("L1T_")]
            l1_res = TrigTools.TrigResults(l1_names)
            path_filters = get_pathfilters(evtdata,"L1TSkimming")
        
        
        #we need to fill it each event
        l1_res.fill(evtdata)
        
        #now we can access the filters for the objects in question via the trigger event, also refered to as the trigger summary
        #to do this just do TrigTools.get_objs_passing_filter_aod(evtdata,filtername)
        #however we'll do it inside this print function
        #print_l1(evtdata,l1_res,"L1T_TkIsoEle28","L1TkIsoEleSingle28Filter")
        
        for path,filters in six.iteritems(path_filters):
            #now we print out the info for each path

            if path.startswith("L1T_"):
                print_l1(evtdata,l1_res,path,filters[-1])
           

        
