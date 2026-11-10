
import os, numpy as np
from scipy.spatial import cKDTree
CUR='C:/PR/worktrees/sfs/328-juglet-wall-side-cure/artifacts/pota328/jobA/outgt_jug/geom'
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
S={k:load_ply(f'{CUR}/Juglet_Piece_{k}.S0') for k in range(1,10)}
Bl={k:load_pcd(f'{CUR}/Juglet_Piece_{k}.Bl0') for k in range(1,10)}
def pair(y,x):
    A=Bl[y]; Bx=Bl[x]
    M=np.linalg.inv(T[y])@T[x]
    B=np.hstack([(M@np.hstack([Bx[:,:3],np.ones((len(Bx),1))]).T).T,(M[:3,:3]@Bx[:,3:6].T).T])
    d=np.linalg.norm(A[None,:,:3]-B[:,None,:3],axis=2)
    j=np.argmin(d,axis=1); dmin=d[np.arange(len(B)),j]
    m=dmin<3.0
    dot=np.sum(A[j[m],3:6]*B[m,3:6],axis=1)
    print("%d-%d n=%d med=%+.3f neg=%d min=%+.3f max=%+.3f gap=%.3f"%(y,x,m.sum(),np.median(dot),(dot<0).sum(),dot.min(),dot.max(),dmin.min()))
for y,x in [(1,2),(1,4),(1,8),(1,9),(2,5),(2,9),(3,5),(6,7),(7,9)]:
    pair(y,x)
