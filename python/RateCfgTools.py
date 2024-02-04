from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import argparse
import sys
import ROOT
import json
import re


from collections import OrderedDict

def parse_l1_logical_express(express):
    """
    only handles the case of ORed seeds for now
    returns empty vec if is AND or NOT
    also returns empty vec if its L1GlobalDecision
    """
    if express.find(" AND ")!=-1 or express.find(" NOT")!=-1 or express.find("NOT ")!=-1 or express == "L1GlobalDecision":
        return []

    return express.split(" OR ")

def get_l1_seeds(process,path):
    """
    looks for a HLTL1TSeed module to determine the L1 seeds
    for now doesnt handle multiple HLTL1TSeed modules nor ignored ones
    we hack in the ignored ones because they all use L1GlobalInputTag = cms.InputTag( "hltGtStage2ObjectMap" )
    but we should do a proper walk of the modules in order
    """
    for modname in path.moduleNames():
        mod = getattr(process,modname)
        if mod.type_() == "HLTL1TSeed" and mod.L1GlobalInputTag.value()!="hltGtStage2ObjectMap":
            return parse_l1_logical_express(mod.L1SeedsLogicalExpression.value())
        
def get_datasets(process,path):
    """
    this parses the "datasets" pset to figure out the datasets the path belongs to
    datasets pset consists of cms.vstrings with the name of the param being the dataset
    and the contents of the cms.vstring being the paths of that dataset
    """
    datasets = []
    if hasattr(process,"datasets"):
        for dataset_name in process.datasets.parameterNames_():
            dataset_paths = getattr(process.datasets,dataset_name)
            if path.label() in dataset_paths:
                datasets.append(dataset_name)
    return datasets

def get_prescales(process,path):
    """
    this parses the prescale service to determine the prescales of the path
    it does not handle multiple prescale services (which would be an error regardless)
    a path has all 1s for prescales if its not found
    """
    prescale_service = [val for name,val in process.services_().items() if val.type_()=="PrescaleService"]
    if prescale_service:
        for para in prescale_service[0].prescaleTable:
            if para.pathName.value()==path.label():
                return para.prescales.value()
        return [1]*max(len(prescale_service[0].lvl1Labels),1)
    else:
        return [1]

def get_group(group_data,path):
    """
    auto groups triggers which differ only by thresholds together
    it does this by stripping numbers out of the name, a better solution could be found
    """
    path_name = path.label()
    group_name = re.sub(r'[0-9]+','',path_name)
    if group_name not in group_data:
        group_data[group_name] = len(group_data.keys())
    return group_data[group_name]
                
def get_physics_datasets(process,physics_streams):
    datasets = []
    if hasattr(process,"streams"):
        for physics_stream in physics_streams:
            if process.streams.hasParameter(physics_stream):
                datasets.extend(process.streams.getParameter(physics_stream).value())
        datasets = list(set(datasets))
    return datasets

def get_path_data(process,path,group_data,physics_datasets):
    data = OrderedDict()
    data['datasets'] = get_datasets(process,path)
    data['group'] = get_group(group_data,path)
    data['pags'] = []
    data['l1_seeds'] = get_l1_seeds(process,path)
    data['prescales'] = get_prescales(process,path)
    data['disable'] = 0
    data['physics'] = any(dataset in physics_datasets for dataset in data['datasets']) if physics_datasets else 1
    return data
