import numpy as np
from scipy.spatial import cKDTree
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
L='C:/PR/SfSpp_preprocessing/.scratch/pota224/lanes/'
A='C:/PR/SfSpp_preprocessing/.scratch/pota222/p12/'
import glob, os
print(os.listdir(L),flush=True)
o0=loadpcd(L+'Pot_D_Piece_12_Breakline_0.pcd'); o1=loadpcd(L+'Pot_D_Piece_12_Breakline_1.pcd')
a0=loadpcd(A+'auth_Bl0.pcd'); a1=loadpcd(A+'auth_Bl1.pcd')
print('n',len(o0),len(o1),flush=True)
for nm,o in [('o0',o0),('o1',o1)]:
    for am,a in [('a0',a0),('a1',a1)]:
        dd,_=cKDTree(a).query(o)
        print(nm,am,'med=%.2f cov=%.1f'%(float(np.median(dd)),100*float((dd<2).mean())),flush=True)
dd,_=cKDTree(a0).query(o1)
bad=o1[dd>=2]
print('o1-vs-a0 bad n=%d max=%.1f'%(len(bad),float(dd.max())),flush=True)
box=np.array([[33,54],[-28,10],[432,474]])
m=(bad[:,0]>=box[0,0])&(bad[:,0]<=box[0,1])&(bad[:,1]>=box[1,0])&(bad[:,1]<=box[1,1])&(bad[:,2]>=box[2,0])&(bad[:,2]<=box[2,1])
print('bad in corner box: %d'%int(m.sum()),flush=True)
print('bad bbox',bad.min(axis=0).round(1),bad.max(axis=0).round(1),flush=True)
