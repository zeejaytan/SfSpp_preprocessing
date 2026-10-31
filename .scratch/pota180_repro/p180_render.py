import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
S180='C:/PR/SfSpp_preprocessing/.scratch/pota180_repro'
HDR=('VERSION','FIELDS','SIZE','TYPE','COUNT','WIDTH','HEIGHT','VIEWPOINT','POINTS','DATA')
def load3(p):
 R=[]
 for ln in open(p):
  s=ln.strip()
  if not s or s[0]=='#' or s.split()[0] in HDR: continue
  R.append([float(x) for x in s.split()[:3]])
 return np.array(R)
G0=load3('C:/PR/SfSpp_preprocessing/artifacts/pota26/pota26_fetch/rims_orig/Pot_C_Piece_01_Breakline_0.pcd')
T=np.loadtxt('C:/PR/SfSpp_preprocessing/.scratch/pota176_repro/inputs/Pot_C_Piece_1_T.txt')
R=T[:3,:3]; t=T[:3,3]
Gs=G0@R.T+t
S=np.load(S180+'/p180_C01_single_walk_seated.npy')
L=np.load('C:/PR/SfSpp_preprocessing/.scratch/pota176_repro/p176_C01_TRUE_walk.npy')
fig=plt.figure(figsize=(15,6))
ax=fig.add_subplot(121,projection='3d')
ax.scatter(L[:,0],L[:,1],L[:,2],s=4,c='gray',alpha=0.25,label='176 TRUE 439 (doubled)')
ax.scatter(Gs[:,0],Gs[:,1],Gs[:,2],s=10,c='green',label='author ORIG 211')
ax.scatter(S[:,0],S[:,1],S[:,2],s=12,c='red',label='180 single 220')
ax.set_title('C01 seated frame: doubled TRUE vs single-loop vs author')
ax.legend(markerscale=2)
ax2=fig.add_subplot(122)
ax2.scatter(L[:,0],L[:,1],s=3,c='gray',alpha=0.25,label='176 TRUE 439')
ax2.scatter(Gs[:,0],Gs[:,1],s=8,c='green',label='author 211')
ax2.scatter(S[:,0],S[:,1],s=10,c='red',label='180 single 220')
ax2.set_title('top view (x-y)'); ax2.legend(); ax2.set_aspect('equal')
fig.tight_layout()
fig.savefig('C:/PR/SfSpp_preprocessing/artifacts/pota180/p180_01_single_vs_ref.png',dpi=110)
print('render saved')
