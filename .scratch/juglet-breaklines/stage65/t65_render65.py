#!/usr/bin/env python3
"""Ticket 65 stage 3 figures (read-only): J1 control/treatment boundary, and J7's fold islands.

Figure 1 (J1): orthographic view along the normal of the common t62F ring frame (the frame
t65_sector.py stores in out/sector/j1_<arm>.npz), identical camera for both panels.  Drawn: Surface_0-
sheet and fracture faces in t59 label colours, the t59 label rim (S0 side dark red, S1 side faint
orange), and Surface_0 boundary (fold) midpoints banded by distance to the S0-side rim
(<= 1 mm / 1-2 mm / > 2 mm, the stage-1 bands).  The control panel also shows, in magenta, the
Surface_0 points the switch removed (control S0 rows with no exact match in treatment S0).
Figure 2 (J7): same drawing for J7 (identical in both arms), frame = circle fit of J7's S0-side
rim, with fold midpoints coloured by the mesh sheet they sit on and the fold-island components
(t65_stage1.piece_arm) ringed; one zoom inset per island component, 1 mm grid.
Usage: t65_render65.py <run_dir> <out_dir>
"""
import os, sys, tempfile
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from scipy.spatial import cKDTree

RUN, OUTD = sys.argv[1], sys.argv[2]
WORK = os.path.dirname(os.path.abspath(__file__))
_argv = sys.argv
sys.argv = [_argv[0], tempfile.mkdtemp()]
sys.path.insert(0, WORK)
import t65_sector as ts
import t65_stage1 as t1
sys.argv = _argv
cs = ts.cs
LABC = {0: '#e3e3e3', 1: '#c6dbef', 2: '#f6c9c4', 3: '#d9f0d3'}
BANDS = ((0.0, 1.0, '#1a9850', '<= 1 mm from rim'), (1.0, 2.0, '#fdae61', '1-2 mm'),
         (2.0, np.inf, '#d73027', '> 2 mm'))


def P2(X, c, e1, e2):
    X = np.asarray(X).reshape(-1, 3)
    return np.stack([(X - c) @ e1, (X - c) @ e2], 1)


def gate_row(arm, piece):
    with open(os.path.join(RUN, 'out', 'gate3_%s.tsv' % arm)) as fh:
        h = fh.readline().rstrip('\n').split('\t')
        for ln in fh:
            r = dict(zip(h, ln.rstrip('\n').split('\t')))
            if r['piece'] == piece:
                return r


def base(ax, V, F, lab, sheet, s0, frame):
    c, e1, e2 = frame
    keep = (sheet == s0) | (lab == 2)
    tri = P2(V[F[keep]], c, e1, e2).reshape(-1, 3, 2)
    ax.add_collection(PolyCollection(tri, facecolors=[LABC[int(l)] for l in lab[keep]],
                                     edgecolors='none', zorder=0))


def rim(ax, midr, on0, frame):
    r = P2(midr, *frame)
    ax.scatter(r[~on0, 0], r[~on0, 1], s=0.6, c='#fd8d3c', alpha=0.35, zorder=1,
               label='break-edge rim, far side (t59)')
    ax.scatter(r[on0, 0], r[on0, 1], s=0.8, c='#67000d', zorder=2, label='break-edge rim, Surface_0 side (t59)')


def grid(ax, step):
    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
    ax.set_xticks(np.arange(np.floor(x0 / step) * step, x1 + step, step))
    ax.set_yticks(np.arange(np.floor(y0 / step) * step, y1 + step, step))
    ax.grid(lw=0.3, alpha=0.5)
    ax.tick_params(labelsize=7)


