import numpy as np, os, sys
sys.path.insert(0, ".scratch/pota176_repro")
from p176_lib import *
H = ".scratch/pota176_repro"
I = os.path.join(H, "inputs")
log = open(os.path.join(H, "p176_stepB.txt"), "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
V, F = load_obj("temp_download/Mesh/Pot_C/Pot_C_Piece_01_Mesh_DS.obj")
assert (len(V), len(F)) == (11875, 23114)
T = np.loadtxt(os.path.join(I, "Pot_C_Piece_1_T.txt")); Rr, t = T[:3,:3], T[:3,3]
Vg = V @ Rr.T + t
G0 = load_pcd3(".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Breaklines/Pot_C_Piece_01_Breakline_0.pcd") @ Rr.T + t
G1 = load_pcd3(".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Breaklines/Pot_C_Piece_01_Breakline_1.pcd") @ Rr.T + t
assert G0.shape == (211, 3)
KG0 = cKDTree(G0); KG = cKDTree(np.vstack([G0, G1]))
S = np.loadtxt(os.path.join(I, "Pot_C_Piece_01_Surface_0.xyz")); X, N = S[:,:3], S[:,3:6]
r = code_r(X)
say("code_r S0 = %.4f (expect 6.4657)" % r)
f0 = pcl_flags(X, N, 6.4657)
say("estimator fires=%d (expect 364)" % int(f0.sum()))
import csv as _c
with open(".scratch/pota162_repro/pota160_repro/C01_ADAPT/veto_align_Pot_C_Piece_01_c0.csv") as fh:
    cr = list(_c.DictReader(fh)); C0 = np.array([[float(x['x']), float(x['y']), float(x['z'])] for x in cr])
Xgf = X[f0] @ Rr.T + t; C0g = C0 @ Rr.T + t
say("estimator bit-exact maxdev=%.6f (expect 0)" % cKDTree(Xgf).query(C0g)[0].max())
loops = mesh_loops(V, F)
say("loops=%s (expect [274,247,97,18])" % sorted([len(l) for l in loops], reverse=True))
HOLE = [i for i, l in enumerate(loops) if len(l) == 247][0]
D = KG.query(C0 @ Rr.T + t)[0]; near, far = D < 2.0, D > 5.0
segs = []
for i, l in enumerate(loops):
    lv = Vg[l]; segs.append(np.stack([lv, np.roll(lv, -1, axis=0)], axis=1))
Sseg = np.vstack(segs); loj = np.concatenate([np.full(len(ll), i) for i, ll in enumerate(loops)])
A, B = Sseg[:,0], Sseg[:,1]; AB = B-A; den = (AB**2).sum(axis=1)
Pmg = C0 @ Rr.T + t
AP = Pmg[None,:,:] if False else None
def seg_dist(P):
    AP2 = P[:,None,:]-A[None,:,:]
    tt = np.clip((AP2*AB[None,:,:]).sum(axis=2)/den[None,:], 0, 1)
    Cc = A[None,:,:]+tt[:,:,None]*AB[None,:,:]
    d = np.linalg.norm(P[:,None,:]-Cc, axis=2); j = d.argmin(axis=1)
    return d[np.arange(len(P)),j], loj[j]
dfar, jfar = seg_dist(Pmg[far])
drop = np.zeros(len(Pmg), bool); drop[np.where(far)[0][jfar == HOLE]] = True
say("curation: NEAR=%d MID=%d FAR=%d drop=%d keep=%d (expect 86/187/91?/73/291)" % (
    int(near.sum()), int((~(near|far)).sum()), int(far.sum()), int(drop.sum()), int((~drop).sum())))
U = load_ply_x(".scratch/pota163_repro/inputs/Pot_C_Piece_01_unclustered.ply")
say("unclustered n=%d" % len(U))
KU = cKDTree(U); Ds0, j0 = KU.query(C0[~drop])
say("uncl-snap disp: med=%.2f n>1mm=%d/%d max=%.1f" % (float(np.median(Ds0)), int((Ds0>1).sum()), int((~drop).sum()), float(Ds0.max())))
KM = cKDTree(V); Dm, jm = KM.query(C0[~drop])
say("mesh-snap disp: med=%.2f n>1mm=%d/%d max=%.1f agree=%d/%d" % (
    float(np.median(Dm)), int((Dm>1).sum()), int((~drop).sum()), float(Dm.max()), int((jm == j0).sum()), len(j0)))
Ug = U @ Rr.T + t
strip = np.where(KG0.query(Ug)[0] <= 2.5)[0]
say("ORIG-guided strip n=%d (expect 612)" % len(strip))
d_off = cKDTree(X).query(V)[0]
F0 = C0
d_edge = cKDTree(F0).query(V)[0]
candM = np.where((d_off >= 1.0) & (d_edge < 6.0))[0]
say("mesh-pool ORIG-free cand n=%d" % len(candM))
UgM = V[candM] @ Rr.T + t
say("candM dist-to-ORIG: min=%.2f med=%.2f max=%.2f frac<2.5=%.3f" % (
    KG0.query(UgM)[0].min(), float(np.median(KG0.query(UgM)[0])), KG0.query(UgM)[0].max(), float((KG0.query(UgM)[0]<2.5).mean())))
stripM = np.where((KG0.query(Vg)[0] <= 2.5) & (d_off >= 1.0))[0]
say("mesh-pool ORIG-guided strip n=%d overlap-with-612pts: need point-compare" % len(stripM))
Kstrip = cKDTree(Ug[strip])
dmp = Kstrip.query(Vg[stripM])[0]
say("stripM->strip612 maxdev=%.4f n>1mm=%d (pool-equivalence)" % (dmp.max(), int((dmp>1).sum())))
cosv = wall_labels(V, F)
for th in [0.3, 0.4, 0.5, 0.6]:
    outer = (cosv > th).sum(); inner = (cosv < -th).sum(); fold = len(cosv)-outer-inner
    say("th=%.1f outer=%d inner=%d fold=%d (target 11769/8692/2653)" % (th, outer, inner, fold))
log.close(); print("saved stepB-part1")
