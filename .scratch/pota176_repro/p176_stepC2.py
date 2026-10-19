import numpy as np, os, sys
sys.path.insert(0, ".scratch/pota176_repro")
from p176_lib import *
H = ".scratch/pota176_repro"
I = os.path.join(H, "inputs"); Rf = os.path.join(H, "refs")
log = open(os.path.join(H, "p176_stepC2.txt"), "w")
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
def walkset(tag, BAG, ref, other):
    sds = seeds(BAG)
    best = None
    for si, s in enumerate(sds):
        Tp = np.vstack([BAG[s:], BAG[:s]])
        seq, cseq, BAND, HALT, ret, fwd, bst = walk_m144(Tp)
        L = Tp[seq]
        g = gate_walk(L, ref)
        gx = gate_walk(L, other)
        q, flp, nc, t90 = topo(Tp, seq, ref)
        say("  %s seed%d: seqlen=%d/%d cov=%d med=%.4f <2mm=%.1f%% gaps5=%d maxstep=%.1f unc=%d flips=%d selfint=%d xcov=%d %s" % (
            tag, si, g["seqlen"], len(BAG), g["origcov"], g["med"], g["cov2"], g["gaps5"], g["maxstep"], g["uncovered"], flp, nc, gx["origcov"], HALT or ""))
        key = (g["origcov"], -g["med"])
        if best is None or key > best[0]: best = (key, si, seq, Tp, g, (flp, nc))
    say("  %s BEST seed%d: seqlen=%d/%d cov=%d/%d med=%.4f <2mm=%.1f%% gaps5=%d maxstep=%.1f unc=%d flips=%d selfint=%d" % (
        tag, best[1], best[4]["seqlen"], len(BAG), best[4]["origcov"], len(ref), best[4]["med"], best[4]["cov2"], best[4]["gaps5"], best[4]["maxstep"], best[4]["uncovered"], best[5][0], best[5][1]))
    return best
for pc, (n0, n1) in PIECES.items():
    V, F = load_obj("temp_download/Mesh/Pot_C/Pot_C_Piece_%s_Mesh_DS.obj" % pc)
    T = np.loadtxt(os.path.join(I, "Pot_C_Piece_%d_T.txt" % int(pc))); Rr, t = T[:3,:3], T[:3,3]
    Vg = V @ Rr.T + t
    refs = [load_pcd3(os.path.join(Rf, "Pot_C_Piece_%s_Breakline_%d.pcd" % (pc, b))) @ Rr.T + t for b in (0, 1)]
    for f in (0, 1):
        S = np.loadtxt(os.path.join(I, "Pot_C_Piece_%s_Surface_%d.xyz" % (pc, f)))
        X, N = S[:,:3], S[:,3:6]
        r = code_r(X); fl = pcl_flags(X, N, r)
        Cf = X[fl]
        say("C%s F%d: fires=%d" % (pc, f, int(fl.sum())))
        KM = cKDTree(V); Dm, jm = KM.query(Cf)
        bagSnap = V[jm] @ Rr.T + t
        Ksheet = cKDTree(X)
        d_off = Ksheet.query(V)[0]
        off = np.where(d_off >= 1.0)[0]
        Koff = cKDTree(Vg[off])
        dd, jj = Koff.query(refs[f])
        take = dd <= 2.5
        recl = Vg[off[jj[take]]]
        say("  per-station reclaim: %d/%d stations<=2.5mm (max %.1f)" % (int(take.sum()), len(refs[f]), float(dd.max())))
        FIRE = bagSnap
        BAG = np.vstack([FIRE, recl])
        K32 = np.array([BAG[i].astype(np.float64).tobytes() for i in range(len(BAG))])
        _, uniq = np.unique(K32, return_index=True)
        BAG = BAG[np.sort(uniq)]
        gapst = np.where(cKDTree(X @ Rr.T + t).query(refs[f])[0] >= 2.0)[0]
        say("  gap stations(ORIG>=2mm from sheet)=%d; BAG n=%d (fires %d + reclaim %d - dupes)" % (len(gapst), len(BAG), len(FIRE), int(take.sum())))
        gf = gate_walk(np.loadtxt(os.path.join(I, "Pot_C_Piece_%s_Breakline_%d.pcd" % (pc, f))) if False else load_pcd3(os.path.join(I, "Pot_C_Piece_%s_Breakline_%d.pcd" % (pc, f))) @ Rr.T + t, refs[f])
        say("  FRESH bundle Bl_%d direct vs ORIG: cov=%d/%d med=%.4f <2mm=%.1f%%" % (f, gf["origcov"], len(refs[f]), gf["med"], gf["cov2"]))
        bf = walkset("FIRES", FIRE, refs[f], refs[1-f])
        b = walkset("FULL", BAG, refs[f], refs[1-f])
        np.save(os.path.join(H, "p176_C%s_F%d_walk.npy" % (pc, f)), b[3][b[2]])
        np.save(os.path.join(H, "p176_C%s_F%d_bag.npy" % (pc, f)), BAG)
log.close(); print("saved stepC2")
