
import numpy as np
from scipy.spatial import cKDTree
IN='C:/PR/worktrees/sfs/328-juglet-wall-side-cure/artifacts/pota328/in'
CUR='C:/PR/worktrees/sfs/328-juglet-wall-side-cure/artifacts/pota328/jobA/outgt_jug/geom'
def load_ply(p):
    rows=[];hdr=True;n=0
    for ln in open(p):
        if hdr:
            t=ln.split()
            if t and t[0]=='element' and t[1]=='vertex': n=int(t[2])
            if t and t[0]=='end_header': hdr=False
            continue
        if len(rows)<n: rows.append([float(x) for x in ln.split()[:6]])
    return np.array(rows)
def load_pcd(p):
    L=open(p).read().splitlines()
    i=[n for n,l in enumerate(L) if l.startswith('DATA')][0]
    rows=[l.split() for l in L[i+1:] if l.strip() and len(l.split())>=6]
    return np.array([[float(x) for x in r[:6]] for r in rows])
T={k:np.loadtxt(f'{IN}/gt/Juglet_Piece_{k}_T.txt') for k in range(1,10)}
S={k:load_ply(f'{CUR}/Juglet_Piece_{k}.S0') for k in range(1,10)}
Bl={k:load_pcd(f'{CUR}/Juglet_Piece_{k}.Bl0') for k in range(1,10)}
def move(X,M):
    return np.hstack([(M[:3,:3]@X[:,:3].T).T+M[:3,3], (M[:3,:3]@X[:,3:6].T).T])
for (y,x) in [(6,7),(1,9),(1,4)]:
    A=Bl[y]; M=np.linalg.inv(T[y])@T[x]; B=move(Bl[x],M)
    tA=cKDTree(A[:,:3]); tB=cKDTree(B[:,:3])
    _,ia=tA.query(B[:,:3]); _,ib=tB.query(A[ia,:3]); keep=ib==np.arange(len(B))
    print("=== pair",y,x)
    for i in np.where(keep)[0]:
        j=ia[i]; d=np.linalg.norm(A[j,:3]-B[i,:3])
        if d<3:
            print("  d=%.2f dA=%+.2f dB=%+.2f  nA=(%+.2f %+.2f %+.2f) nB=(%+.2f %+.2f %+.2f)"%(d,0,0,*A[j,3:6],*B[i,3:6]))
