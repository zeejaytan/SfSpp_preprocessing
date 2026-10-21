import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
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
def loadobj(p):
    v=[]
    for ln in open(p):
        if ln.startswith('v '):
            try: v.append([float(x) for x in ln.split()[1:4]])
            except ValueError: pass
    return np.array(v)
def rimcolor(o,a,A2):
    from scipy.spatial import cKDTree
    dd,_=cKDTree(a).query(o); dd2,_=cKDTree(A2).query(o)
    dd=np.minimum(dd,dd2)
    return np.where(dd<2,'b','k'),float(np.median(dd)),100*float((dd<2).mean())
M=loadobj(B+'.wt-217/temp_download/Mesh/Pot_D/Pot_D_Piece_22_Mesh_DS.obj')
A=B+'pota221/pota221f/author/'
a0=loadpcd(A+'Pot_D_Piece_22_Breakline_0.pcd'); a1=loadpcd(A+'Pot_D_Piece_22_Breakline_1.pcd')
L=B+'pota221/pota221f/'
o0=loadpcd(L+'lanes/Pot_D_Piece_22_Breakline_0.pcd'); o1=loadpcd(L+'lanes/Pot_D_Piece_22_Breakline_1.pcd')
c0,m0,v0=rimcolor(o0,a0,a1); c1,m1,v1=rimcolor(o1,a0,a1)
print('o0 med=%.2f cov=%.1f | o1 med=%.2f cov=%.1f'%(m0,v0,m1,v1),flush=True)
ctr=np.vstack([o0,o1]).mean(axis=0)
print('our-centroid',np.round(ctr,1).tolist(),flush=True)
fig=plt.figure(figsize=(18.7,8.8))
for k,(el,az,box,ttl) in enumerate([(30,-125,None,'full, flipped side'),(30,-125,35,'zoom: our traced section')]):
    ax=fig.add_subplot(1,2,k+1,projection='3d')
    ax.scatter(M[:,0],M[:,1],M[:,2],s=0.15,c='gray',alpha=0.25,depthshade=False)
    ax.scatter(a0[:,0],a0[:,1],a0[:,2],s=9,c='gold',depthshade=False)
    ax.scatter(a1[:,0],a1[:,1],a1[:,2],s=9,c='gold',depthshade=False)
    for o,c in [(o0,c0),(o1,c1)]:
        for col in ['b','k']:
            m=(c==col)
            if m.any(): ax.scatter(o[m,0],o[m,1],o[m,2],s=14,c=col,depthshade=False)
    ax.view_init(elev=el,azim=az)
    if box:
        ax.set_xlim(ctr[0]-box,ctr[0]+box); ax.set_ylim(ctr[1]-box,ctr[1]+box); ax.set_zlim(ctr[2]-box,ctr[2]+box)
    ax.set_title(ttl)
plt.suptitle('P22: gold=author rims, blue=ours-on-rim, black=ours-off-rim (o0 med %.2f/%.0f, o1 med %.2f/%.0f)'%(m0,v0,m1,v1))
plt.savefig(B+'pota228/p228_P22_zoom_ours.png',dpi=100)
print('saved',flush=True)
