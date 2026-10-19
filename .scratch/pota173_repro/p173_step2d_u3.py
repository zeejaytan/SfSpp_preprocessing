import numpy as np
from scipy.spatial import cKDTree
H = ".scratch/pota173_repro"
d = np.load(H + "/p173_bag.npz", allow_pickle=True)
BAG, G0 = d["BAG"], d["G0"]
s1 = np.load(H + "/p173_seq.npy"); s2 = np.load(H + "/p173_seq2.npy"); s3 = np.load(H + "/p173_seq3.npy")
L1, L2, L3 = BAG[s1], BAG[s2], BAG[s3]
DOu = np.minimum.reduce([cKDTree(L1).query(G0)[0], cKDTree(L2).query(G0)[0], cKDTree(L3).query(G0)[0]])
Du = np.sqrt(((np.vstack([L1,L2,L3])[:,None,:]-G0[None,:,:])**2).sum(-1)).min(1)
print("UNION3: ORIGcov=%d/211 med=%.4f <2mm=%.1f%%" % (int((DOu<2).sum()), float(np.median(Du)), float((Du<2).mean()*100)))
C0 = G0.mean(0); Uu, Ss, Vt = np.linalg.svd(G0-C0, full_matrices=False); e1, e2, nn = Vt[0], Vt[1], Vt[2]
A3 = G0[:-1]; AB = G0[1:]-G0[:-1]; Ll = np.linalg.norm(AB,axis=1); Ll[Ll==0]=1; ttv = AB/Ll[:,None]
def topo(sq):
    Lw = BAG[np.array(sq, dtype=int)]
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
print("TOPO s3: cls=%d flips=%d selfint=%d turns90=%d" % topo(s3))
st = np.sqrt(((L3[1:]-L3[:-1])**2).sum(-1))
print("s3: seqlen=%d maxstep=%.1f gaps5=%d" % (len(L3), float(st.max()), int((st>5).sum())))
