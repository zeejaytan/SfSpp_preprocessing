# 175 step8b: flips-floor with CORRECT coverage notion (G0 -> class min distance).
import numpy as np
H = "C:/PR/SfSpp_preprocessing/.scratch/pota175_repro"
log = open(H + "/p175_step8b.txt", "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
d = np.load("C:/PR/SfSpp_preprocessing/.scratch/pota173_repro/p173_bag.npz", allow_pickle=True)
BAG, G0 = d["BAG"], d["G0"]
N = len(G0)
z = np.load(H + "/p175_probe0.npz")
alB = z["alB"]
TRUE = np.load(H + "/p175_mask_true.npy")
inner = (alB < -0.5); edge = (alB >= -0.5) & TRUE
DI = np.sqrt(((G0[:,None,:]-BAG[inner][None,:,:])**2).sum(-1)).min(1)
DE = np.sqrt(((G0[:,None,:]-BAG[edge][None,:,:])**2).sum(-1)).min(1)
covI = DI < 2; covE = DE < 2
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
rE = runs(onlyE); rI = runs(onlyI)
say("edge-only runs (%d): %s" % (len(rE), rE))
say("inner-only runs (%d): %s" % (len(rI), rI[:20]))
say("FLOOR: any single walk covering all 211 must switch sub-tracks >= %d times (enter+leave each edge-only run)" % (2*len(rE)-2))
# where do onlyE stations sit vs the spread2 walk -- does it switch there?
log.close(); print("step8b done")
