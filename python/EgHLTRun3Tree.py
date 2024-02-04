import ROOT
import Analysis.HLTAnalyserPy.CoreTools as CoreTools
import Analysis.HLTAnalyserPy.TrigTools as TrigTools
import Analysis.HLTAnalyserPy.GenTools as GenTools
import Analysis.HLTAnalyserPy.L1Tools as L1Tools
from Analysis.HLTAnalyserPy.CoreTools import UnaryFunc
from Analysis.HLTAnalyserPy.NtupTools import TreeVar,TreeVecVar
from Analysis.HLTAnalyserPy.EvtWeights import EvtWeights
from Analysis.HLTAnalyserPy.EvtData import EvtData

from functools import partial
import itertools
from array import array
import six
import math

class EgHLTRun3Tree:
    def __init__(self,tree_name,evtdata,min_et=0.,weights=None):
        self.tree = ROOT.TTree(tree_name,'')
        self.l1seeded = True
        self.evtdata = evtdata
        self.min_et = min_et
        self.weights = weights
        self.initialised = False
        self.max_l1_upgrade = 60
        self.eg_extra_vars = {}
        self.eg_update_funcs = []

    def add_eg_vars(self,vars_):
        self.eg_extra_vars.update(vars_)

    def add_eg_update_funcs(self,update_funcs):
        self.eg_update_funcs.extend(update_funcs)

    def _init_tree(self,evtdata):
        self.evtdata = evtdata
        self.evtvars = [
            TreeVar(self.tree,"runnr/i",UnaryFunc("eventAuxiliary().run()")),
            TreeVar(self.tree,"lumiSec/i",UnaryFunc("eventAuxiliary().luminosityBlock()")),
            TreeVar(self.tree,"eventnr/i",UnaryFunc("eventAuxiliary().event()")),
            TreeVar(self.tree,"bx/I",UnaryFunc("eventAuxiliary().bunchCrossing()")),
           # TreeVar(self.tree,"time/I",UnaryFunc("eventAuxiliary().time().value()")),

        ]
        self.evtdatavars = []
        if self.weights:
            self.evtdatavars.append(TreeVar(self.tree,"weight/F",self.weights.weight)),
            self.evtdatavars.append(TreeVar(self.tree,"filtweight/F",self.weights.filtweight))
        #self.evtdatavars.append(TreeVar(self.tree,"genPtHat/F",UnaryFunc('get("geninfo").qScale()')))
        self.evtdatavars.append(TreeVar(self.tree,"nrHitsEB1GeV/F",UnaryFunc('get_fundtype("nrHitsEB1GeV_std")'))),
        self.evtdatavars.append(TreeVar(self.tree,"nrHitsEE1GeV/F",UnaryFunc('get_fundtype("nrHitsEE1GeV_std")'))),
