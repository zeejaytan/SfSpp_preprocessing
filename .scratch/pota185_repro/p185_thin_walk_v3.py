import numpy as np, os, sys
sys.path.insert(0, ".scratch/pota176_repro")
from p176_lib import load_obj, load_pcd3, wall_labels, pt_tri_dist, walk_m144
from scipy.spatial import cKDTree

H185 = ".scratch/pota185_repro"
H176 = ".scratch/pota176_repro"
ART = "artifacts/pota185"
TAG = "v3"
log = open(os.path.join(H185, "p185_log_" + TAG + ".txt"), "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")

zb = np.load(".scratch/pota173_repro/p173_bag.npz")
BAG = zb["BAG"]
V, F = load_obj("temp_download/Mesh/Pot_C/Pot_C_Piece_01_Mesh_DS.obj")
T = np.loadtxt(os.path.join(H176, "inputs", "Pot_C_Piece_1_T.txt")); Rr, t = T[:3,:3], T[:3,3]
Vg = V @ Rr.T + t
cosv = wall_labels(V, F)
ddt, jn = pt_tri_dist(BAG, Vg, F)
tl = cosv[jn]
TRUE = BAG[(tl < -0.5) | (np.abs(tl) <= 0.5)]
assert len(TRUE) == 476
say("TRUE n=%d" % len(TRUE))

# KEY-FREE v2 thin. Rule inputs: TRUE xyz only. Constants disclosed below.
C0 = TRUE.mean(0)
Uu, Ss, Vt = np.linalg.svd(TRUE - C0, full_matrices=False)
e1, e2 = Vt[0], Vt[1]
P2 = np.c_[ (TRUE - C0).dot(e1), (TRUE - C0).dot(e2) ]
cc = P2.mean(0)
Q = P2 - cc
ang = np.arctan2(Q[:,1], Q[:,0])
NB = 360
edges = np.linspace(-np.pi, np.pi, NB + 1)
bid = np.clip(np.digitize(ang, edges) - 1, 0, NB - 1)
means = []
for b in range(NB):
    m = bid == b
    if m.sum(): means.append(TRUE[m].mean(0))
M = np.array(means)
say("fine bins: %d non-empty of %d" % (len(M), NB))
# angle-sort -> closed polygon
ma = np.arctan2((M-C0).dot(e2)-cc[1], (M-C0).dot(e1)-cc[0])
Mo = M[np.argsort(ma)]
# closed-loop Laplacian smoothing (dots only)
S = Mo.copy()
for _ in range(8):
    S = S + 0.5 * ((np.roll(S,-1,0) + np.roll(S,1,0)) / 2.0 - S)
# uniform arc-length resample; N1 from smoothed polygon length / 1.8 nominal
seg = np.sqrt(((np.roll(S,-1,0)-S)**2).sum(-1))
poly = float(seg.sum())
N1 = min(240, int(round(poly / 1.8)))
say("smoothed polygon=%.1fmm -> N1=%d (nominal 1.8mm; cap 240)" % (poly, N1))
cum = np.r_[0, np.cumsum(np.sqrt(((S[1:]-S[:-1])**2).sum(-1)))]
tot = cum[-1]
tgt = np.linspace(0, tot, N1, endpoint=False)
CL = np.zeros((N1, 3))
j = 0
for k, d in enumerate(tgt):
    while j < len(cum)-2 and cum[j+1] < d: j += 1
    f = (d - cum[j]) / max(cum[j+1]-cum[j], 1e-12)
    CL[k] = S[j] * (1-f) + S[j+1] * f
st = np.sqrt(((CL-np.roll(CL,-1,0))**2).sum(-1))
say("centreline: n=%d spacing med=%.2f max=%.2f" % (N1, float(np.median(st)), float(st.max())))
np.save(os.path.join(H185, "p185_centreline_%s.npy" % TAG), CL)

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

