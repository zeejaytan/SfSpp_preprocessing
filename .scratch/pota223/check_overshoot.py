import numpy as np
from scipy.spatial import cKDTree
def load(p, skiphead=False):
    d=[]; f=open(p); data=not skiphead
    for ln in f:
        if not data:
            if ln.startswith('DATA'): data=True
            continue
        s=ln.split()
        if len(s)>=3:
            try: d.append([float(x) for x in s[:3]])
            except ValueError: pass
    return np.array(d)
P12='C:/PR/SfSpp_preprocessing/.scratch/pota222/p12/'
s0=load(P12+'p12_S0_at4p5.xyz'); s1=load(P12+'p12_S1_at4p5.xyz')
a0=load(P12+'auth_Bl0.pcd',True); a1=load(P12+'auth_Bl1.pcd',True)
A=np.vstack([a0,a1])
t=cKDTree(A)
for nm,s in [('S0',s0),('S1',s1)]:
    dd,_=t.query(s)
    print(nm,'n=%d med=%.2f p90=%.2f p99=%.2f over2mm=%d (%.1f%%)'%(len(s),float(np.median(dd)),float(np.percentile(dd,90)),float(np.percentile(dd,99)),int((dd>2).sum()),100*float((dd>2).mean())),flush=True)
    over=s[dd>2]
    print(' over-bbox', over.min(axis=0).round(1), over.max(axis=0).round(1),flush=True)
