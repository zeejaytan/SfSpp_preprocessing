#!/usr/bin/env python3
"""stagea309.py -- Ticket 309 Stage A: is each released axis line a stationary point
of OUR cost on the shipped surfaces, and is it cheaper or dearer than our own best line.

Per piece, per surface variant V, per released line k:
  A1  refine_axis(released_k, X, method 2, 300, 1e-9) -> drift in deg.
      IN  = drift <= 0.5 deg (the released line is a local minimum of our cost)
      OUT = drift  > 0.5 deg (report the drift)
  A2  Pottmann residual over V's points: s_min/s_max of M in compute_pottmann_axis,
      and the angle between the released direction and the Pottmann axis.
  A3  robustified (Huber) per-point cost at the released line and at our own best
      line on the same V; ratio released/ours.
Also records our own K on V (run_potsac, shipped default, seed via --seed).

usage: stagea309.py --corpus DIR --out DIR [--v3 DIR] [--seed 0] [--pieces A_07,D_17,...]
Writes stageA.tsv (one row per piece x variant x released line), variants.tsv
(one row per piece x variant: n, n0, n1, md5, K_ours, pottmann), and errors.tsv.
"""
import argparse
import hashlib
import os
import sys
import time

import numpy as np

from sfs_axes.io_surfaces import load_surface, surface_path
from sfs_axes.io_axes import read_axes, direction_angle_deg, radial_axial_errors
from sfs_axes.refine import refine_axis
from sfs_axes.cao import compute_biaxial_cao_error
from sfs_axes.robust import apply_robustifier, robustifier_huber
from sfs_axes.pottmann import compute_pottmann_axis
from sfs_axes.potsac import run_potsac, effective_step, _huber_per_point

