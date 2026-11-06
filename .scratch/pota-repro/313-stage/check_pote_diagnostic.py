#!/usr/bin/env python3
"""Diagnostic script for Ticket 313 Stage A:
Evaluate normalized MLESAC + refinement on the 10 failing Pot E pieces.
"""

import os
import sys
import time
import numpy as np

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"

def load_surface(path):
    a = np.loadtxt(path, usecols=(0, 1, 2, 3, 4, 5), ndmin=2)
    return np.asarray(a, dtype=float).T

def read_axis(path):
    # format: p0x p0y p0z ax ay az
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
    # Import sfs_axes from local directory
    sys.path.insert(0, ".")
    from sfs_axes.pottmann import compute_pottmann_axis
    from sfs_axes.normalized import (
        compute_normalized_residual,
        refine_axis_normalized,
        worst_wall_normalized_cost,
        centroid_distance,
        DEFAULT_CLEARANCE_MM
    )
    from sfs_axes.potsac import _cluster_union, effective_step

    pieces = [3, 9, 23, 24, 25, 26, 27, 28, 29, 31]
    results = []

    print(f"{'Piece':<8} {'Diag(mm)':<10} {'d_GT(mm)':<10} {'d_Top(mm)':<10} {'Ang_GT':<10} {'Ang_Rel':<10} {'Cost_Top':<12} {'<=10deg?':<10}")
    print("-" * 85)

    for p in pieces:
        stem = f"Pot_E_Piece_{p:02d}"
        s0_path = os.path.join(CORPUS, "Surfaces", f"{stem}_Surface_0.xyz")
        s1_path = os.path.join(CORPUS, "Surfaces", f"{stem}_Surface_1.xyz")
        rel_path = os.path.join(CORPUS, "Axes", f"{stem}_Axis.xyz")
        gt_path = os.path.join(CORPUS, "Ground Truth Axes", f"{stem}_Axis.xyz")

        C0 = load_surface(s0_path)
        C1 = load_surface(s1_path)
        C = np.concatenate([C0, C1], axis=1)
        C_centroid = np.mean(C[0:3, :], axis=1)
        diag = np.linalg.norm(np.ptp(C[0:3, :], axis=1))

        rel_axes = read_axis(rel_path)
        gt_axes = read_axis(gt_path) if os.path.isfile(gt_path) else rel_axes
        vt_gt = canonicalize(gt_axes[:, 0])
        vt_rel = canonicalize(rel_axes[:, 0])
        d_gt = centroid_distance(vt_gt, C)

        n = C.shape[1]
        step = effective_step(n, 10)
        Cd = C[:, ::step]

        # Generate Pottmann draws over 10 seeds
        all_cands = []
        for seed in range(10):
            rng = np.random.default_rng(seed)
            nd = Cd.shape[1]
            for _ in range(100):  # 100 draws per seed = 1000 total
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
                    all_cands.append(vt)
                except Exception:
                    pass

        V = np.column_stack(all_cands)
        reps, sizes = _cluster_union(V)

        # Refine candidate basins on Cd using normalized loss
        refined = []
        for j in range(reps.shape[1]):
            v_ref = refine_axis_normalized(reps[:, j], Cd, max_iters=50, tolerance=1e-3)
            refined.append(v_ref)
        V_ref = np.column_stack(refined)
        reps_ref, _ = _cluster_union(V_ref)

        # Apply clearance filter and rank by worst-wall normalized cost
        scores = []
        valid_reps = []
        for j in range(reps_ref.shape[1]):
            cand_axis = reps_ref[:, j]
            d_cent = centroid_distance(cand_axis, C)
            # Clearance filter: must be >= 25 mm from centroid
            if d_cent < DEFAULT_CLEARANCE_MM:
                continue
            cost = worst_wall_normalized_cost(cand_axis, C0, C1, min_clearance_mm=DEFAULT_CLEARANCE_MM)
            scores.append(cost)
            valid_reps.append(cand_axis)

        if not valid_reps:
            # Fallback if all were under clearance
            valid_reps = [reps_ref[:, 0]]
            scores = [9999.0]

        order = np.argsort(scores)
        top_axis = canonicalize(valid_reps[order[0]])
        d_top = centroid_distance(top_axis, C)
        ang_gt = angle_deg(top_axis, vt_gt)
        ang_rel = angle_deg(top_axis, vt_rel)
        cost_top = scores[order[0]]
        pass_10 = "YES" if (ang_gt <= 10.0 or ang_rel <= 10.0) else "NO"

        print(f"Piece {p:02d}  {diag:<10.1f} {d_gt:<10.2f} {d_top:<10.2f} {ang_gt:<10.2f} {ang_rel:<10.2f} {cost_top:<12.5f} {pass_10:<10}")
        results.append((p, diag, d_gt, d_top, ang_gt, ang_rel, cost_top, pass_10))

if __name__ == "__main__":
    main()
