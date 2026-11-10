
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
T={k:np.loadtxt(f'{IN}/gt/Juglet_Piece_{k}_T.txt') for k in range(1,10)}
S={k:load_ply(f'{CUR}/Juglet_Piece_{k}.S0') for k in range(1,10)}
def move(X,M):
    return np.hstack([(M[:3,:3]@X[:,:3].T).T+M[:3,3], (M[:3,:3]@X[:,3:6].T).T])
for (y,x) in [(1,2),(1,4),(1,8),(1,9),(2,5),(2,9),(3,5),(6,7),(7,9)]:
    A=S[y]; M=np.linalg.inv(T[y])@T[x]; B=move(S[x],M)
    d,_=cKDTree(B[:,:3]).query(A[:,:3])
    print("%d-%d nn_med=%.3f nn_p10=%.3f nn_min=%.3f frac<0.2=%.3f frac<1.0=%.3f"%(y,x,np.median(d),np.percentile(d,10),d.min(),(d<0.2).mean(),(d<1.0).mean()))
