#!/usr/bin/env python3
# ticket 47 -- the conservator's eye picture: Juglet Piece 2 before/after.
# before = the shipped 2026-09-25 vertex dump (archived this run); after = the new
# cc_mesh_to_pcd.sh draw installed at Dataset/Point/Juglet.  Both panels sit over the
# piece own mesh outline (mesh vertices, light grey), on the two largest-extent axes,
# in mm, equal aspect; the caption carries the counts and the pts/mm^2 the ticket asks
# for.  One figure, out/figures/j2_before_after.png.
import argparse, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SEED = 47


def read_obj(path):
    verts, faces = [], []
    with open(path, 'r', errors='replace') as f:
        for line in f:
            if line.startswith('v '):
                p = line.split()
                verts.append((float(p[1]), float(p[2]), float(p[3])))
            elif line.startswith('f '):
                idx = []
                for tok in line.split()[1:]:
                    i = int(tok.split('/')[0])
                    idx.append(i - 1 if i > 0 else len(verts) + i)
                faces.append(idx[:3])
    return np.asarray(verts, dtype=np.float64), faces


def mesh_area(v, faces):
    total = 0.0
    for f in faces:
        a, b, c = v[f[0]], v[f[1]], v[f[2]]
        total += 0.5 * float(np.linalg.norm(np.cross(b - a, c - a)))
    return total


def load_pcd_points(path, cap=None):
    pts = []
    in_data = False
    with open(path, 'r', errors='replace') as f:
        for line in f:
            if not in_data:
                if line.startswith('DATA'):
                    in_data = True
                continue
            parts = line.split()
            if len(parts) < 3:
                continue
            try:
                pts.append((float(parts[0]), float(parts[1]), float(parts[2])))
            except ValueError:
                continue
            if cap and len(pts) >= cap:
                break
    return np.asarray(pts, dtype=np.float64)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mesh', required=True)
    ap.add_argument('--before', required=True)
    ap.add_argument('--after', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--runid', default='')
    ap.add_argument('--subsample', type=int, default=30000)
    args = ap.parse_args()

    v, faces = read_obj(args.mesh)
    area = mesh_area(v, faces)

    old = load_pcd_points(args.before)
    new_full = load_pcd_points(args.after)
    rng = np.random.default_rng(SEED)
    if len(new_full) > args.subsample:
        new = new_full[rng.choice(len(new_full), args.subsample, replace=False)]
    else:
        new = new_full

    ext = v.max(axis=0) - v.min(axis=0)
    order = np.argsort(ext)[::-1]
    ax0, ax1 = int(order[0]), int(order[1])
    labels = ['x (mm)', 'y (mm)', 'z (mm)']

    dens_old = len(old) / area
    dens_new = len(new_full) / area

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 6.2), dpi=150)
    fig.suptitle('Juglet Piece 2 input cloud: before / after  --  ' + args.runid,
                 fontsize=11)

    allpts = [old, new]
    titles = [
        'BEFORE: shipped 2026-09-25 vertex dump\n' + str(len(old)) + ' points  =  every mesh vertex, nothing sampled\n'
        + format(dens_old, '.2f') + ' pts/mm^2',
        'AFTER: cc_mesh_to_pcd.sh draw (this run)\n' + str(len(new_full)) + ' points kept of ~1,000,000 sampled (SOR ~84%)\n'
        + format(dens_new, '.2f') + ' pts/mm^2   (' + str(args.subsample) + ' shown)',
    ]
    for ax, pts, title in zip(axes, allpts, titles):
        ax.scatter(v[:, ax0], v[:, ax1], s=0.5, c='0.82', linewidths=0, label='mesh outline')
        ax.scatter(pts[:, ax0], pts[:, ax1], s=0.5, c='tab:red', linewidths=0, label='cloud')
        ax.set_xlabel(labels[ax0])
        ax.set_ylabel(labels[ax1])
        ax.set_aspect('equal', adjustable='box')
        ax.set_title(title, fontsize=9)
        ax.grid(True, linewidth=0.3, alpha=0.5)
        ax.legend(loc='upper right', fontsize=7, markerscale=8, framealpha=0.7)

    cap = ('mesh ' + args.mesh + '  |  mesh area ' + format(area, '.1f') + ' mm^2, '
           + str(len(v)) + ' vertices  |  same mm frame, same axes on both panels')
    fig.text(0.5, 0.015, cap, ha='center', fontsize=7.5, family='monospace')
    fig.tight_layout(rect=(0, 0.03, 1, 0.97))
    fig.savefig(args.out, bbox_inches='tight')
    print('[figure47] wrote ' + args.out)
    print('[figure47] before ' + str(len(old)) + ' pts (' + format(dens_old, '.2f')
          + ' pts/mm^2), after ' + str(len(new_full)) + ' pts (' + format(dens_new, '.2f') + ' pts/mm^2)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
