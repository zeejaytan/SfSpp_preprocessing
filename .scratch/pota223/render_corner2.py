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
def loadxyz(p):
    d=[]
    f=open(p)
    for ln in f:
        s=ln.split()
        if len(s)>=3:
            try: d.append([float(x) for x in s[:3]])
            except ValueError: pass
    return np.array(d)
S0=loadxyz(P12+'p12_S0_at4p5.xyz')
a1=loadpcd(P12+'auth_Bl1.pcd')
o0=loadpcd(L+'Pot_D_Piece_12_Breakline_0.pcd')
dd,_=cKDTree(a1).query(o0)
good,bad=o0[dd<2],o0[dd>=2]
MESH=(0.82,0.80,0.77); AUTH='#ffae00'; OURS='#0057ff'
fig=plt.figure(figsize=(12,17))
ax1=fig.add_subplot(2,1,1,projection='3d')
ax1.add_collection3d(Poly3DCollection(V[F[::6]],facecolor=MESH,edgecolor='none',alpha=0.30))
ax1.scatter(a1[:,0],a1[:,1],a1[:,2],s=16,c=AUTH,label='author edge (156)')
ax1.scatter(good[:,0],good[:,1],good[:,2],s=16,c=OURS,label='our edge on-rim (153)')
ax1.scatter(bad[:,0],bad[:,1],bad[:,2],s=70,c='k',edgecolors='w',linewidths=0.6,label='our edge off-rim (19)')
ax1.set_title('P12 honest split: our edge vs author edge (0.63/89.0) -- full sherd')
ax1.legend(markerscale=2,fontsize=10)
ax1.view_init(elev=18,azim=-62); ax1.set_box_aspect((1,1,1))
ax1.set_xlim(V[:,0].min(),V[:,0].max());ax1.set_ylim(V[:,1].min(),V[:,1].max());ax1.set_zlim(V[:,2].min(),V[:,2].max())
ax2=fig.add_subplot(2,1,2,projection='3d')
ax2.add_collection3d(Poly3DCollection(V[F[::6]],facecolor=MESH,edgecolor='none',alpha=0.30))
ax2.scatter(a1[:,0],a1[:,1],a1[:,2],s=30,c=AUTH,label='author edge')
ax2.scatter(good[:,0],good[:,1],good[:,2],s=30,c=OURS,label='our edge on-rim')
ax2.scatter(bad[:,0],bad[:,1],bad[:,2],s=120,c='k',edgecolors='w',linewidths=1.0,label='our edge off-rim (19)')
ax2.scatter(S0[::5,0],S0[::5,1],S0[::5,2],s=4,c='#9a9a9a',label='face dots (S0, thinned)',alpha=0.6)
ax2.set_title('ZOOM on the corner where our walk cut across')
ax2.legend(markerscale=2,fontsize=10)
ax2.view_init(elev=18,azim=-62); ax2.set_box_aspect((1,1,1))
ax2.set_xlim(33,54); ax2.set_ylim(-28,10); ax2.set_zlim(432,474)
plt.tight_layout();plt.savefig(L+'p12_223_corner2.png',dpi=110)
print('SAVED',flush=True)
