import numpy as np, sys
from scipy.spatial import cKDTree
ROOT='C:/PR/worktrees/sfs/328-juglet-wall-side-cure/artifacts/pota328'
IN=ROOT+'/in'
GEOM=sys.argv[1] if len(sys.argv)>1 else ROOT+'/jobG/geom_gt'
def load_pcd(p):
    L=open(p).read().splitlines()
    i=[n for n,l in enumerate(L) if l.startswith('DATA')][0]
    rows=[l.split() for l in L[i+1:] if l.strip() and len(l.split())>=6]
    return np.array([[float(x) for x in r[:6]] for r in rows])
T={k:np.loadtxt(f'{IN}/gt/Juglet_Piece_{k}_T.txt') for k in range(1,10)}
Bl={k:load_pcd(f'{GEOM}/Juglet_Piece_{k}.Bl0') for k in range(1,10)}
def move(Bx,M):
    xyz=(M[:3,:3]@Bx[:,:3].T).T + M[:3,3]
    n=(M[:3,:3]@Bx[:,3:6].T).T
    return np.hstack([xyz,n])
print('pair  n1to1  n<1.5  inl(|dot|>0.9659)  max|dot|@<1.5  best-dist-at-good  maxdot_any_dist')
for (y,x) in [(1,2),(1,4),(1,8),(1,9),(2,5),(2,9),(3,5),(6,7),(7,9)]:
    A=Bl[y]; M=np.linalg.inv(T[y])@T[x]; B=move(Bl[x],M)
    tA=cKDTree(A[:,:3]); tB=cKDTree(B[:,:3])
    _,ia=tA.query(B[:,:3]); _,ib=tB.query(A[ia,:3])
    keep=ib==np.arange(len(B)); bi=np.where(keep)[0]; ai=ia[keep]
    d=np.linalg.norm(A[ai,:3]-B[bi,:3],axis=1)
    ad=np.abs(np.sum(A[ai,3:6]*B[bi,3:6],axis=1))
    m15=d<1.5
    good=m15&(ad>0.9659)
    print("%d-%d  %3d  %3d  %3d   %.4f   %s   %.4f"%(y,x,len(d),m15.sum(),good.sum(),
        (ad[m15].max() if m15.any() else float('nan')),
        ("%.3f"%d[good].min() if good.any() else "-"),
        ad.max()))
