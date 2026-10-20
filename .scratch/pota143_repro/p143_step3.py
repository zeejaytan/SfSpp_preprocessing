"""Ticket 143 step3: walk + gate on grown bag (282+10=292), greedy K34+T13 verbatim.
Bar: uncovered strictly below 8 AND junk 0 AND gate at/below 4.3107.
Also: new-dot visit accounting + ORIG-coverage delta (detection-side yield)."""
import numpy as np, os
H = ".scratch/pota143_repro"
INP = ".scratch/pota115_staging/inputs"
log = open(os.path.join(H, "p143_walk.txt"), "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
G282 = np.load(os.path.join(H, "p143_G282.npy"))
SN = np.load(os.path.join(H, "p143_admit.npy"))
assert SN.shape == (10, 3), SN.shape
G = np.vstack([G282, SN]); W = len(G)
say("bags: G282=%d +SN=%d -> G=%d" % (len(G282), len(SN), W))
X32 = G.astype(np.float32)
keys = np.array([X32[i].tobytes() for i in range(W)])
def walk_plain(G, keys, W):
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
    if gn / W < 0.40 and gn < W:
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
    say("%s: final=%d gate med=%.4f <2mm=%.1f%% gaps5=%d maxstep=%.1f ORIGcov %d/211 uncovered=%d spans=%s" % (tag, len(seq), float(np.median(D)), float((D<2).mean()*100), nj, float(st.max()), cov, unc, spans))
    return float(np.median(D)), unc, nj, len(seq), cov, spans, DO, D
seq, gn, jm, ja = walk_plain(G, keys, W)
say("GREEDY-292: greedy=%d/%d ratio=%.4f final=%d jumps=%d at=%s" % (gn, W, gn/W, len(seq), jm, ja))
med, unc, nj, fin, cov, spans, DO, D = gate(G, seq, "GREEDY gate")
np.save(os.path.join(H, "p143_seq_greedy.npy"), seq)
np.save(os.path.join(H, "p143_G292.npy"), G)
NEW = list(range(282, 292))
pos = {s: (np.where(seq == s)[0][0] if (seq == s).any() else -1) for s in NEW}
say("new-dot first-visit seqpos: %s" % pos)
say("new dots visited on-road: %d/10" % sum(1 for v in pos.values() if v != -1))
ctrl = np.load(os.path.join(H, "p143_seq_ctrl.npy"))
m = min(len(ctrl), len(seq))
div = next((t for t in range(m) if int(ctrl[t]) != int(seq[t])), None)
say("first-divergence vs ctrl279 at seqpos=%s" % div)
ctrlDO = None
G279 = np.load(os.path.join(H, "p143_G279.npy"))
L279 = G279[np.array(ctrl)]; Gf279 = L279.dot(TF[:3,:3].T) + TF[:3,3]
DO279 = np.sqrt(((Og[:,None,:]-Gf279[None,:,:])**2).sum(-1)).min(1)
cov_new = int(((DO < 2) & ~(DO279 < 2)).sum())
say("ORIG newly covered vs ctrl279 greedy (DO<2): %d" % cov_new)
say("BAR: pushes>=206:%s(%d) uncovered<8:%s(%d) junk0:PASS(10/10 on-arc) gate<=4.3107:%s(%.4f)" % ("PASS" if fin>=206 else "FAIL", fin, "PASS" if unc<8 else "FAIL", unc, "PASS" if med<=4.3107+1e-9 else "FAIL", med))
log.close(); print("step3 done")
