import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial import cKDTree

def load(p):
    d = []
    with open(p) as f:
        for ln in f:
            s = ln.split()
            if len(s) >= 3:
                try: d.append([float(x) for x in s[:3]])
                except ValueError: pass
    return np.array(d)

D = 'C:/PR/SfSpp_preprocessing/.scratch/pota222/p12/'
fig = plt.figure(figsize=(16, 7))
for i, (tag, t) in enumerate([('at8', 'just before shatter (@8: bridged, min gap 0.67mm)'), ('at4p5', 'after shatter (@4.5: gap clean, faces fragmented)')]):
    s0 = load(D + 'p12_S0_%s.xyz' % tag)
    s1 = load(D + 'p12_S1_%s.xyz' % tag)
    # contact dots: S0 within 2mm of S1 and vice versa
    d01, _ = cKDTree(s1).query(s0)
    d10, _ = cKDTree(s0).query(s1)
    c0, c1 = s0[d01 < 2.0], s1[d10 < 2.0]
    ax = fig.add_subplot(1, 2, i + 1, projection='3d')
    ax.scatter(s0[::6, 0], s0[::6, 1], s0[::6, 2], s=0.4, c='#c96a2e', label='outer face S0 (%d pts)' % len(s0))
    ax.scatter(s1[::6, 0], s1[::6, 1], s1[::6, 2], s=0.4, c='#2e6fc9', label='inner face S1 (%d pts)' % len(s1))
    if len(c0): ax.scatter(c0[:, 0], c0[:, 1], c0[:, 2], s=3, c='k', label='touching (<2mm: %d+%d)' % (len(c0), len(c1)))
    ax.set_title(t)
    ax.legend(markerscale=4, fontsize=8)
    ax.view_init(elev=18, azim=-62)
    ax.set_box_aspect((1, 1, 1))
    print(tag, 'S0', len(s0), 'S1', len(s1), 'touch', len(c0), len(c1), flush=True)
plt.tight_layout()
plt.savefig(D + 'p12_before_after.png', dpi=110)
print('SAVED', flush=True)
