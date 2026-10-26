
import os, json
import numpy as np
ROOT = r"C:\PR\worktrees\sfs\299\.scratch\pota-repro\299-work\t299"
GTD, RD, AXD = os.path.join(ROOT,"GT"), os.path.join(ROOT,"R"), os.path.join(ROOT,"AX")
ARMS = {"D":[("authb","20261026-0126_d1f1a4c_p298-Pot_D-authb"),
             ("oursd","20261026-0126_d1f1a4c_p298-Pot_D-oursd"),
             ("authb-rep2","20261026-0301_d1f1a4c_p298-Pot_D-authb-rep2")],
        "H":[("authb","20261026-0126_d1f1a4c_p298-Pot_H-authb"),
             ("oursd","20261026-0126_d1f1a4c_p298-Pot_H-oursd"),
             ("authb-rep2","20261026-0301_d1f1a4c_p298-Pot_H-authb-rep2")]}
N={"D":29,"H":11}
def read_T(p):
    M=np.eye(4); rows=[l.split() for l in open(p) if l.strip()]
    for i in range(len(rows)-1): M[i,:]=[float(x) for x in rows[i][:4]]
    return M
def ang(R):
    return float(np.degrees(np.arccos(np.clip((np.trace(R)-1)/2,-1,1))))
def err(Ta,Tb,Ga,Gb):
    Tr=(np.linalg.inv(Ga)@Gb)@np.linalg.inv(np.linalg.inv(Ta)@Tb)
    return (ang(Tr[:3,:3])<20.0488 and float(np.linalg.norm(Tr[:3,3]))<50.0), ang(Tr[:3,:3]), float(np.linalg.norm(Tr[:3,3]))
def graph(pot):
    return np.array([[int(x) for x in l.split()] for l in open(os.path.join(GTD,"Pot_%s_simple_graph.txt"%pot)) if l.strip()])
def axes(pot,p):
    f=os.path.join(AXD,"Pot_%s_Piece_%02d_Axis.xyz"%(pot,p))
    out=[]
    for l in open(f):
        v=[float(x) for x in l.split()]
        if len(v)>=6:
            d=np.array(v[3:6]); d/=np.linalg.norm(d); out.append(d)
    return out
res={}
for pot in ("D","H"):
    n=N[pot]; G=graph(pot)
    gt=[None]*n
    for i in range(n):
        q=os.path.join(GTD,"Pot_%s_Piece_%d_T.txt"%(pot,i+1))
        gt[i]=read_T(q) if os.path.exists(q) else None
    print("\n########## POT", pot, " undirected GT edges", G.sum()//2)
    for arm,rid in ARMS[pot]:
        T=[None]*n; on=[False]*n
        for i in range(n):
            q=os.path.join(RD,rid,"T_%dto_%d.txt"%(i,i))
            if os.path.exists(q): T[i]=read_T(q); on[i]=True
        Gg=G.copy()
        for i in range(n):
            if not on[i]: Gg[i,:]=0; Gg[:,i]=0
        print("---- %s %s (on=%d)"%(pot,arm,sum(on)))
        for i in range(n):
            for j in range(i+1,n):
                if not Gg[i,j]: continue
                Ga=gt[i] if gt[i] is not None else np.eye(4)
                Gb=gt[j] if gt[j] is not None else np.eye(4)
                ok,d,m=err(T[i],T[j],Ga,Gb)
                print("  E%02d-%02d %s deg %8.2f mm %8.2f"%(i+1,j+1,"OK  " if ok else "FAIL",d,m))
