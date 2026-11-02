#!/usr/bin/env python3
"""Ticket 65: ring-plane figure of J1 -- mesh faces by t59 label, true rim by side, S0 boundary.

View: orthographic, looking along the normal of the plane fitted to the t62F J1 S0 fold midpoints
(the scorer's own ring frame); axes are millimetres in that plane, equal aspect, grid every 1 mm in
the zoom panels.  Usage: t65_plot.py <sector_out_dir> <png_out> [arm ...]
"""
import os, sys
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

D = sys.argv[1]; OUTPNG = sys.argv[2]
ARMS = sys.argv[3:] or ['t55_count', 't62F_r1.0']
LABC = {0: '#d9d9d9', 1: '#9ecae1', 2: '#f2b3ac', 3: '#c7e9c0'}


def P2(X, c, e1, e2):
    X = X.reshape(-1, 3)
    return np.stack([(X - c) @ e1, (X - c) @ e2], 1)


def panel(ax, z, title, lim=None, grid=False):
    c, e1, e2 = z['frame_c'], z['frame_e1'], z['frame_e2']
    V, F, lab, sheet, s0 = z['V'], z['F'], z['labels'], z['sheet'], int(z['s0sheet'])
    # draw only S0-sheet faces + fracture so the far sheet does not hide the near one
    keep = (sheet == s0) | (lab == 2)
    tri = P2(V[F[keep]], c, e1, e2).reshape(-1, 3, 2)
    cols = [LABC[int(l)] for l in lab[keep]]
    ax.add_collection(PolyCollection(tri, facecolors=cols, edgecolors='none', alpha=0.9))
    mr = P2(z['midr'], c, e1, e2)
    on0 = z['rside'] == s0
    ax.scatter(mr[~on0, 0], mr[~on0, 1], s=1.0, c='#e6550d', alpha=0.5, label='true rim, far (S1) side')
    ax.scatter(mr[on0, 0], mr[on0, 1], s=2.0, c='#8b0000', label='true rim, S0 side')
    fm = P2(z['mid'], c, e1, e2)
    d = z['d_f2r0']
    sc = ax.scatter(fm[:, 0], fm[:, 1], s=3, c=np.clip(d, 0, 6), cmap='viridis', vmin=0, vmax=6,
                    label='S0 boundary (colour = mm to S0-side rim)')
    ax.set_aspect('equal')
    if lim:
        ax.set_xlim(lim[0]); ax.set_ylim(lim[1])
    else:
        ax.autoscale_view()
    if grid:
        x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
        ax.set_xticks(np.arange(np.floor(x0), np.ceil(x1) + 1, 1.0), minor=True)
        ax.set_yticks(np.arange(np.floor(y0), np.ceil(y1) + 1, 1.0), minor=True)
        ax.grid(which='minor', lw=0.3, alpha=0.5)
    ax.set_title(title, fontsize=9)
    ax.set_xlabel('mm (ring plane e1)'); ax.set_ylabel('mm (e2)')
    return sc


zs = [(a, np.load(os.path.join(D, 'j1_%s.npz' % a))) for a in ARMS]
fig, axes = plt.subplots(2, len(zs), figsize=(8 * len(zs), 15))
axes = np.atleast_2d(axes).reshape(2, len(zs))
for j, (a, z) in enumerate(zs):
    sc = panel(axes[0, j], z, 'J1 %s - whole piece, spokes every 10 deg (ring centre = +)' % a)
    ax = axes[0, j]
    R = 30
    for k in range(36):
        t = np.radians(10 * k)
        ax.plot([0, R * np.cos(t)], [0, R * np.sin(t)], lw=0.3, c='k', alpha=0.3)
        ax.text(R * np.cos(t), R * np.sin(t), str(10 * k), fontsize=6, ha='center')
    ax.plot([0], [0], 'k+', ms=10)
    ax.legend(loc='lower left', fontsize=7, markerscale=4)
    plt.colorbar(sc, ax=ax, shrink=0.6, label='S0 boundary to S0-side rim (mm)')
fig.text(0.5, 0.005, 'Orthographic view along the normal of the plane fitted to the t62F S0 boundary; '
         'grey = wall faces, blue = roll, pink = fracture, green = anomaly (t59 labels; S0 sheet + fracture only)',
         ha='center', fontsize=9)
# zoom row filled by caller-specified window: whole-piece bbox of S0 boundary in the worst sectors
for j, (a, z) in enumerate(zs):
    c, e1, e2 = z['frame_c'], z['frame_e1'], z['frame_e2']
    fm = P2(z['mid'], c, e1, e2)
    ang = np.mod(np.degrees(np.arctan2(fm[:, 1], fm[:, 0])), 360)
    sel = (ang < 60)
    if sel.sum() < 5:
        sel = np.ones(len(fm), bool)
    x0, y0 = fm[sel].min(0) - 2; x1, y1 = fm[sel].max(0) + 2
    panel(axes[1, j], z, 'J1 %s - zoom, sectors 000-060, 1 mm grid' % a, lim=((x0, x1), (y0, y1)), grid=True)
plt.tight_layout(rect=[0, 0.01, 1, 1])
plt.savefig(OUTPNG, dpi=130)
print(OUTPNG)
