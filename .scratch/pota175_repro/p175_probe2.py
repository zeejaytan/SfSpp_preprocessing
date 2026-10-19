# 175 probe2: TRUE-cloud cap + halt diagnosis + seed sweep (M144 mechanics, seeds vary).
import numpy as np
H = "C:/PR/SfSpp_preprocessing/.scratch/pota175_repro"
log = open(H + "/p175_probe2.txt", "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
d = np.load("C:/PR/SfSpp_preprocessing/.scratch/pota173_repro/p173_bag.npz", allow_pickle=True)
BAG, G0 = d["BAG"], d["G0"]
N = len(G0)
TRUE = np.load(H + "/p175_mask_true.npy")
T = BAG[TRUE]
DO = np.sqrt(((G0[:,None,:]-T[None,:,:])**2).sum(-1)).min(1)
cap = int((DO<2).sum())
ui = sorted(np.where(DO>=2)[0].tolist()); runs = []
if ui:
    a=ui[0]; p=ui[0]
    for q in ui[1:]:
        if q==p+1: p=q
        else: runs.append((a,p)); a=q; p=q
    runs.append((a,p))
say("TRUE-cloud cap: %d/211 stations <2mm; cloud-missing runs=%s" % (cap, runs))
# where did row-0 walk sit? endpoints
seq0 = np.load(H + "/p175_seq_TRUE.npy")
L0 = T[np.array(seq0, dtype=int)]
from scipy.spatial import cKDTree
KG0 = cKDTree(G0)
st0 = KG0.query(L0)[1]
say("row0-walk station span: %d..%d (first=%d last=%d)" % (int(st0.min()), int(st0.max()), int(st0[0]), int(st0[-1])))
# gap profile along TRUE cloud in station order: nearest TRUE dot per station
say("TRUE cloud per-station dmin: max=%.2f stations>2mm=%s" % (float(DO.max()), ui))
# seed sweep
def walk_from(Tc, seed):
    W = len(Tc)
    X32 = Tc.astype(np.float32); kk = np.array([X32[i].tobytes() for i in range(W)])
    cvis = {kk[seed]: 0}; cseq = [seed]; cur = seed
    first = True
    for t in range(1, W):
        dd = np.sqrt(((Tc - Tc[cur]) ** 2).sum(-1))
        idx = np.argsort(dd, kind="stable")[:34]
        if first:
            # first step: nearest unvisited (seed itself excluded as visited)
            unv0 = [int(j) for j in idx if kk[int(j)] not in cvis]
            if not unv0: break
            nxt = int(unv0[0]); cseq.append(nxt); cvis[kk[nxt]] = 1; cur = nxt; first = False; continue
        unv = [int(j) for j in idx if kk[int(j)] not in cvis]
        if not unv: break
        j = int(unv[0]); cseq.append(j); cvis[kk[j]] = len(cseq)-1; cur = j
    Lg = Tc[np.array(cseq)]
    gsteps = np.sqrt(((Lg[1:]-Lg[:-1])**2).sum(-1))
    BAND = float(gsteps.max()) if len(gsteps) else 0.0
    seq = list(cseq); cvm = dict(cvis); cur = seq[-1]
    retreats = 0; forwards = 0; guard = 0; HALT = ""
    while len(set(seq)) < W and guard < 60000:
        guard += 1
        dd = np.sqrt(((Tc - Tc[cur]) ** 2).sum(-1))
        idx = np.argsort(dd, kind="stable")[:34]
        sset = set(seq); nxt = None
        for j in idx:
            j = int(j)
            if j not in sset and float(dd[j]) >= 1.0: nxt = j; break
        if nxt is not None:
            seq.append(nxt); cvm.setdefault(kk[nxt], len(seq)-1); cur = nxt; continue
        dc = np.sqrt(((Tc - Tc[cur])**2).sum(-1))
        order = np.argsort(dc, kind="stable")
        best = None
        for s_ in order:
            s_ = int(s_)
            if s_ == cur: continue
            ddx = np.sqrt(((Tc - Tc[s_])**2).sum(-1)); iix = np.argsort(ddx, kind="stable")[:34]
            if any(int(j) not in sset and float(ddx[int(j)]) >= 1.0 for j in iix): best = s_; break
        if best is not None and float(dc[best]) <= BAND:
            retreats += 1; seq.append(best); cur = best; continue
        if best is not None:
            HALT = "HALT retreat %.2f> BAND %.2f" % (float(dc[best]), BAND); break
        ddx = np.sqrt(((Tc - Tc[cur]) ** 2).sum(-1))
        mask = np.array([kk[i] in cvm for i in range(W)])
        if mask.all(): break
        ddx[mask] = np.inf; nx = int(np.argmin(ddx))
        forwards += 1; seq.append(nx); cvm[kk[nx]] = len(seq)-1; cur = nx
    seq = np.array(seq, dtype=int)
    L = Tc[seq]
    D = np.sqrt(((L[:,None,:]-G0[None,:,:])**2).sum(-1)).min(1)
    DOw = np.sqrt(((G0[:,None,:]-L[None,:,:])**2).sum(-1)).min(1)
    return seq, len(seq), int((DOw<2).sum()), float(np.median(D)), HALT, BAND
# medoid of TRUE cloud
Dall = np.sqrt(((T[:,None,:]-T[None,:,:])**2).sum(-1))
med = int(np.argmin(Dall.sum(0)))
seeds = {"row0": 0, "medoid": med}
# spread seeds: far-apart rows
picked = [med]
for k in range(4):
    dd = np.sqrt(((T[:,None,:]-T[np.array(picked)][None,:,:])**2).sum(-1)).min(1)
    picked.append(int(np.argmax(dd)))
for i,p in enumerate(picked[1:]):
    seeds["spread%d" % i] = p
for nm, s_ in seeds.items():
    seq, ln, cov, medd, halt, band = walk_from(T, int(s_))
    np.save(H + "/p175_seed_%s.npy" % nm, seq)
    say("seed %s(row=%d): seqlen=%d cov=%d/211 med=%.3f BAND=%.2f %s" % (nm, int(s_), ln, cov, medd, band, halt))
log.close(); print("probe2 done")
