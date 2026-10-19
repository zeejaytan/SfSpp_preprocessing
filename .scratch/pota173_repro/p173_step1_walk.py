# 170 step1: walk NO-VETO post-snap curated bag with M144 machinery VERBATIM (p168b_step1 port).
# Frame note: curated bag K is GATE frame already (TF applied in step0), so gating
# uses identity; greedy/recovery strides are rigid-invariant (verbatim mechanics).
import numpy as np, os
H = ".scratch/pota173_repro"
log = open(os.path.join(H, "p173_step1.txt"), "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
def pct(x, q): return float(np.percentile(x, q))
d = np.load(os.path.join(H, "p173_bag.npz"), allow_pickle=True)
T = d["BAG"]; Og = d["G0"]; N = len(Og); W = len(T)
say("densified bag: %d dots (expect 753), ORIG Bl_0 %d" % (W, N))
assert W == 753 and N == 211
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
say("den-greedy: len=%d/%d strand slot=%d T13-ratio=%.4f (strand=>T13 %s)" % (len(cseq), W, int(cseq[-1]), len(cseq)/W, "SUPPRESSED" if len(cseq)/W>=0.40 else "FIRES?"))
Lg = T[np.array(cseq)]
gsteps = np.sqrt(((Lg[1:]-Lg[:-1])**2).sum(-1))
BAND = float(gsteps.max()) if len(gsteps) else 0.0
say("envelope BAND=%.2f (own max greedy stride; greedy med=%.2f n>40=%d)" % (BAND, float(np.median(gsteps)) if len(gsteps) else -1, int((gsteps>40).sum()) if len(gsteps) else -1))
curS = int(cseq[-1])
dS = np.sqrt(((T - T[curS])**2).sum(-1)); iS = np.argsort(dS, kind="stable")[:34]
dups = int((dS[iS] < 1.0).sum()) - 1
say("strand key-space K34: neighbours<1mm (twin-stale)=%d/33" % dups)
sset0 = set(cseq); left = [i for i in range(W) if i not in sset0]
say("leftover beyond strand: %d/%d" % (len(left), W))
if left:
    Dc = np.sqrt(((T - T[curS])**2).sum(-1)); dl = Dc[left]
    say("  leftover dist-from-strand-end: min=%.1f med=%.1f max=%.1f n<=BAND=%.1f%%" % (float(dl.min()), float(np.median(dl)), float(dl.max()), float((dl<=BAND).mean()*100)))
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
        HALT = "HALT: nearest road-retreat %.2f exceeds envelope %.2f -- walk ends" % (float(dc[best]), BAND); say(HALT); break
    ddx = np.sqrt(((T - T[cur]) ** 2).sum(-1))
    mask = np.array([kk[i] in cvm for i in range(W)])
    if mask.all(): break
    ddx[mask] = np.inf; nx = int(np.argmin(ddx))
    forwards.append((len(seq)-1, len(seq), float(np.sqrt(((T[nx]-T[cur])**2).sum()))))
    seq.append(nx); cvm[kk[nx]] = len(seq)-1; cur = nx
seq = np.array(seq, dtype=int)
L = T[seq]
bst = np.sqrt(((L[1:]-L[:-1])**2).sum(-1))
say("DEN M-walk: seqlen=%d unique=%d/%d retreats=%d forwards=%d guard=%d %s" % (len(seq), len(set(seq.tolist())), W, len(retreats), len(forwards), guard, HALT))
for i,(a,b,c) in enumerate(retreats):
    say("  retreat #%d at (%d->%d) len=%.2f" % (i, a, b, c))
for a,b,c in forwards:
    say("  FORWARD at (%d->%d) len=%.2f" % (a, b, c))
np.save(os.path.join(H, "p173_seq.npy"), seq)
np.save(os.path.join(H, "p173_seq_greedy.npy"), np.array(cseq, dtype=int))
D = np.sqrt(((L[:,None,:]-Og[None,:,:])**2).sum(-1)).min(1)
DO = np.sqrt(((Og[:,None,:]-L[None,:,:])**2).sum(-1)).min(1)
cov = int((DO<2).sum()); unc = int((DO>5).sum())
ui = sorted(np.where(DO>5)[0].tolist()); spans = []
if ui:
    a=ui[0]; p=ui[0]
    for q in ui[1:]:
        if q==p+1: p=q
        else: spans.append((a,p)); a=q; p=q
    spans.append((a,p))
med = float(np.median(D))
say("DEN gate: seqlen=%d med=%.4f <2mm=%.1f%% gaps5=%d maxstep=%.1f ORIGcov %d/211 uncovered(DO>5)=%d spans=%s" % (len(seq), med, float((D<2).mean()*100), int((bst>5).sum()), float(bst.max()), cov, unc, spans))
ui2 = sorted(np.where(DO>=2)[0].tolist()); runs = []
if ui2:
    a=ui2[0]; p=ui2[0]
    for q in ui2[1:]:
        if q==p+1: p=q
        else: runs.append((a,p)); a=q; p=q
    runs.append((a,p))
say("uncovered(DO>=2) runs=%s" % (runs,))
over25 = sorted([float(x) for x in bst if x > 25])
say("steps>25mm: n=%d %s" % (len(over25), [round(x,2) for x in over25]))
say("big>=40: n=%d" % int((bst>=40).sum()))
LgF = Lg
DOG = np.sqrt(((Og[:,None,:]-LgF[None,:,:])**2).sum(-1)).min(1)
say("payoff: den-greedy ORIGcov=%d/211 -> den-M ORIGcov=%d/211 (sign %s)" % (int((DOG<2).sum()), cov, "+/-" if cov-int((DOG<2).sum())!=0 else "0"))
C0 = Og.mean(0); Uu, Ss, Vt = np.linalg.svd(Og-C0, full_matrices=False); e1, e2, nn = Vt[0], Vt[1], Vt[2]
A3 = Og[:-1]; AB = Og[1:]-Og[:-1]; Ll = np.linalg.norm(AB,axis=1); Ll[Ll==0]=1; ttv = AB/Ll[:,None]
def topo(Bag, sq):
    Lw = Bag[np.array(sq)]
    w = Lw[:,None,:]-A3[None,:,:]; s = (w*ttv[None,:,:]).sum(-1).clip(0,1)
    proj = A3[None,:,:]+s[:,:,None]*ttv[None,:,:]; r = Lw[:,None,:]-proj
    dd = np.linalg.norm(r,axis=2); j = np.argmin(dd,axis=1)
    rr = r[np.arange(len(Lw)),j]; tj = ttv[j]
    sgn = np.sign(np.cross(tj,rr).dot(nn)); mag = dd[np.arange(len(Lw)),j]
    q = [x for x,m in zip(sgn,np.abs(mag)>=1.0) if m]
    fl = sum(1 for a,b in zip(q,q[1:]) if a != b)
    P2 = np.c_[ (Lw-C0).dot(e1),(Lw-C0).dot(e2)]
    S = [(P2[i],P2[i+1]) for i in range(len(P2)-1)]; nc = 0
    def c2(a,b): return a[0]*b[1]-a[1]*b[0]
    for i in range(len(S)):
        for k in range(i+2,len(S)):
            a,b = S[i]; c,dd2 = S[k]; rv = b-a; sv = dd2-c; den = c2(rv,sv)
            if abs(den) < 1e-12: continue
            t1 = c2(c-a,sv)/den; u1 = c2(c-a,rv)/den
            if 0 < t1 < 1 and 0 < u1 < 1: nc += 1
    dseg = P2[1:]-P2[:-1]; ang = np.arccos(np.clip((dseg[:-1]*dseg[1:]).sum(-1)/np.maximum(np.linalg.norm(dseg[:-1],axis=1)*np.linalg.norm(dseg[1:],axis=1),1e-12),-1,1))*180/np.pi
    return len(q), fl, nc, int((ang>90).sum())
cg, flg, ng, t90g = topo(T, np.array(cseq, dtype=int)); say("TOPO den-greedy: cls=%d flips=%d selfint=%d turns90=%d" % (cg, flg, ng, t90g))
cm, flm, nm, t90m = topo(T, seq); say("TOPO den-M: cls=%d flips=%d selfint=%d turns90=%d" % (cm, flm, nm, t90m))
log.close(); print("saved")