#        self.evtdatavars.append(TreeVar(self.tree,"rho/F",UnaryFunc('get_fundtype("rho",0)')))

        #l1 ntup
        self.l1_upgrade_filler = ROOT.L1Analysis.L1AnalysisL1Upgrade()
        self.l1_upgrade_data = self.l1_upgrade_filler.getData()
        self.tree.Branch("L1Upgrade","L1Analysis::L1AnalysisL1UpgradeDataFormat",self.l1_upgrade_data,32000,3)

        #max_pthats = 400
        #self.nr_pthats = TreeVar(self.tree,"nrPtHats/i",UnaryFunc(partial(len)))
        #self.pthats = TreeVar(self.tree,"ptHats/F",None,maxsize=max_pthats,sizevar="nrPtHats")

        egobjnr_name = "nrEgs"
        max_egs = 200
        self.egobj_nr = TreeVar(self.tree,egobjnr_name+"/i",UnaryFunc(partial(len)))

        prod_tag = "" if self.l1seeded else "Unseeded"

        vars_ = {
            'et/F' : UnaryFunc(partial(ROOT.trigger.EgammaObject.et)),
            'energy/F' : UnaryFunc(partial(ROOT.trigger.EgammaObject.energy)),
            'rawEnergy/F' : UnaryFunc("superCluster().rawEnergy()"),
            'eta/F' : UnaryFunc(partial(ROOT.trigger.EgammaObject.eta)),
            'phi/F' : UnaryFunc(partial(ROOT.trigger.EgammaObject.phi)),
            'phiWidth/F':UnaryFunc("superCluster().phiWidth()"),
            # 'nrClus/I':UnaryFunc("superCluster().clusters().size()"),
            'nrClus/I':nrClusters,
            'seedId/i':UnaryFunc("superCluster().seed().seed().rawId()"),
            'seedDet/I':UnaryFunc("superCluster().seed().seed().det()"),
            'sigmaIEtaIEta/F' : UnaryFunc(partial(ROOT.trigger.EgammaObject.var,"hltEgammaClusterShape{}_sigmaIEtaIEta5x5".format(prod_tag),0)),
            'sigmaIPhiIPhi/F' : UnaryFunc(partial(ROOT.trigger.EgammaObject.var,"hltEgammaClusterShape{}_sigmaIPhiIPhi5x5".format(prod_tag),0)),
            'sigmaIEtaIEtaNoise/F' : UnaryFunc(partial(ROOT.trigger.EgammaObject.var,"hltEgammaClusterShape{}_sigmaIEtaIEta5x5NoiseCleaned".format(prod_tag),0)),
            'sigmaIPhiIPhiNoise/F' : UnaryFunc(partial(ROOT.trigger.EgammaObject.var,"hltEgammaClusterShape{}_sigmaIPhiIPhi5x5NoiseCleaned".format(prod_tag),0)),
            'ecalPFIsol/F' : UnaryFunc(partial(ROOT.trigger.EgammaObject.var,"hltEgammaEcalPFClusterIso{}".format(prod_tag),0)),
            'hcalPFIsol/F' : UnaryFunc(partial(ROOT.trigger.EgammaObject.var,"hltEgammaHcalPFClusterIso{}".format(prod_tag),0)),
            'trkIsol/F' : UnaryFunc(partial(ROOT.trigger.EgammaObject.var,"hltEgammaEleGsfTrackIso{}".format(prod_tag),0)),
            'trkChi2/F' : UnaryFunc(partial(ROOT.trigger.EgammaObject.var,"hltEgammaGsfTrackVars{}_Chi2".format(prod_tag),0)),
            'trkMissHits/F' : UnaryFunc(partial(ROOT.trigger.EgammaObject.var,"hltEgammaGsfTrackVars{}_MissingHits".format(prod_tag),0)),
            'trkValidHits/F' : UnaryFunc(partial(ROOT.trigger.EgammaObject.var,"hltEgammaGsfTrackVars{}_ValidHits".format(prod_tag),0)),
            'invESeedInvP/F' : UnaryFunc(partial(ROOT.trigger.EgammaObject.var,"hltEgammaGsfTrackVars{}_OneOESeedMinusOneOP".format(prod_tag),0)),
            'invEInvP/F' : UnaryFunc(partial(ROOT.trigger.EgammaObject.var,"hltEgammaGsfTrackVars{}_OneOESuperMinusOneOP".format(prod_tag),0)),
            'trkDEta/F' : UnaryFunc(partial(ROOT.trigger.EgammaObject.var,"hltEgammaGsfTrackVars{}_Deta".format(prod_tag),0)),
            'trkDEtaSeed/F' : UnaryFunc(partial(ROOT.trigger.EgammaObject.var,"hltEgammaGsfTrackVars{}_DetaSeed".format(prod_tag),0)),
            'trkDPhi/F' : UnaryFunc(partial(ROOT.trigger.EgammaObject.var,"hltEgammaGsfTrackVars{}_Dphi".format(prod_tag),0)),
            'trkNrLayerIT/F' : UnaryFunc(partial(ROOT.trigger.EgammaObject.var,'hltEgammaGsfTrackVars{}_NLayerIT'.format(prod_tag),0)),
            'pms2/F' : UnaryFunc(partial(ROOT.trigger.EgammaObject.var,'hltEgammaPixelMatchVars{}_s2'.format(prod_tag),0)),
            'hcalHForHoverE/F' : UnaryFunc(partial(ROOT.trigger.EgammaObject.var,'hltEgammaHoverE{}'.format(prod_tag),0)),

            'bestTrkChi2/F' : UnaryFunc(partial(ROOT.trigger.EgammaObject.var,'hltEgammaBestGsfTrackVars{}_Chi2'.format(prod_tag),0)),
            'bestTrkDEta/F' : UnaryFunc(partial(ROOT.trigger.EgammaObject.var,'hltEgammaBestGsfTrackVars{}_Deta'.format(prod_tag),0)),
            'bestTrkDEtaSeed/F' : UnaryFunc(partial(ROOT.trigger.EgammaObject.var,'hltEgammaBestGsfTrackVars{}_DetaSeed'.format(prod_tag),0)),
            'bestTrkDPhi/F' : UnaryFunc(partial(ROOT.trigger.EgammaObject.var,'hltEgammaBestGsfTrackVars{}_Dphi'.format(prod_tag),0)),
            'bestTrkMissHits/F' : UnaryFunc(partial(ROOT.trigger.EgammaObject.var,'hltEgammaBestGsfTrackVars{}_MissingHits'.format(prod_tag),0)),
            'bestTrkNrLayerIT/F' : UnaryFunc(partial(ROOT.trigger.EgammaObject.var,'hltEgammaBestGsfTrackVars{}_NLayerIT'.format(prod_tag),0)),
            'bestTrkESeedInvP/F' : UnaryFunc(partial(ROOT.trigger.EgammaObject.var,'hltEgammaBestGsfTrackVars{}_OneOESeedMinusOneOP'.format(prod_tag),0)),
            'bestTrkInvEInvP/F' : UnaryFunc(partial(ROOT.trigger.EgammaObject.var,'hltEgammaBestGsfTrackVars{}_OneOESuperMinusOneOP'.format(prod_tag),0)),
            'bestTrkValitHits/F' : UnaryFunc(partial(ROOT.trigger.EgammaObject.var,'hltEgammaBestGsfTrackVars{}_ValidHits'.format(prod_tag),0)),
            'clusterMaxDR/F' : cal_cluster_maxdr,
            'r9Frac/F' : CoreTools.UnaryFunc(partial(cal_r9,evtdata,frac=True)),
            'r9Full/F' : CoreTools.UnaryFunc(partial(cal_r9,evtdata,frac=False)),
            'isEB/b' : is_eb,
            'isEE/b' : is_ee,
        }
        vars_.update(self.eg_extra_vars)

        self.egobj_vars = []
        for name,func in six.iteritems(vars_):
            self.egobj_vars.append(TreeVar(self.tree,"eg_"+name,func,max_egs,egobjnr_name))
        self.egobj_vars.append(TreeVecVar(self.tree,"eg_scRegFeatures/float",CoreTools.UnaryFunc(partial(getSCRegFeatures,self.evtdata))))

        gen_vars_names = {
            'energy/F' : UnaryFunc(partial(ROOT.reco.GenParticle.energy)),
            'pt/F' : UnaryFunc(partial(ROOT.reco.GenParticle.pt)),
            'et/F' : UnaryFunc(partial(ROOT.reco.GenParticle.et)),
            'eta/F' : UnaryFunc(partial(ROOT.reco.GenParticle.eta)),
            'phi/F' : UnaryFunc(partial(ROOT.reco.GenParticle.phi)),
            'vz/F' : UnaryFunc(partial(ROOT.reco.GenParticle.vz)),
        }
        self.gen_vars = []
        for name,func in six.iteritems(gen_vars_names):
            self.gen_vars.append(TreeVar(self.tree,"eg_gen_"+name,func,max_egs,egobjnr_name))

        l1eg_vars_names = {
            'et/F' : UnaryFunc("et()"),
            'eta/F' : UnaryFunc("eta()"),
            'phi/F' : UnaryFunc("phi()"),
            'hwEt/F' : UnaryFunc("hwPt()"),
            'hwEta/F' : UnaryFunc("hwEta()"),
            'hwPhi/F' : UnaryFunc("hwPhi()"),
            'hwQual/F' : UnaryFunc("hwQual()"),
            'iso/F' : UnaryFunc("hwIso()"),
            'isoEt/F' : UnaryFunc("isoEt()"),
            'nTT/F' : UnaryFunc("nTT()"),
            'footprintEt/F' : UnaryFunc("footprintEt()"),
            'shape/F' : UnaryFunc("shape()"),
            'towerHoE/F' : UnaryFunc("towerHoE()")
        }

        self.l1eg_vars = []
        for name,func in six.iteritems(l1eg_vars_names):
            self.l1eg_vars.append(TreeVar(self.tree,"eg_l1eg_"+name,func,max_egs,egobjnr_name))

        trig_names = ["Gen_QCDMuGenFilter",
                      "Gen_QCDBCToEFilter",
                      "Gen_QCDEmEnrichingFilter",
                      "Gen_QCDEmEnrichingNoBCToEFilter"]
        self.trig_res = TrigTools.TrigResults(trig_names)
        self.trig_vars = []
        for name in trig_names:
            self.trig_vars.append(TreeVar(self.tree,"path_{}/b".format(name),
                                          UnaryFunc(partial(TrigTools.TrigResults.result,name))))


        self.initialised = True

    def fill(self):
        if not self.initialised:
            self._init_tree(self.evtdata)

        for var_ in self.evtvars:
            var_.fill(self.evtdata.event.object())
        for var_ in self.evtdatavars:
            var_.fill(self.evtdata)

      #  pusum_intime = [x for x in self.evtdata.get("pu_sum") if x.getBunchCrossing()==0]
      #  pt_hats = [x for x in pusum_intime[0].getPU_pT_hats()]
      #  pt_hats.append(self.evtdata.get("geninfo").qScale())
      #  pt_hats.sort(reverse=True)
      #  self.nr_pthats.fill(pt_hats)
      #  for pt_hat_nr,pt_hat in enumerate(pt_hats):
      #      self.pthats.fill(pt_hat,pt_hat_nr)

        egobjs_raw = self.evtdata.get("egtrigobjs_l1seed") if self.l1seeded else self.evtdata.get("egtrigobjs")
        egobjs = [eg for eg in egobjs_raw if eg.et()>self.min_et]
        egobjs.sort(key=ROOT.trigger.EgammaObject.et,reverse=True)
        for obj in egobjs:
            for update_func in self.eg_update_funcs:
                update_func(obj)

        genparts = self.evtdata.get("genparts")
        l1egs  = self.evtdata.get("l1egamma")

        self.egobj_nr.fill(egobjs)
        for var_ in itertools.chain(self.gen_vars,self.l1eg_vars):
            var_.clear()

        gen_eles = GenTools.get_genparts(self.evtdata.get("genparts"),
                                         pid=22,antipart=True,
                                         status=GenTools.PartStatus.PREFSR)


        for objnr,obj in enumerate(egobjs):
            for var_ in self.egobj_vars:
                var_.fill(obj,objnr)

            gen_obj = CoreTools.get_best_dr_match(obj,gen_eles,0.1)
            if gen_obj:
                for var_ in self.gen_vars:
                    var_.fill(gen_obj,objnr)

            l1eg_obj = CoreTools.get_best_dr_match(obj,l1egs,0.2)
            if l1eg_obj:
                for var_ in self.l1eg_vars:
                    var_.fill(l1eg_obj,objnr)


        self.trig_res.fill(self.evtdata)
        for var_ in self.trig_vars:
            var_.fill(self.trig_res)

        self.l1_upgrade_filler.Reset()
        self.l1_upgrade_filler.SetEm(self.evtdata.get("l1egamma"),self.max_l1_upgrade)
        self.l1_upgrade_filler.SetTau(self.evtdata.get("l1tau"),self.max_l1_upgrade)
        self.l1_upgrade_filler.SetJet(self.evtdata.get("l1jet"),self.max_l1_upgrade)
        self.l1_upgrade_filler.SetSum(self.evtdata.get("l1sum"),self.max_l1_upgrade)
        self.l1_upgrade_filler.SetMuon(self.evtdata.get("l1muon"),self.max_l1_upgrade)

        self.tree.Fill()


