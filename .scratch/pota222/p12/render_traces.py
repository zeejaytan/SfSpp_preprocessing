import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def loadpcd(p):
    d = []
    with open(p) as f:
        data = False
        for ln in f:
            if not data:
                if ln.startswith('DATA'): data = True
                continue
            s = ln.split()
            if len(s) >= 3:
                try: d.append([float(x) for x in s[:3]])
                except ValueError: pass
    return np.array(d)

def loadobj(p):
    V, F = [], []
    with open(p) as f:
        for ln in f:
            if ln.startswith('v '): V.append([float(x) for x in ln.split()[1:4]])
            elif ln.startswith('f '):
                F.append([int(x.split('/')[0]) - 1 for x in ln.split()[1:4]])
    return np.array(V), np.array(F)

D = 'C:/PR/SfSpp_preprocessing/.scratch/pota222/p12/'
V, F = loadobj(D + 'mesh.obj')
print('mesh', V.shape, F.shape, flush=True)
Fd = F[::6]
polys = V[Fd]
a0 = loadpcd(D + 'auth_Bl0.pcd'); a1 = loadpcd(D + 'auth_Bl1.pcd')
o0 = loadpcd(D + 'our_Bl0.pcd'); o1 = loadpcd(D + 'our_Bl1.pcd')
print('lanes', len(a0), len(a1), len(o0), len(o1), flush=True)

fig = plt.figure(figsize=(10, 14))
for i, (title, lanes) in enumerate([
    ('author trace on our mesh (Bl0 green %d pts, Bl1 magenta %d pts)' % (len(a0), len(a1)), [(a0, '#00c853', 'author Bl0'), (a1, '#d500f9', 'author Bl1')]),
    ('OUR trace on our mesh (Bl0 red %d pts, Bl1 cyan %d pts)' % (len(o0), len(o1)), [(o0, '#e02020', 'our Bl0'), (o1, '#00b8d4', 'our Bl1')]),
]):
    ax = fig.add_subplot(2, 1, i + 1, projection='3d')
    ax.add_collection3d(Poly3DCollection(polys, facecolor=(0.75, 0.72, 0.68), edgecolor='none', alpha=0.45))
    for pts, c, lb in lanes:
        ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2], s=10, c=c, label='%s (%d)' % (lb, len(pts)))
    ax.set_title(title)
    ax.legend(markerscale=2, fontsize=9)
    ax.view_init(elev=18, azim=-62)
    ax.set_box_aspect((1, 1, 1))
    ax.set_xlim(V[:, 0].min(), V[:, 0].max()); ax.set_ylim(V[:, 1].min(), V[:, 1].max()); ax.set_zlim(V[:, 2].min(), V[:, 2].max())
plt.tight_layout()
plt.savefig(D + 'p12_traces_on_mesh.png', dpi=110)
print('SAVED', flush=True)
