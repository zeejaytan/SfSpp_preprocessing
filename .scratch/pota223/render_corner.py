import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
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
def loadobj(p):
    V,F=[],[]
    f=open(p)
    for ln in f:
        if ln.startswith('v '): V.append([float(x) for x in ln.split()[1:4]])
        elif ln.startswith('f '): F.append([int(x.split('/')[0])-1 for x in ln.split()[1:4]])
    return np.array(V),np.array(F)
P12='C:/PR/SfSpp_preprocessing/.scratch/pota222/p12/'
L='C:/PR/SfSpp_preprocessing/.scratch/pota223/lanes/'
V,F=loadobj(P12+'mesh.obj')
a1=loadpcd(P12+'auth_Bl1.pcd')
o0=loadpcd(L+'Pot_D_Piece_12_Breakline_0.pcd')
dd,_=cKDTree(a1).query(o0)
good,bad=o0[dd<2],o0[dd>=2]
fig=plt.figure(figsize=(11,9))
ax=fig.add_subplot(1,1,1,projection='3d')
ax.add_collection3d(Poly3DCollection(V[F[::6]],facecolor=(0.75,0.72,0.68),edgecolor='none',alpha=0.35))
ax.scatter(a1[:,0],a1[:,1],a1[:,2],s=10,c='#d500f9',label='author Bl1 (156)')
ax.scatter(good[:,0],good[:,1],good[:,2],s=10,c='#e02020',label='our Bl0 on-rim (%d)'%len(good))
ax.scatter(bad[:,0],bad[:,1],bad[:,2],s=40,c='k',label='our Bl0 off-rim (%d)'%len(bad))
ax.set_title('P12 @4.5 honest split: our Bl0 vs author Bl1 (0.63/89.0 -- 19 dots off at one corner)')
ax.legend(markerscale=2,fontsize=9)
ax.view_init(elev=18,azim=-62)
ax.set_box_aspect((1,1,1))
ax.set_xlim(V[:,0].min(),V[:,0].max());ax.set_ylim(V[:,1].min(),V[:,1].max());ax.set_zlim(V[:,2].min(),V[:,2].max())
plt.tight_layout();plt.savefig(L+'p12_223_corner.png',dpi=110)
print('SAVED bad=%d'%len(bad),flush=True)
