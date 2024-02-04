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
    this is a rather specific custom function which depends on the menu
    it assumes the main column is column 1
    [0] = column 1
    [1] = all triggers at ps==1 set to 0
    [2] = all triggers at ps!=1 set to 0
    [3] = all triggers at ps!=1 x2
    [4] = all triggers at ps!=1 x2 + paths disabled

    """
    
    disable_trigs = ["HLT_Ele28_WPTight_Gsf_v","HLT_Ele30_WPTight_Gsf_v","HLT_DoubleEle25_CaloIdL_MW_v","HLT_DiEle27_WPTightCaloOnly_L1DoubleEG_v","HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_v","HLT_Ele35_WPTight_Gsf_L1EGMT_v","HLT_Ele115_CaloIdVT_GsfTrkIdT_v","HLT_DoublePhoton70_v",
                     "HLT_TriplePhoton_35_35_5_CaloIdLV2_R9IdVL_v","HLT_TriplePhoton_30_30_10_CaloIdLV2_v","HLT_TriplePhoton_20_20_20_CaloIdLV2_v"
    ]

    disable_trigs.extend(["HLT_Mu50_v"])

    disable_trigs.extend(["HLT_AK8PFJet330_TrimMass30_PFAK8BoostedDoubleB_np2_v",
                          "HLT_AK8PFJet330_TrimMass30_PFAK8BoostedDoubleB_np4_v",
                          "HLT_AK8PFJet400_TrimMass30_v","HLT_AK8PFJet420_TrimMass30_v",
                          "HLT_CaloJet500_NoJetID_v","HLT_PFJet500_v","HLT_AK8PFJet500_v"])
                          
    
    disable_trigs.extend(["HLT_PFMETNoMu120_PFMHTNoMu120_IDTight_v","HLT_PFMET120_PFMHT120_IDTight_v",
                          "HLT_PFMETNoMu120_PFMHTNoMu120_IDTight_PFHT60_v","HLT_PFMET120_PFMHT120_IDTight_PFHT60_v","HLT_MonoCentralPFJet80_PFMETNoMu120_PFMHTNoMu120_IDTight_v","HLT_DiJet110_35_Mjj650_PFMET110_v","HLT_DiJet110_35_Mjj650_PFMET120_v"])

    disable_trigs.extend(["HLT_DoubleMediumChargedIsoPFTau35_Trk1_eta2p1_Reg_v",
                          "HLT_DoubleMediumChargedIsoPFTau35_Trk1_TightID_eta2p1_Reg_v",
                          "HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg_v",
                          "HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_TightID_eta2p1_Reg_v",
                          "HLT_DoubleMediumChargedIsoPFTauHPS40_Trk1_eta2p1_Reg_v",
                          "HLT_DoubleMediumChargedIsoPFTauHPS40_Trk1_TightID_eta2p1_Reg_v",
                          "HLT_DoubleTightChargedIsoPFTau35_Trk1_eta2p1_Reg_v",
                          "HLT_DoubleTightChargedIsoPFTau35_Trk1_TightID_eta2p1_Reg_v"])

    #for p in disable_trigs:
    #    print(p)

    prescale_by_10 = ["HLT_BTagMu_AK4DiJet20_Mu5_noalgo_v","HLT_BTagMu_AK4DiJet20_Mu5_v",
                      "HLT_BTagMu_AK4DiJet40_Mu5_noalgo_v","HLT_BTagMu_AK4DiJet40_Mu5_v",
                      "HLT_BTagMu_AK4DiJet70_Mu5_noalgo_v","HLT_BTagMu_AK4DiJet70_Mu5_v",
                      "HLT_BTagMu_AK4DiJet110_Mu5_noalgo_v","HLT_BTagMu_AK4DiJet110_Mu5_v",
                      "HLT_BTagMu_AK4DiJet170_Mu5_noalgo_v","HLT_BTagMu_AK4DiJet170_Mu5_v",
                      "HLT_BTagMu_AK8DiJet170_Mu5_noalgo_v","HLT_BTagMu_AK8DiJet170_Mu5_v",
                      ]
#    disable_trigs.extend(prescale_by_10)

    l1psedpath = ['HLT_Mu3_PFJet40_v', 'HLT_Mu7p5_L2Mu2_Jpsi_v', 'HLT_Mu7p5_L2Mu2_Upsilon_v', 'HLT_Mu7p5_Track2_Jpsi_v', 'HLT_Mu7p5_Track3p5_Jpsi_v', 'HLT_Mu7p5_Track7_Jpsi_v', 'HLT_Mu7p5_Track2_Upsilon_v', 'HLT_Mu7p5_Track3p5_Upsilon_v', 'HLT_Mu7p5_Track7_Upsilon_v', 'HLT_IsoMu20_v', 'HLT_UncorrectedJetE30_NoBPTX_v', 'HLT_UncorrectedJetE30_NoBPTX3BX_v', 'HLT_L1SingleMuCosmics_v', 'HLT_L2Mu10_NoVertex_NoBPTX_v', 'HLT_DiPFJetAve80_v', 'HLT_DiPFJetAve140_v', 'HLT_DiPFJetAve200_v', 'HLT_DiPFJetAve60_HFJEC_v', 'HLT_DiPFJetAve100_HFJEC_v', 'HLT_DiPFJetAve160_HFJEC_v', 'HLT_AK8PFJet140_v', 'HLT_AK8PFJet200_v', 'HLT_PFJet60_v', 'HLT_PFJet80_v', 'HLT_PFJet140_v', 'HLT_PFJet200_v', 'HLT_PFJetFwd60_v', 'HLT_PFJetFwd140_v', 'HLT_PFJetFwd200_v', 'HLT_AK8PFJetFwd60_v', 'HLT_AK8PFJetFwd200_v', 'HLT_PFHT180_v', 'HLT_PFHT250_v', 'HLT_PFHT370_v', 'HLT_PFHT430_v', 'HLT_Mu12_DoublePFJets40_CaloBTagDeepCSV_p71_v', 'HLT_Mu12_DoublePFJets100_CaloBTagDeepCSV_p71_v', 'HLT_Mu12_DoublePFJets200_CaloBTagDeepCSV_p71_v', 'HLT_Mu12_DoublePFJets350_CaloBTagDeepCSV_p71_v', 'HLT_DoublePFJets40_CaloBTagDeepCSV_p71_v', 'HLT_DoublePFJets200_CaloBTagDeepCSV_p71_v', 'HLT_DoublePFJets350_CaloBTagDeepCSV_p71_v', 'HLT_Mu17_TrkIsoVVL_v', 'HLT_Mu19_TrkIsoVVL_v', 'HLT_BTagMu_AK4DiJet40_Mu5_v', 'HLT_BTagMu_AK4DiJet70_Mu5_v', 'HLT_BTagMu_AK4DiJet110_Mu5_v', 'HLT_BTagMu_AK4DiJet170_Mu5_v', 'HLT_BTagMu_AK8DiJet170_Mu5_v', 'HLT_BTagMu_AK4DiJet40_Mu5_noalgo_v', 'HLT_BTagMu_AK4DiJet70_Mu5_noalgo_v', 'HLT_BTagMu_AK4DiJet110_Mu5_noalgo_v', 'HLT_BTagMu_AK4DiJet170_Mu5_noalgo_v', 'HLT_BTagMu_AK8DiJet170_Mu5_noalgo_v', 'HLT_Dimuon0_Jpsi_L1_NoOS_v', 'HLT_Dimuon0_Jpsi_NoVertexing_NoOS_v', 'HLT_Dimuon0_Jpsi_NoVertexing_v', 'HLT_Dimuon0_Upsilon_L1_4p5_v', 'HLT_Dimuon0_Upsilon_L1_4p5er2p0_v', 'HLT_Dimuon0_LowMass_L1_0er1p5_v', 'HLT_Dimuon0_LowMass_L1_4_v', 'HLT_Dimuon0_Upsilon_Muon_NoL1Mass_v', 'HLT_DoubleMu3_Trk_Tau3mu_NoL1Mass_v', 'HLT_Mu17_v', 'HLT_Mu19_v', 'HLT_Ele8_CaloIdL_TrackIdL_IsoVL_PFJet30_v', 'HLT_Ele12_CaloIdL_TrackIdL_IsoVL_PFJet30_v', 'HLT_Ele23_CaloIdL_TrackIdL_IsoVL_PFJet30_v', 'HLT_Ele8_CaloIdM_TrackIdM_PFJet30_v', 'HLT_Ele17_CaloIdM_TrackIdM_PFJet30_v', 'HLT_Ele23_CaloIdM_TrackIdM_PFJet30_v', 'HLT_Photon30_HoverELoose_v', 'HLT_CDC_L2cosmic_10_er1p0_v', 'HLT_HcalIsolatedbunch_v', 'HLT_ZeroBias_FirstCollisionAfterAbortGap_v', 'HLT_ZeroBias_LastCollisionInTrain_v', 'HLT_ZeroBias_FirstBXAfterTrain_v', 'HLT_MediumChargedIsoPFTau50_Trk30_eta2p1_1pr_v']


    prescale = input_ps[1]
    prescales = [prescale]
    
    unprescaled_path = prescale==1 and not pathname in l1psedpath
    if pathname in prescale_by_10:
        prescale = prescale*5
    

    prescales.append(prescale if not unprescaled_path else 0)
    prescales.append(prescale if unprescaled_path else 0)
    prescales.append(prescale if unprescaled_path else prescale*2)
    prescales.append(prescales[-1] if pathname not in disable_trigs else 0)
    return prescales
    

if __name__ == "__main__":
    

    parser = argparse.ArgumentParser(description='generates a rate ntup config from HLT file')
    parser.add_argument('cfg',help='input config')
    parser.add_argument('--out','-o',default="output.json",help="output file")
    args = parser.parse_args()
  
    process = CoreTools.load_cmssw_cfg(args.cfg)
    cfg_dict = OrderedDict()
    group_data = {}

    physics_streams = {"PhysicsMuons","PhysicsHadronsTaus","PhysicsEGamma","PhysicsCommissioning"}
    physics_datasets = RateCfgTools.get_physics_datasets(process,physics_streams)

    print(physics_datasets)

    for name,path in process.paths_().items():
        name_novers = TrigTools.strip_trig_ver(name)
        cfg_dict[name_novers] = RateCfgTools.get_path_data(process,path,group_data,physics_datasets)
        cfg_dict[name_novers]['prescales'] =  adjust_ps_cols(name_novers,cfg_dict[name_novers]['prescales'])
        
        

    with open(args.out,'w') as f:
        json.dump(cfg_dict,f,indent=0)
