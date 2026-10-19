# 173 step2: union gate + per-strand topo (verbatim 170 counters) + ownership + same-loop check.
import numpy as np
from scipy.spatial import cKDTree
H = ".scratch/pota173_repro"
log = open(H + "/p173_step2.txt", "w")
def say(s):
    print(s, flush=True); log.write(s + "\n")
d = np.load(H + "/p173_bag.npz", allow_pickle=True)
BAG, G0 = d["BAG"], d["G0"]
N = len(G0)
seq = np.load(H + "/p173_seq.npy"); seq2 = np.load(H + "/p173_seq2.npy")
L1, L2 = BAG[seq], BAG[seq2]
Lu = np.vstack([L1, L2])
D1 = np.sqrt(((L1[:,None,:]-G0[None,:,:])**2).sum(-1)).min(1)
D2 = np.sqrt(((L2[:,None,:]-G0[None,:,:])**2).sum(-1)).min(1)
DO1 = np.sqrt(((G0[:,None,:]-L1[None,:,:])**2).sum(-1)).min(1)
DO2 = np.sqrt(((G0[:,None,:]-L2[None,:,:])**2).sum(-1)).min(1)
DOu = np.minimum(DO1, DO2)
Du = np.sqrt(((Lu[:,None,:]-G0[None,:,:])**2).sum(-1)).min(1)
say("strand1-alone: ORIGcov=%d/211 med=%.4f <2mm=%.1f%%" % (int((DO1<2).sum()), float(np.median(D1)), float((D1<2).mean()*100)))
say("strand2-alone: ORIGcov=%d/211 med=%.4f <2mm=%.1f%%" % (int((DO2<2).sum()), float(np.median(D2)), float((D2<2).mean()*100)))
say("UNION: ORIGcov=%d/211 med=%.4f <2mm=%.1f%%" % (int((DOu<2).sum()), float(np.median(Du)), float((Du<2).mean()*100)))
ui = sorted(np.where(DOu>5)[0].tolist()); spans=[]
if ui:
    a=ui[0]; p=ui[0]
    for q in ui[1:]:
        if q==p+1: p=q
        else: spans.append((a,p)); a=q; p=q
    spans.append((a,p))
say("union uncovered(DO>5)=%d spans=%s" % (len(ui), spans))
ui2 = sorted(np.where(DOu>=2)[0].tolist()); runs=[]
if ui2:
    a=ui2[0]; p=ui2[0]
    for q in ui2[1:]:
        if q==p+1: p=q
        else: runs.append((a,p)); a=q; p=q
    runs.append((a,p))
say("union uncovered(DO>=2) runs=%s" % (runs,))
# per-strand steps
for tag, L in [("s1", L1), ("s2", L2)]:
    st = np.sqrt(((L[1:]-L[:-1])**2).sum(-1))
    say("%s: seqlen=%d maxstep=%.1f gaps5=%d steps>25=%d" % (tag, len(L), float(st.max()), int((st>5).sum()), int((st>25).sum())))
# topo verbatim (170 step1)
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
for tag, sq in [("s1-greedy", None), ("s1-M", seq), ("s2-M", seq2)]:
    pass
g1 = np.load(H + "/p173_seq_greedy.npy")
for tag, sq in [("s1-greedy", g1), ("s1-M", seq), ("s2-M", seq2)]:
    cg, fl, nc, t90 = topo(BAG, np.array(sq, dtype=int))
    say("TOPO %s: cls=%d flips=%d selfint=%d turns90=%d" % (tag, cg, fl, nc, t90))
# 170 reference (Comments): strand1 M 126/19/16/25, greedy 84/7/1/4
say("170-ref: strand1-greedy 84/7/1/4 | strand1-M 126/19/16/25 | union 90/211 med 4.5249 <2mm 31.0%%")
# same-loop check (147 HALF1b steer): radial-from-loop-axis at matched ORIG stations
axis = G0.mean(0)
def radial(P):
    v = P - axis
    ax = Vt[2]
    return v - np.outer(v@ax, ax)
RG0 = radial(G0)
n0 = np.linalg.norm(RG0, axis=1); n0[n0==0]=1; U0 = RG0/n0[:,None]
for tag, L in [("s1", L1), ("s2", L2)]:
    jm = cKDTree(G0).query(L)[1]
    RL = radial(L)
    nl = np.linalg.norm(RL, axis=1); nl[nl==0]=1; UL = RL/nl[:,None]
    cosang = (UL*U0[jm]).sum(-1)
    dm = np.sqrt(((L-G0[jm])**2).sum(-1))
    m = dm < 2.0
    say("%s radial: matched<2mm=%d/%d cos-med=%.3f frac(cos>0.9)=%.3f" % (tag, int(m.sum()), len(L), float(np.median(cosang[m])) if m.sum() else -1, float((cosang[m]>0.9).mean()) if m.sum() else -1))
say("GATE DONE")
log.close()
