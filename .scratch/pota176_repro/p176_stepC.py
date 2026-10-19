import numpy as np, os, sys
sys.path.insert(0, ".scratch/pota176_repro")
from p176_lib import *
H = ".scratch/pota176_repro"
I = os.path.join(H, "inputs"); Rf = os.path.join(H, "refs")
log = open(os.path.join(H, "p176_stepC.txt"), "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
PIECES = {"02": (221, 313), "03": (191, 120), "04": (131, 146)}
def seeds(Tc):
    Dm = np.sqrt(((Tc[:,None,:]-Tc[None,:,:])**2).sum(-1)).sum(0)
    sm = int(Dm.argmin())
    picked = [0, sm]
    for _ in range(4):
        d = np.min([np.sqrt(((Tc-Tc[p])**2).sum(-1)) for p in picked], axis=0)
        d[picked] = -1
        picked.append(int(d.argmax()))
    return picked
for pc, (n0, n1) in PIECES.items():
    V, F = load_obj("temp_download/Mesh/Pot_C/Pot_C_Piece_%s_Mesh_DS.obj" % pc)
    T = np.loadtxt(os.path.join(I, "Pot_C_Piece_%d_T.txt" % int(pc))); Rr, t = T[:3,:3], T[:3,3]
    Vg = V @ Rr.T + t
    loops = mesh_loops(V, F)
    say("C%s mesh nV=%d nF=%d loops=%s" % (pc, len(V), len(F), sorted([len(l) for l in loops], reverse=True)))
    refs = [load_pcd3(os.path.join(Rf, "Pot_C_Piece_%s_Breakline_%d.pcd" % (pc, b))) @ Rr.T + t for b in (0, 1)]
    assert refs[0].shape == (n0, 3) and refs[1].shape == (n1, 3)
    Krefs = [cKDTree(r) for r in refs]
    for f in (0, 1):
        S = np.loadtxt(os.path.join(I, "Pot_C_Piece_%s_Surface_%d.xyz" % (pc, f)))
        X, N = S[:,:3], S[:,3:6]
        r = code_r(X); fl = pcl_flags(X, N, r)
        Cf = X[fl]
        say("C%s S%d: n=%d code_r=%.4f fires=%d" % (pc, f, len(X), r, int(fl.sum())))
        D = Krefs[f].query(Cf @ Rr.T + t)[0]
        near, far = D < 2.0, D > 5.0
        say("  fires vs Bl_%d: NEAR=%d MID=%d FAR=%d (no loops->drop 0, keep %d)" % (f, int(near.sum()), int((~(near|far)).sum()), int(far.sum()), len(Cf)))
        KM = cKDTree(V); Dm, jm = KM.query(Cf)
        say("  mesh-snap disp: med=%.2f n>1mm=%d/%d max=%.1f" % (float(np.median(Dm)), int((Dm>1).sum()), len(Cf), float(Dm.max())))
        bagSnap = V[jm] @ Rr.T + t
        Ksheet = cKDTree(X)
        d_off = Ksheet.query(V)[0]
        strip = np.where((Krefs[f].query(Vg)[0] <= 2.5) & (d_off >= 1.0))[0]
        say("  strip(face-ref<=2.5 & off-sheet>=1): n=%d" % len(strip))
        BAG = np.vstack([bagSnap, Vg[strip]])
        K32 = np.array([BAG[i].astype(np.float64).tobytes() for i in range(len(BAG))])
        _, uniq = np.unique(K32, return_index=True)
        BAG = BAG[np.sort(uniq)]
        say("  BAG n=%d (snap %d + strip %d - dupes)" % (len(BAG), len(bagSnap), len(strip)))
        d_edge = cKDTree(Cf).query(V)[0]
        candM = np.where((d_off >= 1.0) & (d_edge < 6.0))[0]
        gap = np.where(Krefs[f].query(X @ Rr.T + t)[0] >= 2.0)[0]
        say("  ORIG-free cand n=%d; gap stations(>=2mm from sheet)=%d" % (len(candM), len(gap)))
        if len(gap):
            refg = (X @ Rr.T + t)[gap]
            dg = cKDTree(Vg[candM]).query(refg)[0]
            say("  gap->cand: med=%.2f max=%.2f frac<2=%.3f" % (float(np.median(dg)), float(dg.max()), float((dg<2).mean())))
        sds = seeds(BAG)
        best = None
        for si, s in enumerate(sds):
            Tp = np.vstack([BAG[s:], BAG[:s]])
            seq, cseq, BAND, HALT, ret, fwd, bst = walk_m144(Tp)
            L = Tp[seq]
            g = gate_walk(L, refs[f])
            gx = gate_walk(L, refs[1-f])
            q, flp, nc, t90 = topo(Tp, seq, refs[f])
            say("  seed%d: seqlen=%d/%d cov=%d med=%.4f <2mm=%.1f%% gaps5=%d maxstep=%.1f over25=%d unc=%d flips=%d selfint=%d crossRef_cov=%d %s" % (
                si, g["seqlen"], len(BAG), g["origcov"], g["med"], g["cov2"], g["gaps5"], g["maxstep"], len(g["over25"]), g["uncovered"], flp, nc, gx["origcov"], HALT or ""))
            key = (g["origcov"], -g["med"])
            if best is None or key > best[0]: best = (key, si, seq, Tp, g, (flp, nc))
        say("C%s FACE%d BEST seed%d: seqlen=%d/%d ORIGcov=%d/%d med=%.4f <2mm=%.1f%% gaps5=%d maxstep=%.1f unc=%d flips=%d selfint=%d" % (
            pc, f, best[1], best[4]["seqlen"], len(BAG), best[4]["origcov"], len(refs[f]), best[4]["med"], best[4]["cov2"], best[4]["gaps5"], best[4]["maxstep"], best[4]["uncovered"], best[5][0], best[5][1]))
        np.save(os.path.join(H, "p176_C%s_F%d_walk.npy" % (pc, f)), best[3][best[2]])
        np.save(os.path.join(H, "p176_C%s_F%d_bag.npy" % (pc, f)), BAG)
log.close(); print("saved stepC")
