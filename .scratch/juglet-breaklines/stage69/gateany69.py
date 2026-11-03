
import os, sys, numpy as np
CORP="/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
GTD=os.path.join(CORP,"Ground Truth"); AXD=os.path.join(CORP,"Axes")
def unit(v):
    n=np.linalg.norm(v); return v/n if n>0 else v
def fold(a,b):
    return float(np.degrees(np.arccos(np.clip(abs(unit(a)@unit(b)),0.0,1.0))))
def read_axis_lines(path):
    out=[]
    if not os.path.exists(path): return out
    for line in open(path):
        c=line.split()
        if len(c)>=6:
            try: v=[float(x) for x in c[:6]]
            except ValueError: continue
            out.append(np.array(v[3:6]))
    return out
def read_R(path):
    return np.loadtxt(path, ndmin=2).reshape(4,4)[0:3,0:3]
def read_graph(path):
    A=[]
    for line in open(path):
        c=[x for x in line.strip().split("\t") if x!=""]
        if c: A.append([int(float(x)) for x in c])
    return np.array(A,dtype=int)
GATE=25.0
tot=dict(edges=0,l1=0,anyp=0)
print("%-4s %6s %10s %10s %6s" % ("pot","edges","line1","any","gain"))
for pot in "ABCDEFGHIJ":
    gpath=os.path.join(GTD,"Pot_%s_simple_graph.txt"%pot)
    if not os.path.exists(gpath): continue
    A=read_graph(gpath); n=A.shape[0]
    edges=[(i+1,j+1) for i in range(n) for j in range(i+1,n) if A[i,j]]
    Rs={}; L={}
    for k in range(1,n+1):
        t=os.path.join(GTD,"Pot_%s_Piece_%d_T.txt"%(pot,k))
        ap=os.path.join(AXD,"Pot_%s_Piece_%02d_Axis.xyz"%(pot,k))
        ls=read_axis_lines(ap)
        if os.path.exists(t) and ls:
            Rs[k]=read_R(t); L[k]=ls
    usable=[e for e in edges if e[0] in L and e[1] in L]
    l1=anyp=0
    for i,j in usable:
        if fold(Rs[i]@L[i][0], Rs[j]@L[j][0])<=GATE: l1+=1
        ok=False
        for a in L[i]:
            for b in L[j]:
                if fold(Rs[i]@a, Rs[j]@b)<=GATE: ok=True; break
            if ok: break
        if ok: anyp+=1
    tot["edges"]+=len(usable); tot["l1"]+=l1; tot["anyp"]+=anyp
    print("%-4s %6d %5d/%-5d %5d/%-5d %6d" % (pot,len(usable),l1,len(usable),anyp,len(usable),anyp-l1))
print("%-4s %6d %5d/%-5d %5d/%-5d %6d" % ("ALL",tot["edges"],tot["l1"],tot["edges"],tot["anyp"],tot["edges"],tot["anyp"]-tot["l1"]))
