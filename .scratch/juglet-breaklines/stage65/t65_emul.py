#!/usr/bin/env python3
"""Ticket 65 stage 2 falsification: emulate an admission side rule offline on frozen surfaces.

Each written surface is [admitted block] + [growth cluster] (t65_admit.py checked the split on all
nine pieces in both arms).  Rule emulated: an admitted point is kept only when its normal agrees
with the normal of the nearest growth-cluster point of the same surface (dot > 0).  Cluster rows are
kept untouched.  Writes <out>/<arm>/<P>.{S0,S1} (ASCII PLY x y z nx ny nz) and links Bl0/Bl1 from the
source bundle (the dots column therefore still reads the source run's edgelines).
Usage: t65_emul.py <out_dir> arm=geom_dir=pieces_dir [...]
"""
import os, sys
import numpy as np
from scipy.spatial import cKDTree

WORK = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WORK)
import t65_admit as ta
cs = ta.cs


def write_ply(path, X, N):
    with open(path, 'w') as fh:
        fh.write('ply\nformat ascii 1.0\ncomment t65 emulation\nelement vertex %d\n' % len(X))
        for p in ('x', 'y', 'z', 'nx', 'ny', 'nz'):
            fh.write('property float %s\n' % p)
        fh.write('end_header\n')
        np.savetxt(fh, np.hstack([X, N]), fmt='%.6f')


def main():
    out = sys.argv[1]
    for spec in sys.argv[2:]:
        arm, geom, pieces = spec.split('=', 2)
        od = os.path.join(out, arm)
        os.makedirs(od, exist_ok=True)
        with open(os.path.join(od, 'emul_counts.tsv'), 'w') as fh:
            fh.write('piece\tsurface\tn_in\tn_adm\tn_cl\tadm_kept\tadm_dropped\tn_out\tdup_adm_dot_med\n')
            for i in range(1, 10):
                P = 'Juglet_Piece_%d' % i
                fin, cls, swapped = ta.parse(os.path.join(pieces, P, 'mesh.log'))
                for s, suf in ((0, 'S0'), (1, 'S1')):
                    p = cs.read_ply(os.path.join(geom, P + '.' + suf))
                    X = np.stack([p[c] for c in 'xyz'], 1)
                    N = np.stack([p[c] for c in ('nx', 'ny', 'nz')], 1)
                    n_adm = fin[s][0]
                    Xa, Na, Xc, Nc = X[:n_adm], N[:n_adm], X[n_adm:], N[n_adm:]
                    d, j = cKDTree(Xc).query(Xa)
                    dot = (Na * Nc[j]).sum(1)
                    # the two blocks are written with independent normal signs on some surfaces;
                    # rows present in both (distance 0) fix the relative sign
                    dupdot = float(np.median(dot[d == 0])) if (d == 0).any() else float('nan')
                    sgn = -1.0 if dupdot < 0 else 1.0
                    keep = sgn * dot > 0
                    Xo = np.vstack([Xa[keep], Xc]); No = np.vstack([Na[keep], Nc])
                    write_ply(os.path.join(od, P + '.' + suf), Xo, No)
                    fh.write('%s\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%.4f\n' % (
                        P, s, len(X), n_adm, len(Xc), int(keep.sum()), int((~keep).sum()), len(Xo), dupdot))
                for b in ('Bl0', 'Bl1'):
                    src = os.path.join(geom, P + '.' + b)
                    dst = os.path.join(od, P + '.' + b)
                    if os.path.isfile(src) and not os.path.lexists(dst):
                        os.symlink(src, dst)
                ta.ts.log('%s %s written' % (arm, P))


if __name__ == '__main__':
    main()
