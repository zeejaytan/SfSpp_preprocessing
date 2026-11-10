
import os, numpy as np
from scipy.spatial import cKDTree
IN='C:/PR/worktrees/sfs/328-juglet-wall-side-cure/artifacts/pota328/in'
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
CUR='C:/PR/worktrees/sfs/328-juglet-wall-side-cure/artifacts/pota328/jobA/outgt_jug/geom'
S={k:load_ply(f'{CUR}/Juglet_Piece_{k}.S0') for k in range(1,10)}   # cured: S0 = interior on all nine
def move(X,M):
    xyz=(M[:3,:3]@X[:,:3].T).T+M[:3,3]
    n=(M[:3,:3]@X[:,3:6].T).T
    return np.hstack([xyz,n])
for (y,x) in [(1,2),(1,4),(1,8),(1,9),(2,5),(2,9),(3,5),(6,7),(7,9)]:
    A=S[y]; M=np.linalg.inv(T[y])@T[x]; B=move(S[x],M)
    tA=cKDTree(A[:,:3]); tB=cKDTree(B[:,:3])
    d,idx=tB.query(A[:,:3])       # A point -> nearest B
    m=d<2.0
    dots=np.sum(A[m,3:6]*B[idx[m],3:6],axis=1)
    ang=np.degrees(np.arccos(np.clip(np.abs(dots),-1,1)))
    print("%d-%d pts=%5d med_dot=%+.3f frac>0.7=%.2f med_angle=%.1f"%(y,x,m.sum(),np.median(dots),(dots>0.7).mean(),np.median(ang)))
