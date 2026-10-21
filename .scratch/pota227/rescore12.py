import numpy as np
from scipy.spatial import cKDTree
import os
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
D='C:/PR/SfSpp_preprocessing/.scratch/pota227/'
L=D+'lanes/'
print(sorted(os.listdir(L)),flush=True)
o0=loadpcd(L+'Pot_D_Piece_27_Breakline_0.pcd'); o1=loadpcd(L+'Pot_D_Piece_27_Breakline_1.pcd')
A='C:/PR/SfSpp_preprocessing/.scratch/pota225/'
a0=loadpcd(A+'Pot_D_Piece_27_Breakline_0_author.pcd'); a1=loadpcd(A+'Pot_D_Piece_27_Breakline_1_author.pcd')
print('n',len(o0),len(o1),len(a0),len(a1),flush=True)
for nm,o in [('o0',o0),('o1',o1)]:
    for am,a in [('a0',a0),('a1',a1)]:
        dd,_=cKDTree(a).query(o)
        print(nm,am,'med=%.2f cov=%.1f'%(float(np.median(dd)),100*float((dd<2).mean())),flush=True)
