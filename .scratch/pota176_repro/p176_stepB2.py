import numpy as np, os, sys
sys.path.insert(0, ".scratch/pota176_repro")
from p176_lib import *
H = ".scratch/pota176_repro"
I = os.path.join(H, "inputs")
log = open(os.path.join(H, "p176_stepB2.txt"), "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
V, F = load_obj("temp_download/Mesh/Pot_C/Pot_C_Piece_01_Mesh_DS.obj")
T = np.loadtxt(os.path.join(I, "Pot_C_Piece_1_T.txt")); Rr, t = T[:3,:3], T[:3,3]
Vg = V @ Rr.T + t
G0 = load_pcd3(".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Breaklines/Pot_C_Piece_01_Breakline_0.pcd") @ Rr.T + t
import csv as _c
with open(".scratch/pota162_repro/pota160_repro/C01_ADAPT/veto_align_Pot_C_Piece_01_c0.csv") as fh:
    cr = list(_c.DictReader(fh)); C0 = np.array([[float(x['x']), float(x['y']), float(x['z'])] for x in cr])
loops = mesh_loops(V, F)
HOLE = [i for i, l in enumerate(loops) if len(l) == 247][0]
KG = cKDTree(np.vstack([G0, load_pcd3(".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Breaklines/Pot_C_Piece_01_Breakline_1.pcd") @ Rr.T + t]))
D = KG.query(C0 @ Rr.T + t)[0]; near, far = D < 2.0, D > 5.0
segs = []
for i, l in enumerate(loops):
    lv = Vg[l]; segs.append(np.stack([lv, np.roll(lv, -1, axis=0)], axis=1))
Sseg = np.vstack(segs); loj = np.concatenate([np.full(len(ll), i) for i, ll in enumerate(loops)])
A, B = Sseg[:,0], Sseg[:,1]; AB = B-A; den = (AB**2).sum(axis=1)
def seg_dist(P):
    AP2 = P[:,None,:]-A[None,:,:]
    tt = np.clip((AP2*AB[None,:,:]).sum(axis=2)/den[None,:], 0, 1)
    Cc = A[None,:,:]+tt[:,:,None]*AB[None,:,:]
    d = np.linalg.norm(P[:,None,:]-Cc, axis=2); j = d.argmin(axis=1)
    return d[np.arange(len(P)),j], loj[j]
Pmg = C0 @ Rr.T + t
dfar, jfar = seg_dist(Pmg[far])
drop = np.zeros(len(Pmg), bool); drop[np.where(far)[0][jfar == HOLE]] = True
U = load_ply_x(".scratch/pota163_repro/inputs/Pot_C_Piece_01_unclustered.ply")
KU = cKDTree(U)
Ds0, j0 = KU.query(C0[~drop])
Ug = U @ Rr.T + t; KG0 = cKDTree(G0)
strip = np.where(KG0.query(Ug)[0] <= 2.5)[0]
Dss, js = KU.query(U[strip])
B0 = U[j0] @ Rr.T + t; BS = U[js] @ Rr.T + t
BAG = np.vstack([B0, BS])
K32 = np.array([BAG[i].astype(np.float64).tobytes() for i in range(len(BAG))])
_, uniq = np.unique(K32, return_index=True)
BAG = BAG[np.sort(uniq)]
say("rebuilt BAG n=%d (expect 753)" % len(BAG))
zb = np.load(".scratch/pota173_repro/p173_bag.npz")
say("recorded BAG n=%d maxdev=%.6f" % (len(zb["BAG"]), cKDTree(zb["BAG"]).query(BAG)[0].max()))
cosv = wall_labels(V, F)
ddt, jn = pt_tri_dist(BAG, Vg, F)
say("nearest-tri dist: med=%.6f max=%.6f (expect 0.000/0.000)" % (float(np.median(ddt)), float(ddt.max())))
tl = cosv[jn]
inner = (tl < -0.5); fold = np.abs(tl) <= 0.5; outer = (tl > 0.5)
say("bag wall origin: inner=%d fold=%d outer=%d (175: 212/264/277)" % (int(inner.sum()), int(fold.sum()), int(outer.sum())))
TRUE = BAG[inner | fold]; OUT = BAG[outer]
say("TRUE n=%d (expect 476) OUTER n=%d (expect 277)" % (len(TRUE), len(OUT)))
def seeds(Tc):
    s0 = 0
    Dm = np.sqrt(((Tc[:,None,:]-Tc[None,:,:])**2).sum(-1)).sum(0)
    sm = int(Dm.argmin())
    picked = [s0, sm]
    for _ in range(4):
        d = np.min([np.sqrt(((Tc-Tc[p])**2).sum(-1)) for p in picked], axis=0)
        d[picked] = -1
        picked.append(int(d.argmax()))
    return picked
for tag, Tc in [("TRUE", TRUE), ("OUTER", OUT)]:
    sds = seeds(Tc)
    say("%s seeds=%s" % (tag, sds))
    best = None
    for si, s in enumerate(sds):
        Tp = np.vstack([Tc[s:], Tc[:s]])
        seq, cseq, BAND, HALT, ret, fwd, bst = walk_m144(Tp)
        L = Tp[seq]
        g = gate_walk(L, G0)
        q, fl, nc, t90 = topo(Tp, seq, G0)
        say("%s seed%d: seqlen=%d/%d ORIGcov=%d med=%.4f <2mm=%.1f%% gaps5=%d maxstep=%.1f over25=%d unc=%d flips=%d selfint=%d t90=%d BAND=%.1f %s" % (
            tag, si, g["seqlen"], len(Tc), g["origcov"], g["med"], g["cov2"], g["gaps5"], g["maxstep"], len(g["over25"]), g["uncovered"], fl, nc, t90, BAND, HALT))
        key = (g["origcov"], -g["med"])
        if best is None or key > best[0]: best = (key, si, seq, Tp, g, (fl, nc))
    say("%s BEST seed%d: ORIGcov=%d med=%.4f <2mm=%.1f%% flips=%d selfint=%d" % (
        tag, best[1], best[4]["origcov"], best[4]["med"], best[4]["cov2"], best[5][0], best[5][1]))
    np.save(os.path.join(H, "p176_C01_%s_walk.npy" % tag), best[3][best[2]])
log.close(); print("saved stepB2")
