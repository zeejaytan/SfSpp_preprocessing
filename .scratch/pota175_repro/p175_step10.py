# 175 step10: controls + slot filing (local frame, pipeline-shape PCD) + OUTER walk render.
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree
H = "C:/PR/SfSpp_preprocessing/.scratch/pota175_repro"
OUT = "C:/PR/SfSpp_preprocessing/artifacts/pota175"
log = open(H + "/p175_step10.txt", "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
d = np.load("C:/PR/SfSpp_preprocessing/.scratch/pota173_repro/p173_bag.npz", allow_pickle=True)
BAG, G0, TF = d["BAG"], d["G0"], d["TF"]
assert BAG.shape == (753,3) and G0.shape == (211,3)
say("bag identity: BAG=(753,3) ORIG=(211,3) (173 input intact)")
R, t = TF[:3,:3], TF[:3,3]
# round-trip: gate -> local -> gate
Bloc = (BAG - t) @ R
Bback = Bloc @ R.T + t
say("frame round-trip maxdev=%.2e (expect ~0)" % float(np.abs(Bback-BAG).max()))
assert float(np.abs(Bback-BAG).max()) < 1e-6
TRUE = np.load(H + "/p175_mask_true.npy")
# BASE control (173 verbatim path)
def load_pcd3(p):
    HDR = ('VERSION','FIELDS','SIZE','TYPE','COUNT','WIDTH','HEIGHT','VIEWPOINT','POINTS','DATA')
    P = []
    for ln in open(p):
        s = ln.strip()
        if not s or s[0] == '#' or s.split()[0] in HDR: continue
        try: P.append(list(map(float, s.split()[:3])))
        except ValueError: continue
    return np.array(P)
BASE = load_pcd3("C:/PR/SfSpp_preprocessing/.scratch/pota161_repro/C01_BASE_Pot_C_Piece_01_Breakline_0.pcd")
assert len(BASE) == 402
Gb = BASE @ R.T + t
Db = np.sqrt(((Gb[:,None,:]-G0[None,:,:])**2).sum(-1)).min(1)
DOb = np.sqrt(((G0[:,None,:]-Gb[None,:,:])**2).sum(-1)).min(1)
say("BASE control: n=402 med=%.2f <2mm=%.1f%% ORIGcov=%d/211 (expect 5.61/22.9/92)" % (
    float(np.median(Db)), float((Db<2).mean()*100), int((DOb<2).sum())))
assert abs(float(np.median(Db))-5.61) < 0.01 and int((DOb<2).sum()) == 92
say("BASE CONTROL GREEN")
# slot filing: slot0 = true-face walk (spread2 plain, best seating), slot1 = outer walk (plain row0, full clean loop)
T = BAG[TRUE]; O = BAG[~TRUE]
seq0 = np.load(H + "/p175_seed_spread2.npy")
seq1 = np.load(H + "/p175_seq_OUTER.npy")
W0 = T[np.array(seq0, dtype=int)]; W1 = O[np.array(seq1, dtype=int)]
L0 = (W0 - t) @ R; L1 = (W1 - t) @ R  # local frame
def write_slot(L, tag, slot):
    hdr = "# .PCD v0.7 - Point Cloud Data file format\n# 1 %d 0\nVERSION 0.7\nFIELDS x y z\nSIZE 4 4 4\nTYPE F F F\nCOUNT 1 1 1\nWIDTH %d\nHEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0\nPOINTS %d\nDATA ascii\n" % (len(L), len(L), len(L))
    body = "\n".join("%.6f %.6f %.6f" % (x, y, z) for x, y, z in L)
    open(H + "/p175_slot%d_%s.pcd" % (slot, tag), "w").write(hdr + body + "\n")
    np.save(H + "/p175_slot%d_%s_walk.npy" % (slot, tag), L)
    say("slot%d (%s): n=%d filed (local frame, single-segment # 1 N 0 header)" % (slot, tag, len(L)))
write_slot(L0, "trueface", 0)
write_slot(L1, "outerface", 1)
# OUTER walk render (top view, order-colored) + slot overlay
C0 = G0.mean(0); Uu, Ss, Vt = np.linalg.svd(G0-C0, full_matrices=False); e1, e2, nn = Vt[0], Vt[1], Vt[2]
P2 = lambda P: np.c_[ (P-C0).dot(e1),(P-C0).dot(e2)]
Gp = P2(G0)
fig, ax = plt.subplots(figsize=(9,9))
ax.plot(np.append(Gp[:,0],Gp[0,0]), np.append(Gp[:,1],Gp[0,1]), "k--", lw=1, label="ORIG Bl_0")
sc = ax.scatter(P2(W1)[:,0], P2(W1)[:,1], s=6, c=np.arange(len(W1)), cmap="plasma", alpha=0.8)
plt.colorbar(sc, ax=ax, label="walk order")
ax.set_aspect("equal"); ax.legend(fontsize=8); ax.set_title("p175: OUTER walk (155) vs ORIG -- order-colored")
fig.tight_layout(); fig.savefig(OUT+"/p175_outer_top.png", dpi=110, bbox_inches="tight"); print("wrote outer")
# slot overlay: slot0 walk + slot1 walk + ORIG
fig, ax = plt.subplots(figsize=(9,9))
ax.plot(np.append(Gp[:,0],Gp[0,0]), np.append(Gp[:,1],Gp[0,1]), "k--", lw=1, label="ORIG Bl_0")
ax.scatter(P2(W0)[:,0], P2(W0)[:,1], s=6, c="blue", alpha=0.6, label="slot0 true-face (553)")
ax.scatter(P2(W1)[:,0], P2(W1)[:,1], s=10, c="red", alpha=0.7, label="slot1 outer-face (155)")
ax.set_aspect("equal"); ax.legend(fontsize=8); ax.set_title("p175: two filed slots vs ORIG (top view)")
fig.tight_layout(); fig.savefig(OUT+"/p175_slots_top.png", dpi=110, bbox_inches="tight"); print("wrote slots")
say("STEP10 DONE")
log.close(); print("step10 done")
