import json, os, numpy as np
from scipy.spatial import cKDTree
B='C:/PR/worktrees/sfs/328-juglet-wall-side-cure'
GEOM=os.path.join(B,'artifacts/pota328/in/geom'); GT=os.path.join(B,'artifacts/pota328/in/gt')
def load_ply6(p):
    L=open(p).read().splitlines(); i=[n for n,l in enumerate(L) if l.strip()=='end_header'][0]
    d=[l.split() for l in L[i+1:] if l.strip() and not l.startswith('camera')]
    return np.array([[float(x) for x in r[:6]] for r in d])
def load_ax(p):
    v=[float(x) for x in open(p).read().split()]; return np.array(v[-6:-3]),np.array(v[-3:])
def unit(a): return a/np.maximum(np.linalg.norm(a,axis=1,keepdims=True),1e-12)
def curv(P,N,k=40,seed=5,sample=600):
    tree=cKDTree(P); rng=np.random.default_rng(seed)
    idx=rng.choice(len(P),min(sample,len(P)),replace=False); N=unit(N); out=[]
    for i in idx:
        d,nb=tree.query(P[i],k=min(k+1,len(P))); nb=nb[1:]
        Q=P[nb]-P[i]; n=N[i]
        a=np.array([1.0,0,0]) if abs(n[0])<0.9 else np.array([0,1.0,0])
        t1=np.cross(n,a); t1/=np.linalg.norm(t1); t2=np.cross(n,t1)
        u=Q@t1; v=Q@t2; w=Q@n
        A=np.stack([0.5*u*u,u*v,0.5*v*v,u,v],axis=1)
        sol,*_=np.linalg.lstsq(A,w,rcond=None)
        S=np.array([[sol[0],sol[1]],[sol[1],sol[2]]]); ev=np.linalg.eigvalsh(S)
        out.append(max(abs(ev[0]),abs(ev[1])))
    return float(np.median(out)), float(np.percentile(out,25)), float(np.percentile(out,75))
for k in (80,150):
    print('=== k =',k)
    for p in range(1,10):
        A={f:load_ply6(os.path.join(GEOM,'Juglet_Piece_%d.S%d'%(p,f))) for f in (0,1)}
        g0,gd=load_ax(os.path.join(GT,'Juglet_Piece_%d_Axis.xyz'%p)); gd=gd/np.linalg.norm(gd)
        r={}
        for f in (0,1):
            w=A[f][:,:3]-g0; r[f]=float(np.median(np.linalg.norm(w-np.outer(w@gd,gd),axis=1)))
        ti=0 if r[0]<r[1] else 1
        c=[curv(A[f][:,:3],A[f][:,3:6],k=k) for f in (0,1)]
        pick=0 if c[0][0]>c[1][0] else 1
        print('piece %d true %d | S0 %.4f S1 %.4f | ratio %.2f | 1/R %.4f %.4f | pick %d %s'%(
            p,ti,c[0][0],c[1][0],max(c[0][0],c[1][0])/max(min(c[0][0],c[1][0]),1e-9),1/r[0],1/r[1],pick,'OK' if pick==ti else 'FAIL'))
