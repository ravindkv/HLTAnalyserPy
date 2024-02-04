import ROOT
import Analysis.HLTAnalyserPy.CoreTools as CoreTools
import argparse
import json
import re
import time
from collections import OrderedDict
import math


def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
    return [int(text) if text.isdigit() else text.lower()
            for text in _nsre.split(s)]  

def make_path2indx(path_names_vec):
    path2indx  = {}
    for indx,name in enumerate(path_names_vec):
        path2indx[strip_path_version(str(name))] = indx
    return path2indx


def get_match_paths(paths,patterns):
    matched = []
    for path  in paths:
        for pattern in patterns:
            if re.match(pattern,str(path.name())):
                matched.append(path)
                break
    return matched

def print_paths(paths,coll,norm):
    print("   {:80}      rate (Hz)   pure rate (Hz)    ps".format("path"))
    for path in paths:
        nrpassed = path.nrPassed()[coll]
        nrpassed_uniq = path.nrUnique()[coll]
        prescale  = path.prescales()[coll]
        if prescale==0: 
            continue
        print_str = "   {:80} : {:5.1f} +/- {:2.1f} {:5.1f} +/- {:2.1f}   {:6}"

        print(print_str.format(path.name(),
                               nrpassed*norm,
                               math.sqrt(nrpassed)*norm, 
                               nrpassed_uniq*norm,
                               math.sqrt(nrpassed_uniq)*norm, 
                               prescale))

def get_overlaps(path,paths,coll,cutoff=0.1):
    overlaps = sorted([[paths[i].name(),v] for i,v in enumerate(path.overlaps()[coll]) if paths[i].name()!=path.name()],key=lambda x:x[1],reverse=True)

    overlaps_percent = sorted([[paths[i].name(),v/path.nrPassed()[coll]] for i,v in enumerate(path.overlaps()[coll]) if paths[i].name()!=path.name()],key=lambda x:x[1],reverse=True)
    
    overlaps_str = ["{} {:.2f}".format(x[0],x[1]) for x in overlaps_percent if x[1]>cutoff]

    return overlaps_str

def print_dataset(trigmenu,name,coll,norm,key=None):
    dataset = [d for d in trigmenu.datasets() if str(d.name())==name]
    if not dataset:
        return
    dataset = dataset[0]
    
    print("nr pass {}  rate {:3.1f} Hz".format(dataset.nrPassed()[coll],dataset.nrPassed()[coll]*norm))
    
    paths = [trigmenu.paths()[i] for i in dataset.pathIndices()]
    if key:
        paths.sort(key=key)
    else:
        paths.sort(key=lambda x: x.nrPassed()[coll])

    print_paths(paths,coll,norm)
    


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='analyses HLT rate')
    parser.add_argument('in_filename',help='input filename')
    args = parser.parse_args()

    rootfile = ROOT.TFile.Open(args.in_filename,"READ")
    trigmenu = rootfile.trigMenu
    
    nr_ls = 97*8
    ls_length = 23.31
    prescale = 1110
    inst_lumi_actual = 1.71
    inst_lumi_target = 1.9
    normfac = inst_lumi_target/inst_lumi_actual*prescale/(nr_ls*ls_length)
    

    double_eg = [r'HLT_DoubleEle[0-9]+_CaloIdL_MW_v',
                 r'HLT_DiEle27_WPTightCaloOnly_L1DoubleEG_v',
                 r'^(HLT_Diphoton30_18_R9IdL_AND_HE_AND_IsoCaloId_NoPixelVeto_)',
                 r'HLT_Diphoton30_22_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass[0-9]+_v',
                 r'HLT_Diphoton30PV_18PV_R9Id_AND_IsoCaloId_AND_HE_R9Id_(No|)PixelVeto_Mass55_v',
                 r'HLT_DiSC30_18_EIso_AND_HE_Mass70_v',
                 r'^(HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_)',
                 ]
                 
    
    physics_datasets = ['JetHT', 'NoBPTX', 'DoubleMuon', 'MuOnia', 'HcalNZS', 'Cosmics', 'BTagMu', 'MuonEG', 'HLTPhysics', 'DoubleMuonLowMass', 'SingleMuon', 'DisplacedJet', 'ZeroBias', 'EGamma', 'Tau', 'IsolatedBunch', 'Charmonium', 'MET', 'Commissioning']
