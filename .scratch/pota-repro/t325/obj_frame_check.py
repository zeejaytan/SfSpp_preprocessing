
import glob, os, numpy as np
ART=r"C:/PR/worktrees/sfs/325/artifacts/pota325"
def objv(p):
    V=[l.split()[1:4] for l in open(p,errors="replace") if l.startswith("v ")]
    return np.array(V,float)
def ply(p,want=0):
    with open(p,errors="replace") as fh:
        n=None
        for line in fh:
            s=line.split()
            if len(s)>=3 and s[0]=="element" and s[1]=="vertex": n=int(s[2])
            if line.strip()=="end_header": break
        rows=[fh.readline().split() for _ in range(n)]
    return np.array([[float(v) for v in r[:3]] for r in rows])
def bb(P): return np.round(P.max(0)-P.min(0),2), np.round((P.max(0)+P.min(0))/2,1)
for f in sorted(glob.glob(ART+"/outgt/*_OBJ_*.obj")):
    V=objv(f); k=int(f.rsplit("_OBJ_",1)[1].split(".")[0])
    print("OBJ",k,len(V),"bbox",*bb(V))
print()
for i in (1,7):
    P=np.vstack([ply(f"{ART}/juggeom/Juglet_Piece_{i}.S0",0),ply(f"{ART}/juggeom/Juglet_Piece_{i}.S1",0)])
    print("piece",i,"cloud pts",len(P),"bbox",*bb(P))
