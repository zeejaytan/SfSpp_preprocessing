# 175 step9: per-bin 2-means track labels + Viterbi orientation + hysteresis walk.
import numpy as np
from scipy.spatial import cKDTree
H = "C:/PR/SfSpp_preprocessing/.scratch/pota175_repro"
log = open(H + "/p175_step9.txt", "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
d = np.load("C:/PR/SfSpp_preprocessing/.scratch/pota173_repro/p173_bag.npz", allow_pickle=True)
BAG, G0 = d["BAG"], d["G0"]
N = len(G0)
TRUE = np.load(H + "/p175_mask_true.npy")
T = BAG[TRUE]
cenB = BAG.mean(0)
Ub,Sb,Vtb = np.linalg.svd(BAG-cenB, full_matrices=False); nB = Vtb[2]
v = T-cenB; ax = v.dot(nB)
rr = np.sqrt(np.maximum((v**2).sum(-1)-ax**2,0))
ang = np.arctan2(v.dot(Vtb[1]), v.dot(Vtb[0]))
nb = 72
bins = (np.floor((ang+np.pi)/(2*np.pi)*nb)).astype(int).clip(0,nb-1)
lab = np.zeros(len(T), dtype=int)  # per-bin 2-means label (0/1 arbitrary)
for b in range(nb):
    m = np.where(bins==b)[0]
    if len(m) < 2: continue
    x = rr[m]
    c0, c1 = x.min(), x.max()
    for _ in range(20):
        d0 = np.abs(x-c0); d1 = np.abs(x-c1)
        m0 = d0 <= d1
        if m0.sum()==0 or m0.sum()==len(m): break
        c0, c1 = x[m0].mean(), x[~m0].mean()
    lab[m[m0]] = 0; lab[m[~m0]] = 1
# orient: Viterbi-lite -- flip per-bin labels so label-0 median radius is continuous with previous bin
labO = lab.copy()
prev_med0 = None
for b in range(nb):
    m = np.where(bins==b)[0]
    if len(m) < 2: continue
    med0 = np.median(rr[m[labO[m]==0]]) if (labO[m]==0).sum() else None
    med1 = np.median(rr[m[labO[m]==1]]) if (labO[m]==1).sum() else None
    if med0 is None or med1 is None: continue
    if prev_med0 is not None and abs(med1-prev_med0) < abs(med0-prev_med0):
        labO[m] = 1-labO[m]
        med0 = med1
    prev_med0 = med0
# label-0 = inner track? check ruler composition (scoring only)
z = np.load(H + "/p175_probe0.npz")
alB = z["alB"]; dr = z["dr"]
L0 = (labO==0); L1 = (labO==1)
say("label0: n=%d ruler-inner=%d ruler-outer=%d ruler-mid=%d" % (int(L0.sum()), int((dr[TRUE]<1.0)[L0].sum()), int((dr[TRUE]>2.5)[L0].sum()), int(((np.abs(dr[TRUE])>=1.0)&(dr[TRUE]<=2.5))[L0].sum())))
say("label1: n=%d ruler-inner=%d ruler-outer=%d ruler-mid=%d" % (int(L1.sum()), int((dr[TRUE]<1.0)[L1].sum()), int((dr[TRUE]>2.5)[L1].sum()), int(((np.abs(dr[TRUE])>=1.0)&(dr[TRUE]<=2.5))[L1].sum())))
np.save(H+"/p175_labels.npy", labO)
def walk_lab(Tc, BB, seed, tag):
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
        same = [j for j in unv if BB[j] == s0]
        far = [j for j in unv if BB[j] != s0 and float(dd[j]) >= 1.0]
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
        same = [j for j in cand if BB[j] == s0]
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
    D = np.sqrt(((L[:,None,:]-G0[None,:,:])**2).sum(-1)).min(1)
    DO = np.sqrt(((G0[:,None,:]-L[None,:,:])**2).sum(-1)).min(1)
    st = np.sqrt(((L[1:]-L[:-1])**2).sum(-1))
    C0 = G0.mean(0); Uu2, Ss2, Vt2 = np.linalg.svd(G0-C0, full_matrices=False); e1, e2, nn = Vt2[0], Vt2[1], Vt2[2]
    A3 = G0[:-1]; AB = G0[1:]-G0[:-1]; Ll = np.linalg.norm(AB,axis=1); Ll[Ll==0]=1; ttv = AB/Ll[:,None]
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
    say("%s seed=%d: seqlen=%d unique=%d/%d ORIGcov=%d/211 med=%.4f <2mm=%.1f%% gaps5=%d maxstep=%.1f steps>25=%d flips=%d selfint=%d turns90=%d retreats=%d %s" % (
        tag, seed, len(seq), len(set(seq.tolist())), W, int((DO<2).sum()), float(np.median(D)), float((D<2).mean()*100), int((st>5).sum()), float(st.max()), int((st>25).sum()), fl, nc, int((ang>90).sum()), retreats, HALT))
    return seq
KT = cKDTree(T)
Tc_full = BAG[TRUE]
for nm, r_ in [("row0",0),("medoid",54),("spread1",495),("spread2",394),("spread3",70),("spread4",None)]:
    if r_ is None:
        dd, ii = KT.query(T.mean(0)); nm = "center"
    else:
        dd, ii = KT.query(Tc_full[r_])
    sseq = walk_lab(T, labO, int(ii), "lab-"+nm)
    np.save(H + "/p175_lab_%s.npy" % nm, sseq)
say("STEP9 DONE")
log.close(); print("step9 done")
