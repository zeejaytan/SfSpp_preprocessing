import numpy as np
from scipy.spatial import cKDTree
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
B='C:/PR/SfSpp_preprocessing/.scratch/'
# mesh
V=[]
with open(B+'.wt-217/temp_download/Mesh/Pot_D/Pot_D_Piece_27_Mesh_DS.obj') as f:
    for ln in f:
        if ln.startswith('v '):
            s=ln.split()
            V.append([float(s[1]),float(s[2]),float(s[3])])
V=np.array(V)
print('mesh verts',len(V),flush=True)
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
d0,_=cKDTree(A).query(o0); d1,_=cKDTree(A).query(o1)
GOLD='#ffae00'; BLUE='#0057ff'
fig=plt.figure(figsize=(17,8))
for k,(el,az,title) in enumerate([(10,-60,'view 1'),(25,45,'view 2')]):
    ax=fig.add_subplot(1,2,k+1,projection='3d')
    ax.scatter(V[::7,0],V[::7,1],V[::7,2],s=0.3,c='#bbbbbb',depthshade=False)
    ax.scatter(a0[:,0],a0[:,1],a0[:,2],s=14,c=GOLD,depthshade=False,label='author')
    ax.scatter(a1[:,0],a1[:,1],a1[:,2],s=14,c=GOLD,depthshade=False)
    ax.scatter(o0[d0<=2,0],o0[d0<=2,1],o0[d0<=2,2],s=14,c=BLUE,depthshade=False,label='ours on-rim')
    ax.scatter(o1[d1<=2,0],o1[d1<=2,1],o1[d1<=2,2],s=14,c=BLUE,depthshade=False)
    ax.scatter(o0[d0>2,0],o0[d0>2,1],o0[d0>2,2],s=22,c='black',depthshade=False,label='ours off-rim')
    ax.scatter(o1[d1>2,0],o1[d1>2,1],o1[d1>2,2],s=22,c='black',depthshade=False)
    ax.view_init(elev=el,azim=az)
    ax.set_title('P27@12 '+title+' (mesh gray, author GOLD, ours BLUE, off-rim BLACK)')
    ax.legend(loc='upper left',fontsize=8)
plt.tight_layout(); plt.savefig(B+'pota228/p228_P27_face_mesh.png',dpi=110)
print('saved',flush=True)
