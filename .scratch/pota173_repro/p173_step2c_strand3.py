# 173 step2c: diagnostic THIRD strand from still-unsequenced dots from unsequenced dots (same M144 mechanics).
# Question: are the 45 bag-covered-but-walk-missed stations reachable by chaining
# leftover dots, i.e. is the miss multi-strand-recoverable? Diagnostic only.
import numpy as np, os
from scipy.spatial import cKDTree
H = ".scratch/pota173_repro"
log = open(os.path.join(H, "p173_step2c.txt"), "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
d = np.load(os.path.join(H, "p173_bag.npz"), allow_pickle=True)
BAG = d["BAG"]; G0 = d["G0"]
seq = np.load(os.path.join(H, "p173_seq.npy")); seqA = seq
used = set(np.load(os.path.join(H, "p173_seq.npy")).tolist()) | set(np.load(os.path.join(H, "p173_seq2.npy")).tolist())
uns = np.array([i for i in range(len(BAG)) if i not in used])
say("unsequenced=%d" % len(uns))
U = BAG[uns]
# greedy strand seeded at medoid of leftover, same K34/twin-skip rule, own envelope
c = U.mean(0)
s0 = int(uns[int(np.argmin(((U-c)**2).sum(-1)))])
X32 = BAG.astype(np.float32); kk = np.array([X32[i].tobytes() for i in range(len(BAG))])
cvis = {kk[s0]: 0}; cseq = [s0]; cur = s0
W = len(BAG)
for t in range(1, W):
    dd = np.sqrt(((BAG - BAG[cur]) ** 2).sum(-1))
    idx = np.argsort(dd, kind="stable")[:34]
    if t == 1:
        nxt = int(idx[1]); cseq.append(nxt); cvis[kk[nxt]] = 1; cur = nxt; continue
    unv = [int(j) for j in idx if kk[int(j)] not in cvis]
    if not unv: break
    j = int(unv[0]); cseq.append(j); cvis[kk[j]] = len(cseq)-1; cur = j
say("strand2 greedy len=%d seed=%d" % (len(cseq), s0))
Lg = BAG[np.array(cseq)]
gsteps = np.sqrt(((Lg[1:]-Lg[:-1])**2).sum(-1))
BAND = float(gsteps.max()) if len(gsteps) else 0.0
say("strand2 BAND=%.2f med=%.2f" % (BAND, float(np.median(gsteps)) if len(gsteps) else -1))
seq2 = list(cseq); cur = seq2[-1]; guard = 0; HALT2 = ""
while guard < 60000:
    guard += 1
    dd = np.sqrt(((BAG - BAG[cur])**2).sum(-1))
    idx = np.argsort(dd, kind="stable")[:34]
    sset = set(seq2); nxt = None
    for j in idx:
        j = int(j)
        if j not in sset and float(dd[j]) >= 1.0: nxt = j; break
    if nxt is not None:
        seq2.append(nxt); cur = nxt; continue
    dc = np.sqrt(((BAG - BAG[cur])**2).sum(-1))
    order = np.argsort(dc, kind="stable")
    seen = {}
    for p, s_ in enumerate(seq2):
        if int(s_) not in seen: seen[int(s_)] = p
    best = None
    for s_ in order:
        s_ = int(s_)
        if s_ == cur: continue
        ddx = np.sqrt(((BAG - BAG[s_])**2).sum(-1)); iix = np.argsort(ddx, kind="stable")[:34]
        if any(int(j) not in sset and float(ddx[int(j)]) >= 1.0 for j in iix): best = s_; break
    if best is not None and float(dc[best]) <= BAND:
        seq2.append(best); cur = best; continue
    if best is not None:
        HALT2 = "HALT2 %.2f > %.2f" % (float(dc[best]), BAND); say(HALT2); break
    break
seq2 = np.array(seq2, dtype=int)
say("strand2 seqlen=%d unique=%d %s" % (len(seq2), len(set(seq2.tolist())), HALT2))
# union coverage: primary walk L1 + strand2 L2
L1 = BAG[np.load(os.path.join(H, "p173_seq.npy"))]; L2 = BAG[seq2]
Lu = np.vstack([L1, L2])
KW = cKDTree(Lu)
do_u = KW.query(G0)[0]
say("union ORIGcov=%d/211" % int((do_u<2).sum()))
# of the 45 walk-missed-bag-covered, how many does strand2 visit?
KW2 = cKDTree(L2)
do_w1 = cKDTree(L1).query(G0)[0]
miss45 = np.where((cKDTree(BAG).query(G0)[0]<2) & ~(do_w1<2))[0]
say("strand2 visits %d/45 of walk-missed-bag-covered" % int((KW2.query(G0[miss45])[0]<2).sum()))
# overlap of strand2 with primary seq (shared dots)
say("strand2 dots already in primary: %d/%d" % (len(set(seq2.tolist()) & used), len(seq2)))
np.save(os.path.join(H, "p173_seq3.npy"), seq2)
D = np.sqrt(((L2[:,None,:]-G0[None,:,:])**2).sum(-1)).min(1)
say("strand2-alone gate: med=%.4f <2mm=%.1f%%" % (float(np.median(D)), float((D<2).mean()*100)))
log.close(); print("STEP2B DONE");
