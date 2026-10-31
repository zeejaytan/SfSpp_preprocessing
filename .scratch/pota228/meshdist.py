import numpy as np
from scipy.spatial import cKDTree
B='C:/PR/SfSpp_preprocessing/.scratch/'
V=[]
with open(B+'.wt-217/temp_download/Mesh/Pot_D/Pot_D_Piece_27_Mesh_DS.obj') as f:
    for ln in f:
        if ln.startswith('v '):
            s=ln.split(); V.append([float(s[1]),float(s[2]),float(s[3])])
V=np.array(V)
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
a0=loadpcd(B+'pota225/Pot_D_Piece_27_Breakline_0_author.pcd')
a1=loadpcd(B+'pota225/Pot_D_Piece_27_Breakline_1_author.pcd')
o0=loadpcd(B+'pota227/lanes/Pot_D_Piece_27_Breakline_0.pcd')
o1=loadpcd(B+'pota227/lanes/Pot_D_Piece_27_Breakline_1.pcd')
A=np.vstack([a0,a1])
T=cKDTree(V)
d0,_=cKDTree(A).query(o0); d1,_=cKDTree(A).query(o1)
for nm,pts in [('author0',a0),('author1',a1)]:
    dd,_=T.query(pts)
    print('%s to MESH: med=%.2f p90=%.2f max=%.2f'%(nm,float(np.median(dd)),float(np.percentile(dd,90)),float(dd.max())),flush=True)
for nm,pts,dd in [('ours0-on',o0[d0<=2],None),('ours0-off',o0[d0>2],None),('ours1-on',o1[d1<=2],None),('ours1-off',o1[d1>2],None)]:
    if len(pts)==0: print(nm,'n=0',flush=True); continue
    m,_=T.query(pts)
    print('%s n=%d to MESH: med=%.2f p90=%.2f max=%.2f'%(nm,len(pts),float(np.median(m)),float(np.percentile(m,90)),float(m.max())),flush=True)
