
import os, glob, math
import numpy as np
ROOT = r"C:\PR\worktrees\sfs\299\.scratch\pota-repro\299-work\t299"
BL=os.path.join(ROOT,"BL")
GT={}
for d in ("GT","GTE"):
    for f in glob.glob(os.path.join(ROOT,d,"*_T.txt")): GT[os.path.basename(f)]=f
def read_T(p):
    M=np.eye(4); rows=[l.split() for l in open(p) if l.strip()]
    for i in range(len(rows)-1): M[i,:]=[float(x) for x in rows[i][:4]]
    return M
def read_pcd(p):
    pts=[]; data=False
    for l in open(p):
        if l.startswith("DATA"): data=True; continue
        if data:
            v=l.split()
            if len(v)>=3: pts.append([float(v[0]),float(v[1]),float(v[2])])
    return np.array(pts)
def dist(A,B):
    d=np.linalg.norm(A[:,None,:]-B[None,:,:],axis=2)
    return d.min(axis=1)
def graph(pot):
    f=os.path.join(ROOT,"GT","Pot_%s_simple_graph.txt"%pot)
    return np.array([[int(x) for x in l.split()] for l in open(f) if l.strip()])
out={}
for pot in ("D","H","B","E","G"):
    G=graph(pot); n=G.shape[0]; P={}
    for i in range(n):
        f=os.path.join(BL,"Pot_%s_Piece_%02d_Breakline_0.pcd"%(pot,i+1))
        if os.path.exists(f): P[i]=read_pcd(f)
    rows=[]
    for i in range(n):
        for j in range(i+1,n):
            if not G[i,j]: continue
            if i not in P or j not in P: continue
            gi=GT.get("Pot_%s_Piece_%d_T.txt"%(pot,i+1)); gj=GT.get("Pot_%s_Piece_%d_T.txt"%(pot,j+1))
            if not gi or not gj: continue
            Ti=read_T(gi) if not isinstance(gi,str) else None
            Ts=read_T(gi); Tj=read_T(gj)
            Q=(np.linalg.inv(Ts)@Tj)
            Pj=(Q[:3,:3]@P[j].T).T+Q[:3,3]
            a=dist(Pj,P[i]); b=dist(P[i],Pj)
            rows.append((i+1,j+1,float(np.median(a)),float(np.median(b)),
                         float((a<2).mean()),float((b<2).mean()),len(P[i]),len(P[j])))
    out[pot]=rows
    med=[max(r[2],r[3]) for r in rows]
    print("\n## Pot %s  %d GT edges measured; median(med) %.2f mm  max %.2f mm"%(pot,len(rows),float(np.median(med)),max(med)))
    for r in sorted(rows,key=lambda r:-max(r[2],r[3]))[:45]:
        print("  E%02d-%02d  medA %7.2f medB %7.2f  frac<2mm %4.2f/%4.2f  n %d/%d"%r)
    print("  edges with BOTH fractions <0.20 :", [(r[0],r[1]) for r in rows if r[4]<0.20 and r[5]<0.20])
