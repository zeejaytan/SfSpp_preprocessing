
import numpy as np
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
SWAP={2:1,6:1,9:1}
S={k:load_ply(f'{IN}/geom/Juglet_Piece_{k}.S{SWAP.get(k,0)}') for k in range(1,10)}
Bl={k:load_pcd(f'{IN}/geom/Juglet_Piece_{k}.Bl{SWAP.get(k,0)}') for k in range(1,10)}
def move(X,M):
    return np.hstack([(M[:3,:3]@X[:,:3].T).T+M[:3,3], (M[:3,:3]@X[:,3:6].T).T])
def variants(k):
    L=Bl[k].copy(); wall=S[k]
    out={}
    out['fitted']=L.copy()
    # per-point sign correction against the wall
    _,idx=cKDTree(wall[:,:3]).query(L[:,:3],k=5)
    wn=np.zeros((len(L),3))
    for i in range(len(L)):
        acc=wall[idx[i],3:6].sum(0); nn=np.linalg.norm(acc)
        wn[i]=acc/nn if nn>1e-9 else L[i,3:6]
    P=L.copy(); s=np.sign(np.sum(P[:,3:6]*wn,axis=1)); s[s==0]=1
    P[:,3:6]=P[:,3:6]*s[:,None]
    out['fit_signed']=P
    out['wall5']=np.hstack([L[:,:3],wn])
    _,i1=cKDTree(wall[:,:3]).query(L[:,:3])
    out['wall1']=np.hstack([L[:,:3],wall[i1,3:6]])
    return out
V={k:variants(k) for k in range(1,10)}
def pairs(key):
    res={}
    for (y,x) in [(1,2),(1,4),(1,8),(1,9),(2,5),(2,9),(3,5),(6,7),(7,9)]:
        A=V[y][key]; M=np.linalg.inv(T[y])@T[x]; B=move(V[x][key],M)
        tA=cKDTree(A[:,:3]); tB=cKDTree(B[:,:3])
        _,ia=tA.query(B[:,:3]); _,ib=tB.query(A[ia,:3]); keep=ib==np.arange(len(B))
        bi=np.where(keep)[0]; j=ia[bi]
        d=np.linalg.norm(A[j,:3]-B[bi,:3],axis=1); m=d<3
        dots=np.sum(A[j[m],3:6]*B[bi[m],3:6],axis=1)
        res[(y,x)]=(int(m.sum()),float(np.median(dots)) if m.sum() else float('nan'),int((dots<0).sum()))
    return res
H={(1,2):0.704,(1,4):0.786,(1,8):0.971,(1,9):-0.039,(2,5):0.948,(2,9):0.971,(3,5):0.987,(6,7):-0.183,(7,9):0.708}
keys=['fitted','fit_signed','wall5','wall1']
R={k:pairs(k) for k in keys}
print("pair  n | " + " | ".join("%-22s"%k for k in keys) + " | 327swap")
for p in [(1,2),(1,4),(1,8),(1,9),(2,5),(2,9),(3,5),(6,7),(7,9)]:

    line="%d-%d n=%2d"%(p[0],p[1],R['fitted'][p][0])
    for k in keys:
        n,med,neg=R[k][p]; line+=" | %+.3f neg%d"%(med,neg)
    line+=" | %+.3f"%H[p]
    print(line)
