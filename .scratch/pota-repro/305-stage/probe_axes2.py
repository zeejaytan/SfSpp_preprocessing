#!/usr/bin/env python3
"""probe_axes2.py RELEASED CANDIDATE — full matrix: each candidate line vs each released line."""
import sys, numpy as np
def readlines(p):
    out=[]
    for ln in open(p):
        f=ln.split()
        if len(f)>=6: out.append(np.array([float(x) for x in f[:6]]))
    return out
def ang(a,b):
    a=a/np.linalg.norm(a); b=b/np.linalg.norm(b)
    return np.degrees(np.arccos(min(1.0,abs(float(np.dot(a,b))))))
rel=readlines(sys.argv[1])
print("released K=%d"%len(rel))
for ri,r in enumerate(rel):
    print("  rel%d dir=(%.4f,%.4f,%.4f) pos=(%.2f,%.2f,%.2f)"%(ri,*r[3:],*r[:3]))
for p in sys.argv[2:]:
    c=readlines(p)
    print("%s K=%d"%(p.split("/")[-1],len(c)))
    for ci,q in enumerate(c):
        print("   cand%d pos=(%.2f,%.2f,%.2f) %s"%(ci,*q[:3]," ".join("%.2f"%ang(q[3:],r[3:]) for r in rel)))
