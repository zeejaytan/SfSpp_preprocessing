# 175 step12: walk parent-surface clouds (M144 verbatim, 6-seed protocol) + gate + topo.
import numpy as np
from scipy.spatial import cKDTree
H = "C:/PR/SfSpp_preprocessing/.scratch/.wt-dchain-port/.scratch/pota175_repro"
P = "C:/PR/SfSpp_preprocessing/.scratch/.wt-dchain-port"
log = open(H + "/p175_step12.txt", "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
d = np.load(P + "/.scratch/pota173_repro/p173_bag.npz", allow_pickle=True)
BAG, G0 = d["BAG"], d["G0"]
N = len(G0)
plab = np.load(H+"/p175_parentface.npy")
CTRUE = (plab==-1)|(plab==0); COUT = (plab==1)
say("parent clouds: TRUE(inner+fold)=%d OUTER=%d" % (int(CTRUE.sum()), int(COUT.sum())))
def walk(Tc, seed):
    W = len(Tc)
    X32 = Tc.astype(np.float32); kk = np.array([X32[i].tobytes() for i in range(W)])
    cvis = {kk[seed]: 0}; cseq = [seed]; cur = seed
    first = True
    for t in range(1, W):
        dd = np.sqrt(((Tc - Tc[cur]) ** 2).sum(-1))
        idx = np.argsort(dd, kind="stable")[:34]
        if first:
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
    retreats = 0; guard = 0; HALT = ""
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
        seq.append(nx); cvm[kk[nx]] = len(seq)-1; cur = nx
    return np.array(seq, dtype=int), BAND, HALT, retreats
C0 = G0.mean(0); Uu, Ss, Vt = np.linalg.svd(G0-C0, full_matrices=False); e1, e2, nn = Vt[0], Vt[1], Vt[2]
A3 = G0[:-1]; AB = G0[1:]-G0[:-1]; Ll = np.linalg.norm(AB,axis=1); Ll[Ll==0]=1; ttv = AB/Ll[:,None]
def gate_topo(L, tag):
    D = np.sqrt(((L[:,None,:]-G0[None,:,:])**2).sum(-1)).min(1)
    DO = np.sqrt(((G0[:,None,:]-L[None,:,:])**2).sum(-1)).min(1)
    st = np.sqrt(((L[1:]-L[:-1])**2).sum(-1)) if len(L) > 1 else np.array([0.0])
    w = L[:,None,:]-A3[None,:,:]; s = (w*ttv[None,:,:]).sum(-1).clip(0,1)
    proj = A3[None,:,:]+s[:,:,None]*ttv[None,:,:]; r2 = L[:,None,:]-proj
    dd2 = np.linalg.norm(r2,axis=2); j = np.argmin(dd2,axis=1)
    rr2 = r2[np.arange(len(L)),j]; tj = ttv[j]
    sgn = np.sign(np.cross(tj,rr2).dot(nn)); mag = dd2[np.arange(len(L)),j]
    q = [x for x,m in zip(sgn,np.abs(mag)>=1.0) if m]
    fl = sum(1 for a,b in zip(q,q[1:]) if a != b)
    P2 = np.c_[ (L-C0).dot(e1),(L-C0).dot(e2)]
    S = [(P2[i],P2[i+1]) for i in range(len(P2)-1)]; nc = 0
    def c2(a,b): return a[0]*b[1]-a[1]*b[0]
    for i in range(len(S)):
        for k in range(i+2,len(S)):
            a, b = S[i]; c, dd3 = S[k]; rv = b-a; sv = dd3-c; den = c2(rv,sv)
            if abs(den) < 1e-12: continue
            t1 = c2(c-a,sv)/den; u1 = c2(c-a,rv)/den
            if 0 < t1 < 1 and 0 < u1 < 1: nc += 1
    dseg = P2[1:]-P2[:-1]; ang = np.arccos(np.clip((dseg[:-1]*dseg[1:]).sum(-1)/np.maximum(np.linalg.norm(dseg[:-1],axis=1)*np.linalg.norm(dseg[1:],axis=1),1e-12),-1,1))*180/np.pi
    t90 = int((ang>90).sum())
    unc = int((DO>5).sum())
    say("%s: seqlen=%d ORIGcov=%d/211 med=%.4f <2mm=%.1f%% gaps5=%d maxstep=%.1f steps>25=%d uncovered=%d flips=%d selfint=%d turns90=%d" % (
      tag, len(L), int((DO<2).sum()), float(np.median(D)), float((D<2).mean()*100), int((st>5).sum()), float(st.max()), int((st>25).sum()), unc, fl, nc, t90))
    return int((DO<2).sum()), fl, nc
for ctag, mask in [("TRUE",CTRUE),("OUTER",COUT)]:
    Tc = BAG[mask]
    Dall = np.sqrt(((Tc[:,None,:]-Tc[None,:,:])**2).sum(-1))
    med = int(np.argmin(Dall.sum(0)))
    picked = [med]
    for k in range(4):
        dd = np.sqrt(((Tc[:,None,:]-Tc[np.array(picked)][None,:,:])**2).sum(-1)).min(1)
        picked.append(int(np.argmax(dd)))
    seeds = {"row0": 0, "medoid": med}
    for i,p_ in enumerate(picked[1:]):
        seeds["spread%d" % i] = p_
    best = None
    for nm, s_ in seeds.items():
        seq, BAND, HALT, ret = walk(Tc, int(s_))
        L = Tc[seq]
        cov, fl, nc = gate_topo(L, "%s-%s BAND=%.2f ret=%d %s" % (ctag, nm, BAND, ret, HALT))
        np.save(H + "/p175_ps_%s_%s.npy" % (ctag, nm), seq)
        score = (cov, -fl, -nc)
        if best is None or score > best[0]:
            best = (score, nm, seq, BAND, HALT, ret)
    say("%s BEST: %s cov=%d flips=%d selfint=%d (N=6 best-of-N)" % (ctag, best[1], best[0][0], -best[0][1], -best[0][2]))
    np.save(H + "/p175_ps_%s_BEST.npy" % ctag, best[2])
say("STEP12 DONE")
log.close(); print("step12 done")
