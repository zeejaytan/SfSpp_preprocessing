"""Ticket 143 step1: CONTROL - rebuild 279, greedy K34+T13, gate vs 128 marks.
Reproduce-or-stop: 206 / med 4.3107 / uncovered 15 spans [(32,37),(46,50),(96,97),(165,165),(173,173)]."""
import numpy as np, os
H = ".scratch/pota143_repro"
INP = ".scratch/pota115_staging/inputs"
R119 = ".scratch/pota119_repro"
os.makedirs(H, exist_ok=True)
log = open(os.path.join(H, "p143_control.txt"), "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
C = np.load(os.path.join(INP, "p113_guarded.npz"))["bag"]
SN124 = np.load(".scratch/pota124_repro/p124_admit_c2p5.npy")
SN128 = np.load(".scratch/pota128_repro/p128_admit.npy")
SN133 = np.load(".scratch/pota133_repro/p133_admit.npy")
G279 = np.vstack([C, SN124, SN128])
assert len(G279) == 279, len(G279)
G282 = np.vstack([G279, SN133])
assert len(G282) == 282, len(G282)
say("bags: C=%d SN124=%d SN128=%d SN133=%d -> 279=%d 282=%d" % (len(C), len(SN124), len(SN128), len(SN133), len(G279), len(G282)))
W = len(G279); G1 = G279
X32 = G1.astype(np.float32)
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
say("ORIG gate pts: %d" % len(Og))
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
    return float(np.median(D)), unc, nj, len(seq), cov, spans, DO
seq, gn, jm, ja = walk_plain(G1, keys, W)
say("GREEDY-279: greedy=%d/%d final=%d jumps=%d at=%s" % (gn, W, len(seq), jm, ja))
med, unc, nj, fin, cov, spans, DO = gate(G1, seq, "GREEDY gate")
ok = (fin==206 and abs(med-4.3107)<1e-3 and unc==15 and spans==[(32,37),(46,50),(96,97),(165,165),(173,173)])
say("CONTROL ~= 128 marks (206/4.3107/15/spans): %s" % ("GREEN" if ok else "RED - STOP"))
np.save(os.path.join(H, "p143_seq_ctrl.npy"), seq)
np.save(os.path.join(H, "p143_G279.npy"), G279)
np.save(os.path.join(H, "p143_G282.npy"), G282)
log.close(); print("step1 done GREEN" if ok else "step1 done RED")
