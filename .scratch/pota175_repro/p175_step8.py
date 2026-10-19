# 175 step8: flips-floor analysis -- per-station sub-track coverage runs (ruler accounting only).
import numpy as np
H = "C:/PR/SfSpp_preprocessing/.scratch/pota175_repro"
log = open(H + "/p175_step8.txt", "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
d = np.load("C:/PR/SfSpp_preprocessing/.scratch/pota173_repro/p173_bag.npz", allow_pickle=True)
BAG, G0 = d["BAG"], d["G0"]
N = len(G0)
z = np.load(H + "/p175_probe0.npz")
alB, sta, dmin = z["alB"], z["sta"], z["dmin"]
TRUE = np.load(H + "/p175_mask_true.npy")
inner = alB < -0.5; edge = (alB >= -0.5) & TRUE
covI = np.zeros(N, bool); covE = np.zeros(N, bool)
covI[np.unique(sta[inner & (dmin<2)])] = True
covE[np.unique(sta[edge & (dmin<2)])] = True
say("stations: inner-covered=%d edge-covered=%d union=%d neither=%d" % (
    int(covI.sum()), int(covE.sum()), int((covI|covE).sum()), int((~(covI|covE)).sum())))
onlyI = covI & ~covE; onlyE = covE & ~covI; both = covI & covE
say("inner-only=%d edge-only=%d both=%d" % (int(onlyI.sum()), int(onlyE.sum()), int(both.sum())))
def runs(m):
    idx = sorted(np.where(m)[0].tolist()); out = []
    if not idx: return out
    a=idx[0]; p=idx[0]
    for q in idx[1:]:
        if q==p+1: p=q
        else: out.append((a,p)); a=q; p=q
    out.append((a,p)); return out
rI = runs(onlyI); rE = runs(onlyE); rB = runs(both)
say("inner-only runs (%d): %s" % (len(rI), rI))
say("edge-only runs (%d): %s" % (len(rE), rE))
say("both-covered runs (%d): %s" % (len(rB), rB))
# flips floor: a single walk covering all stations must enter each edge-only run from inner (or start/end there)
# and leave it: >= 2 switches per interior edge-only run (>=1 if run touches station 0/210 wrap or walk endpoint)
# same for inner-only runs if walking edge-first. Lower bound = 2*min(#edge-only runs, #inner-only runs)-ish; state simply:
say("mandatory-handoff lower bound: >= %d switches (2 per edge-only run x %d runs, minus wrap sharing)" % (2*len(rE)-2, len(rE)))
np.savez(H+"/p175_floor.npz", covI=covI, covE=covE)
log.close(); print("step8 done")
