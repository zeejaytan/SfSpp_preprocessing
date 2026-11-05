import glob, os, numpy as np
def rd(p):
    A=np.loadtxt(p,ndmin=2); return A.T
def ang(a,b):
    c=abs(float(np.dot(a,b))/(np.linalg.norm(a)*np.linalg.norm(b))); return float(np.degrees(np.arccos(min(1.0,c))))
rows=[]
for p in sorted(glob.glob("out/rel/*.xyz")):
    R=rd(p); K=R.shape[1]
    if K<2: continue
    pair=[ang(R[0:3,i],R[0:3,j]) for i in range(K) for j in range(i+1,K)]
    rows.append((os.path.basename(p)[:-4],K,min(pair),max(pair),np.median(pair)))
print("released multi-line pieces:",len(rows))
print("angle between any two released lines: min %.1f max %.1f median %.1f"%(min(r[2] for r in rows),max(r[3] for r in rows),float(np.median([r[4] for r in rows]))))
for r in rows: print("  %-22s K=%d pairmin=%.1f pairmax=%.1f"%(r[0],r[1],r[2],r[3]))
print()
print("our union Pot A pairwise angles:")
for p in sorted(glob.glob("out/union/*.xyz")):
    O=rd(p); K=O.shape[1]
    pair=[ang(O[0:3,i],O[0:3,j]) for i in range(K) for j in range(i+1,K)]
    print("  %-22s K=%d %s"%(os.path.basename(p)[:-4],K," ".join("%.1f"%x for x in sorted(pair))))
