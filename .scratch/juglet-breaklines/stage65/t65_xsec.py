#!/usr/bin/env python3
"""Ticket 65: wall cross-sections of J1 at chosen ring angles (read-only).

At each angle theta the cut plane contains the ring normal n and the radial direction at theta
(common t62F frame); everything within +-HALF mm of the plane is drawn in (radial mm, height mm),
equal aspect, 1 mm grid -- a view that resolves 1 mm by construction.
Mesh vertices by t59 vertex label, S0 / S1 points of each arm, true-rim midpoints, S0 fold midpoints.
Usage: t65_xsec.py <sector_out_dir> <png> <geom_t55> <geom_t62F> theta [theta ...]
"""
import os, sys
import numpy as np
sys.path.insert(0, '/data/gpfs/projects/punim2657/SfSpp/runs/20261102-0450_05be12c_t57-sweep')
import check_separation as cs
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

D, PNG, G55, G62 = sys.argv[1:5]
TH = [float(t) for t in sys.argv[5:]]
HALF = 0.3
z = np.load(os.path.join(D, 'j1_t62F_r1.0.npz'))
c, e1, e2 = z['frame_c'], z['frame_e1'], z['frame_e2']
n = np.cross(e1, e2)
V = z['V']
lab = np.load('/data/gpfs/projects/punim2657/SfSpp/runs/20261102-1144_638504b_t59-breakstop-stage0/out/labels/Juglet_Piece_1.npz')['vlab']
LC = {-1: '#777777', 0: '#bdbdbd', 1: '#3182bd', 2: '#e34a33', 3: '#31a354'}
LN = {-1: 'mixed', 0: 'wall', 1: 'roll', 2: 'fracture', 3: 'anomaly'}


def pts(geom, suf):
    p = cs.read_ply(os.path.join(geom, 'Juglet_Piece_1.' + suf))
    return np.stack([p[k] for k in 'xyz'], 1)


A = {'t55': (pts(G55, 'S0'), pts(G55, 'S1')), 't62F': (pts(G62, 'S0'), pts(G62, 'S1'))}
z55 = np.load(os.path.join(D, 'j1_t55_count.npz'))
fig, axes = plt.subplots(len(TH), 2, figsize=(14, 4.2 * len(TH)))
axes = np.atleast_2d(axes)
for i, th in enumerate(TH):
    t = np.radians(th)
    rdir = np.cos(t) * e1 + np.sin(t) * e2
    tdir = -np.sin(t) * e1 + np.cos(t) * e2

    def cut(X):
        Q = X - c
        m = (np.abs(Q @ tdir) < HALF) & (Q @ rdir > 0)
        return m, Q[m] @ rdir, Q[m] @ n

    for j, (arm, zz) in enumerate((('t55', z55), ('t62F', z))):
        ax = axes[i, j]
        m, r, h = cut(V)
        for k in (-1, 0, 1, 3, 2):
            mm = lab[m] == k
            if mm.any():
                ax.scatter(r[mm], h[mm], s=10, c=LC[k], label='mesh ' + LN[k], zorder=1)
        S0, S1 = A[arm]
        for X, col, nm, s in ((S1, '#fdae6b', 'S1 pts', 4), (S0, '#2171b5', 'S0 pts', 4)):
            _, rr, hh = cut(X)
            ax.scatter(rr, hh, s=s, c=col, label=nm, zorder=2, alpha=0.8)
        _, rr, hh = cut(zz['midr'])
        ax.scatter(rr, hh, s=40, marker='x', c='#8b0000', label='true rim (t59)', zorder=4)
        _, rr, hh = cut(zz['mid'])
        ax.scatter(rr, hh, s=60, marker='o', facecolors='none', edgecolors='k', lw=1.4,
                   label='S0 boundary', zorder=5)
        ax.set_aspect('equal')
        x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
        ax.set_xticks(np.arange(np.floor(x0), np.ceil(x1) + 1, 1.0), minor=True)
        ax.set_yticks(np.arange(np.floor(y0), np.ceil(y1) + 1, 1.0), minor=True)
        ax.grid(which='minor', lw=0.3, alpha=0.6)
        ax.set_title('J1 %s  cut at ring angle %g deg (slab +-%.1f mm)' % (arm, th, HALF), fontsize=9)
        ax.set_xlabel('radial mm from ring centre'); ax.set_ylabel('mm along ring normal')
        if i == 0:
            ax.legend(fontsize=6, loc='best', ncol=2)
plt.tight_layout()
plt.savefig(PNG, dpi=110)
print(PNG)
