"""Ticket 143 step4: forced-T13 MECHANISM PROBE on 292 (NOT banked, same class as 133 s4).
Same walk_plain but T13 recovery un-gated (fires regardless of gn/W ratio).
Question: do the 10 true dots pay under honest recovery (uncovered <8)?"""
import numpy as np, os
H = ".scratch/pota143_repro"
INP = ".scratch/pota115_staging/inputs"
log = open(os.path.join(H, "p143_probe.txt"), "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
G = np.load(os.path.join(H, "p143_G292.npy")); W = len(G)
assert W == 292, W
X32 = G.astype(np.float32)
keys = np.array([X32[i].tobytes() for i in range(W)])
def walk_forced(G, keys, W):
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
    big = [float(x) for x in st[st>=40]]
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
    say("%s: final=%d gate med=%.4f <2mm=%.1f%% gaps5=%d maxstep=%.1f big40=%d ORIGcov %d/211 uncovered=%d spans=%s" % (tag, len(seq), float(np.median(D)), float((D<2).mean()*100), nj, float(st.max()), len(big), cov, unc, spans))
    return float(np.median(D)), unc, len(seq), cov, spans
seq, gn, jm, ja = walk_forced(G, keys, W)
say("FORCED-292: greedy=%d/%d final=%d jumps=%d" % (gn, W, len(seq), jm))
for a, b in ja:
    L = G[np.array(seq)]; st = float(np.sqrt(((L[b]-L[a])**2).sum()))
    say("  jump seqpos %d->%d len=%.1f" % (a, b, st))
med, unc, fin, cov, spans = gate(G, seq, "FORCED gate")
np.save(os.path.join(H, "p143_seq_forced.npy"), seq)
say("vs M134d-282 (290/278u/med 4.2488/unc 8/same spans): beat-or-match?")
log.close(); print("step4 done")
