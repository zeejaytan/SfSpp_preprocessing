#!/usr/bin/env python3
"""Criterion-2 support: does each piece's Breakline_0 ride Surface_0?

The edge stage derives Breakline_0 from the Surface_0 file alone
(edgeline_extraction_headless.cpp:3517-3520, :3702, :3718) and Surface_0 is
whatever the [PAPER-234] classify vote put in slot 0 (:2045/:2047 swapped/kept).
That chain is in the source. This script adds the geometric check that the
exported artefact is consistent with it: distance from every Breakline_0 point
to the nearest Surface_0 point against the nearest Surface_1 point.

usage: check_ride.py <geom dir>      (files: <piece>.S0.xyz, <piece>.S1.xyz, <piece>.Bl0.pcd)
"""
import glob
import os
import sys

import numpy as np
from scipy.spatial import cKDTree

PCD_SKIP = ("#", "VERSION", "FIELDS", "SIZE", "TYPE", "COUNT", "WIDTH",
            "HEIGHT", "VIEWPOINT", "POINTS", "DATA")


def read_pcd(path):
    lines = open(path).read().splitlines()
    segs = []
    for ln in lines[2:]:
        if ln.startswith("#"):
            a = ln[1:].split()
            if len(a) >= 3:
                segs.append((int(a[0]) - 1, int(a[1]) - 1))
        else:
            break
    rows = []
    for ln in lines:
        s = ln.split()
        if len(s) >= 6 and not ln.startswith(PCD_SKIP):
            try:
                rows.append([float(x) for x in s[:6]])
            except ValueError:
                pass
    return segs, np.asarray(rows)


def read_xyz(path):
    arr = np.loadtxt(path, dtype=float)
    if arr.ndim == 1:
        arr = arr[None, :]
    return arr


def main():
    d = sys.argv[1]
    print("piece\tbl0_dots\tbl0_segments\ts0_pts\ts1_pts\tmed_d0_mm\tmed_d1_mm\tfrac_d0<1mm\tfrac_d1<1mm\tverdict")
    for bl in sorted(glob.glob(os.path.join(d, "*.Bl0.pcd"))):
        piece = os.path.basename(bl)[:-8]
        s0p = os.path.join(d, piece + ".S0.xyz")
        s1p = os.path.join(d, piece + ".S1.xyz")
        if not (os.path.exists(s0p) and os.path.exists(s1p)):
            print("%s\t-\t-\t-\t-\t-\t-\t-\t-\tMISSING_SURFACE" % piece)
            continue
        segs, b = read_pcd(bl)
        S0, S1 = read_xyz(s0p), read_xyz(s1p)
        b = b[:, :3]
        d0, _ = cKDTree(S0[:, :3]).query(b)
        d1, _ = cKDTree(S1[:, :3]).query(b)
        med0, med1 = float(np.median(d0)), float(np.median(d1))
        f0, f1 = float((d0 < 1.0).mean()), float((d1 < 1.0).mean())
        verdict = "rides_S0" if med0 < med1 else "rides_S1"
        print("%s\t%d\t%d\t%d\t%d\t%.3f\t%.3f\t%.3f\t%.3f\t%s"
              % (piece, b.shape[0], len(segs), S0.shape[0], S1.shape[0], med0, med1, f0, f1, verdict))


if __name__ == "__main__":
    main()
