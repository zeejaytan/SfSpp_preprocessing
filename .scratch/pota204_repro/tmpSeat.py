import numpy as np, sys
sys.path.insert(0, ".scratch/pota176_repro")
from p176_lib import load_pcd3
from scipy.spatial import cKDTree
def med(A,B):
    D = np.sqrt(((A[:,None,:]-B[None,:,:])**2).sum(-1)).min(1)
    DO = np.sqrt(((B[:,None,:]-A[None,:,:])**2).sum(-1)).min(1)
    return float(np.median(D)), int((DO<2).sum()), len(B)
for pc in ["01","02","03","04"]:
    T = np.loadtxt(".scratch/pota176_repro/inputs/Pot_C_Piece_%d_T.txt" % int(pc)); Rr,t = T[:3,:3], T[:3,3]
    W = np.load(".scratch/pota204_repro/p204_C%s_true_walk.npy" % pc)
    O = np.load(".scratch/pota204_repro/p204_C%s_outer_walk.npy" % pc)
    Wb = (W - t) @ Rr
    Ob = (O - t) @ Rr
    np.save(".scratch/pota204_repro/p204_C%s_true_seated.npy" % pc, Wb)
    np.save(".scratch/pota204_repro/p204_C%s_outer_seated.npy" % pc, Ob)
    print("C"+pc, "seated-true mean", Wb.mean(0).round(1))
print("done-seat")
