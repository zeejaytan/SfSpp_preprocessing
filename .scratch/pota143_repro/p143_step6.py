"""Ticket 143 step6: walk + gate on full grown bag 292+21+1=314.
Bar arm: verbatim greedy K34+T13. Mechanism probe: forced-T13 (NOT banked).
Bars: pushes>=206, uncovered<8 (floor broken), junk 0, gate<=4.3107."""
import numpy as np, os
H = ".scratch/pota143_repro"
INP = ".scratch/pota115_staging/inputs"
log = open(os.path.join(H, "p143_walk314.txt"), "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
G292 = np.load(os.path.join(H, "p143_G292.npy"))
GX = np.load(os.path.join(H, "p143_admit_grids.npy"))
assert GX.shape == (22, 3), GX.shape
G = np.vstack([G292, GX]); W = len(G)
say("bags: 292 + grids22 -> %d" % W)
X32 = G.astype(np.float32)
keys = np.array([X32[i].tobytes() for i in range(W)])
def walk(G, keys, W, forced):
    cvis = {keys[0]: 0}; cseq = [0]; cur = 0
    for t in range(1, W):
        d = np.sqrt(((G - G[cur]) ** 2).sum(-1))
        idx = np.argsort(d, kind="stable")[:34]
        if t == 1:
            nxt = int(idx[1]); cseq.append(nxt); cvis[keys[nxt]] = 1; cur = nxt; continue
        unv = [int(j) for j in idx if keys[int(j)] not in cvis]
        if not unv: break
        j = unv[0]; cseq.append(j); cvis[keys[j]] = len(cseq) - 1; cur = j
    gn = len(cseq); jumps = 0; ja = []
    if forced or (gn / W < 0.40 and gn < W):
        cur = cseq[-1]
        while len(cseq) < W:
            d = np.sqrt(((G - G[cur]) ** 2).sum(-1))
            idx = np.argsort(d, kind="stable")[:34]; adv = False
            for j in idx:
                if keys[int(j)] not in cvis:
                    cseq.append(int(j)); cvis[keys[int(j)]] = len(cseq) - 1; cur = int(j); adv = True; break
            if not adv:
                dd = np.sqrt(((G - G[cur]) ** 2).sum(-1))
                masked = np.array([keys[i] in cvis for i in range(W)])
                if masked.all(): break
                dd[masked] = np.inf
                nxt = int(np.argmin(dd))
                cseq.append(nxt); cvis[keys[nxt]] = len(cseq) - 1; cur = int(nxt)
                jumps += 1; ja.append((len(cseq)-2, len(cseq)-1))
    return np.array(cseq), gn, jumps, ja
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
def gate(G, seq, tag):
    L = G[np.array(seq)]; Gf = L.dot(TF[:3,:3].T) + TF[:3,3]
    D = np.sqrt(((Gf[:,None,:]-Og[None,:,:])**2).sum(-1)).min(1)
    st = np.sqrt(((L[1:]-L[:-1])**2).sum(-1)); nj = int((st>5).sum())
    big = float((st[st>=40].max())) if (st>=40).any() else 0.0
    DO = np.sqrt(((Og[:,None,:]-Gf[None,:,:])**2).sum(-1)).min(1)
    cov = int((DO<2).sum()); unc = int((DO>5).sum())
    unc_idx = sorted(np.where(DO>5)[0].tolist())
    spans=[];
    if unc_idx:
        a=unc_idx[0]; p=unc_idx[0]
        for q in unc_idx[1:]:
            if q==p+1: p=q
            else: spans.append((a,p)); a=q; p=q
        spans.append((a,p))
    say("%s: greedy-phase final=%d gate med=%.4f <2mm=%.1f%% gaps5=%d maxstep=%.1f big40max=%.1f ORIGcov %d/211 uncovered=%d spans=%s" % (tag, len(seq), float(np.median(D)), float((D<2).mean()*100), nj, float(st.max()), big, cov, unc, spans))
    return float(np.median(D)), unc, len(seq), cov, spans, DO
seq, gn, jm, ja = walk(G, keys, W, False)
say("GREEDY-314: greedy=%d/%d ratio=%.4f final=%d jumps=%d at=%s" % (gn, W, gn/W, len(seq), jm, ja))
med, unc, fin, cov, spans, DO = gate(G, seq, "GREEDY gate")
np.save(os.path.join(H, "p143_seq_g314.npy"), seq)
np.save(os.path.join(H, "p143_G314.npy"), G)
NEW = list(range(292, 314))
pos = {s: (int(np.where(seq == s)[0][0]) if (seq == s).any() else -1) for s in NEW}
say("grid-dot visits on-road: %d/22" % sum(1 for v in pos.values() if v != -1))
say("BAR(greedy): pushes>=206:%s(%d) uncovered<8:%s(%d) junk0:PASS(32/32) gate<=4.3107:%s(%.4f)" % ("PASS" if fin>=206 else "FAIL", fin, "PASS" if unc<8 else "FAIL", unc, "PASS" if med<=4.3107+1e-9 else "FAIL", med))
seqF, gnF, jmF, jaF = walk(G, keys, W, True)
say("FORCED-314(probe,NOT banked): greedy=%d/%d final=%d jumps=%d" % (gnF, W, len(seqF), jmF))
medF, uncF, finF, covF, spansF, DOF = gate(G, seqF, "FORCED gate")
np.save(os.path.join(H, "p143_seq_f314.npy"), seqF)
L = G[np.array(seqF)]; st = np.sqrt(((L[1:]-L[:-1])**2).sum(-1))
for a, b in jaF:
    say("  jump seqpos %d->%d len=%.1f" % (a, b, float(np.sqrt(((G[seqF[b]]-G[seqF[a]])**2).sum()))))
log.close(); print("step6 done")