# def is_eb(obj):
#     eb = False
#     sc = obj.superCluster()
#     sceta = abs(sc.eta())
#     if sceta<1.479:
#        eb = True
#     return eb

def is_eb(obj):
    eb = False
    if obj.superCluster().seed().hitsAndFractions()[0].first.subdetId() == 1:
       eb = True
    return eb

# def is_ee(obj):
#     ee = False
#     sc = obj.superCluster()
#     sceta = abs(sc.eta())
#     if sceta>1.479:
#        ee = True
#     return ee

def is_ee(obj):
    ee = False
    if obj.superCluster().seed().hitsAndFractions()[0].first.subdetId() == 2:
       ee = True
    return ee

def nrClusters(obj):
    return obj.superCluster().clusters().size() -1

def cal_cluster_maxdr(obj):
    max_dr2 = 0.
    sc = obj.superCluster()
    seed_eta = sc.seed().eta()
    seed_phi = sc.seed().phi()
    for clus in sc.clusters():
        if clus == sc.seed():
            continue
        dr2 = ROOT.reco.deltaR2(clus.eta(),clus.phi(),seed_eta,seed_phi)
        max_dr2 = max(max_dr2,dr2)

    #ECAL takes 999. if not other cluster for maxDR2
    if max_dr2==0. and sc.seed().seed().det()==ROOT.DetId.Ecal:
        return 999.
    else:
        return math.sqrt(max_dr2)