G0 = load_pcd3(".scratch/pota162_repro/sfs_main/original_samples/SfS_pp/Breaklines/Pot_C_Piece_01_Breakline_0.pcd") @ Rr.T + t
KG0 = cKDTree(G0)
from collections import Counter
results = []
for si, s in enumerate(seeds(CL)):
    Tp = np.vstack([CL[s:], CL[:s]])
    seq, cseq, BAND, HALT, ret, fwd, bst = walk_m144(Tp)
    L = Tp[seq]
    steps = np.sqrt(((L[1:]-L[:-1])**2).sum(-1))
    arc = float(steps.sum()); closure = float(np.linalg.norm(L[-1]-L[0]))
    gaps5 = int((steps > 5).sum())
    j = KG0.query(L)[1]
    uniq = len(set(j.tolist()))
    dj = np.diff(np.r_[j, j[0]]) % 211
    skip = int(((dj != 0) & (dj != 1)).sum())
    back = int((dj > 211 // 2).sum())
    toks = np.floor(steps / 0.15).astype(int)
    cc2 = Counter(toks.tolist())
    run = ml = 1
    for a, b2 in zip(toks[:-1], toks[1:]):
        run = run + 1 if b2 == a else 1
        ml = max(ml, run)
    D = np.sqrt(((L[:,None,:]-G0[None,:,:])**2).sum(-1)).min(1)
    DO = np.sqrt(((G0[:,None,:]-L[None,:,:])**2).sum(-1)).min(1)
    med = float(np.median(D)); cov = int((DO < 2).sum())
    say("seed%d rot=%d: n=%d arc=%.1f closure=%.2f med/max=%.2f/%.2f gaps5=%d uniqSta=%d skip=%d back=%d Dtok=%d run=%d rimmed=%.4f cov=%d/211 BAND=%.1f %s" % (
        si, s, len(L), arc, closure, float(np.median(steps)), float(steps.max()), gaps5, uniq, skip, back, len(cc2), ml, med, cov, BAND, HALT))
    results.append(dict(si=si, s=s, L=L, seq=seq, arc=arc, closure=closure, steps=steps, gaps5=gaps5, uniq=uniq, skip=skip, back=back, ntok=len(cc2), run=ml, med=med, cov=cov, top3=cc2.most_common(3)))

ok = [r for r in results if r["closure"] <= 2.0 and r["gaps5"] == 0]
fwd = [r for r in ok if r["back"] == 0]
pool = fwd if fwd else ok
best = min(pool if pool else results, key=lambda r: (r["arc"]))
say("PICK seed%d (key-free%s): n=%d arc=%.1f closure=%.2f gaps5=%d" % (best["si"], "" if ok else " -- NONE MET GATE, min-arc fallback", len(best["L"]), best["arc"], best["closure"], best["gaps5"]))
say("PICK top3 D-tokens: %s longest-run=%d ntok=%d" % (best["top3"], best["run"], best["ntok"]))
say("PICK rim-truth (CHECK-ONLY): med=%.4f cov=%d/211 uniqSta=%d skip=%d back=%d" % (best["med"], best["cov"], best["uniq"], best["skip"], best["back"]))
np.save(os.path.join(H185, "p185_thin_walk_%s.npy" % TAG), best["L"])

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
L = best["L"]
fig, ax = plt.subplots(figsize=(9, 9))
ax.scatter(P2[:,0], P2[:,1], c="lightgray", s=6, label="TRUE strip (476)")
CE = np.c_[ (CL-C0).dot(e1), (CL-C0).dot(e2) ]
ax.scatter(CE[:,0], CE[:,1], c="green", s=18, label="centreline v2 (%d)" % N1)
ax.set_aspect("equal"); ax.legend(); ax.set_title("p185 v2 thin: strip + smoothed resampled centreline")
fig.savefig(os.path.join(ART, "p185_01_thin_%s.png" % TAG), dpi=80)
plt.close(fig)
LW = np.c_[ (L-C0).dot(e1), (L-C0).dot(e2) ]
fig, ax = plt.subplots(figsize=(9, 9))
ax.scatter(P2[:,0], P2[:,1], c="lightgray", s=4)
ax.scatter(LW[:,0], LW[:,1], c=np.arange(len(LW)), cmap="hsv", s=22)
for k in [0, len(LW)//3, 2*len(LW)//3]:
    ax.text(LW[k,0], LW[k,1], str(k), fontsize=9)
ax.set_aspect("equal"); ax.set_title("p185 v2 walk seed%d n=%d arc=%.0f closure=%.2f" % (best["si"], len(L), best["arc"], best["closure"]))
fig.savefig(os.path.join(ART, "p185_02_order_trace_%s.png" % TAG), dpi=80)
plt.close(fig)
j = KG0.query(L)[1]
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(j, ".", ms=3)
ax.set_xlabel("walk order"); ax.set_ylabel("nearest author station"); ax.set_title("p185 v2 station sweep")
fig.savefig(os.path.join(ART, "p185_03_station_sweep_%s.png" % TAG), dpi=80)
plt.close(fig)
say("renders: p185_01/02/03_v2")
log.close(); print("P185 V2 DONE")
