#!/usr/bin/env python3
"""blcheck328.py - ticket 328 bar 2: does each exported line's normal agree with the wall it rides?

For every line point, the k=5 mean of the nearest wall points' own normals is the reference
(the same k=5 identity check that passed on job A), plus the single nearest point as a control.
Prints, per piece and per line: n, frac(dot>0), median dot, frac(|dot|>0.5).

Usage: blcheck328.py GEOMDIR LABEL     (GEOMDIR holds Juglet_Piece_<n>.{S0,S1,Bl0,Bl1})
"""
import sys
import numpy as np
from scipy.spatial import cKDTree


def read_ply(path):
    rows = []
    n = None
    hdr = True
    for ln in open(path, errors='ignore'):
        if hdr:
            s = ln.split()
            if s and s[0] == 'element' and s[1] == 'vertex':
                n = int(s[2])
            if s and s[0] == 'end_header':
                hdr = False
            continue
        if len(rows) >= (n or 10 ** 9):
            break
        p = ln.split()
        if len(p) >= 6:
            rows.append([float(x) for x in p[:6]])
    return np.array(rows)


def read_pcd(path):
    rows = []
    started = False
    for ln in open(path, errors='ignore'):
        if not started:
            if ln.startswith('DATA'):
                started = True
            continue
        p = ln.split()
        if len(p) >= 7 and not p[0].startswith('#'):
            rows.append([float(x) for x in p[:7]])
    return np.array(rows)


def cmp(line, wall, k=5):
    t = cKDTree(wall[:, :3])
    d, idx = t.query(line[:, :3], k=k)
    wn = wall[:, 3:6][idx]                      # (n,k,3)
    ln_ = line[:, 3:6]
    dot1 = np.einsum('ij,ij->i', ln_, wn[:, 0, :])
    m = wn.mean(axis=1)
    m /= np.linalg.norm(m, axis=1, keepdims=True)
    dot5 = np.einsum('ij,ij->i', ln_, m)
    return dot1, dot5


def main():
    g, label = sys.argv[1], sys.argv[2]
    print('%s\tpiece\tline\tn\tfrac_pos\tmed_dot\tfrac_absdot_gt05\tfrac_pos_k1\tmed_dot_k1' % label)
    for i in range(1, 10):
        walls = {k: read_ply('%s/Juglet_Piece_%d.S%d' % (g, i, k)) for k in (0, 1)}
        for k in (0, 1):
            bl = read_pcd('%s/Juglet_Piece_%d.Bl%d' % (g, i, k))
            if len(bl) == 0:
                print('%s\t%d\tBl%d\t0\t-\t-\t-\t-\t-' % (label, i, k))
                continue
            d1, d5 = cmp(bl, walls[k])
            print('%s\t%d\tBl%d\t%d\t%.3f\t%+.3f\t%.3f\t%.3f\t%+.3f' % (
                label, i, k, len(bl), (d5 > 0).mean(), np.median(d5),
                (np.abs(d5) > 0.5).mean(), (d1 > 0).mean(), np.median(d1)))


if __name__ == '__main__':
    main()
