
import numpy as np
G="C:/PR/worktrees/sfs/325/artifacts/pota325/juggeom"
T="C:/PR/worktrees/sfs/325/artifacts/pota325/gtT"
def load_pcd(p):
    lines=open(p).read().splitlines()
    i=[n for n,l in enumerate(lines) if l.startswith("DATA")][0]
    rows=[l.split()[:3] for l in lines[i+1:] if l.strip()]
    return np.array(rows,dtype=float)
adj=[(0,1),(0,4),(0,5),(0,7),(0,8),(1,4),(1,8),(2,4),(2,6),(3,4),(3,5),(4,8),(5,6),(5,7),(5,8),(6,7),(6,8),(7,8)]
pts={}
for k in range(1,10):
    M=np.loadtxt(f"{T}/Juglet_Piece_{k}_T.txt"); R,t=M[:3,:3],M[:3,3]
    for tag in ("Bl0","Bl1"):
        pts[(k,tag)]=load_pcd(f"{G}/Juglet_Piece_{k}.{tag}")@R.T+t
non={(1,5),(1,6),(4,5),(4,6),(5,9),(6,8),(7,8),(8,9)}
def mind(a,b):
    return np.sqrt(((a[:,None,:]-b[None,:,:])**2).sum(-1)).min()
print("pair contact  Bl0-Bl0  Bl0-Bl1  Bl1-Bl0  Bl1-Bl1")
for (i,j) in adj:
    a,b=i+1,j+1
    row=[mind(pts[(a,"Bl0")],pts[(b,"Bl0")]),mind(pts[(a,"Bl0")],pts[(b,"Bl1")]),
         mind(pts[(a,"Bl1")],pts[(b,"Bl0")]),mind(pts[(a,"Bl1")],pts[(b,"Bl1")])]
    print(f"{a}-{b}  {'NO ' if (a,b) in non else 'YES'}   " + "  ".join(f"{x:8.2f}" for x in row))
print("Bl0 n:", [len(pts[(k,'Bl0')]) for k in range(1,10)])
print("Bl1 n:", [len(pts[(k,'Bl1')]) for k in range(1,10)])
