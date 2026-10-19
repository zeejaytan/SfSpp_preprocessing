# 175 step2: walk EACH face cloud with M144-family recipe VERBATIM (p173_step1 mechanics).
# Clouds (ORIG-free split, stated from probe0/probe1): TRUE = align<-0.5 OR |align|<=0.5 (598),
# OUTER = align>+0.5 (155). ORIG used ONLY inside gate scoring.
import numpy as np, os
H = "C:/PR/SfSpp_preprocessing/.scratch/pota175_repro"
os.makedirs(H, exist_ok=True)
log = open(H + "/p175_step2.txt", "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
def walk(T, tag):
    W = len(T)
    X32 = T.astype(np.float32); kk = np.array([X32[i].tobytes() for i in range(W)])
    cvis = {kk[0]: 0}; cseq = [0]; cur = 0
    for t in range(1, W):
        dd = np.sqrt(((T - T[cur]) ** 2).sum(-1))
        idx = np.argsort(dd, kind="stable")[:34]
        if t == 1:
            nxt = int(idx[1]); cseq.append(nxt); cvis[kk[nxt]] = 1; cur = nxt; continue
        unv = [int(j) for j in idx if kk[int(j)] not in cvis]
        if not unv: break
        j = int(unv[0]); cseq.append(j); cvis[kk[j]] = len(cseq)-1; cur = j
    say("%s greedy: len=%d/%d strand slot=%d T13-ratio=%.4f (%s)" % (tag, len(cseq), W, int(cseq[-1]), len(cseq)/W, "SUPPRESSED" if len(cseq)/W>=0.40 else "FIRES?"))
    Lg = T[np.array(cseq)]
    gsteps = np.sqrt(((Lg[1:]-Lg[:-1])**2).sum(-1))
    BAND = float(gsteps.max()) if len(gsteps) else 0.0
    say("%s envelope BAND=%.2f (greedy med=%.2f n>40=%d)" % (tag, BAND, float(np.median(gsteps)) if len(gsteps) else -1, int((gsteps>40).sum()) if len(gsteps) else -1))
    seq = list(cseq); cvm = dict(cvis); cur = seq[-1]
    retreats = []; forwards = []; guard = 0; HALT = ""
    while len(set(seq)) < W and guard < 60000:
        guard += 1
        dd = np.sqrt(((T - T[cur]) ** 2).sum(-1))
        idx = np.argsort(dd, kind="stable")[:34]
        sset = set(seq); nxt = None
        for j in idx:
            j = int(j)
            if j not in sset and float(dd[j]) >= 1.0: nxt = j; break
        if nxt is not None:
            seq.append(nxt); cvm.setdefault(kk[nxt], len(seq)-1); cur = nxt; continue
        dc = np.sqrt(((T - T[cur])**2).sum(-1))
        order = np.argsort(dc, kind="stable")
        seen = {}
        for p, s_ in enumerate(seq):
            if int(s_) not in seen: seen[int(s_)] = p
        best = None
        for s_ in order:
            s_ = int(s_)
            if s_ == cur: continue
            ddx = np.sqrt(((T - T[s_])**2).sum(-1)); iix = np.argsort(ddx, kind="stable")[:34]
            if any(int(j) not in sset and float(ddx[int(j)]) >= 1.0 for j in iix): best = s_; break
        if best is not None and float(dc[best]) <= BAND:
            retreats.append((len(seq)-1, len(seq), float(dc[best])))
            seq.append(best); cur = best; continue
        if best is not None:
            HALT = "HALT: nearest road-retreat %.2f exceeds envelope %.2f" % (float(dc[best]), BAND); say("%s %s" % (tag, HALT)); break
        ddx = np.sqrt(((T - T[cur]) ** 2).sum(-1))
        mask = np.array([kk[i] in cvm for i in range(W)])
        if mask.all(): break
        ddx[mask] = np.inf; nx = int(np.argmin(ddx))
        forwards.append((len(seq)-1, len(seq), float(np.sqrt(((T[nx]-T[cur])**2).sum()))))
        seq.append(nx); cvm[kk[nx]] = len(seq)-1; cur = nx
    seq = np.array(seq, dtype=int)
    say("%s M-walk: seqlen=%d unique=%d/%d retreats=%d forwards=%d guard=%d %s" % (tag, len(seq), len(set(seq.tolist())), W, len(retreats), len(forwards), guard, HALT))
    for i,(a,b,c) in enumerate(retreats):
        say("  %s retreat #%d at (%d->%d) len=%.2f" % (tag, i, a, b, c))
    for a,b,c in forwards:
        say("  %s FORWARD at (%d->%d) len=%.2f" % (tag, a, b, c))
    np.save(H + "/p175_seq_%s.npy" % tag, seq)
    np.save(H + "/p175_greedy_%s.npy" % tag, np.array(cseq, dtype=int))
    return seq
d = np.load("C:/PR/SfSpp_preprocessing/.scratch/pota173_repro/p173_bag.npz", allow_pickle=True)
BAG, G0 = d["BAG"], d["G0"]
z = np.load(H + "/p175_probe0.npz")
alB = z["alB"]
TRUE = (alB <= 0.5); OUT = (alB > 0.5)
say("clouds: TRUE=%d OUTER=%d" % (int(TRUE.sum()), int(OUT.sum())))
sT = walk(BAG[TRUE], "TRUE")
sO = walk(BAG[OUT], "OUTER")
np.save(H + "/p175_mask_true.npy", TRUE)
log.close(); print("step2 done")
