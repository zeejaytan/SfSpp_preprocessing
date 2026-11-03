#!/usr/bin/env python3
"""cost70.py -- ticket 70 stage-2 diagnostic: the released line 1 and our M0 line 1 scored
under the port's own two PotSAC objectives on the same cloud, step 10, no truncation:
  gm    = GM-robustified biaxial Cao error (the MLESAC ranking, potsac.py:49-50)
  huber = Huber-robustified biaxial Cao error (the candidate cost, potsac.py:113-117)
If the released axis scores lower, our search misses an axis its objective prefers;
if higher, the released axis was not chosen by this objective on this cloud.

usage: cost70.py CORPUS RUNOUT  (RUNOUT = the stage-2 out/ with axes/M0/)
"""
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(_HERE, "..", "..", "..")))
from sfs_axes.cao import compute_biaxial_cao_error  # noqa: E402
from sfs_axes.io_axes import read_axes  # noqa: E402
from sfs_axes.robust import apply_robustifier, robustifier_gm, robustifier_huber  # noqa: E402


def load(path):
    return np.loadtxt(path, usecols=(0, 1, 2, 3, 4, 5), ndmin=2).T


def costs(vt, Cd):
    e = np.atleast_1d(compute_biaxial_cao_error(vt, Cd))
    return (float(np.sum(apply_robustifier(robustifier_gm, e))),
            float(np.sum(apply_robustifier(robustifier_huber, e))), float(np.ravel(e)[0]))


def main():
    corpus, runout = sys.argv[1], sys.argv[2]
    out = open(os.path.join(runout, "cost70.tsv"), "w")
    out.write("pot\tpiece\terr_rel\terr_ours\tgm_rel\tgm_ours\thuber_rel\thuber_ours\n")
    n = rel_lower_gm = rel_lower_hub = 0
    for fn in sorted(os.listdir(os.path.join(runout, "axes", "M0"))):
        t = fn.split("_")
        pot, piece = t[1], int(t[3])
        stem = "Pot_%s_Piece_%02d" % (pot, piece)
        C = np.concatenate([load(os.path.join(corpus, "Surfaces", stem + "_Surface_%d.xyz" % k))
                            for k in (0, 1)], axis=1)
        C[3:6] = C[3:6] / np.linalg.norm(C[3:6], axis=0)
        Cd = C[:, 0:C.shape[1]:10]
        rel = read_axes(os.path.join(corpus, "Axes", stem + "_Axis.xyz"))[:, 0]
        ours = read_axes(os.path.join(runout, "axes", "M0", fn))[:, 0]
        rel[0:3] /= np.linalg.norm(rel[0:3])
        ours[0:3] /= np.linalg.norm(ours[0:3])
        gr, hr, er = costs(rel, Cd)
        go, ho, eo = costs(ours, Cd)
        out.write("%s\t%d\t%.6g\t%.6g\t%.6g\t%.6g\t%.6g\t%.6g\n" % (pot, piece, er, eo, gr, go, hr, ho))
        n += 1
        rel_lower_gm += int(gr < go)
        rel_lower_hub += int(hr < ho)
    out.close()
    print("[C70] pieces %d; released line 1 lower GM cost on %d, lower Huber cost on %d"
          % (n, rel_lower_gm, rel_lower_hub), flush=True)


if __name__ == "__main__":
    main()
