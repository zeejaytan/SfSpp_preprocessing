#!/usr/bin/env python3
"""sanity70.py -- ticket 70 stage 2b: does live method-2 refinement move an axis, and does its
cost fall? Six good-pot pieces, step 10, no truncation, seed 0.

Per piece, two starts: the top MLESAC candidate (potsac.compute_axis_of_symmetry on C[:, ::10])
and the released line 1. Each is refined as run_potsac does (stage 1: Cd, 300 it, 1e-3; stage 2:
full C, 300 it, 1e-9) with refine.optimize_using_lm + refine.biaxial_blocks. The cost trajectory is
read by re-running the LM with max_iters = 1, 2, 5, 10, 30, 100, 300 (deterministic, so each is a
prefix of the full run). Then one full live run_potsac per piece (K, line 1 vs released and GT, time).

usage: sanity70.py CORPUS OUTDIR
"""
import os
import sys
import time

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(_HERE, "..", "..", "..")))
from sfs_axes.cao import compute_biaxial_cao_error  # noqa: E402
from sfs_axes.io_axes import direction_angle_deg, radial_axial_errors, read_axes  # noqa: E402
from sfs_axes.potsac import compute_axis_of_symmetry, run_potsac  # noqa: E402
from sfs_axes.refine import biaxial_blocks, cao_update_func, optimize_using_lm  # noqa: E402
from sfs_axes.robust import apply_robustifier, robustifier_huber  # noqa: E402

PIECES = [("A", 2), ("A", 3), ("B", 3), ("D", 5), ("E", 10), ("I", 4)]
SWEEP = [1, 2, 5, 10, 30, 100, 300]


def load(path):
    return np.loadtxt(path, usecols=(0, 1, 2, 3, 4, 5), ndmin=2).T


def pp_huber(vt, X):
    R, _J = biaxial_blocks(vt, X)
    return float(np.sum(apply_robustifier(robustifier_huber, R)))


def lm(vt, X, iters, tol):
    res = lambda v: biaxial_blocks(v, X)  # noqa: E731
    x, _e, xlog = optimize_using_lm(vt, res, cao_update_func, robustifier_huber, iters, tol)
    x[0:3] /= np.linalg.norm(x[0:3])
    x[3:6] -= x[0:3] * (x[0:3] @ x[3:6])
    return x, xlog.shape[1] - 1


def describe(tag, vt, X, rel, gt):
    return ("%s ppHuber=%.6g biaxial=%.6g ang_rel=%.2f rad_rel=%.1f ang_gt=%s"
            % (tag, pp_huber(vt, X), compute_biaxial_cao_error(vt, X),
               direction_angle_deg(vt[0:3], rel[0:3]),
               radial_axial_errors(vt[3:6], rel[0:3] / np.linalg.norm(rel[0:3]), rel[3:6])[0],
               "%.2f" % direction_angle_deg(vt[0:3], gt) if gt is not None else "nan"))


def main():
    corpus, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    log = open(os.path.join(outdir, "sanity70.txt"), "w")

    def say(s):
        print(s, flush=True)
        log.write(s + "\n")

    for pot, piece in PIECES:
        stem = "Pot_%s_Piece_%02d" % (pot, piece)
        C = np.concatenate([load(os.path.join(corpus, "Surfaces", stem + "_Surface_%d.xyz" % k))
                            for k in (0, 1)], axis=1)
        C[3:6] = C[3:6] / np.linalg.norm(C[3:6], axis=0)
        Cd = C[:, 0:C.shape[1]:10]
        rel = read_axes(os.path.join(corpus, "Axes", stem + "_Axis.xyz"))[:, 0].copy()
        rel[0:3] /= np.linalg.norm(rel[0:3])
        g = os.path.join(corpus, "Ground Truth Axes", stem + "_Axis.xyz")
        gt = read_axes(g)[0:3, 0] if os.path.isfile(g) else None
        say("=== %s n=%d nd=%d" % (stem, C.shape[1], Cd.shape[1]))
        vts = compute_axis_of_symmetry(Cd, rng=np.random.default_rng(0))[0]
        for name, v0 in (("mlesac_top", vts[:, 0].copy()), ("released_l1", rel.copy())):
            say(describe("  %s start      " % name, v0, Cd, rel, gt))
            prev = None
            for k in SWEEP:
                vk, ev = lm(v0, Cd, k, 1e-3)
                c = pp_huber(vk, Cd)
                mono = "" if prev is None else ("  (ppHuber %s)" % ("down/same" if c <= prev + 1e-9 * abs(prev) else "UP"))
                prev = c
                say(describe("  %s s1 it<=%-3d evals=%-4d" % (name, k, ev), vk, Cd, rel, gt) + mono)
            t0 = time.time()
            v1, ev1 = lm(v0, Cd, 300, 1e-3)
            v2, ev2 = lm(v1, C, 300, 1e-9)
            say(describe("  %s s2 full-C evals=%d (%.1fs)" % (name, ev2, time.time() - t0), v2, C, rel, gt))
        t0 = time.time()
        C0 = load(os.path.join(corpus, "Surfaces", stem + "_Surface_0.xyz"))
        C1 = load(os.path.join(corpus, "Surfaces", stem + "_Surface_1.xyz"))
        vt = run_potsac(C0, C1, rng=np.random.default_rng(0), step=10)
        secs = time.time() - t0
        angs = ["%.2f" % direction_angle_deg(vt[0:3, k], rel[0:3]) for k in range(vt.shape[1])]
        gts = ["%.2f" % direction_angle_deg(vt[0:3, k], gt) for k in range(vt.shape[1])] if gt is not None else []
        say("  run_potsac live: K=%d (%.1fs) ang_to_rel1=%s ang_to_gt=%s"
            % (vt.shape[1], secs, ",".join(angs), ",".join(gts)))
    log.close()


if __name__ == "__main__":
    main()
