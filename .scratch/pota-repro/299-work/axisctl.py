
import os, math, glob
import numpy as np
ROOT = r"C:\PR\worktrees\sfs\299\.scratch\pota-repro\299-work\t299"
AXD=os.path.join(ROOT,"AX"); GT={}
for d in ("GT","GTE"):
    for f in glob.glob(os.path.join(ROOT,d,"*_T.txt")): GT[os.path.basename(f)]=f
def read_T(p):
    M=np.eye(4); rows=[l.split() for l in open(p) if l.strip()]
    for i in range(len(rows)-1): M[i,:]=[float(x) for x in rows[i][:4]]
    return M
def axes(pot,p):
    f=os.path.join(AXD,"Pot_%s_Piece_%02d_Axis.xyz"%(pot,p)); out=[]
    if not os.path.exists(f): return out
    for l in open(f):
        v=[float(x) for x in l.split()]
        if len(v)>=6:
            d=np.array(v[3:6]); out.append(d/np.linalg.norm(d))
    return out
print("pot  npc  dev_median  dev_max  pieces with min-dev>15deg")
for pot in ("B","E","G","D","H"):
    pcs=sorted(int(os.path.basename(f).split("_Piece_")[1].split("_")[0]) for f in glob.glob(os.path.join(AXD,"Pot_%s_Piece_*_Axis.xyz"%pot)))
    devs=[]; rows=[]
    # principal axis from single-axis pieces that also have GT
    V=[]
    for p in pcs:
        ax=axes(pot,p); g=GT.get("Pot_%s_Piece_%d_T.txt"%(pot,p))
        if len(ax)==1 and g: V.append(read_T(g)[:3,:3]@ax[0])
    if not V: continue
    u,s,vt=np.linalg.svd(np.array(V)); pax=vt[0]/np.linalg.norm(vt[0])
    for p in pcs:
        ax=axes(pot,p); g=GT.get("Pot_%s_Piece_%d_T.txt"%(pot,p))
        if not g or not ax: continue
        R=read_T(g)[:3,:3]
        a=[math.degrees(math.acos(min(1.0,abs(float((R@d)@pax))))) for d in ax]
        devs.append(min(a)); rows.append((p,len(ax),round(min(a),1),round(max(a),1)))
    bad=[r for r in rows if r[2]>15]
    print("%-3s %3d  %8.2f  %8.2f   %s"%(pot,len(devs),float(np.median(devs)),max(devs),
        " ".join("p%02d(%dx %.0f-%.0f)"%(r[0],r[1],r[2],r[3]) for r in bad)))
