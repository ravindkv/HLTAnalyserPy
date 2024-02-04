import ROOT

ROOT.gROOT.SetBatch(True)
import numpy as np
import sys

# InputFile = "/afs/cern.ch/user/r/rasharma/work/EGamma-POG/HLT_tasks/regression/GetReducedNtuples/CMSSW_12_0_1/src/Updated.root"
# InputFile = "/afs/cern.ch/user/r/rasharma/work/EGamma-POG/HLT_tasks/regression/GetReducedNtuples/CMSSW_12_0_1/src/Updated_v1.root"
# InputFile = "/eos/cms//store/group/phys_egamma/ec/Run3Studies/SCRegression/CMSSW_Var_ValidationCheck.root"
# InputFile = "/eos/cms//store/group/phys_egamma/ec/Run3Studies/SCRegression/CMSSW_Var_ValidationCheck_Small.root"
# InputFile = "/afs/cern.ch/user/r/rasharma/work/EGamma-POG/HLT_tasks/regression/GetReducedNtuples/CMSSW_12_0_1/src/test.root"
# InputFile = "/afs/cern.ch/user/r/rasharma/work/EGamma-POG/HLT_tasks/regression/GetReducedNtuples/CMSSW_12_0_1/src/test_v1.root"
# InputFile = "/afs/cern.ch/user/r/rasharma/work/EGamma-POG/HLT_tasks/regression/GetReducedNtuples/CMSSW_12_0_1/src/test_v2.root"
# InputFile = "/afs/cern.ch/user/r/rasharma/work/EGamma-POG/HLT_tasks/regression/GetReducedNtuples/CMSSW_12_0_1/src/test_v2_RemovedGenL1eg_v2.root"
# InputFile = "/afs/cern.ch/user/r/rasharma/work/EGamma-POG/HLT_tasks/regression/GetReducedNtuples/CMSSW_12_0_1/src/test_check.root"
InputFile = "/afs/cern.ch/user/r/rasharma/work/EGamma-POG/HLT_tasks/regression/GetReducedNtuples/CMSSW_12_0_1/src/NoET_Cut.root"
# InputFile = "/afs/cern.ch/user/r/rasharma/work/EGamma-POG/HLT_tasks/regression/GetReducedNtuples/CMSSW_12_0_1/src/Default.root"
Tree1 = "egHLTRun3Tree"

inFile = ROOT.TFile(InputFile)
inTree = inFile.Get(Tree1)

print("Total entries: "+str(inTree.GetEntries()))

nEntries = inTree.GetEntries()
print("Total entries: "+str(nEntries))
nEntriesStart = 0
# nEntriesStart = 50
# nEntries = 100
counterOfMismatch = 0
counterOfFailed = 0
counterBlankCMSSWVars = 0
ifcounterOfFailedPrint = 0
ifcounterOfMismatchPrint = 0
# import pprint
# pp = pprint.PrettyPrinter(indent=4)
# print("|{:7} | ({:13}) | ({:13})|".format("Entries", "CMSSW Var","HLTAnalyzer Var"))
# print("|{:7} | ({:13}) | ({:13})|".format("---", "---","---"))

