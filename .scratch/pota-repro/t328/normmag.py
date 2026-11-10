
import numpy as np, glob, os
def load_pcd(p):
    L=open(p).read().splitlines()
    i=[n for n,l in enumerate(L) if l.startswith('DATA')][0]
    rows=[l.split() for l in L[i+1:] if l.strip() and len(l.split())>=6]
    return np.array([[float(x) for x in r[:7]] for r in rows])
for tag,d in [("shipped","C:/PR/worktrees/sfs/328-juglet-wall-side-cure/artifacts/pota328/in/geom"),("cured","C:/PR/worktrees/sfs/328-juglet-wall-side-cure/artifacts/pota328/jobA/outgt_jug/geom")]:
    print("==",tag)
    for k in range(1,10):
        P=load_pcd(os.path.join(d,"Juglet_Piece_%d.Bl0"%k))
        n=np.linalg.norm(P[:,3:6],axis=1)
        print(" piece %d n=%3d |n| min=%.3f med=%.3f max=%.3f cur=%s"%(k,len(P),n.min(),np.median(n),n.max(),P[0,6] if P.shape[1]>6 else '?'))
