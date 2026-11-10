#!/usr/bin/env python3
"""bl_vs_both.py - which face does each exported line's normal agree with?

Usage: bl_vs_both.py GEOMDIR LABEL
Per piece and line: frac(dot>0) and median dot of the line normal against the k=5 mean wall
normal of S0 and of S1 (the two faces of the piece).
"""
import sys
import numpy as np
from scipy.spatial import cKDTree


def read_ply(path):
    rows, n, hdr = [], None, True
    for ln in open(path, errors='ignore'):
        if hdr:
            s = ln.split()
            if s and s[0] == 'element' and s[1] == 'vertex':
                n = int(s[2])
            if s and s[0] == 'end_header':
                hdr = False
            continue
        if n is not None and len(rows) >= n:
            break
        p = ln.split()
        if len(p) >= 6:
            rows.append([float(x) for x in p[:6]])
    return np.array(rows)


def read_pcd(path):
    rows, started = [], False
    for ln in open(path, errors='ignore'):
        if not started:
            if ln.startswith('DATA'):
                started = True
            continue
        p = ln.split()
        if len(p) >= 7 and not p[0].startswith('#'):
            rows.append([float(x) for x in p[:7]])
    return np.array(rows)


def agree(line, wall, k=5):
    t = cKDTree(wall[:, :3])
    d, idx = t.query(line[:, :3], k=k)
    m = wall[:, 3:6][idx].mean(axis=1)
    m /= np.linalg.norm(m, axis=1, keepdims=True)
    dot = np.einsum('ij,ij->i', line[:, 3:6], m)
    return (dot > 0).mean(), float(np.median(dot))


def main():
    g, label = sys.argv[1], sys.argv[2]
    print('%s\tpiece\tline\tn\tS0_frac\tS0_med\tS1_frac\tS1_med' % label)
    for i in range(1, 10):
        w = {k: read_ply('%s/Juglet_Piece_%d.S%d' % (g, i, k)) for k in (0, 1)}
        for k in (0, 1):
            bl = read_pcd('%s/Juglet_Piece_%d.Bl%d' % (g, i, k))
            a0 = agree(bl, w[0])
            a1 = agree(bl, w[1])
            print('%s\t%d\tBl%d\t%d\t%.3f\t%+.3f\t%.3f\t%+.3f' % (label, i, k, len(bl), a0[0], a0[1], a1[0], a1[1]))


if __name__ == '__main__':
    main()
