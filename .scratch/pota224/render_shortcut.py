import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
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
def loadobj(p):
    V,F=[],[]
    f=open(p)
    for ln in f:
        if ln.startswith('v '): V.append([float(x) for x in ln.split()[1:4]])
        elif ln.startswith('f '): F.append([int(x.split('/')[0])-1 for x in ln.split()[1:4]])
    return np.array(V),np.array(F)
P12='C:/PR/SfSpp_preprocessing/.scratch/pota222/p12/'
L='C:/PR/SfSpp_preprocessing/.scratch/pota224/lanes/'
V,F=loadobj(P12+'mesh.obj')
a0=loadpcd(P12+'auth_Bl0.pcd')
o1=loadpcd(L+'Pot_D_Piece_12_Breakline_1.pcd')
dd,_=cKDTree(a0).query(o1)
good,bad=o1[dd<2],o1[dd>=2]
fig=plt.figure(figsize=(12,10))
ax=fig.add_subplot(1,1,1,projection='3d')
ax.add_collection3d(Poly3DCollection(V[F[::6]],facecolor=(0.82,0.80,0.77),edgecolor='none',alpha=0.30))
ax.scatter(a0[:,0],a0[:,1],a0[:,2],s=16,c='#ffae00',label='author edge (156)')
ax.scatter(good[:,0],good[:,1],good[:,2],s=16,c='#0057ff',label='our @3 edge on-rim (%d)'%len(good))
ax.scatter(bad[:,0],bad[:,1],bad[:,2],s=70,c='k',edgecolors='w',linewidths=0.6,label='our @3 edge shortcut (%d, max %.0fmm)'%(len(bad),float(dd.max())))
ax.set_title('P12 @3: fixing the corner broke the lane elsewhere (Bl1 0.71/80.8)')
ax.legend(markerscale=2,fontsize=10)
ax.view_init(elev=18,azim=-62); ax.set_box_aspect((1,1,1))
ax.set_xlim(V[:,0].min(),V[:,0].max());ax.set_ylim(V[:,1].min(),V[:,1].max());ax.set_zlim(V[:,2].min(),V[:,2].max())
plt.tight_layout();plt.savefig(L+'p12_224_shortcut.png',dpi=110)
print('SAVED bad=%d'%len(bad),flush=True)
