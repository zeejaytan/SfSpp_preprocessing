#!/usr/bin/env python3
"""Ticket 331 -- axis direction agreement between arms and the answer key, in degrees.

Reads each arm's Juglet_Piece_<i>_Axis.xyz (one line: px py pz dx dy dz) and the answer key's
Juglet_Piece_<i>_Axis.xyz (same layout, scaled by Part A with the direction unchanged), and prints
the unsigned angle between the direction vectors (sign folded, as a line has no orientation).
"""
import argparse
import math
import os

ARMS = ['ctl', 'large', 'rad3']


def read_axis(path):
    with open(path) as fh:
        for line in fh:
            f = line.split()
            if len(f) >= 6:
                return [float(x) for x in f[:6]]
    raise SystemExit('no axis line in ' + path)


def unit(v):
    n = math.sqrt(sum(x * x for x in v))
    return [x / n for x in v]


def ang(a, b):
    a, b = unit(a), unit(b)
    c = sum(x * y for x, y in zip(a, b))
    c = max(-1.0, min(1.0, abs(c)))
    return math.degrees(math.acos(c))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--arms', required=True, help='RUN dir (axes_<tag>/ subdirs inside)')
    ap.add_argument('--key', required=True, help='key dir (Juglet_Piece_<i>_Axis.xyz)')
    ap.add_argument('--out', default='')
    a = ap.parse_args()
    rows = []
    hdr = ['piece'] + ['%s_vs_gt' % x for x in ARMS] + ['large_vs_ctl', 'rad3_vs_large']
    print('\t'.join(hdr))
    rows.append(hdr)
    for i in range(1, 10):
        name = 'Juglet_Piece_%d_Axis.xyz' % i
        d = {}
        for arm in ARMS:
            p = os.path.join(a.arms, 'axes_' + arm, name)
            d[arm] = read_axis(p)[3:6] if os.path.exists(p) else None
        gt = read_axis(os.path.join(a.key, name))[3:6]
        def f(x):
            return '%.3f' % x if x is not None else ''
        cols = ['%d' % i]
        for arm in ARMS:
            cols.append(f(ang(d[arm], gt)) if d[arm] else '')
        cols.append(f(ang(d['large'], d['ctl'])) if (d['large'] and d['ctl']) else '')
        cols.append(f(ang(d['rad3'], d['large'])) if (d['rad3'] and d['large']) else '')
        print('\t'.join(cols))
        rows.append(cols)
    if a.out:
        with open(a.out, 'w') as fh:
            for r in rows:
                fh.write('\t'.join(r) + '\n')


if __name__ == '__main__':
    main()
