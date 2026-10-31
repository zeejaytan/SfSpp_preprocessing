import numpy as np, sys
sys.path.insert(0, ".scratch/pota176_repro")
from p176_lib import load_obj, wall_labels, pt_tri_dist
from scipy.spatial import cKDTree
def med(A,B):
    return float(np.median(np.sqrt(((A[:,None,:]-B[None,:,:])**2).sum(-1)).min(1)))
import sys as _s
_s.path.insert(0, ".scratch/pota201_repro")
from p201_lib import read_pcd
for pc in ["03"]:
    V, F = load_obj("temp_download/Mesh/Pot_C/Pot_C_Piece_%s_Mesh_DS.obj" % pc)
    T = np.loadtxt(".scratch/pota176_repro/inputs/Pot_C_Piece_%d_T.txt" % int(pc)); Rr, t = T[:3,:3], T[:3,3]
    Vg = V @ Rr.T + t
    cosv = wall_labels(V, F)
    A, n1, c1 = read_pcd(".scratch/pota204_repro/ORIG_C03_Bl0.pcd")
    At = (A - 0)  # bundle frame already
    # transform AUTH into mesh-T frame like dchain did, then nearest-tri label per AUTH station
    AAt = A @ Rr.T + t
    ddt, jn = pt_tri_dist(AAt, Vg, F)
    tl = cosv[jn]
    import collections
    print("C03 AUTH stations wall-label vs Bl_0: inner=%d fold=%d outer=%d" % ((tl<-0.5).sum(), (np.abs(tl)<=0.5).sum(), (tl>0.5).sum()))
    # cloud-level meds (bundle frame): TRUE cloud vs Bl_0
    TRUE = np.load(".scratch/pota204_repro/p204_C03_true_walk.npy")
    # reload clouds from dchain? recompute split quickly
    f0 = np.load(".scratch/pota176_repro/p176_C03_F0_bag.npy"); f1 = np.load(".scratch/pota176_repro/p176_C03_F1_bag.npy")
    B = np.vstack([f0, f1])
    K = np.array([B[i].astype(np.float64).tobytes() for i in range(len(B))])
    _, uniq = np.unique(K, return_index=True)
    P = B[np.sort(uniq)]
    d2, j2 = pt_tri_dist(P, Vg, F)
    t2 = cosv[j2]
    inner = P[t2 < -0.5]; fold = P[np.abs(t2) <= 0.5]; outer = P[t2 > 0.5]
    # seat clouds to bundle frame
    def seat(X): return (X - t) @ Rr
    print("cloud med vs Bl_0: inner-only", round(med(seat(inner),A),3), "fold-only", round(med(seat(fold),A),3), "outer-only", round(med(seat(outer),A),3))
    print("cloud med vs Bl_1: inner-only", end=" ")
    B1, n3, c3 = read_pcd(".scratch/pota204_repro/ORIG_C03_Bl1.pcd")
    print(round(med(seat(inner),B1),3), "fold-only", round(med(seat(fold),B1),3), "outer-only", round(med(seat(outer),B1),3))
print("DIAG DONE")
