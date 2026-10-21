import numpy as np
from scipy.spatial import cKDTree
B='C:/PR/SfSpp_preprocessing/.scratch/'
def loadpcd(p):
    d=[]; f=open(p); data=False
    for ln in f:
        if not data:
            if ln.startswith('DATA'): data=True
            continue
        s=ln.split()
        if len(s)>=3:
            try: d.append([float(x) for x in s[:3]])
            except ValueError: pass
    return np.array(d)
L=B+'pota228/'
a0=loadpcd(L+'p25_auth0.pcd'); a1=loadpcd(L+'p25_auth1.pcd')
o0=loadpcd(L+'p25_fresh0.pcd'); o1=loadpcd(L+'p25_fresh1.pcd')
print('n',len(o0),len(o1),len(a0),len(a1),flush=True)
for nm,o,a in [('o0-a0 STRAIGHT',o0,a0),('o0-a1 SWAPPED',o0,a1),('o1-a0 SWAPPED',o1,a0),('o1-a1 STRAIGHT',o1,a1)]:
    dd,_=cKDTree(a).query(o)
    print('%s med=%.2f cov=%.1f max=%.1f'%(nm,float(np.median(dd)),100*float((dd<2).mean()),float(dd.max())),flush=True)
