
import os, json, math
import numpy as np
ROOT = r"C:\PR\worktrees\sfs\299\.scratch\pota-repro\299-work\t299"
GTD, RD, AXD = os.path.join(ROOT,"GT"), os.path.join(ROOT,"R"), os.path.join(ROOT,"AX")
ARMS = {"D":[("authb","20261026-0126_d1f1a4c_p298-Pot_D-authb"),
             ("oursd","20261026-0126_d1f1a4c_p298-Pot_D-oursd")],
        "H":[("authb","20261026-0126_d1f1a4c_p298-Pot_H-authb"),
             ("oursd","20261026-0126_d1f1a4c_p298-Pot_H-oursd")]}
N={"D":29,"H":11}
def read_T(p):
    M=np.eye(4); rows=[l.split() for l in open(p) if l.strip()]
    for i in range(len(rows)-1): M[i,:]=[float(x) for x in rows[i][:4]]
    return M
def ang(R): return float(np.degrees(np.arccos(np.clip((np.trace(R)-1)/2,-1,1))))
def axes(pot,p):
    f=os.path.join(AXD,"Pot_%s_Piece_%02d_Axis.xyz"%(pot,p)); out=[]
    for l in open(f):
        v=[float(x) for x in l.split()]
        if len(v)>=6:
            d=np.array(v[3:6]); out.append(d/np.linalg.norm(d))
    return out
for pot in ("D","H"):
    n=N[pot]; gt=[None]*n; ax=[[] for _ in range(n)]
    for i in range(n):
        q=os.path.join(GTD,"Pot_%s_Piece_%d_T.txt"%(pot,i+1))
        gt[i]=read_T(q) if os.path.exists(q) else None
        ax[i]=axes(pot,i+1)
    # principal axis in GT frame from single-axis pieces
    V=[gt[i][:3,:3]@ax[i][0] for i in range(n) if gt[i] is not None and len(ax[i])==1]
    M=np.array(V); u,s,vt=np.linalg.svd(M); pax=vt[0]; pax/=np.linalg.norm(pax)
    print("\n#### POT",pot,"principal axis (GT frame) =",np.round(pax,4)," sing",np.round(s,2))
    for i in range(n):
        if gt[i] is None:
            print("  p%02d  axis lines %d  GT MISSING"%(i+1,len(ax[i]))); continue
        angs=[math.degrees(math.acos(min(1.0,abs(float((gt[i][:3,:3]@d)@pax))))) for d in ax[i]]
        print("  p%02d lines %d  GT-axis dev (min/mean/max) %6.2f %6.2f %6.2f  all=%s"%(
            i+1,len(ax[i]),min(angs),sum(angs)/len(angs),max(angs),np.round(angs,1).tolist()))
    for arm,rid in ARMS[pot]:
        print("  -- arm",arm,"result-frame axis dev & abs-pose error")
        for i in range(n):
            q=os.path.join(RD,rid,"T_%dto_%d.txt"%(i,i))
            if not os.path.exists(q): print("    p%02d OFF"%(i+1)); continue
            T=read_T(q)
            if gt[i] is None: print("    p%02d  (gt missing)"%(i+1)); continue
            dev=min(math.degrees(math.acos(min(1.0,abs(float((T[:3,:3]@d)@pax))))) for d in ax[i])
            A=np.linalg.inv(gt[i])@T
            print("    p%02d axisdev %6.2f  abs %7.2f deg %8.2f mm"%(i+1,dev,ang(A[:3,:3]),np.linalg.norm(A[:3,3])))
