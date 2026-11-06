#!/usr/bin/env python3
"""Inspect candidate pools and loss at GT / Released axes on failing Pot E pieces."""

import os
import sys
import numpy as np

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"

def load_surface(path):
    a = np.loadtxt(path, usecols=(0, 1, 2, 3, 4, 5), ndmin=2)
    return np.asarray(a, dtype=float).T

def read_axis(path):
    lines = [line.strip().split() for line in open(path) if line.strip()]
    axes = []
    for l in lines:
        p0 = [float(x) for x in l[:3]]
        a = [float(x) for x in l[3:6]]
        axes.append(np.r_[a, p0])
    return np.column_stack(axes)

def canonicalize(vt):
    vt = np.asarray(vt, dtype=float).copy()
    if vt[2] < 0:
        vt[0:3] = -vt[0:3]
    return vt

def angle_deg(v1, v2):
    a1 = v1[0:3] / np.linalg.norm(v1[0:3])
    a2 = v2[0:3] / np.linalg.norm(v2[0:3])
    cos = np.clip(abs(float(np.dot(a1, a2))), 0.0, 1.0)
    return float(np.degrees(np.arccos(cos)))

def main():
    sys.path.insert(0, ".")
    from sfs_axes.pottmann import compute_pottmann_axis
    from sfs_axes.normalized import (
        refine_axis_normalized,
        worst_wall_normalized_cost,
        centroid_distance,
        normalized_huber_cost
    )
    from sfs_axes.potsac import _cluster_union, effective_step

    pieces = [3, 9, 23, 24, 25, 26, 27, 28, 29, 31]

    for p in pieces:
        stem = f"Pot_E_Piece_{p:02d}"
        s0_path = os.path.join(CORPUS, "Surfaces", f"{stem}_Surface_0.xyz")
        s1_path = os.path.join(CORPUS, "Surfaces", f"{stem}_Surface_1.xyz")
        rel_path = os.path.join(CORPUS, "Axes", f"{stem}_Axis.xyz")
        gt_path = os.path.join(CORPUS, "Ground Truth Axes", f"{stem}_Axis.xyz")

        C0 = load_surface(s0_path)
        C1 = load_surface(s1_path)
        C = np.concatenate([C0, C1], axis=1)

        rel_axes = read_axis(rel_path)
        gt_axes = read_axis(gt_path) if os.path.isfile(gt_path) else rel_axes
        vt_gt = canonicalize(gt_axes[:, 0])
        vt_rel = canonicalize(rel_axes[:, 0])

        cost_gt = worst_wall_normalized_cost(vt_gt, C0, C1, min_clearance_mm=0.0)
        cost_rel = worst_wall_normalized_cost(vt_rel, C0, C1, min_clearance_mm=0.0)

        # What happens if we refine directly FROM GT or FROM Released under normalized loss?
        ref_from_gt = refine_axis_normalized(vt_gt, C, max_iters=100, tolerance=1e-9)
        ref_from_rel = refine_axis_normalized(vt_rel, C, max_iters=100, tolerance=1e-9)
        ang_from_gt = angle_deg(ref_from_gt, vt_gt)
        ang_from_rel = angle_deg(ref_from_rel, vt_rel)
        cost_from_gt = worst_wall_normalized_cost(ref_from_gt, C0, C1, min_clearance_mm=0.0)
        cost_from_rel = worst_wall_normalized_cost(ref_from_rel, C0, C1, min_clearance_mm=0.0)

        # Also check Pottmann draws: how close does Pottmann get?
        n = C.shape[1]
        step = effective_step(n, 10)
        Cd = C[:, ::step]
        nd = Cd.shape[1]
        min_pott_gt = 999.0
        min_pott_rel = 999.0
        pott_cands = []
        for seed in range(10):
            rng = np.random.default_rng(seed)
            for _ in range(100):
                kidx = rng.choice(nd, 6, replace=False)
                Cs = Cd[:, kidx].copy()
                mCs = Cs[0:3, :].mean(axis=1)
                Cs[0:3, :] -= mCs[:, None]
                scale = float(np.mean(np.abs(Cs)))
                if scale < 1e-8:
                    continue
                Cs[0:3, :] /= scale
                try:
                    vt = compute_pottmann_axis(Cs)
                    vt[3:6] = vt[3:6] * scale + mCs
                    vt[3:6] -= (vt[0:3] @ vt[3:6]) * vt[0:3]
                    pott_cands.append(vt)
                    a_gt = angle_deg(vt, vt_gt)
                    a_rel = angle_deg(vt, vt_rel)
                    if a_gt < min_pott_gt: min_pott_gt = a_gt
                    if a_rel < min_pott_rel: min_pott_rel = a_rel
                except Exception:
                    pass

        print(f"Piece {p:02d}: cost_gt={cost_gt:.5f}, cost_rel={cost_rel:.5f} | "
              f"ref_from_gt ang={ang_from_gt:.2f} cost={cost_from_gt:.5f} | "
              f"ref_from_rel ang={ang_from_rel:.2f} cost={cost_from_rel:.5f} | "
              f"min_pott_gt={min_pott_gt:.2f} min_pott_rel={min_pott_rel:.2f}")

if __name__ == "__main__":
    main()
