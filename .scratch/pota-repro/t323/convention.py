#!/usr/bin/env python3
"""Ticket 323: which way do the pose files map a piece's own axis into the assembled frame?

For a set of pieces, take each piece's axis direction in its own (scan) frame and its 4x4 pose; map the
direction with R (a' = R a) and with R^T (a' = R^T a). Under the right convention every piece of one
vessel shares one axis, so the pairwise angles between mapped axes are small. Prints median / max
pairwise angle (deg, folded to <= 90) for each convention.
usage: convention.py LABEL T_PATTERN AXIS_PATTERN N [N ...]
  patterns take one %d (1-based piece number) or %m (0-based, the assembler's T_<m>to_<m>.txt);
  T files are read as the top-left 3x3.
"""

import glob
import itertools
import sys

import numpy as np


def first_dir(path):
    for ln in open(path):
        v = ln.split()
        if len(v) >= 6:
            d = np.array(v[3:6], float)
            return d / np.linalg.norm(d)
    raise ValueError(path)


def rot(path):
    a = np.loadtxt(path, ndmin=2)
    return a[0:3, 0:3]


def one(p):
    g = glob.glob(p)
    if len(g) != 1:
        raise FileNotFoundError("%s -> %d matches" % (p, len(g)))
    return g[0]


def main():
    label, tp, ap = sys.argv[1:4]
    ns = [int(x) for x in sys.argv[4:]]
    R = {n: rot(one(tp.replace("%m", str(n - 1)) % n if "%d" in tp else tp.replace("%m", str(n - 1)))) for n in ns}
    A = {n: first_dir(one(ap % n)) for n in ns}
    for name, f in (("R a", lambda n: R[n] @ A[n]), ("R^T a", lambda n: R[n].T @ A[n])):
        m = {n: f(n) for n in ns}
        ang = [np.degrees(np.arccos(min(1.0, abs(float(m[i] @ m[j]))))) for i, j in itertools.combinations(ns, 2)]
        print("%-28s %-6s pairs %3d  median %6.2f  max %6.2f deg" % (label, name, len(ang), np.median(ang), max(ang)))


if __name__ == "__main__":
    main()
