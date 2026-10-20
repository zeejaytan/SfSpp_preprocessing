"""Ticket 144 step3: M144 (= M134d form, 314 values) envelope-retreat walk. Trigger T144 already fired."""
import numpy as np, os
H = ".scratch/pota144_repro"; P143 = ".scratch/pota143_repro"; INP = ".scratch/pota115_staging/inputs"
log = open(os.path.join(H, "p144_walk.txt"), "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
G = np.load(os.path.join(P143, "p143_G314.npy")); W = len(G)
assert W == 314
X32 = G.astype(np.float32); kk = np.array([X32[i].tobytes() for i in range(W)])
# greedy phase VERBATIM (must re-strand at 140/slot221)
cvis = {kk[0]: 0}; cseq = [0]; cur = 0
for t in range(1, W):
    d = np.sqrt(((G - G[cur]) ** 2).sum(-1))
    idx = np.argsort(d, kind="stable")[:34]
    if t == 1:
        nxt = int(idx[1]); cseq.append(nxt); cvis[kk[nxt]] = 1; cur = nxt; continue
    unv = [int(j) for j in idx if kk[int(j)] not in cvis]
    if not unv: break
    j = unv[0]; cseq.append(j); cvis[kk[j]] = len(cseq)-1; cur = j
assert len(cseq) == 140 and int(cseq[-1]) == 221, (len(cseq), cseq[-1])
say("greedy-phase verbatim: strand %d/314 slot %d (latch L144 re-confirmed)" % (len(cseq), int(cseq[-1])))
# envelope = walk's own max greedy stride (frozen latch value; assert == freeze 21.72)
Lg = G[np.array(cseq)]
BAND = float(np.sqrt(((Lg[1:]-Lg[:-1])**2).sum(-1)).max())
say("envelope BAND=%.2f (freeze 21.72)" % BAND)
assert abs(BAND - 21.72) < 0.01
# M134d-form recovery (port of p134_step8, 314 values)
retreats = []; forwards = []; guard = 0
while len(set(cseq)) < W and guard < 60000:
    guard += 1
    d = np.sqrt(((G - G[cur]) ** 2).sum(-1))
    idx = np.argsort(d, kind="stable")[:34]
    sset = set(cseq); nxt = None
    for j in idx:
        j = int(j)
        if j not in sset and float(d[j]) >= 1.0: nxt = j; break
    if nxt is not None:
        cseq.append(nxt); cvis.setdefault(kk[nxt], len(cseq)-1); cur = nxt; continue
    dc = np.sqrt(((G - G[cur])**2).sum(-1))
    order = np.argsort(dc, kind="stable")
    seen = {}
    for p, s_ in enumerate(cseq):
        if int(s_) not in seen: seen[int(s_)] = p
    best = None
    for s_ in order:
        s_ = int(s_)
        if s_ == cur: continue
        dd = np.sqrt(((G - G[s_])**2).sum(-1)); ii = np.argsort(dd, kind="stable")[:34]
        if any(int(j) not in sset and float(dd[int(j)]) >= 1.0 for j in ii): best = s_; break
    if best is not None and float(dc[best]) <= BAND:
        retreats.append((len(cseq)-1, len(cseq), float(dc[best])))
        cseq.append(best); cur = best; continue
    if best is not None:
        say("HALT: nearest road-retreat %.2f exceeds envelope %.2f -- walk ends" % (float(dc[best]), BAND)); break
    dd = np.sqrt(((G - G[cur]) ** 2).sum(-1))
    mask = np.array([kk[i] in cvis for i in range(W)])
    if mask.all(): break
    dd[mask] = np.inf; nx = int(np.argmin(dd))
    forwards.append((len(cseq)-1, len(cseq), float(np.sqrt(((G[nx]-G[cur])**2).sum()))))
    cseq.append(nx); cvis[kk[nx]] = len(cseq)-1; cur = nx
seq = np.array(cseq, dtype=int)
L = G[seq]
bst = np.sqrt(((L[1:]-L[:-1])**2).sum(-1))
say("M144 walk: seqlen=%d unique=%d retreats=%d forwards=%d guard=%d" % (len(seq), len(set(cseq)), len(retreats), len(forwards), guard))
for i,(a,b,c) in enumerate(retreats):
    say("  retreat #%d at (%d->%d) len=%.2f" % (i, a, b, c))
for a,b,c in forwards:
    say("  FORWARD at (%d->%d) len=%.2f" % (a, b, c))
# gate VERBATIM p143 (Og-only, to compare vs 3.9851)
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
Gf = L.dot(TF[:3,:3].T)+TF[:3,3]
D = np.sqrt(((Gf[:,None,:]-Og[None,:,:])**2).sum(-1)).min(1)
DO = np.sqrt(((Og[:,None,:]-Gf[None,:,:])**2).sum(-1)).min(1)
cov = int((DO<2).sum()); unc = int((DO>5).sum())
ui = sorted(np.where(DO>5)[0].tolist()); spans = []
if ui:
    a=ui[0]; p=ui[0]
    for q in ui[1:]:
        if q==p+1: p=q
        else: spans.append((a,p)); a=q; p=q
    spans.append((a,p))
med = float(np.median(D))
say("M144 gate: seqlen=%d med=%.4f <2mm=%.1f%% gaps5=%d maxstep=%.1f ORIGcov %d/211 uncovered=%d spans=%s" % (len(seq), med, float((D<2).mean()*100), int((bst>5).sum()), float(bst.max()), cov, unc, spans))
over25 = sorted([float(x) for x in bst if x > 25])
say("steps>25mm: n=%d %s" % (len(over25), [round(x,2) for x in over25]))
big = int((bst>=40).sum())
bar = (len(set(cseq))>140 and med<=3.9851 and unc<15 and big==0 and len(over25)==0)
say("BAR: unique>140 %s | gate<=3.9851 %s | uncovered<15 %s | big0(>=40) %s | nostep>25 %s -> %s" % (len(set(cseq))>140, med<=3.9851, unc<15, big==0, len(over25)==0, "ALL-HOLD" if bar else "MISS"))
np.save(os.path.join(H, "p144_seq_m144.npy"), seq)
log.close(); print("recover done")
