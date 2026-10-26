
import os, glob, math, json
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
def ang(R): return float(np.degrees(np.arccos(np.clip((np.trace(R)-1)/2,-1,1))))
def err(Ta,Tb,Ga,Gb):
    Tr=(np.linalg.inv(Ga)@Gb)@np.linalg.inv(np.linalg.inv(Ta)@Tb)
    d,m=ang(Tr[:3,:3]),float(np.linalg.norm(Tr[:3,3]))
    return (d<20.0488 and m<50.0),d,m
def graph(pot): return np.array([[int(x) for x in l.split()] for l in open(os.path.join(GTD,"Pot_%s_simple_graph.txt"%pot)) if l.strip()])
def axes(pot,p):
    f=os.path.join(AXD,"Pot_%s_Piece_%02d_Axis.xyz"%(pot,p)); o=[]
    if not os.path.exists(f): return o
    for l in open(f):
        v=[float(x) for x in l.split()]
        if len(v)>=6: d=np.array(v[3:6]); o.append(d/np.linalg.norm(d))
    return o
res={}
for pot in ("D","H"):
    n=N[pot]; G=graph(pot)
    gt=[None]*n
    for i in range(n):
        q=os.path.join(GTD,"Pot_%s_Piece_%d_T.txt"%(pot,i+1)); gt[i]=read_T(q) if os.path.exists(q) else None
    # axis deviation
    V=[gt[i][:3,:3]@axes(pot,i+1)[0] for i in range(n) if gt[i] is not None and len(axes(pot,i+1))==1]
    u,s,vt=np.linalg.svd(np.array(V)); pax=vt[0]/np.linalg.norm(vt[0])
    adev={}
    for i in range(n):
        ax=axes(pot,i+1)
        if gt[i] is None or not ax: adev[i+1]=(len(ax),None,None); continue
        a=[math.degrees(math.acos(min(1.0,abs(float((gt[i][:3,:3]@d)@pax))))) for d in ax]
        adev[i+1]=(len(ax),min(a),max(a))
    per={}
    for arm,rid in ARMS[pot]:
        T=[None]*n; on=[False]*n
        for i in range(n):
            q=os.path.join(RD,rid,"T_%dto_%d.txt"%(i,i))
            if os.path.exists(q): T[i]=read_T(q); on[i]=True
        Gg=G.copy()
        for i in range(n):
            if not on[i]: Gg[i,:]=0; Gg[:,i]=0
        seated=[False]*n; best=[None]*n; fail=[]
        for i in range(n):
            for j in range(n):
                if Gg[i,j] and gt[i] is not None and gt[j] is not None:
                    ok,d,m=err(T[i],T[j],gt[i],gt[j])
                    if ok: seated[i]=True
                    key=d/20.0488+m/50.0
                    if best[i] is None or key<best[i][0]: best[i]=(key,j+1,d,m,ok)
                elif Gg[i,j]: fail.append((i+1,j+1,None,None))
        per[arm]=dict(on=on,seated=seated,best=best)
    res[pot]=(adev,per,G)
# markdown tables
for pot in ("D","H"):
    adev,per,G=res[pot]; n=N[pot]
    print("\n### " + pot + " per-piece")
    hdr="| piece | GT deg | axes | axis-GT dev min/max deg |"
    for arm,_ in ARMS[pot]: hdr+=" %s best (deg / mm) |"%arm
    print(hdr)
    print("|"+"---|"*(3+len(ARMS[pot])))
    for i in range(n):
        Lv,amn,amx=adev[i+1]
        line="| %d | %d | %d | %s |"%(i+1,int(G[i].sum()),Lv, ("%.1f / %.1f"%(amn,amx)) if amn is not None else "GT absent")
        for arm,_ in ARMS[pot]:
            p=per[arm]
            if not p["on"][i]: line+=" off |"; continue
            b=p["best"][i]
            if b is None: line+=" no GT edge |"; continue
            line+=" %.2f / %.2f%s |"%(b[2],b[3]," OK" if b[4] else "")
        print(line)
    for arm,_ in ARMS[pot]:
        p=per[arm]
        print("  %-10s seated=%d on=%d  not seated: %s"%(arm,sum(p["seated"]),sum(p["on"]),
              [i+1 for i in range(n) if p["on"][i] and not p["seated"][i]]))
