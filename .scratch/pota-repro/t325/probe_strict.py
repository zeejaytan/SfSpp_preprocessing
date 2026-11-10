
import numpy as np
from scipy.spatial import cKDTree
G="C:/PR/worktrees/sfs/325/artifacts/pota325/juggeom"; T="C:/PR/worktrees/sfs/325/artifacts/pota325/gtT"
def load(p):
    L=open(p).read().splitlines(); i=[n for n,l in enumerate(L) if l.startswith("DATA")][0]
    rows=[l.split() for l in L[i+1:] if l.strip()]
    a=np.array(rows,dtype=float)
    return a[:,:3], a[:,3:6]
adj=[(0,1),(0,4),(0,5),(0,7),(0,8),(1,4),(1,8),(2,4),(2,6),(3,4),(3,5),(4,8),(5,6),(5,7),(5,8),(6,7),(6,8),(7,8)]
non={(1,5),(1,6),(4,5),(4,6),(5,9),(6,8),(7,8),(8,9)}
P={}
for k in range(1,10):
    M=np.loadtxt(f"{T}/Juglet_Piece_{k}_T.txt"); R,t=M[:3,:3],M[:3,3]
    p,n=load(f"{G}/Juglet_Piece_{k}.Bl0")
    P[k]=(p@R.T+t, n@R.T)
def inl(a,b,gate=2.0,nd=0.85):
    pa,na=P[a]; pb,nb=P[b]
    tree=cKDTree(pb)
    d,idx=tree.query(pa)
    m=d<=gate
    if m.sum()==0: return 0,0.0
    dots=(na[m]*nb[idx[m]]).sum(1)
    ok=(dots>=nd)
    return int(ok.sum()), float(d[m][ok].max()) if ok.sum() else 0.0
print("pair contact   A->B(inl,maxd)   B->A(inl,maxd)")
for (i,j) in adj:
    a,b=i+1,j+1
    n1,d1=inl(a,b); n2,d2=inl(b,a)
    print(f"{a}-{b} {'NO ' if (a,b) in non else 'YES'}   {n1:3d} {d1:5.2f}      {n2:3d} {d2:5.2f}")
