
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
    xyz=(M[:3,:3]@Bx[:,:3].T).T + M[:3,3]
    n=(M[:3,:3]@Bx[:,3:6].T).T
    return np.hstack([xyz,n])
def mutual(A,B):
    tA=cKDTree(A[:,:3]); tB=cKDTree(B[:,:3])
    _,ia=tA.query(B[:,:3]); _,ib=tB.query(A[ia,:3])
    keep=ib==np.arange(len(B))
    return ia[keep], keep
for (y,x) in [(1,2),(1,4),(1,8),(1,9),(2,5),(2,9),(3,5),(6,7),(7,9)]:
    A=Bl[y]; M=np.linalg.inv(T[y])@T[x]; B=move(Bl[x],M)
    ia,keep=mutual(A,B); bi=np.where(keep)[0]
    d=np.linalg.norm(A[ia,:3]-B[bi,:3],axis=1); m=d<3
    dots=np.sum(A[ia[m],3:6]*B[bi[m],3:6],axis=1)
    print("%d-%d n=%d med=%+.3f neg=%d min=%+.3f max=%+.3f gap=%.3f"%(y,x,m.sum(),np.median(dots),(dots<0).sum(),dots.min(),dots.max(),d.min()))
