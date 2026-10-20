"""Ticket 144 step2 FREEZE: per-bag latch anchor + trigger-feature geometry on 314. No recovery run."""
import numpy as np, os
H = ".scratch/pota144_repro"; P143 = ".scratch/pota143_repro"; INP = ".scratch/pota115_staging/inputs"
log = open(os.path.join(H, "p144_freeze.txt"), "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
G292 = np.load(os.path.join(P143, "p143_G292.npy"))
G = np.load(os.path.join(P143, "p143_G314.npy"))
seq = np.load(os.path.join(H, "p144_seq_greedy314.npy"))
seq292 = np.load(os.path.join(P143, "p143_seq_greedy.npy"))  # greedy-292, read-only
seq279 = np.load(os.path.join(P143, "p143_seq_ctrl.npy"))   # ctrl-279, read-only
W = len(G)
X32 = G.astype(np.float32); keys = np.array([X32[i].tobytes() for i in range(W)])
strand = int(seq[-1])
say("strand slot=%d coord=%s final=%d/314 ratio=%.4f" % (strand, np.round(G[strand],2), len(seq), len(seq)/W))
L = G[np.array(seq)]
st = np.sqrt(((L[1:]-L[:-1])**2).sum(-1))
say("greedy strides: n=%d max=%.2f median=%.2f p90=%.2f n>40mm=%d" % (len(st), st.max(), np.median(st), np.percentile(st,90), int((st>40).sum())))
vis_keys = set(keys[j] for j in seq)
unv = [i for i in range(W) if keys[i] not in vis_keys]
say("visited slots=%d unique visited keys=%d key-fresh unvisited=%d (key never sequenced)" % (len(seq), len(vis_keys), len(unv)))
d = np.sqrt(((G - G[strand]) ** 2).sum(-1))
order = np.argsort(d, kind="stable"); sset = set(seq.tolist()); shown = 0; fresh_d = []
say("nearest unvisited-by-slot to strand:")
for j in order:
    j = int(j)
    if j in sset: continue
    is_fresh = keys[j] not in vis_keys
    if shown < 10:
        say("  slot %d d=%.2f keyfresh=%s" % (j, float(d[j]), is_fresh)); shown += 1
    if is_fresh: fresh_d.append(float(d[j]))
fresh_d = np.array(sorted(fresh_d))
say("key-fresh count=%d nearest key-fresh d=%.2f (next: %s)" % (len(fresh_d), fresh_d[0] if len(fresh_d) else -1, np.round(fresh_d[1:6],2) if len(fresh_d)>1 else []))
idx34 = np.argsort(d, kind="stable")[:34]
say("K-net(34) key-fresh=%d index-unvisited-in-K=%d" % (sum(1 for j in idx34 if keys[int(j)] not in vis_keys), sum(1 for j in idx34 if int(j) not in sset)))
# ORIG gate objects (verbatim p143 gate)
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
def DO_of(Gbag, s):
    Gf = Gbag[np.array(s)].dot(TF[:3,:3].T) + TF[:3,3]
    return np.sqrt(((Og[:,None,:]-Gf[None,:,:])**2).sum(-1)).min(1)
DO314 = DO_of(G, seq); DO292 = DO_of(G292, seq292); DO279 = DO_of(np.load(os.path.join(P143, "p143_G279.npy")), seq279)
for name, DO in [("314-greedy",DO314),("292-greedy",DO292),("279-greedy",DO279)]:
    say("%s: ORIGcov %d/211 uncovered %d" % (name, int((DO<2).sum()), int((DO>5).sum())))
new_vs_292 = sorted(np.where((DO314<2)&(DO292>=2))[0].tolist())
new_vs_279 = sorted(np.where((DO314<2)&(DO279>=2))[0].tolist())
say("newly covered (DO<2) vs 292-greedy: %d %s" % (len(new_vs_292), new_vs_292))
say("newly covered (DO<2) vs 279-greedy: %d %s" % (len(new_vs_279), new_vs_279))
# admitted-32: visits + unvisited geometry vs frozen road
NEW = list(range(282, 314))
road = G[np.array(seq)]
for s in NEW:
    pos = (np.where(seq == s)[0][0] if (seq == s).any() else -1)
    dd = float(np.sqrt(((road - G[s])**2).sum(-1)).min())
    seat = int(np.argmin(np.sqrt(((Og - (G[s].dot(TF[:3,:3].T)+TF[:3,3]))**2).sum(-1))))
    seatd = float(np.sqrt(((Og[seat] - (G[s].dot(TF[:3,:3].T)+TF[:3,3]))**2).sum()))
    say("slot %d seqpos=%d minDistRoad=%.2f seat=O%d seatDO=%.2f" % (s, int(pos), dd, seat, seatd))
# ORIGcov trajectory every 20 steps
Gf_all = L.dot(TF[:3,:3].T) + TF[:3,3]
Dall = np.sqrt(((Og[:,None,:]-Gf_all[None,:,:])**2).sum(-1))
cov_steps = [int((Dall[:t].min(axis=0) < 2).sum()) for t in range(20, len(seq)+1, 20)]
say("ORIGcov trajectory every20steps: %s" % cov_steps)
say("QUOTE stuck (116 Comments s5, read-only): far-arc strand K-window 34/34 visited; nearest fresh=B slots 101.6-102.9mm")
log.close(); print("freeze done")
