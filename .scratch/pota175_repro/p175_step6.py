# 175 step6: debris veto (ORIG-free) + side-hysteresis walk (ORIG-free) + gate.
# Debris rule: drop dots with bag-frame radius < 45 (loop rides 51-64). Ruler verifies, never drives.
# Hysteresis rule: side(x) = sign(r(x) - median(r(last 16 sequenced))); K-stepper prefers
# same-side candidates, falls back to any (track switch where a sub-track ends). Retreat/forward verbatim.
import numpy as np
H = "C:/PR/SfSpp_preprocessing/.scratch/pota175_repro"
log = open(H + "/p175_step6.txt", "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
d = np.load("C:/PR/SfSpp_preprocessing/.scratch/pota173_repro/p173_bag.npz", allow_pickle=True)
BAG, G0 = d["BAG"], d["G0"]
N = len(G0)
TRUE = np.load(H + "/p175_mask_true.npy")
z = np.load(H + "/p175_probe0.npz")
rB, dmin = z["rB"], z["dmin"]
for nm, m in [("TRUE",TRUE),("OUTER",~TRUE)]:
    dd = dmin[m]
    say("%s debris census (rB<45): n=%d dmin: min=%.1f med=%.1f -- %s" % (
        nm, int((rB[m]<45).sum()), float(dd[rB[m]<45].min()) if (rB[m]<45).sum() else -1,
        float(np.median(dd[rB[m]<45])) if (rB[m]<45).sum() else -1,
        "ALL FAR (drop safe)" if (rB[m]<45).sum() and (dd[rB[m]<45]>5).all() else ("none" if not (rB[m]<45).sum() else "MIXED -- DO NOT DROP")))
KEEP = (rB >= 45)
say("debris veto keeps %d/%d" % (int(KEEP.sum()), len(BAG)))
T = BAG[TRUE & KEEP]; O = BAG[(~TRUE) & KEEP]
say("curated clouds: TRUE=%d OUTER=%d" % (len(T), len(O)))
def walk_hyst(Tc, seed, tag):
    W = len(Tc)
    r = np.sqrt(np.maximum(((Tc-Tc.mean(0))**2).sum(-1),0))  # placeholder, replaced below
    # bag-frame radius w.r.t. FULL-bag frame (fixed reference)
    cenB = BAG.mean(0)
    Ub,Sb,Vtb = np.linalg.svd(BAG-cenB, full_matrices=False); nB = Vtb[2]
    v = Tc-cenB; ax = v.dot(nB)
    rr = np.sqrt(np.maximum((v**2).sum(-1)-ax**2,0))
    X32 = Tc.astype(np.float32); kk = np.array([X32[i].tobytes() for i in range(W)])
    cvis = {kk[seed]: 0}; cseq = [seed]; cur = seed
    def side_of(x, ref):
        return 1 if rr[x] >= ref else -1
    def ref_now():
        return float(np.median(rr[np.array(cseq[-16:], dtype=int)]))
    first = True
    for t in range(1, W):
        dd = np.sqrt(((Tc - Tc[cur]) ** 2).sum(-1))
        idx = np.argsort(dd, kind="stable")[:34]
        if first:
            unv0 = [int(j) for j in idx if kk[int(j)] not in cvis]
            if not unv0: break
            nxt = int(unv0[0]); cseq.append(nxt); cvis[kk[nxt]] = 1; cur = nxt; first = False; continue
        ref = ref_now(); s0 = side_of(cur, ref)
        unv = [int(j) for j in idx if kk[int(j)] not in cvis]
        if not unv: break
        same = [j for j in unv if side_of(j, ref) == s0 and float(dd[j]) >= 0]
        nxt = int(same[0]) if same else int(unv[0])
        cseq.append(nxt); cvis[kk[nxt]] = len(cseq)-1; cur = nxt
    Lg = Tc[np.array(cseq)]
    gsteps = np.sqrt(((Lg[1:]-Lg[:-1])**2).sum(-1))
    BAND = float(gsteps.max()) if len(gsteps) else 0.0
    seq = list(cseq); cvm = dict(cvis); cur = seq[-1]
    retreats = 0; forwards = 0; guard = 0; HALT = ""
    while len(set(seq)) < W and guard < 60000:
        guard += 1
        dd = np.sqrt(((Tc - Tc[cur]) ** 2).sum(-1))
        idx = np.argsort(dd, kind="stable")[:34]
        sset = set(seq)
        ref = float(np.median(rr[np.array(seq[-16:], dtype=int)])); s0 = side_of(cur, ref)
        cand = [int(j) for j in idx if int(j) not in sset and float(dd[int(j)]) >= 1.0]
        same = [j for j in cand if side_of(j, ref) == s0]
        if same: nxt = same[0]
        elif cand: nxt = cand[0]
        else: nxt = None
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
        forwards += 1; seq.append(nx); cvm[kk[nx]] = len(seq)-1; cur = nx
    seq = np.array(seq, dtype=int)
    L = Tc[seq]
    D = np.sqrt(((L[:,None,:]-G0[None,:,:])**2).sum(-1)).min(1)
    DO = np.sqrt(((G0[:,None,:]-L[None,:,:])**2).sum(-1)).min(1)
    st = np.sqrt(((L[1:]-L[:-1])**2).sum(-1))
    C0 = G0.mean(0); Uu2, Ss2, Vt2 = np.linalg.svd(G0-C0, full_matrices=False); e1, e2, nn = Vt2[0], Vt2[1], Vt2[2]
    A3 = G0[:-1]; AB = G0[1:]-G0[:-1]; Ll = np.linalg.norm(AB,axis=1); Ll[Ll==0]=1; ttv = AB/Ll[:,None]
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
    t90 = int((ang>90).sum())
    uniq = len(set(seq.tolist()))
    say("%s seed=%d: seqlen=%d unique=%d/%d ORIGcov=%d/211 med=%.4f <2mm=%.1f%% gaps5=%d maxstep=%.1f steps>25=%d flips=%d selfint=%d turns90=%d retreats=%d forwards=%d %s" % (
        tag, seed, len(seq), uniq, W, int((DO<2).sum()), float(np.median(D)), float((D<2).mean()*100), int((st>5).sum()), float(st.max()), int((st>25).sum()), fl, nc, t90, retreats, forwards, HALT))
    return seq
# seed set: same 6 as probe2 (row remapped to curated index space via coordinate match)
Tc_full = BAG[TRUE]
seeds_rows = {"row0": 0, "medoid": 54, "spread0": 0, "spread1": 495, "spread2": 394, "spread3": 70}
Kfull = cKDTree_T = None
from scipy.spatial import cKDTree
K = cKDTree(Tc_full)
for nm, r_ in seeds_rows.items():
    if r_ >= len(Tc_full): continue
    dd, ii = cKDTree(T).query(Tc_full[r_])
    sseq = walk_hyst(T, int(ii), "TRUE-"+nm)
    np.save(H + "/p175_hyst_TRUE_%s.npy" % nm, sseq)
# OUTER cloud: row0 in its own space
sseqO = walk_hyst(O, 0, "OUTER-row0")
np.save(H + "/p175_hyst_OUTER_row0.npy", sseqO)
say("STEP6 DONE")
log.close(); print("step6 done")
