
import os, numpy as np
from scipy.spatial import cKDTree
IN='C:/PR/worktrees/sfs/328-juglet-wall-side-cure/artifacts/pota328/in'
CUR='C:/PR/worktrees/sfs/328-juglet-wall-side-cure/artifacts/pota328/jobA/outgt_jug/geom'
def load_pcd(p):
    L=open(p).read().splitlines()
    i=[n for n,l in enumerate(L) if l.startswith('DATA')][0]
    rows=[l.split() for l in L[i+1:] if l.strip() and len(l.split())>=6]
    return np.array([[float(x) for x in r[:6]] for r in rows])
T={k:np.loadtxt(f'{IN}/gt/Juglet_Piece_{k}_T.txt') for k in range(1,10)}
Bl={k:load_pcd(f'{CUR}/Juglet_Piece_{k}.Bl0') for k in range(1,10)}
def move(Bx,M):
    return np.hstack([(M@np.hstack([Bx[:,:3],np.ones((len(Bx),1))]).T).T,(M[:3,:3]@Bx[:,3:6].T).T])
for (y,x) in [(6,7),(1,9),(1,4),(1,8),(2,9),(3,5),(7,9),(1,2),(2,5)]:
    A=Bl[y]; M=np.linalg.inv(T[y])@T[x]; B=move(Bl[x],M)
    d=np.linalg.norm(A[None,:,:3]-B[:,None,:3],axis=2)
    best=[]
    for i in range(len(B)):
        j=np.argmin(d[i])
        if d[i,j]<3:
            dots=A[:,3:6]@B[i,3:6]
            # best-dot partner among A points within 3mm
            cand=np.where(d[i]<3)[0]
            best.append((d[i,j],A[j,:3],B[i,:3],dots[j],dots[cand].max()))
    best=np.array([(b[0],b[3],b[4]) for b in best])
    print("%d-%d n=%d nearest-dot med=%+.3f best-dot med=%+.3f  (nearest neg %d)"%(y,x,len(best),np.median(best[:,1]),np.median(best[:,2]),(best[:,1]<0).sum()))
