# 175 step11b: U-row origin matching with correct tolerance (noise floor 5.8e-4).
import numpy as np
from scipy.spatial import cKDTree as KD
H = "C:/PR/SfSpp_preprocessing/.scratch/pota175_repro"
P = "C:/PR/SfSpp_preprocessing"
log = open(H + "/p175_step11b.txt", "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
def load_ply_x(p):
    XX = []
    for ln in open(p):
        s = ln.strip()
        if not s or s[0] == '#' or s.startswith(('ply','format','element','property','end_header','comment')): continue
        f = s.split()
        try: vals = list(map(float, f[:3]))
        except ValueError: continue
        XX.append(vals)
    return np.array(XX)
d = np.load(P + "/.scratch/pota173_repro/p173_bag.npz", allow_pickle=True)
BAG, G0, TF = d["BAG"], d["G0"], d["TF"]
R, t = TF[:3,:3], TF[:3,3]
U = load_ply_x(P + "/.scratch/pota163_repro/inputs/Pot_C_Piece_01_unclustered.ply")
KU = KD(U)
Bloc = (BAG - t) @ R
drow, jrow = KU.query(Bloc, k=2)
say("match dist: nearest max=%.2e | second-nearest min=%.3f (uniqueness gap)" % (float(drow[:,0].max()), float(drow[:,1].min())))
okm = drow[:,0] < 2e-3
say("matched: %d/753 at tol 2e-3" % int(okm.sum()))
plab = np.load(H+"/p175_parentface.npy")
R753 = set(jrow[okm,0].tolist())
strip = np.load(H+"/p175_strip.npy")
Sset = set(strip.tolist())
say("BAG unclustered-rows=%d | in-strip=%d | S0-exclusive=%d" % (len(R753), len(R753 & Sset), len(R753 - Sset)))
inS = np.array([r in Sset for r in jrow[:,0]])
say("strip-row dots=%d (parent inner=%d outer=%d fold=%d)" % (int(inS.sum()), int(((plab==-1)&inS).sum()), int(((plab==1)&inS).sum()), int(((plab==0)&inS).sum())))
say("S0-exclusive dots=%d (parent inner=%d outer=%d fold=%d)" % (int((~inS).sum()), int(((plab==-1)&~inS).sum()), int(((plab==1)&~inS).sum()), int(((plab==0)&~inS).sum())))
# ruler check of clouds (scoring only)
from scipy.spatial import cKDTree
KG0 = cKDTree(G0)
dmin = KG0.query(BAG)[0]
CIN = (plab==-1); COUT = (plab==1); CFL = (plab==0)
for nm, m in [("parent-inner",CIN),("parent-outer",COUT),("parent-fold",CFL)]:
    cov = len(set(KG0.query(BAG[m])[1][dmin[m]<2].tolist()))
    say("%s: n=%d dmin<2=%d (%.1f%%) med=%.2f station-cover=%d/211" % (
      nm, int(m.sum()), int((dmin[m]<2).sum()), float((dmin[m]<2).mean()*100), float(np.median(dmin[m])), cov))
# fold disposition candidate: fold JOIN inner (rim continuity) -> true cloud
CTRUE = CIN | CFL
covT = len(set(KG0.query(BAG[CTRUE])[1][dmin[CTRUE]<2].tolist()))
say("TRUE-candidate (inner+fold): n=%d station-cover=%d/211" % (int(CTRUE.sum()), covT))
np.save(H+"/p175_pmask_true.npy", CTRUE)
log.close(); print("step11b done")
