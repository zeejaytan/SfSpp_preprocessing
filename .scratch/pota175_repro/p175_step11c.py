# 175 step11c: correct-notion coverage of parent clouds (G0 -> class min).
import numpy as np
H = "C:/PR/SfSpp_preprocessing/.scratch/pota175_repro"
P = "C:/PR/SfSpp_preprocessing"
log = open(H + "/p175_step11c.txt", "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
d = np.load(P + "/.scratch/pota173_repro/p173_bag.npz", allow_pickle=True)
BAG, G0 = d["BAG"], d["G0"]
plab = np.load(H+"/p175_parentface.npy")
DI = np.sqrt(((G0[:,None,:]-BAG[plab==-1][None,:,:])**2).sum(-1)).min(1)
DO = np.sqrt(((G0[:,None,:]-BAG[plab==1][None,:,:])**2).sum(-1)).min(1)
DF = np.sqrt(((G0[:,None,:]-BAG[plab==0][None,:,:])**2).sum(-1)).min(1)
DT = np.minimum(DI, DF)
for nm, DD in [("parent-inner",DI),("parent-outer",DO),("parent-fold",DF),("TRUE-cand inner+fold",DT)]:
    say("%s: cover=%d/211 med-seat=%.3f" % (nm, int((DD<2).sum()), float(np.median(DD))))
miss = sorted(np.where(DT>=2)[0].tolist())
say("TRUE-missing stations (%d): %s" % (len(miss), miss))
say("their outer-dot distance: min=%.2f med=%.2f" % (float(DO[miss].min()) if miss else -1, float(np.median(DO[miss])) if miss else -1))
log.close(); print("step11c done")
