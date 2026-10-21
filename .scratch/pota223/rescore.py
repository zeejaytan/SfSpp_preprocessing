import numpy as np
from scipy.spatial import cKDTree
def loadpcd(p):
    d = []
    f = open(p); data=False
    for ln in f:
        if not data:
            if ln.startswith('DATA'): data=True
            continue
        s=ln.split()
        if len(s)>=3:
            try: d.append([float(x) for x in s[:3]])
            except ValueError: pass
    return np.array(d)
D='C:/PR/SfSpp_preprocessing/.scratch/pota223/lanes/'
A='C:/PR/SfSpp_preprocessing/.scratch/pota222/p12/'
o0=loadpcd(D+'Pot_D_Piece_12_Breakline_0.pcd'); o1=loadpcd(D+'Pot_D_Piece_12_Breakline_1.pcd')
a0=loadpcd(A+'auth_Bl0.pcd'); a1=loadpcd(A+'auth_Bl1.pcd')
print('n', len(o0), len(o1), flush=True)
for nm,o in [('o0',o0),('o1',o1)]:
    for am,a in [('a0',a0),('a1',a1)]:
        dd,_=cKDTree(a).query(o)
        print(nm,am,'med=%.2f cov=%.1f'%(float(np.median(dd)),100*float((dd<2).mean())),flush=True)
# deviation geography: o0 vs a1 (claimed straight slot)
dd,_=cKDTree(a1).query(o0)
bad=o0[dd>=2]
print('o0-vs-a1 bad n=%d'%len(bad),flush=True)
print('bbox', bad.min(axis=0).round(1), bad.max(axis=0).round(1),flush=True)
