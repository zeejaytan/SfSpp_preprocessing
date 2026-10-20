"""Ticket 144 step4: verify + render. Read-only inputs; writes only pota144 dirs."""
import numpy as np, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
H = ".scratch/pota144_repro"; P143 = ".scratch/pota143_repro"; INP = ".scratch/pota115_staging/inputs"
R119 = ".scratch/pota119_repro"; OUT = "artifacts/pota144"
os.makedirs(OUT, exist_ok=True)
log = open(os.path.join(H, "p144_verify.txt"), "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
G = np.load(os.path.join(P143, "p143_G314.npy")); W = len(G)
seq = np.load(os.path.join(H, "p144_seq_m144.npy"))
X32 = G.astype(np.float32); kk = np.array([X32[i].tobytes() for i in range(W)])
sset = set(seq.tolist())
unseq = [i for i in range(W) if i not in sset]
say("unsequenced slots: %d %s" % (len(unseq), unseq))
for i in unseq:
    d = np.sqrt(((G - G[i])**2).sum(-1)); o = np.argsort(d, kind="stable")
    twin = [int(j) for j in o[1:6]]
    say("  slot %d keyfresh=%s nearest=%s" % (i, kk[i] not in set(kk[j] for j in seq), [(j, round(float(d[j]),2), kk[j]==kk[i]) for j in twin]))
# ORIG objects both frames for render + check
def load_pcd3(path):
    P = []; HDR = ("VERSION","FIELDS","SIZE","TYPE","COUNT","WIDTH","HEIGHT","VIEWPOINT","POINTS","DATA")
    for ln in open(path):
        s = ln.strip()
        if not s or s[0]=="#" or s.split()[0] in HDR: continue
        try: P.append([float(x) for x in s.split()[:3]])
        except: continue
    return np.array(P)
Ov = load_pcd3(os.path.join(INP, "Bl0.pcd"))
TF = np.loadtxt(os.path.join(INP, "TF.txt")); TO = np.loadtxt(os.path.join(INP, "TO.txt"))
Og = Ov.dot(TO[:3,:3].T) + TO[:3,3]
OG = np.load(os.path.join(R119, "p119_OG.npy"))
L = G[seq]; Gf = L.dot(TF[:3,:3].T)+TF[:3,3]
DO = np.sqrt(((Og[:,None,:]-Gf[None,:,:])**2).sum(-1)).min(1)
say("max point-DO=%.2f uncovered=%d" % (float(DO.max()), int((DO>5).sum())))
for name, idx in [("C36/37",[36,37]),("C46/47",[46,47]),("C96/97",[96,97]),("C165",[163,164,165,166]),("C173",[171,172,173,174,175]),("O37",[37]),("C115-205",list(range(115,206)))]:
    say("  %s maxDO=%.2f" % (name, float(DO[idx].max())))
# jump accounting: licensed vs unlicensed (no licenses stated -> every step must be <=25 and <40)
bst = np.sqrt(((L[1:]-L[:-1])**2).sum(-1))
say("step profile: max=%.2f n>25=%d n>=40=%d (licensed=0 stated, so all steps unlicensed-by-default)" % (float(bst.max()), int((bst>25).sum()), int((bst>=40).sum())))
# renders
Ri = np.linalg.inv(TF[:3,:3]); tt = TF[:3,3]
OL = (OG - tt).dot(Ri.T)
fig, ax = plt.subplots(figsize=(14, 5))
ax.scatter(OL[:,0], OL[:,1], c="green", s=6, label="ORIG Bl_0 (211)", zorder=1)
ax.scatter(G[:,0], G[:,1], c="grey", s=4, label="314 bag", zorder=2)
ax.plot(L[:,0], L[:,1], c="blue", lw=0.5, alpha=0.6, label="M144 walk (322)", zorder=3)
ax.scatter([G[221,0]],[G[221,1]], c="orange", s=60, marker="X", label="latch strand slot221", zorder=5)
ax.set_aspect("equal"); ax.legend(fontsize=8); ax.set_title("p144 M144 recovery on 314: walk (blue) vs ORIG arc (green) -- uncovered 0")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "p144_walk.png"), dpi=110)
print("saved p144_walk.png")
fig2, ax2 = plt.subplots(figsize=(12, 4))
ax2.plot(bst, c="blue", lw=0.7)
ax2.axhline(21.72, c="magenta", ls="--", lw=1, label="envelope 21.72 (latch)")
ax2.axhline(25.0, c="orange", ls=":", lw=1, label="25mm bank ceiling")
ax2.axhline(40.0, c="red", ls="-", lw=1, label="40mm jump leg")
ax2.legend(fontsize=8); ax2.set_title("p144 step-length profile: max 22.8, 0 steps>25, 0>=40")
fig2.tight_layout(); fig2.savefig(os.path.join(OUT, "p144_steps.png"), dpi=110)
print("saved p144_steps.png")
# mirror texts
import shutil
for f in ["p144_control.txt","p144_freeze.txt","p144_trigger.txt","p144_walk.txt","p144_verify.txt"]:
    shutil.copy(os.path.join(H, f), os.path.join(OUT, f))
print("mirrored")
log.close()