def fig_j1():
    zs = {a: np.load(os.path.join(RUN, 'out', 'sector', 'j1_%s.npz' % a)) for a in ('C', 'T')}
    pc = cs.read_ply(os.path.join(RUN, 'outC', 'geom', 'Juglet_Piece_1.S0'))
    pt = cs.read_ply(os.path.join(RUN, 'outT', 'geom', 'Juglet_Piece_1.S0'))
    XC = np.stack([pc[k] for k in 'xyz'], 1); XT = np.stack([pt[k] for k in 'xyz'], 1)
    dropped = XC[cKDTree(XT).query(XC)[0] > 0]
    z0 = zs['C']
    frame = (z0['frame_c'], z0['frame_e1'], z0['frame_e2'])
    V, F, lab, sheet, s0 = z0['V'], z0['F'], z0['labels'], z0['sheet'], int(z0['s0sheet'])
    on0 = z0['rside'] == s0
    allp = np.vstack([P2(V[np.unique(F[(sheet == s0) | (lab == 2)])], *frame)])
    lo, hi = allp.min(0) - 1.5, allp.max(0) + 1.5
    fig, axes = plt.subplots(1, 2, figsize=(20, 10.6))
    names = {'C': 'CONTROL (switch off = t62 radius-1.0 lane)', 'T': 'TREATMENT (SFS_ADMIT_SIGN=1)'}
    for ax, a in zip(axes, ('C', 'T')):
        z = zs[a]
        base(ax, V, F, lab, sheet, s0, frame)
        rim(ax, z['midr'], on0, frame)
        if a == 'C':
            dp = P2(dropped, *frame)
            ax.scatter(dp[:, 0], dp[:, 1], s=2.0, c='#c51b8a', alpha=0.55, zorder=3,
                       label='Surface_0 points the switch removes (%d, far-face spill)' % len(dropped))
        fm = P2(z['mid'], *frame); d = z['d_f2r0']
        for lo_, hi_, col, lbl in BANDS:
            m = (d > lo_) & (d <= hi_) if lo_ > 0 else d <= hi_
            ax.scatter(fm[m, 0], fm[m, 1], s=5, c=col, zorder=4,
                       label='Surface_0 boundary, %s (%d)' % (lbl, m.sum()))
        g = gate_row(a, 'Juglet_Piece_1')
        ax.set_xlim(lo[0], hi[0]); ax.set_ylim(lo[1], hi[1]); ax.set_aspect('equal')
        grid(ax, 5.0)
        ax.set_title('J1 %s\nboundary > 2 mm off rim %.1f %%   boundary within 1 mm of rim %.1f %%   '
                     'ring covered %s of 360 deg' % (names[a], 100 * float(g['fold_off2']),
                                                     100 * float(g['f2r_le1']), g['ring_cov_deg5'].split('.')[0]),
                     fontsize=11)
        ax.set_xlabel('mm (ring plane)'); ax.set_ylabel('mm (ring plane)')
        ax.legend(loc='lower left', fontsize=8, markerscale=3, framealpha=0.85)
    fig.text(0.5, 0.01, 'Juglet piece 1, same orthographic camera both panels: looking along the normal of the '
             'plane of the break-edge ring (t62 frame); grid 5 mm.  Faces: grey wall, blue roll, pink break face '
             '(t59 labels; Surface_0 sheet and break face only).  run 20261103-0709_a47d478_t65-admitsign',
             ha='center', fontsize=9)
    plt.tight_layout(rect=[0, 0.025, 1, 1])
    p = os.path.join(OUTD, 'admitsign_j1_before_after.png')
    plt.savefig(p, dpi=110)
    print(p, 'dropped', len(dropped))


