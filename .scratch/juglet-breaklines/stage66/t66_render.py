#!/usr/bin/env python3
"""Ticket 66 Part D: J1 Breakline_0 dots over the shaded mesh, before (t65 control) vs after (t66 arm U).

Camera: the t65 common ring frame (t62F J1 S0 fold midpoints, stored by t65_sector.py in
<t65>/out/sector/j1_C.npz), orthographic along its normal, identical for every panel.  Drawn: the
Surface_0-sheet and break faces (t59 labels, t65_render65 colours) Lambert-shaded by the view
direction and painted far-to-near; the t59 label rim (label 2 = fracture; S0 side dark red, far side
faint orange); the Breakline_0 dots banded by distance to the nearest S0-side rim midpoint
(<= 1 mm / 1-2 mm / > 2 mm, the t65 stage-1 bands).  The bands are a drawing aid, not a score:
the scores are check_separation.py (t57) and t65_sector / t65_stage1, run separately.
Usage: t66_render.py <before.Bl0> <after.Bl0> <j1_C.npz> <out_dir> <runid>
"""
import os, sys
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.colors import to_rgb
from scipy.spatial import cKDTree
sys.path.insert(0, '/data/gpfs/projects/punim2657/SfSpp/runs/20261102-0450_05be12c_t57-sweep')
import check_separation as cs

BEFORE, AFTER, NPZ, OUTD, RUNID = sys.argv[1:6]
LABC = {0: '#e3e3e3', 1: '#c6dbef', 2: '#f6c9c4', 3: '#d9f0d3'}
BANDS = ((0.0, 1.0, '#1a9850', '<= 1 mm from rim'), (1.0, 2.0, '#fdae61', '1-2 mm'),
         (2.0, np.inf, '#d73027', '> 2 mm'))


def xyz(path):
    p = cs.read_pcd(path)
    if isinstance(p, dict):
        return np.stack([np.asarray(p[k], float) for k in 'xyz'], 1)
    if isinstance(p, tuple):
        p = p[0]
    return np.asarray(p, float)[:, :3]


def P2(X, c, e1, e2):
    X = np.asarray(X).reshape(-1, 3)
    return np.stack([(X - c) @ e1, (X - c) @ e2], 1)


z = np.load(NPZ)
c, e1, e2 = z['frame_c'], z['frame_e1'], z['frame_e2']
nv = np.cross(e1, e2); nv /= np.linalg.norm(nv)
V, F, lab, sheet, s0 = z['V'], z['F'], z['labels'], z['sheet'], int(z['s0sheet'])
keep = (sheet == s0) | (lab == 2)
Fk = F[keep]; lk = lab[keep]
tri3 = V[Fk]
fn = np.cross(tri3[:, 1] - tri3[:, 0], tri3[:, 2] - tri3[:, 0])
fn /= np.maximum(np.linalg.norm(fn, axis=1, keepdims=True), 1e-12)
shade = 0.45 + 0.55 * np.abs(fn @ nv)
depth = (tri3.mean(1) - c) @ nv
order = np.argsort(depth)
tri2 = P2(tri3, c, e1, e2).reshape(-1, 3, 2)[order]
cols = np.array([to_rgb(LABC[int(l)]) for l in lk])[order] * shade[order, None]
midr = z['midr']; on0 = z['rside'] == s0
r2 = P2(midr, c, e1, e2)
rim0 = cKDTree(midr[on0])
allp = P2(V[np.unique(Fk)], c, e1, e2)
lo, hi = allp.min(0) - 1.5, allp.max(0) + 1.5


def panel(ax, path, title):
    ax.add_collection(PolyCollection(tri2, facecolors=np.clip(cols, 0, 1), edgecolors='none', zorder=0))
    ax.scatter(r2[~on0, 0], r2[~on0, 1], s=0.6, c='#fd8d3c', alpha=0.35, zorder=1,
               label='true break-edge rim, far side (t59 label 2)')
    ax.scatter(r2[on0, 0], r2[on0, 1], s=0.8, c='#67000d', zorder=2,
               label='true break-edge rim, Surface_0 side (t59 label 2)')
    B = xyz(path)
    d = rim0.query(B)[0]
    b2 = P2(B, c, e1, e2)
    for lo_, hi_, col, lbl in BANDS:
        m = (d > lo_) & (d <= hi_) if lo_ > 0 else d <= hi_
        ax.scatter(b2[m, 0], b2[m, 1], s=34, c=col, edgecolors='k', linewidths=0.5, zorder=4,
                   label='Breakline_0 dot, %s (%d)' % (lbl, m.sum()))
    ax.set_xlim(lo[0], hi[0]); ax.set_ylim(lo[1], hi[1]); ax.set_aspect('equal')
    ax.set_xticks(np.arange(np.floor(lo[0] / 5) * 5, hi[0] + 5, 5.0))
    ax.set_yticks(np.arange(np.floor(lo[1] / 5) * 5, hi[1] + 5, 5.0))
    ax.grid(lw=0.3, alpha=0.5); ax.tick_params(labelsize=7)
    ax.set_title('%s\nBreakline_0: %d dots; median %.2f mm, max %.2f mm to the Surface_0-side rim'
                 % (title, len(B), float(np.median(d)), float(d.max())), fontsize=11)
    ax.set_xlabel('mm (ring plane)'); ax.set_ylabel('mm (ring plane)')
    ax.legend(loc='lower left', fontsize=8, markerscale=1.2, framealpha=0.85)
    return len(B), d


FOOT = ('Juglet piece 1 (read as the conservator\'s "J01"), same orthographic camera in every panel: looking along '
        'the normal of the break-edge ring plane (t62 frame, as t65).  Faces: grey wall, blue roll, pink break face '
        '(t59 labels; Surface_0 sheet and break face only), shaded by view angle; grid 5 mm.')
os.makedirs(OUTD, exist_ok=True)
names = (('before', BEFORE, 'BEFORE - t65 control (SFS_ADMIT_SIGN off), run 20261103-0709_a47d478_t65-admitsign'),
         ('after', AFTER, 'AFTER - t66 arm U (new default, SFS_ADMIT_SIGN unset = on), run %s' % RUNID))
for tag, path, title in names:
    fig, ax = plt.subplots(1, 1, figsize=(11, 11))
    n, d = panel(ax, path, title)
    fig.text(0.5, 0.01, FOOT, ha='center', fontsize=7, wrap=True)
    plt.tight_layout(rect=[0, 0.03, 1, 1])
    p = os.path.join(OUTD, 'j1_bl0_%s.png' % tag)
    plt.savefig(p, dpi=110); plt.close(fig)
    print(p, 'dots', n, 'le1', int((d <= 1).sum()), 'b12', int(((d > 1) & (d <= 2)).sum()), 'gt2', int((d > 2).sum()),
          'med', round(float(np.median(d)), 3), 'max', round(float(d.max()), 3))
fig, axes = plt.subplots(1, 2, figsize=(22, 11.5))
for ax, (tag, path, title) in zip(axes, names):
    panel(ax, path, title)
fig.text(0.5, 0.01, FOOT, ha='center', fontsize=9)
plt.tight_layout(rect=[0, 0.025, 1, 1])
p = os.path.join(OUTD, 'j1_bl0_before_after.png')
plt.savefig(p, dpi=100)
print(p)