PIECES = ["A_07", "D_17", "D_24", "D_30", "E_21", "E_31", "E_34",
          "F_07", "H_06", "H_09", "J_11", "J_13", "J_14"]


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def pottmann_residual(X):
    """(s_min/s_max, axis (6,)) for a (6, n) cloud -- the A2 admissibility measure."""
    J = np.zeros((X.shape[1], 6))
    from sfs_axes.plucker import euc2plucker
    Jm = euc2plucker(X[np.r_[3:6, 0:3], :])
    J = Jm[np.r_[3:6, 0:3], :].T
    JTJ = J.T @ J
    M11, M12, M22 = JTJ[0:3, 0:3], JTJ[0:3, 3:6], JTJ[3:6, 3:6]
    try:
        Minv_M12t = np.linalg.solve(M22, M12.T)
    except np.linalg.LinAlgError:
        Minv_M12t = np.linalg.lstsq(M22, M12.T, rcond=None)[0]
    M = M11 - M12 @ Minv_M12t
    s = np.linalg.svd(M, compute_uv=False)
    return float(s[-1] / s[0]), compute_pottmann_axis(X)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--v3", default=None)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--pieces", default=",".join(PIECES))
    ap.add_argument("--reps", type=int, default=300)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    pieces = [p.strip() for p in a.pieces.split(",") if p.strip()]

    vrows = [("piece", "variant", "n0", "n1", "n", "step", "md5_s0", "md5_s1",
              "K_ours", "pott_smin_smax", "pott_ang_deg", "secs_ours")]
    rows = [("piece", "variant", "line", "n", "step",
             "released_huber_pt", "released_huber_sum",
             "refined_ang_deg", "refined_rad_mm", "refined_ax_mm",
             "refined_huber_pt", "refined_huber_sum", "in_out",
             "pott_ang_deg", "our_best_ang_deg", "our_best_huber_pt",
             "huber_ratio_rel_over_ours", "ourK")]
    errs = [("piece", "variant", "where", "msg")]

    for pc in pieces:
        pot, num = pc.split("_")
        num = int(num)
        # released lines
        rax = os.path.join(a.corpus, "Axes", "Pot_%s_Piece_%02d_Axis.xyz" % (pot, num))
        R = read_axes(rax)
        variants = []
        variants.append(("V1", a.corpus, False))
        variants.append(("V2", a.corpus, True))
        if a.v3 and os.path.isdir(a.v3):
            variants.append(("V3", a.v3, False))
        for vname, sdir, trunc in variants:
            f0 = surface_path(sdir, pot, num, 0)
            f1 = surface_path(sdir, pot, num, 1)
            if not (os.path.isfile(f0) and os.path.isfile(f1)):
                errs.append((pc, vname, "load", "surface file missing: %s" % f0))
                continue
            try:
                C0 = load_surface(f0)
                C1 = load_surface(f1)
            except Exception as exc:
                errs.append((pc, vname, "load", repr(exc)))
                continue
            if trunc:
                m = min(C0.shape[1], C1.shape[1])
                C0, C1 = C0[:, 0:m], C1[:, 0:m]
            X = np.concatenate([C0, C1], axis=1)
            n = X.shape[1]
            step = effective_step(n, None)
            t0 = time.time()
            try:
                smin, pa = pottmann_residual(X)
                pa_ang = direction_angle_deg(R[0:3, 0], pa[0:3])
            except Exception as exc:
                errs.append((pc, vname, "pottmann", repr(exc)))
                smin, pa_ang = float("nan"), float("nan")
            K = 0
            best_pt = float("nan")
            best_ang = [float("nan")] * R.shape[1]
            try:
                vt = run_potsac(C0, C1, rng=np.random.default_rng(a.seed), step=None)
                K = vt.shape[1]
                if K:
                    pt = [_huber_per_point(vt[:, j], X) for j in range(K)]
                    jb = int(np.argmin(pt))
                    best_pt = pt[jb]
                    for k in range(R.shape[1]):
                        best_ang[k] = min(direction_angle_deg(R[0:3, k], vt[0:3, j])
                                          for j in range(K))
            except Exception as exc:
                errs.append((pc, vname, "run_potsac", repr(exc)))
            secs = time.time() - t0
            vrows.append((pc, vname, C0.shape[1], C1.shape[1], n, step,
                          md5(f0), md5(f1), K, smin, pa_ang, "%.1f" % secs))
            for k in range(R.shape[1]):
                r = R[:, k].copy()
                h0 = _huber_per_point(r, X)
                g0 = float(np.sum(apply_robustifier(
                    robustifier_huber, np.atleast_1d(compute_biaxial_cao_error(r, X)))))
                try:
                    rref = refine_axis(r, X, 2, a.reps, 1e-9)
                except Exception as exc:
                    errs.append((pc, vname, "refine%d" % k, repr(exc)))
                    rref = r
                ang = direction_angle_deg(r[0:3], rref[0:3])
                rad, ax = radial_axial_errors(rref[3:6], r[0:3], r[3:6])
                h1 = _huber_per_point(rref, X)
                g1 = float(np.sum(apply_robustifier(
                    robustifier_huber, np.atleast_1d(compute_biaxial_cao_error(rref, X)))))
                verdict = "IN" if ang <= 0.5 else "OUT"
                rows.append((pc, vname, k, n, step, h0, g0, ang, rad, ax, h1, g1,
                             verdict, pa_ang, best_ang[k], best_pt,
                             (h0 / best_pt) if best_pt and best_pt == best_pt and best_pt > 0 else float("nan"),
                             K))
            print("[A] %s %s n=%d step=%d K=%d pott=%.4g pa=%.2fdeg %.1fs"
                  % (pc, vname, n, step, K, smin, pa_ang, secs), flush=True)

    for name, tab in (("variants.tsv", vrows), ("stageA.tsv", rows), ("errors.tsv", errs)):
        with open(os.path.join(a.out, name), "w") as fh:
            for row in tab:
                fh.write("\t".join(str(x) for x in row) + "\n")
    print("[A] wrote %s" % a.out)


if __name__ == "__main__":
    main()
