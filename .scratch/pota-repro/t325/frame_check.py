
import os, numpy as np, itertools
ART = r"C:/PR/worktrees/sfs/325/artifacts/pota325"

def read_ply(path, want=6000):
    with open(path, errors="replace") as fh:
        n=None
        for line in fh:
            s=line.split()
            if len(s)>=3 and s[0]=="element" and s[1]=="vertex": n=int(s[2])
            if line.strip()=="end_header": break
        rows=[fh.readline().split() for _ in range(n)]
    P=np.array([[float(v) for v in r[:3]] for r in rows])
    return P[::max(1,len(P)//want)] if want and len(P)>want else P

def read_bl0(path):
    segs=[]; ranges=[]; data=False; rows=[]
    with open(path, errors="replace") as fh:
        for line in fh:
            if line.startswith("#"):
                s=line[1:].split()
                if len(s)==3 and all(x.lstrip("-").isdigit() for x in s):
                    ranges.append((int(s[0]),int(s[1]),int(s[2])))
                continue
            if line.startswith("DATA"): data=True; continue
            if not data: continue
            s=line.split()
            if len(s)>=3: rows.append([float(s[0]),float(s[1]),float(s[2])])
    if not ranges: return [np.array(rows)]
    P=np.array(rows)
    for a,b,sg in ranges:
        segs.append(P[max(0,a-1):b])
    return [s for s in segs if len(s)]

def T(i):
    M=np.loadtxt(f"{ART}/gtT/Juglet_Piece_{i}_T.txt")
    return M[:3,:3], M[:3,3]

pts={i:np.vstack([read_ply(f"{ART}/juggeom/Juglet_Piece_{i}.S0"),read_ply(f"{ART}/juggeom/Juglet_Piece_{i}.S1")]) for i in range(1,10)}
bls={i:read_bl0(f"{ART}/juggeom/Juglet_Piece_{i}.Bl0") for i in range(1,10)}
print("bl0 segments per piece", {i:len(v) for i,v in bls.items()})

def bbox(P):
    lo,hi=P.min(0),P.max(0); return np.round(hi-lo,2), np.round((lo+hi)/2,2)

allraw=np.vstack([pts[i] for i in range(1,10)])
allT=np.vstack([pts[i]@T(i)[0].T+T(i)[1] for i in range(1,10)])
print("raw union bbox,centre", *bbox(allraw))
print("T-applied union bbox,centre", *bbox(allT))

def pair_gap(a,b):
    return float(np.min(np.linalg.norm(a[:,None,:]-b[None,:,:],axis=2)))
def gap_table(applyT):
    out=[]
    for i,j in itertools.combinations(range(1,10),2):
        A=np.vstack(bls[i]); B=np.vstack(bls[j])
        if applyT:
            A=A@T(i)[0].T+T(i)[1]; B=B@T(j)[0].T+T(j)[1]
        out.append((pair_gap(A,B),i,j))
    return sorted(out)
for lab,flag in (("raw",False),("T",True)):
    g=gap_table(flag)
    print(lab,"closest pairs:", [(f"{d:.3f}",i,j) for d,i,j in g[:12]])
    print(lab,"n pairs <0.1mm:", sum(1 for d,i,j in g if d<0.1))
