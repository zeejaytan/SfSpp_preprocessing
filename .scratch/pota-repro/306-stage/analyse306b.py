#!/usr/bin/env python3
"""Ticket 306 Stage B diagnostics: what the union rule writes for Pot A.

Reads our written axis files and the authors' released ones, and reports, per
piece: how many lines each has, for every line of ours its angle to the nearest
released line (and the index), for every released line the angle to the nearest
line of ours (that is B3: the needed lines must be THERE, not merely close),
and the worst-surface Huber cost per point of each of our lines.

Usage: analyse306b.py --corp CORP --out RUNDIR/out --res RESULT.tsv
"""
import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sfs_axes.io_axes import direction_angle_deg, read_axes  # noqa: E402
from sfs_axes.io_surfaces import read_surfaces  # noqa: E402
from sfs_axes.potsac import _worst_surface_cost  # noqa: E402

PIECES = [1, 2, 3, 4, 5, 6, 7, 8]


def one(corp, sub, piece):
    surf = os.path.join(corp, "Surfaces")
    C0, C1 = read_surfaces(surf, "A", piece, truncate=False)
    ours_p = os.path.join(sub, "union", "Pot_A_Piece_%02d_Axis.xyz" % piece)
    rel_p = os.path.join(corp, "Axes", "Pot_A_Piece_%02d_Axis.xyz" % piece)
    ours = read_axes(ours_p) if os.path.exists(ours_p) else np.zeros((6, 0))
    rel = read_axes(rel_p) if os.path.exists(rel_p) else np.zeros((6, 0))
    rows = []
    for i in range(ours.shape[1]):
        ang = [direction_angle_deg(ours[0:3, i], rel[0:3, j])
               for j in range(rel.shape[1])]
        cost = _worst_surface_cost(ours[:, i], C0, C1)
        j = int(np.argmin(ang)) if ang else -1
        rows.append((piece, i, len(ang) and float(np.min(ang)) or float("nan"), j,
                     cost, ours.shape[1], rel.shape[1]))
    cover = []
    for j in range(rel.shape[1]):
        ang = [direction_angle_deg(rel[0:3, j], ours[0:3, i])
               for i in range(ours.shape[1])]
        cover.append((piece, j, float(np.min(ang)) if ang else float("nan"),
                      int(np.argmin(ang)) if ang else -1, ours.shape[1]))
    return rows, cover


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--res", required=True)
    a = ap.parse_args()
    allrows, allcover = [], []
    for p in PIECES:
        r, c = one(a.corp, a.out, p)
        allrows += r
        allcover += c
    with open(a.res, "w") as f:
        f.write("piece\tline\tang_to_nearest_released\tnearest_released_idx"
                "\tworst_surface_cost_pt\tK_ours\tK_released\n")
        for r in allrows:
            f.write("%d\t%d\t%.3f\t%d\t%.3f\t%d\t%d\n" % r)
    cov = a.res.replace(".tsv", "_cover.tsv")
    with open(cov, "w") as f:
        f.write("piece\treleased_line\tang_to_nearest_ours\tnearest_ours_idx"
                "\tK_ours\n")
        for r in allcover:
            f.write("%d\t%d\t%.3f\t%d\t%d\n" % r)
    print("piece  K_ours K_rel  our_lines:ang_to_released[min]   released:ang_to_ours[min]")
    for p in PIECES:
        rr = [r for r in allrows if r[0] == p]
        cc = [r for r in allcover if r[0] == p]
        ko = rr[0][5] if rr else 0
        kr = rr[0][6] if rr else 0
        print("%5d  %6d %5d  %s   %s"
              % (p, ko, kr,
                 " ".join("%.2f" % r[2] for r in rr) or "-",
                 " ".join("%.2f" % c[2] for c in cc) or "-"))


if __name__ == "__main__":
    main()
