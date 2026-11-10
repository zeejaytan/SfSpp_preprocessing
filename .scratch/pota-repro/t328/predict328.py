
import os, numpy as np, json
from scipy.spatial import cKDTree
IN='artifacts/pota328/in'
OUT='artifacts/pota328/probe'

def load_ply(p):
    rows=[];hdr=True
    for ln in open(p):
        if hdr:
            if ln.strip()=='end_header': hdr=False
            continue
        t=ln.split()
        if len(t)>=6: rows.append([float(x) for x in t[:6]])
    return np.array(rows)
def load_pcd(p):
    L=open(p).read().splitlines()
    i=[n for n,l in enumerate(L) if l.startswith('DATA')][0]
    rows=[l.split() for l in L[i+1:] if l.strip() and len(l.split())>=6]
    return np.array([[float(x) for x in r[:6]] for r in rows])

T={k:np.loadtxt(f'{IN}/gt/Juglet_Piece_{k}_T.txt') for k in range(1,10)}
S={k:{0:load_ply(f'{IN}/geom/Juglet_Piece_{k}.S0'),1:load_ply(f'{IN}/geom/Juglet_Piece_{k}.S1')} for k in range(1,10)}
Bl={k:{0:load_pcd(f'{IN}/geom/Juglet_Piece_{k}.Bl0'),1:load_pcd(f'{IN}/geom/Juglet_Piece_{k}.Bl1')} for k in range(1,10)}
INTERIOR={2:1,6:1,9:1}   # from the census: the interior face is S1 on these three

def wall_normals(P,N,k=5):
    tr=cKDTree(P)
    _,idx=tr.query(P,k=k)
    acc=N[idx].sum(axis=1)
    n=np.linalg.norm(acc,axis=1,keepdims=True)
    return acc/np.maximum(n,1e-12)

def after_line(k):
    f=INTERIOR.get(k,0)
    L=Bl[k][f].copy()
    P,N=S[k][f][:,:3],S[k][f][:,3:6]
    L[:,3:6]=wall_normals(L[:,:3],P,N) if False else wall_normals(P,N)  # placeholder
    return L

def rederive(k):
    f=INTERIOR.get(k,0)
    L=Bl[k][f].copy()
    P,N=S[k][f][:,:3],S[k][f][:,3:6]
    tr=cKDTree(P)
    for i in range(len(L)):
        _,idx=tr.query(L[i,:3],k=5)
        acc=N[idx].sum(axis=0); n=np.linalg.norm(acc)
        L[i,3:6]=acc/n if n>1e-12 else L[i,3:6]
    return L

def pair(y,x,La,Lb):
    A=La[y]; Bx=Lb[x]
    M=np.linalg.inv(T[y])@T[x]
    B=np.hstack([(M@np.hstack([Bx[:,:3],np.ones((len(Bx),1))]).T).T,(M[:3,:3]@Bx[:,3:6].T).T])
    P,N=A[:,:3],A[:,3:6]
    d=np.linalg.norm(P[None,:,:]-B[:,None,:3],axis=2)
    j=np.argmin(d,axis=1); dmin=d[np.arange(len(B)),j]
    m=dmin<3.0
    if m.sum()==0: return dict(n3=0,dot_med=float('nan'),neg=0)
    dot=np.sum(N[j[m]]*B[m,3:6],axis=1)
    return dict(n3=int(m.sum()),dot_med=round(float(np.median(dot)),3),neg=int((dot<0).sum()),
                frac_neg=round(float((dot<0).mean()),3),gap=round(float(dmin.min()),3))

PAIRS=[(1,2),(1,4),(1,8),(1,9),(2,5),(2,9),(3,5),(6,7),(7,9)]
before={k:Bl[k][0] for k in range(1,10)}          # as shipped: Bl0 rides S0
after={k:rederive(k) for k in range(1,10)}        # post-cure: Bl0 rides the interior face, wall normals
rows=[]
for (y,x) in PAIRS:
    b=pair(y,x,before,before); a=pair(y,x,after,after)
    rows.append(dict(pair=f'{y}-{x}',before=b,after=a))
    print(f'{y}-{x}: before dot_med={b["dot_med"]:+.3f} neg={b["neg"]}/{b["n3"]}   after dot_med={a["dot_med"]:+.3f} neg={a["neg"]}/{a["n3"]} n3={a["n3"]}')
json.dump(rows,open(f'{OUT}/predict_pairs.json','w'),indent=1)
