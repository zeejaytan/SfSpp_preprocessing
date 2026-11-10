
import numpy as np, os, glob
G="C:/PR/worktrees/sfs/328-juglet-wall-side-cure/artifacts/pota328/in/gt"
CUR="C:/PR/worktrees/sfs/328-juglet-wall-side-cure/artifacts/pota328/jobA/outgt_jug/geom"
def readPCD(p):
    rows=[]; hdr=True; n=0
    for line in open(p):
        if hdr:
            t=line.split()
            if t and t[0]=="POINTS": n=int(t[1])
            if t and t[0]=="DATA": hdr=False
            continue
        if line.startswith("#"): continue
        v=line.split()
        if len(v)>=6: rows.append([float(x) for x in v[:6]])
    return np.array(rows)[:n]
def readPLY(p):
    rows=[]; hdr=True; n=0
    for line in open(p):
        if hdr:
            t=line.split()
            if t and t[0]=="element" and t[1]=="vertex": n=int(t[2])
            if t and t[0]=="end_header": hdr=False
            continue
        if len(rows)<n: rows.append([float(x) for x in line.split()[:6]])
    return np.array(rows)
for k in range(1,10):
    ax=np.loadtxt(os.path.join(G,"Juglet_Piece_%d_Axis.xyz"%k)).ravel()
    c=ax[0:3]; d=ax[3:6]; d=d/np.linalg.norm(d)
    out=[]
    for tag,path in [("S0",os.path.join(CUR,"Juglet_Piece_%d.S0"%k)),("Bl0",os.path.join(CUR,"Juglet_Piece_%d.Bl0"%k))]:
        P=readPLY(path) if path.endswith(".S0") else readPCD(path)
        p=P[:,:3]; n=P[:,3:6]
        r=p-c; r=r-np.outer(r@d,d)
        rh=r/np.linalg.norm(r,axis=1)[:,None]
        dot=(n*rh).sum(1)
        out.append("%s n=%d mean=%+.2f frac_out=%.2f"%(tag,len(p),dot.mean(),(dot>0).mean()))
    print("piece",k," | ".join(out))
