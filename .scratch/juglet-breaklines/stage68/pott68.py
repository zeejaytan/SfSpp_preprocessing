#!/usr/bin/env python3
"""t68 quick check: deterministic Pottmann on all wall points (+ Cao refine), GT gate.

usage: pott68.py <in_dir>   (same inputs as fit68.py)
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..")))
sys.path.insert(0, HERE)
from fit68 import N, fold, gate, read_axis, read_ply, read_T  # noqa: E402
from sfs_axes.pottmann import compute_pottmann_axis  # noqa: E402
from sfs_axes.refine import refine_axis  # noqa: E402


def main():
    ind = sys.argv[1]
    R = {k: read_T(os.path.join(ind, "Juglet_Piece_%d_T.txt" % k))[0] for k in range(1, N + 1)}
    est = {"old": {}, "pott": {}, "pott_ref": {}, "pottS0": {}, "pottS1": {}}
    for k in range(1, N + 1):
        est["old"][k] = read_axis(os.path.join(ind, "Juglet_Piece_%d_Axis.xyz" % k))[1]
        C0 = read_ply(os.path.join(ind, "Juglet_Piece_%d.S0" % k))
        C1 = read_ply(os.path.join(ind, "Juglet_Piece_%d.S1" % k))
        C = np.hstack([C0, C1])
        vt = compute_pottmann_axis(C)
        est["pott"][k] = vt[0:3] / np.linalg.norm(vt[0:3])
        try:
            vr = refine_axis(vt, C)
            vr = np.asarray(vr).reshape(-1)[0:3]
            est["pott_ref"][k] = vr / np.linalg.norm(vr)
        except Exception as e:  # report, do not hide
            print("P%d refine failed: %r" % (k, e))
            est["pott_ref"][k] = est["pott"][k]
        for nm, Cs in (("pottS0", C0), ("pottS1", C1)):
            v = compute_pottmann_axis(Cs)[0:3]
            est[nm][k] = v / np.linalg.norm(v)
        print("P%d old-vs-pott %.1f  pott-vs-ref %.1f  S0-vs-S1 %.1f" % (
            k, fold(est["old"][k], est["pott"][k]), fold(est["pott"][k], est["pott_ref"][k]),
            fold(est["pottS0"][k], est["pottS1"][k])))
    names = list(est)
    G = {n: gate([R[k] @ est[n][k] for k in range(1, N + 1)]) for n in names}
    print("piece  " + "  ".join("%9s" % n for n in names))
    for i in range(N):
        print("P%d     " % (i + 1) + "  ".join("%9.1f" % G[n][i] for n in names))
    for n in names:
        g = np.array(G[n])
        print("%-9s max %.1f  n<=10: %d  n>25: %d" % (n, g.max(), (g <= 10).sum(), (g > 25).sum()))


if __name__ == "__main__":
    main()
