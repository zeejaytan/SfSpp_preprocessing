# 175 step7: (a) first-lap extraction of plain spread2 walk; (b) anchored hysteresis (bin-median + deadband).
import numpy as np
from scipy.spatial import cKDTree
H = "C:/PR/SfSpp_preprocessing/.scratch/pota175_repro"
log = open(H + "/p175_step7.txt", "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
d = np.load("C:/PR/SfSpp_preprocessing/.scratch/pota173_repro/p173_bag.npz", allow_pickle=True)
BAG, G0 = d["BAG"], d["G0"]
N = len(G0)
TRUE = np.load(H + "/p175_mask_true.npy")
T = BAG[TRUE]
C0 = G0.mean(0); Uu, Ss, Vt = np.linalg.svd(G0-C0, full_matrices=False); e1, e2, nn = Vt[0], Vt[1], Vt[2]
A3 = G0[:-1]; AB = G0[1:]-G0[:-1]; Ll = np.linalg.norm(AB,axis=1); Ll[Ll==0]=1; ttv = AB/Ll[:,None]
def gate_topo(L, tag):
    D = np.sqrt(((L[:,None,:]-G0[None,:,:])**2).sum(-1)).min(1)
    DO = np.sqrt(((G0[:,None,:]-L[None,:,:])**2).sum(-1)).min(1)
    st = np.sqrt(((L[1:]-L[:-1])**2).sum(-1))
    Lw = L
    w = Lw[:,None,:]-A3[None,:,:]; s = (w*ttv[None,:,:]).sum(-1).clip(0,1)
    proj = A3[None,:,:]+s[:,:,None]*ttv[None,:,:]; r2 = Lw[:,None,:]-proj
    dd2 = np.linalg.norm(r2,axis=2); j = np.argmin(dd2,axis=1)
    rr2 = r2[np.arange(len(Lw)),j]; tj = ttv[j]
    sgn = np.sign(np.cross(tj,rr2).dot(nn)); mag = dd2[np.arange(len(Lw)),j]
    q = [x for x,m in zip(sgn,np.abs(mag)>=1.0) if m]
    fl = sum(1 for a,b in zip(q,q[1:]) if a != b)
    P2 = np.c_[ (Lw-C0).dot(e1),(Lw-C0).dot(e2)]
    S = [(P2[i],P2[i+1]) for i in range(len(P2)-1)]; nc = 0
    def c2(a,b): return a[0]*b[1]-a[1]*b[0]
    for i in range(len(S)):
        for k in range(i+2,len(S)):
            a, b = S[i]; c, dd3 = S[k]; rv = b-a; sv = dd3-c; den = c2(rv,sv)
            if abs(den) < 1e-12: continue
            t1 = c2(c-a,sv)/den; u1 = c2(c-a,rv)/den
            if 0 < t1 < 1 and 0 < u1 < 1: nc += 1
    dseg = P2[1:]-P2[:-1]; ang = np.arccos(np.clip((dseg[:-1]*dseg[1:]).sum(-1)/np.maximum(np.linalg.norm(dseg[:-1],axis=1)*np.linalg.norm(dseg[1:],axis=1),1e-12),-1,1))*180/np.pi
    say("%s: seqlen=%d ORIGcov=%d/211 med=%.4f <2mm=%.1f%% gaps5=%d maxstep=%.1f steps>25=%d flips=%d selfint=%d turns90=%d" % (
        tag, len(L), int((DO<2).sum()), float(np.median(D)), float((D<2).mean()*100), int((st>5).sum()), float(st.max()), int((st>25).sum()), fl, nc, int((ang>90).sum())))
    return int((DO<2).sum()), fl, nc
# (a) first lap of plain spread2 walk: closure = first return within 6.58 (its BAND) of seed dot, min 100 steps
seq = np.load(H + "/p175_seed_spread2.npy")
Lfull = T[np.array(seq, dtype=int)]
dseed = np.sqrt(((Lfull - Lfull[0])**2).sum(-1))
cand = np.where(dseed < 6.58)[0]
cand = cand[cand >= 100]
lap_end = int(cand[0]) if len(cand) else len(Lfull)
say("spread2 plain: closure idx=%d/%d" % (lap_end, len(Lfull)))
gate_topo(Lfull[:lap_end], "spread2-first-lap")
np.save(H + "/p175_firstlap.npy", np.array(seq[:lap_end], dtype=int))
# (b) anchored hysteresis: bin-median reference (bag-frame angle, 72 bins), deadband 0.75
cenB = BAG.mean(0)
Ub,Sb,Vtb = np.linalg.svd(BAG-cenB, full_matrices=False); nB = Vtb[2]
v = T-cenB; ax = v.dot(nB)
rr = np.sqrt(np.maximum((v**2).sum(-1)-ax**2,0))
ang = np.arctan2(v.dot(Vtb[1]), v.dot(Vtb[0]))
nb = 72
bins = (np.floor((ang+np.pi)/(2*np.pi)*nb)).astype(int).clip(0,nb-1)
binmed = np.full(nb, np.median(rr))
for b in range(nb):
    if (bins==b).sum() >= 3: binmed[b] = np.median(rr[bins==b])
def bside(i):
    d = rr[i]-binmed[bins[i]]
    return 1 if d > 0.75 else (-1 if d < -0.75 else 0)
BS = np.array([bside(i) for i in range(len(T))])
say("anchored sides: +1=%d -1=%d center=%d" % (int((BS==1).sum()), int((BS==-1).sum()), int((BS==0).sum())))
def walk_anch(Tc, RR, BB, seed, tag):
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
        s0 = BB[cur]
        if s0 == 0:
            nxt = int(unv[0])
        else:
            same = [j for j in unv if BB[j] == s0 or BB[j] == 0]
            far = [j for j in unv if BB[j] == -s0 and float(dd[j]) >= 1.0]
            nxt = int(same[0]) if same else (int(far[0]) if far else int(unv[0]))
        cseq.append(nxt); cvis[kk[nxt]] = len(cseq)-1; cur = nxt
    Lg = Tc[np.array(cseq)]
    gsteps = np.sqrt(((Lg[1:]-Lg[:-1])**2).sum(-1))
    BAND = float(gsteps.max()) if len(gsteps) else 0.0
    seq = list(cseq); cvm = dict(cvis); cur = seq[-1]
    retreats = 0; guard = 0; HALT = ""
    while len(set(seq)) < W and guard < 60000:
        guard += 1
        dd = np.sqrt(((Tc - Tc[cur]) ** 2).sum(-1))
        idx = np.argsort(dd, kind="stable")[:34]
        sset = set(seq)
        cand = [int(j) for j in idx if int(j) not in sset and float(dd[int(j)]) >= 1.0]
        s0 = BB[cur]
        if s0 == 0: nxt = cand[0] if cand else None
        else:
            same = [j for j in cand if BB[j] == s0 or BB[j] == 0]
            nxt = same[0] if same else (cand[0] if cand else None)
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
    seq = np.array(seq, dtype=int)
    L = Tc[seq]
    cov, fl, nc = gate_topo(L, tag + (" "+HALT if HALT else ""))
    return seq, cov, fl, nc
Tc_full = BAG[TRUE]
KT = cKDTree(T)
for nm, r_ in [("row0",0),("medoid",54),("spread1",495),("spread2",394),("spread3",70)]:
    dd, ii = KT.query(Tc_full[r_])
    sseq, cov, fl, nc = walk_anch(T, rr, BS, int(ii), "anch-"+nm)
    np.save(H + "/p175_anch_%s.npy" % nm, sseq)
say("STEP7 DONE")
log.close(); print("step7 done")