def get_hit_frac(detid,hits_and_fracs):
    for hit_and_frac  in hits_and_fracs:
        if hit_and_frac.first==detid:
            return hit_and_frac.second
    return 0.

def cal_r9(obj,evtdata,frac=True):
    sc = obj.superCluster()
    seed_id = sc.seed().seed()
    if seed_id.det()!=ROOT.DetId.Ecal or sc.rawEnergy()==0:
        return 0
    e3x3 = 0.
    if seed_id.subdetId()==1:
        seed_id = ROOT.EBDetId(seed_id)
        hits = evtdata.get("ebhits_std")
    else:
        seed_id = ROOT.EEDetId(seed_id)
        hits = evtdata.get("eehits_std")

    for local_ieta in [-1,0,1]:
        for local_iphi in [-1,0,1]:
            hit_id = seed_id.offsetBy(local_ieta,local_iphi)
            if hit_id.rawId()!=0:
                hit = hits.find(hit_id)
                if hit!=hits.end():
                    hit_energy = hit.energy()
                    if frac:
                        hit_energy *=get_hit_frac(hit_id,sc.seed().hitsAndFractions())
                    e3x3+=hit_energy
    return e3x3/sc.rawEnergy()

def getSCRegFeatures(obj,evtdata):
    region_label = "EB" if is_eb(obj) else "EE"
    features_vec = ROOT.std.vector("float")()
    scs =  evtdata.get(f"scEnergyCorr{region_label}")
    sc_features = evtdata.get(f"scEnergyCorr{region_label}Features")
    if scs is None or sc_features is None:
        return features_vec

    for sc_indx,sc in enumerate(scs):
        if sc.seed().seed() == obj.superCluster().seed().seed():
            for feature in sc_features.begin()[sc_indx]:
                features_vec.push_back(feature)

    return features_vec
