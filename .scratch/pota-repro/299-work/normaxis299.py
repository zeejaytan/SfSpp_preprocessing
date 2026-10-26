
import os, math
import numpy as np
ROOT = r"C:\PR\worktrees\sfs\299\.scratch\pota-repro\299-work\t299"
DIRS={"GT":[ROOT+r"\GT",ROOT+r"\GTE"],"AX":ROOT+r"\AX","BL":ROOT+r"\BL"}
def findT(pot,p):
    for d in DIRS["GT"]:
        f=os.path.join(d,"Pot_%s_Piece_%d_T.txt"%(pot,p))
        if os.path.exists(f): return f
    return None
def read_T(p):
    M=np.eye(4); rows=[l.split() for l in open(p) if l.strip()]
    for i in range(len(rows)-1): M[i,:]=[float(x) for x in rows[i][:4]]
    return M
def read_pcd(p):
    d=[];  inD=False
    for l in open(p,'r',errors='ignore'):
        s=l.strip()
        if s.startswith('DATA'): inD=True; continue
        if inD:
            v=s.split()
            if len(v)>=6: d.append([float(x) for x in v[:6]])
    return np.array(d)
def axes(f):
    o=[]
    if not os.path.exists(f): return o
    for l in open(f):
        v=[float(x) for x in l.split()]
        if len(v)>=6:
            d=np.array(v[3:6]); o.append(d/np.linalg.norm(d))
    return o
def ang(a,b): return math.degrees(math.acos(min(1.0,abs(float(a@b)))))
out=[]
for pot,ps in (("B",range(1,10)),("E",range(1,32)),("D",range(1,30)),("H",range(1,12))):
    gt={}; ax={}
    for p in ps:
        f=findT(pot,p)
        if f: gt[p]=read_T(f)
        ax[p]=axes(os.path.join(DIRS["AX"],"Pot_%s_Piece_%02d_Axis.xyz"%(pot,p)))
    V=[gt[p][:3,:3]@ax[p][0] for p in ps if p in gt and len(ax[p])==1]
    M=np.array(V); pax=np.linalg.svd(M)[2][0]; pax/=np.linalg.norm(pax)
    for p in ps:
        q=os.path.join(DIRS["BL"],"Pot_%s_Piece_%02d_Breakline_0.pcd"%(pot,p))
        if p not in gt or not os.path.exists(q) or not ax[p]: continue
        P=read_pcd(q); N=P[:,3:6]; nn=np.linalg.norm(N,axis=1); keep=nn>0.5
        N=N[keep]/nn[keep][:,None]
        if len(N)<20: continue
        a=np.linalg.svd(N.T@N)[2][-1]
        g=gt[p][:3,:3]@ax[p][0]
        out.append((pot,p,len(N),min(ang(a,d) for d in ax[p]),ang(a,g),ang(a,pax),len(ax[p])))
print("pot pc nBL  est~axisFile est~GT*axis est~potAxis nAxes")
for t in out: print("%-2s %2d %5d %8.1f %8.1f %8.1f %3d"%t)
# summary: how often the normal-estimate agrees better with the axis file than with GT*axis
import collections
bypot=collections.defaultdict(list)
for t in out: bypot[t[0]].append(t)
print()
for pot in ("B","E","G","D","H"):
    if pot not in bypot: continue
    L=bypot[pot]
    ag=sum(1 for t in L if t[3]<t[4]); print("%s: %d pieces, est closer to AXIS FILE in %d, to GT*axis in %d"%(pot,len(L),ag,len(L)-ag))
