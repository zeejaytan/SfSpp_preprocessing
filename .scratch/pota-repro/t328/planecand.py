
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
def planefit(L,R):
    wall=S[k] if False else None
def normal_at(pts,rad,k):
    wall=S[k]; tr=cKDTree(wall[:,:3]); out=[]
    for p in pts:
        idx=tr.query_ball_point(p,rad)
        if len(idx)<8: idx=tr.query(p,k=20)[1]
        Q=wall[idx,:3]
        C=Q-Q.mean(0)
        w,v=np.linalg.eigh(C.T@C)
        n=v[:,0]
        out.append(n/np.linalg.norm(n))
    return np.array(out)
def variants(k,rads):
    out={'fitted':Bl[k].copy()}
    for rad in rads:
        n=normal_at(Bl[k][:,:3],rad,k)
        # align sign with the fitted normal (wall has no handedness; the sign must come from the fit)
        s=np.sign(np.sum(n*Bl[k][:,3:6],axis=1)); s[s==0]=1
        out['plane%g'%rad]=np.hstack([Bl[k][:,:3],n*s[:,None]])
    return out
RADS=[1.0,2.0,3.0]
V={k:variants(k,RADS) for k in range(1,10)}
KEYS=['fitted']+['plane%g'%r for r in RADS]
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
R={k:pairs(k) for k in KEYS}
print("pair   n |"+"|".join("%-16s"%k for k in KEYS))
for p in [(1,2),(1,4),(1,8),(1,9),(2,5),(2,9),(3,5),(6,7),(7,9)]:
    line="%d-%d n=%2d"%(p[0],p[1],R['fitted'][p][0])
    for k in KEYS:
        n,med,neg=R[k][p]; line+="| %+.3f neg%-2d "%(med,neg)
    print(line)
