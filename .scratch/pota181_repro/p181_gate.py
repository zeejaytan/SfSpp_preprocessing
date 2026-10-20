"""Ticket 181: gate pre-densify M134d C01 walk vs author, 176-s1 recipe verbatim + 179 input features."""
import numpy as np, os
from scipy.spatial import cKDTree
H = ".scratch/pota181_repro"
log = open(os.path.join(H, "p181_gate.txt"), "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")

def load_pcd3(p):
    P=[]; HDR=('VERSION','FIELDS','SIZE','TYPE','COUNT','WIDTH','HEIGHT','VIEWPOINT','POINTS','DATA')
    for ln in open(p):
        s=ln.strip()
        if not s or s[0]=='#' or s.split()[0] in HDR: continue
        try: P.append([float(x) for x in s.split()[:3]])
        except: continue
    return np.array(P)

# --- source integrity: 282 bag has no 143/146 densified dots ---
G282 = np.load(".scratch/pota134_repro/p134_G282.npy")
C = np.load(".scratch/pota115_staging/inputs/p113_guarded.npz")["bag"]
SN124 = np.load(".scratch/pota124_repro/p124_admit_c2p5.npy")
SN128 = np.load(".scratch/pota128_repro/p128_admit.npy")
SN133 = np.load(".scratch/pota133_repro/p133_admit.npy")
G282_re = np.vstack([C, SN124, SN128, SN133])
say("G282 shape %s; rebuild-equals-stored: %s" % (G282.shape, np.array_equal(G282, G282_re)))
say("bag parts: guarded=%d +124=%d +128=%d +133=%d -> 282 (no 143/146 dots)" % (len(C), len(SN124), len(SN128), len(SN133)))
seq = np.load(".scratch/pota134_repro/p134_seq_d.npy")
say("M134d seq: seqlen=%d unique=%d (expect 290/278)" % (len(seq), len(set(seq.tolist()))))

# --- author reference, 176-s1 recipe verbatim (stepB lines) ---
C01 = load_pcd3(".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Breaklines/Pot_C_Piece_01_Breakline_0.pcd")
T1 = np.loadtxt(".scratch/pota176_repro/inputs/Pot_C_Piece_1_T.txt"); Rr, t = T1[:3,:3], T1[:3,3]
G0 = C01.dot(Rr.T) + t
say("author G0 shape %s (expect (211,3))" % (G0.shape,))
OG = np.load(".scratch/pota119_repro/p119_OG.npy")
say("G0 vs 134-OG maxdev=%.6f (expect 0: same frame)" % (cKDTree(OG).query(G0)[0].max(),))

# --- walk into seated frame: 134 gate uses TF (=TO, verified identical) ---
TF = np.loadtxt(".scratch/pota115_staging/inputs/TF.txt")
L = G282[np.array(seq)]
Ls = L.dot(TF[:3,:3].T) + TF[:3,3]

# --- gate_walk verbatim from p176_lib ---
def gate_walk(Lw, Og):
    D = np.sqrt(((Lw[:,None,:]-Og[None,:,:])**2).sum(-1)).min(1)
    DO = np.sqrt(((Og[:,None,:]-Lw[None,:,:])**2).sum(-1)).min(1)
    bst = np.sqrt(((Lw[1:]-Lw[:-1])**2).sum(-1))
    return dict(seqlen=len(Lw), med=float(np.median(D)), cov2=float((D<2).mean()*100),
        gaps5=int((bst>5).sum()), maxstep=float(bst.max()) if len(bst) else 0.0,
        origcov=int((DO<2).sum()), uncovered=int((DO>5).sum()),
        over25=sorted([float(x) for x in bst if x > 25]))
g = gate_walk(Ls, G0)
say("M134d 176-recipe gate: seqlen=%d med=%.4f <2mm=%.1f%% gaps5=%d maxstep=%.1f ORIGcov %d/211 uncovered=%d over25=%s" % (
    g["seqlen"], g["med"], g["cov2"], g["gaps5"], g["maxstep"], g["origcov"], g["uncovered"], [round(x,1) for x in g["over25"]]))
ok = (g["seqlen"]==290 and abs(g["med"]-4.2488)<0.005 and g["origcov"]==99 and g["uncovered"]==8)
say("CONTROL vs 134 file (290/4.2488/99/8): " + ("GREEN" if ok else "RED - STOP"))
say("176-s1 reference (Comments s1): 439 dots, ORIGcov 211/211, med 0.9492, <2mm 92.0%%, gaps5 3, maxstep 14.8")

# --- 179 input features (laptop proxy definitions from 179 Comments) ---
def features(P, tag):
    st = np.sqrt(((P[1:]-P[:-1])**2).sum(-1))
    arc = float(st.sum())
    closure = float(np.linalg.norm(P[-1]-P[0]))
    gaps = int((st>5).sum())
    zeros = int((st==0).sum())
    bins = (st/0.15).astype(int)
    uniq = sorted(set(bins.tolist()))
    from collections import Counter
    c = Counter(bins.tolist())
    top = c.most_common(3)
    run = 1; best = 1
    for a, b in zip(bins.tolist(), bins.tolist()[1:]):
        run = run+1 if b==a else 1
        best = max(best, run)
    say("%s: n=%d arc=%.1fmm closure=%.2fmm max=%.2f med=%.2f gaps>5=%d zero-steps=%d D-tokens=%d bins=%s top3=%s longest-run=%d" % (
        tag, len(P), arc, closure, float(st.max()), float(np.median(st)), gaps, zeros, len(uniq), uniq, top, best))
    return arc, closure, gaps, len(uniq)
# validate D proxy on author loop first (179 row 12: 3 tokens bins 11,12,13; top-2 109+100 of 210; run 4)
features(G0, "AUTHOR-ORIG (proxy validation; expect n=211 arc~380 closure~1.8 gaps0 tokens3 bins[11,12,13])")
features(L, "M134d pre-densify walk (bag frame, rigid-invariant)")
log.close(); print("p181 gate done")
