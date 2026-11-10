#!/usr/bin/env python3
"""extract_pairs.py - ticket 328 bar 3: pull the nine touching-pair rows out of a diag326 GTPAIR table.

GTPAIR columns (diag326_pairs.cpp): y x gap_min n_1to1 n_d20 n_dot07 n_reject_kept
n_inl15_15deg inlierCalc score_at_gt overlap50 area overlap100 dot_closest linedot_closest
dot_med_d3 absdot_med_d3 n_d3 n_d3_dotneg
This script keeps the nine pairs that touch in the true pose.
"""
import sys

TOUCH = {(1, 2), (1, 4), (1, 8), (1, 9), (2, 5), (2, 9), (3, 5), (6, 7), (7, 9)}
COLS = ['gap_min', 'n_1to1', 'n_d20', 'n_dot07', 'n_reject_kept', 'n_inl15_15deg',
        'inlierCalc', 'score_at_gt', 'overlap50', 'area', 'overlap100', 'dot_closest',
        'linedot_closest', 'dot_med_d3', 'absdot_med_d3', 'n_d3', 'n_d3_dotneg']


def rows(path):
    out = {}
    for ln in open(path, errors='replace'):
        if not ln.startswith('GTPAIR'):
            continue
        p = ln.split()
        if not p[1].isdigit() or not p[2].isdigit():
            continue
        y, x = int(p[1]), int(p[2])
        v = dict(zip(COLS, p[3:3 + len(COLS)]))
        out[(y, x)] = v
        out[(x, y)] = v
    return out


def main():
    a, b = sys.argv[1], sys.argv[2]
    A, B = rows(a), rows(b)
    print('pair\t' + '\t'.join('%s_before\t%s_after' % (k, k) for k in
                                ('dot_med_d3', 'n_d3', 'n_d3_dotneg', 'n_inl15_15deg', 'gap_min', 'n_dot07')))
    for pr in sorted(TOUCH):
        va, vb = A.get(pr), B.get(pr)
        if va is None or vb is None:
            print('%d-%d\tMISSING' % pr)
            continue
        cells = []
        for k in ('dot_med_d3', 'n_d3', 'n_d3_dotneg', 'n_inl15_15deg', 'gap_min', 'n_dot07'):
            cells += [va[k], vb[k]]
        print('%d-%d\t%s' % (pr[0], pr[1], '\t'.join(cells)))


if __name__ == '__main__':
    main()