def fig_j7():
    P = 'Juglet_Piece_7'
    z = ts.load_piece(P)
    sh = ts.sheets(z['V'], z['F'], z['labels'])
    geom = os.path.join(RUN, 'outT', 'geom')
    row, dump = t1.piece_arm(P, geom, z, sh)
    V, F, lab = z['V'], z['F'], z['labels']
    sheet = sh[0]; s0 = int(dump['s0s'])
    on0 = dump['on0']
    c_, R, (e1, e2, _n), _ = cs.circle_fit(dump['midr'][on0])
    frame = (c_, e1, e2)
    p0 = cs.read_ply(os.path.join(geom, P + '.S0'))
    S0 = np.stack([p0[k] for k in 'xyz'], 1)
    covA = cKDTree(S0).query(V)[0] <= cs.COV_TOL
    isl = dump['fold_island']; fcomp = dump['fcomp']; fsh = dump['fsh']
    comps = [k for k in np.unique(fcomp[isl])]
    n_in = len(comps)
    fig = plt.figure(figsize=(20, 11))
    ax = fig.add_axes([0.03, 0.06, 0.55, 0.88])
    base(ax, V, F, lab, sheet, s0, frame)
    # Surface_0-sheet faces that Surface_0 does not cover: holes in the surface show white-outlined
    unc = (sheet == s0) & (covA[F].sum(1) < 2)
    tri = P2(V[F[unc]], *frame).reshape(-1, 3, 2)
    ax.add_collection(PolyCollection(tri, facecolors='#ffffff', edgecolors='#636363', linewidths=0.2, zorder=0.5))
    rim(ax, dump['midr'], on0, frame)
    fm = P2(dump['mid'], *frame)
    ax.scatter(fm[~isl, 0], fm[~isl, 1], s=3, c='#2171b5', zorder=3, label='Surface_0 boundary, main loop')
    shname = {s0: 'own (Surface_0) sheet', 1 - s0: 'FAR sheet', 2: 'break face'}
    for sv, col in ((s0, '#d73027'), (1 - s0, '#000000'), (2, '#ff7f00')):
        m = isl & (fsh == sv)
        if m.any():
            ax.scatter(fm[m, 0], fm[m, 1], s=9, c=col, zorder=4,
                       label='island boundary on %s (%d)' % (shname[sv], m.sum()))
    m = isl & ~np.isin(fsh, [s0, 1 - s0, 2])
    if m.any():
        ax.scatter(fm[m, 0], fm[m, 1], s=9, c='#6a3d9a', zorder=4, label='island boundary, unresolved sheet (%d)' % m.sum())
    for k in comps:
        q = fm[fcomp == k]; cc = q.mean(0); rr = max(np.linalg.norm(q - cc, axis=1).max() + 1.0, 1.5)
        ax.add_patch(plt.Circle(cc, rr, fill=False, lw=1.0, ec='k', ls='--', zorder=5))
    ax.set_aspect('equal'); ax.autoscale_view(); grid(ax, 5.0)
    ax.legend(loc='lower left', fontsize=8, markerscale=2.5, framealpha=0.85)
    ax.set_title('Juglet piece 7 - fold islands (%d components, %d of %d boundary points = share %.4f), '
                 'dashed circles; white = Surface_0-sheet faces Surface_0 does not cover'
                 % (n_in, isl.sum(), len(isl), isl.mean()), fontsize=10)
    ax.set_xlabel('mm (plane of the Surface_0-side rim)'); ax.set_ylabel('mm')
    # zoom insets, one per island component (up to 4), 1 mm grid
    for j, k in enumerate(comps[:4]):
        a2 = fig.add_axes([0.62 + 0.19 * (j % 2), 0.53 - 0.45 * (j // 2), 0.17, 0.40])
        q = fm[fcomp == k]; cc = q.mean(0); rr = max(np.abs(q - cc).max() + 2.0, 3.0)
        base(a2, V, F, lab, sheet, s0, frame)
        a2.add_collection(PolyCollection(tri, facecolors='#ffffff', edgecolors='#636363', linewidths=0.3, zorder=0.5))
        rim(a2, dump['midr'], on0, frame)
        mk = fcomp == k
        for sv, col in ((s0, '#d73027'), (1 - s0, '#000000'), (2, '#ff7f00')):
            m = mk & (fsh == sv)
            a2.scatter(fm[m, 0], fm[m, 1], s=14, c=col, zorder=4)
        a2.set_xlim(cc[0] - rr, cc[0] + rr); a2.set_ylim(cc[1] - rr, cc[1] + rr); a2.set_aspect('equal')
        grid(a2, 1.0)
        dr = dump['d_f2r0'][mk]
        a2.set_title('island %d: %d pts, %.1f-%.1f mm from rim\nsheet: own %d / far %d / break %d'
                     % (j + 1, mk.sum(), dr.min(), dr.max(), (mk & (fsh == s0)).sum(),
                        (mk & (fsh == 1 - s0)).sum(), (mk & (fsh == 2)).sum()), fontsize=9)
    fig.text(0.5, 0.01, 'Orthographic view along the normal of the circle fitted to J7\'s Surface_0-side rim; '
             'main grid 5 mm, insets 1 mm.  Treatment arm (identical to control on J7).  '
             'run 20261103-0709_a47d478_t65-admitsign', ha='center', fontsize=9)
    p = os.path.join(OUTD, 'admitsign_j7_islands.png')
    plt.savefig(p, dpi=110)
    print(p, 'islands', n_in, 'pts', int(isl.sum()), 'share', round(float(isl.mean()), 4),
          'sheets own/far/break', int((isl & (fsh == s0)).sum()), int((isl & (fsh == 1 - s0)).sum()),
          int((isl & (fsh == 2)).sum()))


if __name__ == '__main__':
    os.makedirs(OUTD, exist_ok=True)
    fig_j1()
    fig_j7()
