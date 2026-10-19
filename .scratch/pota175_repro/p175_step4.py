# 175 step4: gate seed-sweep winners (spread1/spread2) + topo verbatim + lap check.
import numpy as np
H = "C:/PR/SfSpp_preprocessing/.scratch/pota175_repro"
log = open(H + "/p175_step4.txt", "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
d = np.load("C:/PR/SfSpp_preprocessing/.scratch/pota173_repro/p173_bag.npz", allow_pickle=True)
BAG, G0 = d["BAG"], d["G0"]
N = len(G0)
TRUE = np.load(H + "/p175_mask_true.npy")
T = BAG[TRUE]
C0 = G0.mean(0); Uu, Ss, Vt = np.linalg.svd(G0-C0, full_matrices=False); e1, e2, nn = Vt[0], Vt[1], Vt[2]
A3 = G0[:-1]; AB = G0[1:]-G0[:-1]; Ll = np.linalg.norm(AB,axis=1); Ll[Ll==0]=1; ttv = AB/Ll[:,None]
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
            a, b = S[i]; c, dd2 = S[k]; rv = b-a; sv = dd2-c; den = c2(rv,sv)
            if abs(den) < 1e-12: continue
            t1 = c2(c-a,sv)/den; u1 = c2(c-a,rv)/den
            if 0 < t1 < 1 and 0 < u1 < 1: nc += 1
    dseg = P2[1:]-P2[:-1]; ang = np.arccos(np.clip((dseg[:-1]*dseg[1:]).sum(-1)/np.maximum(np.linalg.norm(dseg[:-1],axis=1)*np.linalg.norm(dseg[1:],axis=1),1e-12),-1,1))*180/np.pi
    return len(q), fl, nc, int((ang>90).sum())
for tag in ["spread1", "spread2", "medoid"]:
    seq = np.load(H + "/p175_seed_%s.npy" % tag)
    L = T[np.array(seq, dtype=int)]
    D = np.sqrt(((L[:,None,:]-G0[None,:,:])**2).sum(-1)).min(1)
    DO = np.sqrt(((G0[:,None,:]-L[None,:,:])**2).sum(-1)).min(1)
    cov = int((DO<2).sum()); unc = int((DO>5).sum())
    st = np.sqrt(((L[1:]-L[:-1])**2).sum(-1))
    uniq = len(set(np.array(seq, dtype=int).tolist()))
    say("%s: seqlen=%d unique=%d/%d ORIGcov=%d/211 med=%.4f <2mm=%.1f%% gaps5=%d maxstep=%.1f steps>25=%d uncovered=%d" % (
        tag, len(seq), uniq, len(T), cov, float(np.median(D)), float((D<2).mean()*100), int((st>5).sum()), float(st.max()), int((st>25).sum()), unc))
    cm, flm, nm_, t90m = topo(T, seq)
    say("TOPO %s: cls=%d flips=%d selfint=%d turns90=%d" % (tag, cm, flm, nm_, t90m))
    # lap check: path length vs author loop length
    plen = float(st.sum())
    da = np.sqrt(((np.roll(G0,-1,axis=0)-G0)**2).sum(-1)).sum()
    say("  pathlen=%.1f author-loop=%.1f laps=%.2f" % (plen, float(da), plen/float(da)))
say("GATE DONE")
log.close(); print("step4 done")
