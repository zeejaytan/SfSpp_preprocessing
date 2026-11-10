
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
def load_root(root):
    S={k:load_ply(os.path.join(root,'Juglet_Piece_%d.S0'%k)) for k in range(1,10)}
    B={k:load_pcd(os.path.join(root,'Juglet_Piece_%d.Bl0'%k)) for k in range(1,10)}
    return S,B
def pair(A,Bx,y,x):
    M=np.linalg.inv(T[y])@T[x]
    B=np.hstack([(M@np.hstack([Bx[:,:3],np.ones((len(Bx),1))]).T).T,(M[:3,:3]@Bx[:,3:6].T).T])
    tA=cKDTree(A[:,:3]); tB=cKDTree(B[:,:3])
    _,ia=tA.query(B[:,:3])          # for each B point, nearest A
    _,ib=tB.query(A[ia,:3])         # mutual check
    keep=np.abs(ib-np.arange(len(B)))<1e-9
    dots=[];ds=[]
    for i in range(len(B)):
        if not keep[i]: continue
        pA=A[ia[i]]; pB=B[i]
        dots.append(float(pA[3:6]@pB[3:6])); ds.append(float(np.linalg.norm(pA[:3]-pB[:3])))
    dots=np.array(dots); ds=np.array(ds); m=ds<3
    return dict(n=int(m.sum()), med=float(np.median(dots[m])) if m.sum() else float('nan'), neg=int((dots[m]<0).sum()), gap=float(ds.min()))
PAIRS=[(1,2),(1,4),(1,8),(1,9),(2,5),(2,9),(3,5),(6,7),(7,9)]
HARN_B={(1,2):(-0.896,10,10),(1,4):(0.786,9,0),(1,8):(0.971,19,0),(1,9):(-0.945,8,8),(2,5):(-0.991,1,1),(2,9):(0.991,4,0),(3,5):(0.987,3,0),(6,7):(0.106,16,6),(7,9):(-0.674,4,4)}
HARN_C={(1,2):(0.311,13,0),(1,4):(0.469,9,0),(1,8):(0.741,19,0),(1,9):(-0.408,7,6),(2,5):(0.642,1,0),(2,9):(0.693,4,0),(3,5):(0.674,3,0),(6,7):(-0.786,15,12),(7,9):(0.287,3,0)}
for tag,root,H in [('shipped',f'{IN}/geom',HARN_B),('cured','C:/PR/worktrees/sfs/328-juglet-wall-side-cure/artifacts/pota328/jobA/outgt_jug/geom',HARN_C)]:
    S,Bl=load_root(root)
    print('==',tag)
    for (y,x) in PAIRS:
        r=pair(Bl[y],Bl[x],y,x)
        print('  %d-%d mine n=%d med=%+.3f neg=%d gap=%.3f | harness med=%+.3f n=%d neg=%d'%(y,x,r['n'],r['med'],r['neg'],r['gap'],H[(y,x)][0],H[(y,x)][1],H[(y,x)][2]))
