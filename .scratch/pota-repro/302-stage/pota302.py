#!/usr/bin/env python3
"""Ticket 302 gate 2: corrected port vs MATLAB run_potsac, corpus Pot A.

MATLAB arm (pota_ml302.m) runs the shipped run_potsac.m (adaptive step,
rng(0)) on the same corpus clouds. Here: seeds 0..9, adaptive step (None) to
match, LIVE refiner. PASS: some seed within 0.01 deg / 0.01 mm of the MATLAB
line 1 for every piece; seed 0 and K also reported, plus released-axis
context.
"""
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "sfs_axes")))

from sfs_axes.io_axes import (direction_angle_deg, radial_axial_errors,  # noqa: E402
                              read_axes)
from sfs_axes.potsac import run_potsac  # noqa: E402

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
ANG_TOL = 0.01
RAD_TOL = 0.01


def canonicalize(vt):
    vt = np.asarray(vt, dtype=float).copy()
    if vt[2] < 0:
        vt = -vt
    return vt


def load_surface(path):
    a = np.loadtxt(path, usecols=(0, 1, 2, 3, 4, 5), ndmin=2)
    return np.asarray(a, dtype=float).T


def main(ml_dir, out_tsv):
    rows = []
    for piece in range(1, 9):
        stem = "Pot_A_Piece_%02d" % piece
        C0 = load_surface(os.path.join(CORPUS, "Surfaces", stem + "_Surface_0.xyz"))
        C1 = load_surface(os.path.join(CORPUS, "Surfaces", stem + "_Surface_1.xyz"))
        ml = read_axes(os.path.join(ml_dir, stem + "_Axis.xyz"))
        m1 = canonicalize(ml[:, 0])
        rel = read_axes(os.path.join(CORPUS, "Axes", stem + "_Axis.xyz"))
        r1 = canonicalize(rel[:, 0])
        for seed in range(10):
            t0 = time.time()
            vt = run_potsac(C0, C1, rng=np.random.default_rng(seed))
            secs = time.time() - t0
            K = vt.shape[1] if vt.size else 0
            o1 = canonicalize(vt[:, 0]) if K else None
            ang = direction_angle_deg(o1[0:3], m1[0:3]) if K else float("nan")
            rad = radial_axial_errors(o1[3:6], m1[0:3], m1[3:6])[0] if K else float("nan")
            arel = direction_angle_deg(o1[0:3], r1[0:3]) if K else float("nan")
            rows.append((piece, seed, K, ml.shape[1], ang, rad, arel, secs))
            print("%s seed=%d K=%d/%d vs_ml=%.3e/%.3e vs_rel=%.3f (%.1fs)"
                  % (stem, seed, K, ml.shape[1], ang, rad, arel, secs), flush=True)
    with open(out_tsv, "w") as fh:
        fh.write("piece\tseed\tK\tK_matlab\tang_deg\trad_mm\tang_vs_released\tsecs\n")
        for r in rows:
            fh.write("\t".join(("%.17g" % v if isinstance(v, float) else str(v))
                                for v in r) + "\n")
    print("--- per-piece summary (line 1 vs MATLAB line 1)")
    ok_all = True
    for piece in range(1, 9):
        sel = [r for r in rows if r[0] == piece]
        s0 = sel[0]
        best = min(sel, key=lambda r: r[4])
        ok = best[4] <= ANG_TOL and best[5] <= RAD_TOL
        ok_all = ok_all and ok
        print("piece %02d: seed0 %.3e/%.3e | best s%d %.3e/%.3e | vs_released %.2f deg | K %d/%d %s"
              % (piece, s0[4], s0[5], best[1], best[4], best[5], s0[6], s0[2], s0[3],
                 "PASS" if ok else "FAIL"))
    print("OVERALL:", "PASS" if ok_all else "FAIL")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
