import os, numpy as np
from scipy.optimize import least_squares
B='C:/PR/worktrees/sfs/328-juglet-wall-side-cure/artifacts/pota328/in'
GEOM=os.path.join(B,'geom'); GT=os.path.join(B,'gt')
def load_ply6(p):
    L=open(p).read().splitlines(); i=[n for n,l in enumerate(L) if l.strip()=='end_header'][0]
    d=[l.split() for l in L[i+1:] if l.strip() and not l.startswith('camera')]
    return np.array([[float(x) for x in r[:6]] for r in d])
def load_ax(p):
    v=[float(x) for x in open(p).read().split()]; return np.array(v[-6:-3]),np.array(v[-3:])
def unit(a): return a/np.maximum(np.linalg.norm(a,axis=1,keepdims=True),1e-12)
def line_axis_res(P,N,c,d):
    A=P-c; A=A-np.outer(A@d,d); nt=N-np.outer(N@d,d); nn=np.sum(nt*nt,axis=1)
    ok=nn>1e-8; r=np.linalg.norm(A,axis=1); s=np.zeros(len(P))
    s[ok]=-np.sum(A[ok]*nt[ok],axis=1)/nn[ok]
    return np.linalg.norm(A+np.outer(s,np.ones(3))*nt,axis=1)
for k in (9,2,3,6):
    A={f:load_ply6(os.path.join(GEOM,'Juglet_Piece_%d.S%d'%(k,f))) for f in (0,1)}
    P=np.vstack([A[0][:,:3],A[1][:,:3]]); N=unit(np.vstack([A[0][:,3:6],A[1][:,3:6]]))
    g0,gd=load_ax(os.path.join(GT,'Juglet_Piece_%d_Axis.xyz'%k)); gd=gd/np.linalg.norm(gd)
    res=line_axis_res(P,N,g0,gd)
    print('piece',k,'n=',len(P),'res at GT axis: median %.3f p90 %.3f'%(np.median(res),np.percentile(res,90)))