print("|{:7} | (nF,nE) | {:21} | {:17} | {:15} | {:15} | ifmatch |".format("Entries", "(pT1, pT2)","(eta1,eta2)", "CMSSW Var","HLTAnalyzer Var"))
print("|{:7} | {:7} | {:21} | {:17} | {:15} | {:15} | --- | ".format("---", "---", "---","---","---","---"))
for nentries_ in range(nEntriesStart, nEntries):
    inTree.GetEntry(nentries_)
    ifmatch = "TRUE"

    # print("Entries: "+str(nentries_))
    # print(inTree.eg_scRegFeatures)
    if inTree.eg_scRegFeatures == {}:
        counterBlankCMSSWVars = counterBlankCMSSWVars+1
        continue;
    # print("nEntries: {} \n\t{}\n\t{}".format(nentries_, inTree.eg_scRegFeatures[0], inTree.eg_scRegFeatures[1]))
    # for nele in range(inTree.nrEgs):
        # print("\t{}, {}, {}, {}, {}, {}, {}".format(inTree.nrHitsEB1GeV+inTree.nrHitsEE1GeV,
        #         inTree.eg_eta[nele], inTree.eg_phiWidth[nele],
        #         inTree.eg_r9Frac[nele], inTree.eg_nrClus[nele],
        #         inTree.eg_clusterMaxDR[nele], inTree.eg_rawEnergy[nele]
        # ))

    scArray0 = []
    scArray1 = []
    NtupleArray0 = []
    NtupleArray1 = []
    NtupleArray2 = []
    NtupleArray3 = []

    for items_ in inTree.eg_scRegFeatures[0]:
        scArray0.append(round(float(items_),4))
    for items_ in inTree.eg_scRegFeatures[1]:
        scArray1.append(round(float(items_),4))

    # Append ntuple arrays:
    nele = inTree.nrEgs
    # for nele_ in range(0,nele):
    #     if inTree.eg_r9Frac[nele_] > 1.0:
    #         print("r9 is > 1.0: "+str(inTree.eg_r9Frac[nele_] ))
    #         sys.exit()
    if nele>0:
        NtupleArray0.append(round(float(inTree.nrHitsEB1GeV+inTree.nrHitsEE1GeV), 4))
        NtupleArray0.append(round(float(inTree.eg_eta[0]), 4))
        NtupleArray0.append(round(float(inTree.eg_phiWidth[0]), 4))
        NtupleArray0.append(round(float(inTree.eg_r9Frac[0]), 4))
        NtupleArray0.append(round(float(inTree.eg_nrClus[0]), 4))
        NtupleArray0.append(round(float(inTree.eg_clusterMaxDR[0]), 4))
        NtupleArray0.append(round(float(inTree.eg_rawEnergy[0]), 4))

    if nele>1:
        NtupleArray1.append(round(float(inTree.nrHitsEB1GeV+inTree.nrHitsEE1GeV), 4))
        NtupleArray1.append(round(float(inTree.eg_eta[1]), 4))
        NtupleArray1.append(round(float(inTree.eg_phiWidth[1]), 4))
        NtupleArray1.append(round(float(inTree.eg_r9Frac[1]), 4))
        NtupleArray1.append(round(float(inTree.eg_nrClus[1]), 4))
        NtupleArray1.append(round(float(inTree.eg_clusterMaxDR[1]), 4))
        NtupleArray1.append(round(float(inTree.eg_rawEnergy[1]), 4))

    if nele>2:
        NtupleArray2.append(round(float(inTree.nrHitsEB1GeV+inTree.nrHitsEE1GeV), 4))
        NtupleArray2.append(round(float(inTree.eg_eta[2]), 4))
        NtupleArray2.append(round(float(inTree.eg_phiWidth[2]), 4))
        NtupleArray2.append(round(float(inTree.eg_r9Frac[2]), 4))
        NtupleArray2.append(round(float(inTree.eg_nrClus[2]), 4))
        NtupleArray2.append(round(float(inTree.eg_clusterMaxDR[2]), 4))
        NtupleArray2.append(round(float(inTree.eg_rawEnergy[2]), 4))

    # scArray0 = []
    # scArray1 = []
    # NtupleArray0 = []
    # NtupleArray1 = []

    a1 = np.array(scArray0)
    a2 = np.array(scArray1)
    b1 = np.array(NtupleArray0)
    b2 = np.array(NtupleArray1)
    b3 = np.array(NtupleArray2)

    if (len(a1)<7 or len(a2)<7 or len(b1) < 7 or len(b2) < 7):
        if ifcounterOfFailedPrint: print("Entries: "+str(nentries_))
        if ifcounterOfFailedPrint: print("{:15}: {}".format("CMSSW Var", scArray0))
        if ifcounterOfFailedPrint: print("{:15}: {}".format("HLTAnalyzer Var", NtupleArray0))
        if ifcounterOfFailedPrint: print("==")
        if ifcounterOfFailedPrint: print("{:15}: {}".format("CMSSW Var", scArray1))
        if ifcounterOfFailedPrint: print("{:15}: {}".format("HLTAnalyzer Var", NtupleArray1))
        counterOfFailed  = counterOfFailed + 1
        ifmatch = "FALSE"
        if (not ifcounterOfFailedPrint): print("|{:7}| ({},{}) |({:9},{:9}) | ({:7},{:7}) |({:6},{:6}) | ({:6},{:6}) | {} |".format(nentries_, len(inTree.eg_scRegFeatures), nele , scArray0[6], scArray1[6], scArray0[1], scArray1[1], scArray0[3],scArray1[3], "-", "-", ifmatch))
        continue

    if ( not (np.array_equal(a1,b1) or np.array_equal(a2,b2))):
        if ifcounterOfMismatchPrint: print("#"*51+"\nEntries: "+str(nentries_))
        if ifcounterOfMismatchPrint: print("{:15}: {}".format("CMSSW Var", scArray0))
        if ifcounterOfMismatchPrint: print("{:15}: {}".format("HLTAnalyzer Var", NtupleArray0))
        if ifcounterOfMismatchPrint: print("==")
        if ifcounterOfMismatchPrint: print("{:15}: {}".format("CMSSW Var", scArray1))
        if ifcounterOfMismatchPrint: print("{:15}: {}".format("HLTAnalyzer Var", NtupleArray1))
        if ifcounterOfMismatchPrint: print("==")
        if ifcounterOfMismatchPrint: print("{:15}: {}".format("HLTAnalyzer Var", NtupleArray2))
        if ifcounterOfMismatchPrint: print(len(inTree.eg_scRegFeatures))
        if ifcounterOfMismatchPrint: print(inTree.eg_scRegFeatures)
        if ifcounterOfMismatchPrint: print("The two array is not same....")
        ifmatch = "FALSE"
        counterOfMismatch  = counterOfMismatch + 1
        if (not ifcounterOfMismatchPrint): print("|{:7}| ({},{}) |({:9},{:9}) | ({:7},{:7}) |({:6},{:6}) | ({:6},{:6}) | {} |".format(nentries_, len(inTree.eg_scRegFeatures), nele , scArray0[6], scArray1[6], scArray0[1], scArray1[1], scArray0[3],scArray1[3], NtupleArray0[3], NtupleArray1[3], ifmatch))
        continue
        # sys.exit()
    # print("|{:7}| ({},{}) |({:9},{:9}) | ({:7},{:7}) |({:6},{:6}) | ({:6},{:6}) | {} |".format(nentries_, len(inTree.eg_scRegFeatures), nele , scArray0[6], scArray1[6], scArray0[1], scArray1[1], scArray0[3],scArray1[3], NtupleArray0[3], NtupleArray1[3], ifmatch))

print("Success...")
print("Total counterOfMismatch = "+str(counterOfMismatch))
print("Total counterOfFailed = "+str(counterOfFailed))
print("Total counterBlankCMSSWVars = "+str(counterBlankCMSSWVars))
print("total misMatch = "+str(counterOfMismatch+counterOfFailed)+"/"+str(nEntries)+"\t("+str(((counterOfMismatch+counterOfFailed)/nEntries)*100)+")")
