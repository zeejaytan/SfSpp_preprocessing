#!/usr/bin/env python3
"""cost70.py -- ticket 70 stage-2 diagnostic: the released line 1 and our M0 line 1 scored
under the port's own two PotSAC objectives on the same cloud, step 10, no truncation:
  gm    = GM-robustified biaxial Cao error (the MLESAC ranking, potsac.py:49-50)
  huber = Huber-robustified biaxial Cao error (the candidate cost, potsac.py:113-117)
If the released axis scores lower, our search misses an axis its objective prefers;
if higher, the released axis was not chosen by this objective on this cloud.

Stage 2b adds pp = the per-point Huber cost of refine.biaxial_blocks on the full cloud, the
objective live method-2 refinement minimises (refine.py module docstring).

usage: cost70.py CORPUS RUNOUT [ARM [OUTDIR]]  (RUNOUT = a stage-2 out/ with axes/ARM/, ARM default M0)
"""
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(_HERE, "..", "..", "..")))
from sfs_axes.cao import compute_biaxial_cao_error  # noqa: E402
from sfs_axes.io_axes import direction_angle_deg, read_axes  # noqa: E402
from sfs_axes.refine import biaxial_blocks, refine_axis  # noqa: E402
from sfs_axes.robust import apply_robustifier, robustifier_gm, robustifier_huber  # noqa: E402


def load(path):
    return np.loadtxt(path, usecols=(0, 1, 2, 3, 4, 5), ndmin=2).T


def costs(vt, Cd):
    e = np.atleast_1d(compute_biaxial_cao_error(vt, Cd))
    return (float(np.sum(apply_robustifier(robustifier_gm, e))),
            float(np.sum(apply_robustifier(robustifier_huber, e))), float(np.ravel(e)[0]))


def pp(vt, X):
    R, _J = biaxial_blocks(vt, X)
    return float(np.sum(apply_robustifier(robustifier_huber, R)))


def main():
    corpus, runout = sys.argv[1], sys.argv[2]
    arm = sys.argv[3] if len(sys.argv) > 3 else "M0"
    outdir = sys.argv[4] if len(sys.argv) > 4 else runout
    os.makedirs(outdir, exist_ok=True)
    out = open(os.path.join(outdir, "cost70_%s.tsv" % arm), "w")
    out.write("pot\tpiece\terr_rel\terr_ours\tgm_rel\tgm_ours\thuber_rel\thuber_ours"
              "\tpp_rel\tpp_ours\tpp_relref\trelref_to_rel_deg\trelref_to_gt_deg\trel_to_gt_deg\n")
    n = rel_lower_gm = rel_lower_hub = rel_lower_pp = 0
    for fn in sorted(os.listdir(os.path.join(runout, "axes", arm))):
        t = fn.split("_")
        pot, piece = t[1], int(t[3])
        stem = "Pot_%s_Piece_%02d" % (pot, piece)
        C = np.concatenate([load(os.path.join(corpus, "Surfaces", stem + "_Surface_%d.xyz" % k))
                            for k in (0, 1)], axis=1)
        C[3:6] = C[3:6] / np.linalg.norm(C[3:6], axis=0)
        Cd = C[:, 0:C.shape[1]:10]
        rel = read_axes(os.path.join(corpus, "Axes", stem + "_Axis.xyz"))[:, 0]
        ours = read_axes(os.path.join(runout, "axes", arm, fn))[:, 0]
        rel[0:3] /= np.linalg.norm(rel[0:3])
        ours[0:3] /= np.linalg.norm(ours[0:3])
        gr, hr, er = costs(rel, Cd)
        go, ho, eo = costs(ours, Cd)
        pr, po = pp(rel, C), pp(ours, C)
        rr = refine_axis(refine_axis(rel, Cd, 2, 300, 1e-3, noop=False), C, 2, 300, 1e-9, noop=False)
        g = os.path.join(corpus, "Ground Truth Axes", stem + "_Axis.xyz")
        if os.path.isfile(g):
            gt = read_axes(g)[0:3, 0]
            rr_gt, rel_gt = direction_angle_deg(rr[0:3], gt), direction_angle_deg(rel[0:3], gt)
        else:
            rr_gt = rel_gt = float("nan")
        out.write("%s\t%d\t%.6g\t%.6g\t%.6g\t%.6g\t%.6g\t%.6g\t%.6g\t%.6g\t%.6g\t%.3f\t%.3f\t%.3f\n"
                  % (pot, piece, er, eo, gr, go, hr, ho, pr, po, pp(rr, C),
                     direction_angle_deg(rr[0:3], rel[0:3]), rr_gt, rel_gt))
        n += 1
        rel_lower_gm += int(gr < go)
        rel_lower_hub += int(hr < ho)
        rel_lower_pp += int(pr < po)
    out.close()
    print("[C70] arm %s pieces %d; released line 1 lower GM cost on %d, lower Huber cost on %d, "
          "lower per-point Huber (full C) on %d" % (arm, n, rel_lower_gm, rel_lower_hub, rel_lower_pp),
          flush=True)


if __name__ == "__main__":
    main()
