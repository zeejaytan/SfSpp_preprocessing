
import numpy as np
G="C:/PR/worktrees/sfs/325/artifacts/pota325/juggeom"; T="C:/PR/worktrees/sfs/325/artifacts/pota325/gtT"; A="C:/PR/worktrees/sfs/325/artifacts/pota325/axes/gt"
def load_pcd(p):
    L=open(p).read().splitlines(); i=[n for n,l in enumerate(L) if l.startswith("DATA")][0]
    return np.array([l.split()[:3] for l in L[i+1:] if l.strip()],dtype=float)
def load_ply(p):
    L=open(p).read().splitlines(); i=[n for n,l in enumerate(L) if l=="end_header"][0]
    rows=[l.split() for l in L[i+1:] if l.strip()]
    return np.array([[float(x) for x in r[:3]] for r in rows],dtype=float)
def load_ax(p):
    v=[float(x) for x in open(p).read().split()]
    return np.array(v[-6:-3]), np.array(v[-3:])
print("piece  r_mean S0   r_mean S1   S0 side   (mean radius about own GT axis, world frame)")
sides={}
for k in range(1,10):
    M=np.loadtxt(f"{T}/Juglet_Piece_{k}_T.txt"); R,t=M[:3,:3],M[:3,3]
    o,d=load_ax(f"{A}/Juglet_Piece_{k}_Axis.xyz")
    o=o@R.T+t; d=d@R.T; d=d/np.linalg.norm(d)
    s0=load_ply(f"{G}/Juglet_Piece_{k}.S0")@R.T+t
    s1=load_ply(f"{G}/Juglet_Piece_{k}.S1")@R.T+t
    def rmean(P):
        v=P-P.mean(0); v=v-np.outer(v@d,d)
        return np.linalg.norm(v,axis=1).mean()
    r0,r1=rmean(s0),rmean(s1)
    side="OUTER" if r0>r1 else "inner"
    sides[k]=side
    print(f"  {k}    {r0:8.2f}     {r1:8.2f}    {side}")
print("S0-OUTER pieces:", sorted(k for k,v in sides.items() if v=="OUTER"))
