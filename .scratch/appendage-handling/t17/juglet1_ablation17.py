#!/usr/bin/env python3
"""Ticket 17 deliverable 2: Juglet_Piece_1 handle ablation.

The handle of t09's Juglet_Piece_1 lies further than 4.0 mm from the S0 body
surface.  Cutting every S1 point further than 4.0 mm (and, as a sensitivity
check, 6.0 mm) from S0 gives the NO_HANDLE arms, which are re-solved with the
frozen SHIP selector (draw_pool -> select_union_lines, max_candidates=6).  The
FULL arm must reproduce the shipped axes09_juglet_def3x_regen direction.

Geometry is solved in the native 3x t09 frame; only scoring against the 1x
ground truth divides vertex positions by JUG_ROWS = 3.0.
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import t17_common as tc  # noqa: E402

HEADER = ["arm", "s0_pts", "s1_pts", "s1_far_from_s0_pts", "wrap_deg", "k",
          "rank0_gt_deg", "best_gt_deg", "d_gt_to_est_mm"]
NEAR_MM = 4.0
NEAR6_MM = 6.0
STEM = "Juglet_Piece_1"
CONTRAST = "Pot_J_Piece_01"


def load_t03(path):
    sys.path.insert(0, path)
    import t03_lib as dl  # noqa: F401
    return dl


def solve(dl, C0, C1):
    C = np.hstack([C0, C1]) if C1.shape[1] else C0.copy()
    out = dl.draw_pool(C, seeds=10, step=10)
    reps, sizes, V = out[0], out[1], out[2]
    if V.shape[1] == 0:
        raise RuntimeError("draw_pool drew no candidate axes")
    su = getattr(dl, "select_union_lines", None)
    if su is None:
        from sfs_axes.select import select_union_lines as su
    vt, costs = su(reps, sizes, C0, C1, C, 6, tri_select=None)
    return C, vt, costs


def score(dl, vt, gt):
    d_est = np.asarray(vt[0:3, 0], dtype=float)
    p_est = np.asarray(vt[3:6, 0], dtype=float) / tc.JUG_ROWS
    rank0 = tc.line_angle_deg(d_est, gt[0:3])
    best = min(tc.line_angle_deg(vt[0:3, i], gt[0:3]) for i in range(min(3, vt.shape[1])))
    dmm = dl.radial_axial_errors(gt[3:6], vt[0:3, 0], vt[3:6, 0] / tc.JUG_ROWS)[0]
    return float(rank0), float(best), float(dmm), p_est


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--t03", required=True, help="t03-ship work dir holding t03_lib.py")
    ap.add_argument("--out", required=True)
    ap.add_argument("--json", required=True)
    a = ap.parse_args()
    dl = load_t03(a.t03)

    # 6xN walls (x,y,z,nx,ny,nz): potsac's draw_pool and select_union_lines take
    # the point-plus-normal matrix, and only the 4 mm partition uses positions.
    C0 = np.ascontiguousarray(tc.read_wall(os.path.join(tc.geom_dir(STEM), STEM + ".S0"),
                                           with_normals=True), dtype=float)
    C1 = np.ascontiguousarray(tc.read_wall(os.path.join(tc.geom_dir(STEM), STEM + ".S1"),
                                           with_normals=True), dtype=float)
    if C0.shape[0] < 6 or C1.shape[0] < 6:
        raise RuntimeError("juglet walls must carry normals: C0=%s C1=%s" % (C0.shape, C1.shape))
    P0, P1 = C0[0:3], C1[0:3]
    n0, n1 = int(C0.shape[1]), int(C1.shape[1])

    d = cKDTree((P0 / tc.JUG_ROWS).T).query((P1 / tc.JUG_ROWS).T, k=1)[0]
    near = d <= NEAR_MM
    near6 = d <= NEAR6_MM
    n_far = int((~near).sum())
    n_far6 = int((~near6).sum())
    print("S0=%d S1=%d far>%.1fmm=%d far>%.1fmm=%d" % (n0, n1, NEAR_MM, n_far, NEAR6_MM, n_far6), flush=True)

    gt = tc.gt_axis(STEM)
    assert gt is not None, "no Juglet_Piece_1 GT axis"
    wrap = tc.wrap_deg((P0 / tc.JUG_ROWS).T, gt)
    print("S0 wrap_deg about GT axis = %.2f" % wrap, flush=True)

    contrast = None
    ps = tc.read_wall(os.path.join(tc.geom_dir(CONTRAST), CONTRAST + ".S0"), with_normals=False)[0:3]
    pgt = tc.gt_axis(CONTRAST)
    if pgt is not None:
        contrast = tc.wrap_deg(ps.T, pgt)
        print("contrast %s S0 wrap_deg = %.2f" % (CONTRAST, contrast), flush=True)

    # each arm carries the mask it keeps, so its own "far from S0" count is exact
    arms = [
        ("JUGLET1_FULL_T09", np.ones(n1, dtype=bool)),
        ("JUGLET1_NO_HANDLE", near),
        ("JUGLET1_NO_HANDLE_6MM", near6),
    ]
    rows, log = [], []
    shipped = tc.read_axis_lines(tc.axis09_path(STEM))
    for name, keep in arms:
        c1arm = np.ascontiguousarray(C1[:, keep])
        far_arm = int((keep & ~near).sum())
        C, vt, costs = solve(dl, C0, c1arm)
        rank0, best, dmm, p_est = score(dl, vt, gt)
        row = [name, n0, int(c1arm.shape[1]), far_arm,
               "%.2f" % wrap, int(vt.shape[1]), "%.4f" % rank0, "%.4f" % best, "%.4f" % dmm]
        rows.append(row)
        rep = tc.line_angle_deg(vt[0:3, 0], shipped[0:3]) if shipped.shape[1] else -1.0
        log.append({"arm": name, "s1_pts": int(c1arm.shape[1]), "k": int(vt.shape[1]),
                    "costs": [float(x) for x in np.asarray(costs)[:6]],
                    "rank0_deg": rank0, "best_deg": best, "d_mm": dmm,
                    "pos_est_1x": [float(x) for x in p_est],
                    "delta_vs_axes09_deg": float(rep)})
        print("arm %-24s s1=%6d k=%3d rank0=%8.4f best=%8.4f d_mm=%8.4f delta09=%7.4f"
              % (name, c1arm.shape[1], vt.shape[1], rank0, best, dmm, rep), flush=True)
        if name == "JUGLET1_FULL_T09":
            print("rank0<=0.1deg vs axes09: %s" % (rep <= 0.1), flush=True)

    tc.write_tsv(a.out, HEADER, rows)
    with open(a.json, "w") as fh:
        json.dump({"stem": STEM, "near_mm": NEAR_MM, "near6_mm": NEAR6_MM,
                   "s0_pts": n0, "s1_pts": n1, "s1_far": n_far, "s1_far6": n_far6,
                   "wrap_deg": wrap, "wrap_deg_contrast": {CONTRAST: contrast},
                   "arms": log, "gt_axis": [float(x) for x in gt]}, fh, indent=1)
    print("wrote %s" % a.out, flush=True)


if __name__ == "__main__":
    main()
