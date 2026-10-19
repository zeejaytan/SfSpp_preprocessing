# 173 step3: renders (bag top, walk top, coverage). Eye-checked by worker before reporting.
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree
H = ".scratch/pota173_repro"
OUT = "artifacts/pota173"
d = np.load(H + "/p173_bag.npz", allow_pickle=True)
BAG, G0, TF = d["BAG"], d["G0"], d["TF"]
seq = np.load(H + "/p173_seq.npy"); seq2 = np.load(H + "/p173_seq2.npy")
L1, L2 = BAG[seq], BAG[seq2]
C0 = G0.mean(0); Uu, Ss, Vt = np.linalg.svd(G0-C0, full_matrices=False); e1, e2 = Vt[0], Vt[1]
P = lambda X: np.c_[(X-C0).dot(e1), (X-C0).dot(e2)]
PG0, PB, PL1, PL2 = P(G0), P(BAG), P(L1), P(L2)
d_bag = cKDTree(BAG).query(G0)[0]
is_strip_only = np.zeros(len(BAG), bool)
# bag rows 0..290 = S0 part, rest = strip part (pre-dedup order kept? dedup sorted uniq) -> recompute: strip pts via vertex match
fig, ax = plt.subplots(figsize=(9,9))
ax.scatter(PB[:,0], PB[:,1], s=4, c="gray", label="bag S0+strip (753)")
ax.plot(PG0[:,0], PG0[:,1], "g-", lw=1.2, label="ORIG Bl_0 (211)")
ax.set_aspect("equal"); ax.legend(fontsize=8); ax.set_title("p173 densified bag vs ORIG (top)")
fig.savefig(OUT + "/p173_bag_top.png", dpi=110); plt.close(fig)
print("bag render ok")
fig, ax = plt.subplots(figsize=(9,9))
ax.plot(PL1[:,0], PL1[:,1], "g-", lw=1.0, label="strand1 (211 steps)")
ax.plot(PL2[:,0], PL2[:,1], "m-", lw=0.7, alpha=0.8, label="strand2 (507 steps)")
DOu = np.minimum(cKDTree(L1).query(G0)[0], cKDTree(L2).query(G0)[0])
unc = G0[DOu>5]
if len(unc):
    PU = P(unc)
    ax.scatter(PU[:,0], PU[:,1], s=36, marker="s", facecolor="none", edgecolor="red", label="uncovered>5mm (%d)" % len(unc))
ax.plot(PG0[:,0], PG0[:,1], "c--", lw=0.8, label="ORIG")
ax.set_aspect("equal"); ax.legend(fontsize=8); ax.set_title("p173 walks vs ORIG (top): green s1, purple s2, red uncovered")
fig.savefig(OUT + "/p173_walk_top.png", dpi=110); plt.close(fig)
print("walk render ok")
def load_pcd3(p):
    HDR = ('VERSION','FIELDS','SIZE','TYPE','COUNT','WIDTH','HEIGHT','VIEWPOINT','POINTS','DATA')
    P_ = []
    for ln in open(p):
        s = ln.strip()
        if not s or s[0] == '#' or s.split()[0] in HDR: continue
        try: P_.append(list(map(float, s.split()[:3])))
        except ValueError: continue
    return np.array(P_)
R, t = TF[:3,:3], TF[:3,3]
BASE = load_pcd3(".scratch/pota161_repro/C01_BASE_Pot_C_Piece_01_Breakline_0.pcd") @ R.T + t
DOb = cKDTree(BASE).query(G0)[0]
DO1 = cKDTree(L1).query(G0)[0]
fig, ax = plt.subplots(figsize=(11,4))
xs = np.arange(len(G0))
ax.plot(xs, DOb, "b-", lw=0.9, label="BASE/fresh")
ax.plot(xs, DO1, "g-", lw=0.9, label="strand1")
ax.plot(xs, DOu, "m-", lw=0.9, label="union s1+s2")
ax.axhline(2.0, color="k", ls="--", lw=0.8)
ax.set_ylim(0, 40); ax.set_xlabel("ORIG station"); ax.set_ylabel("dist to walk (mm)")
ax.legend(fontsize=8); ax.set_title("p173 coverage: BASE blue / s1 green / union purple (2mm line)")
fig.savefig(OUT + "/p173_coverage.png", dpi=110); plt.close(fig)
print("coverage render ok")
