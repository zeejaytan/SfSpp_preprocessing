#!/usr/bin/env python3
"""Ticket 65: six-view shaded render of J1 coloured by surface claim (read-only).

Orthographic views along +-e1, +-e2, +-n of the common t62F ring frame.  Face colour: claimed by
S0 only (blue), S1 only (orange), both (purple), neither (white); t59 fracture faces hatched darker;
true rim (S0 side) dark red, S0 boundary black.  Only faces facing the camera are drawn (painter's
order by depth), Lambert shading.
Usage: t65_render.py <sector_out_dir> <arm> <png>
"""
import os, sys
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

D, ARM, PNG = sys.argv[1:4]
z = np.load(os.path.join(D, 'j1_%s.npz' % ARM))
V, F, lab = z['V'], z['F'], z['labels']
covA, covB = z['covA'], z['covB']
c, e1, e2 = z['frame_c'], z['frame_e1'], z['frame_e2']
n = np.cross(e1, e2)
tri = V[F]
fn = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
fn /= np.maximum(np.linalg.norm(fn, axis=1, keepdims=True), 1e-12)
# orient outward
vol = np.einsum('ij,ij->i', tri[:, 0], np.cross(tri[:, 1], tri[:, 2])).sum()
if vol < 0:
    fn = -fn
a = covA[F].sum(1) >= 2
b = covB[F].sum(1) >= 2
base = np.ones((len(F), 3))
base[a & ~b] = (0.25, 0.45, 0.85)
base[b & ~a] = (0.98, 0.65, 0.35)
base[a & b] = (0.55, 0.25, 0.65)
fr = lab == 2
base[fr & ~a & ~b] = (0.95, 0.75, 0.72)
views = [('+n', n, e1), ('-n', -n, e1), ('+e1', e1, e2), ('-e1', -e1, e2), ('+e2', e2, e1), ('-e2', -e2, e1)]
fig, axes = plt.subplots(2, 3, figsize=(21, 14))
for ax, (nm, d, up) in zip(axes.ravel(), views):
    # camera looks along -d (from +d side)
    x = np.cross(up, d); x /= np.linalg.norm(x); y = np.cross(d, x)
    front = fn @ d > 0
    depth = (tri.mean(1) - c) @ d
    idx = np.where(front)[0]
    idx = idx[np.argsort(depth[idx])]
    shade = 0.35 + 0.65 * np.clip(fn[idx] @ d, 0, 1)
    col = base[idx] * shade[:, None]
    P = np.stack([(tri[idx] - c) @ x, (tri[idx] - c) @ y], -1)
    ax.add_collection(PolyCollection(P, facecolors=col, edgecolors='none'))
    # overlay rim and boundary points that are on visible side (depth test by nearest face is costly;
    # draw points whose outward offset is toward camera)
    for X, col_, s, lbl in ((z['midr'][z['rside'] == int(z['s0sheet'])], '#8b0000', 2, 'true rim S0 side'),
                            (z['mid'], 'k', 2, 'S0 boundary')):
        Q = X - c
        ax.scatter(Q @ x, Q @ y, s=s, c=col_, label=lbl, alpha=0.6)
    ax.set_aspect('equal'); ax.autoscale_view()
    ax.set_title('J1 %s view from %s (orthographic, mm)' % (ARM, nm), fontsize=10)
    ax.grid(lw=0.3, alpha=0.4)
axes[0, 0].legend(fontsize=8, markerscale=4)
fig.suptitle('Face colour: blue = Surface_0 only, orange = Surface_1 only, purple = both, white = neither, '
             'pink = t59 fracture unclaimed.  Points drawn without occlusion.', fontsize=11)
plt.tight_layout(rect=[0, 0, 1, 0.97])
plt.savefig(PNG, dpi=90)
print(PNG)
