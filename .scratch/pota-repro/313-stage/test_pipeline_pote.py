#!/usr/bin/env python3
"""Test candidate generation + clearance filter + ranking on the 10 failing Pot E pieces."""

import os
import sys
import numpy as np

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, ".")

from sfs_axes.pottmann import compute_pottmann_axis
from sfs_axes.normalized import (
    centroid_distance,
    worst_wall_normalized_cost,
    normalized_huber_cost,
    refine_axis_least_squares,
    DEFAULT_CLEARANCE_MM
)
from sfs_axes.potsac import _cluster_union, effective_step
from sfs_axes.io_axes import direction_angle_deg

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
    pieces = [3, 9, 23, 24, 25, 26, 27, 28, 29, 31]
    print(f"{'Piece':<8} {'d_GT':<8} {'d_Rel':<8} {'d_Top':<8} {'Ang_GT':<9} {'Ang_Rel':<9} {'Rank1_Ang':<10} {'Rank1_d':<9} {'Cost':<10}")
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
        N = C[3:6, :]

        rel_axes = read_axis(rel_path)
        gt_axes = read_axis(gt_path) if os.path.isfile(gt_path) else rel_axes
        vt_gt = canonicalize(gt_axes[:, 0])
        vt_rel = canonicalize(rel_axes[:, 0])
        d_gt = centroid_distance(vt_gt, C)
        d_rel = centroid_distance(vt_rel, C)

        n = C.shape[1]
        step = effective_step(n, 10)
        Cd = C[:, ::step]
        nd = Cd.shape[1]

        # 10 seeds x 1000 Pottmann draws
        all_cands = []
        for seed in range(10):
            rng = np.random.default_rng(seed)
            for _ in range(1000):
                kidx = rng.choice(nd, 6, replace=False)
                Cs = Cd[:, kidx].copy()
                mCs = Cs[0:3, :].mean(axis=1)
                Cs[0:3, :] -= mCs[:, None]
                scale = float(np.mean(np.abs(Cs)))
                if scale < 1e-8: continue
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

        # Filter candidate basins by physical priors:
        # 1) Centroid clearance >= 25 mm
        # 2) Mean |n . a| <= 0.6 (reject perpendicular decoys)
        valid_reps = []
        for j in range(reps.shape[1]):
            cand = reps[:, j]
            d_c = centroid_distance(cand, C)
            if d_c < DEFAULT_CLEARANCE_MM:
                continue
            a_cand = cand[:3] / np.linalg.norm(cand[:3])
            mean_axial = np.mean(np.abs(a_cand @ N))
            if mean_axial > 0.6:
                continue
            valid_reps.append(cand)

        if not valid_reps:
            # Fallback
            valid_reps = [reps[:, 0]]

        V_valid = np.column_stack(valid_reps)
        # Score each candidate by worst-wall normalized Huber cost
        costs = [worst_wall_normalized_cost(V_valid[:, j], C0, C1, min_clearance_mm=DEFAULT_CLEARANCE_MM)
                 for j in range(V_valid.shape[1])]
        order = np.argsort(costs)

        top = canonicalize(V_valid[:, order[0]])
        d_top = centroid_distance(top, C)
        ang_gt = angle_deg(top, vt_gt)
        ang_rel = angle_deg(top, vt_rel)
        best_ang = min(ang_gt, ang_rel)

        # Also find best candidate in the top 3 or top 6
        topK_angs = [min(angle_deg(canonicalize(V_valid[:, order[k]]), vt_gt),
                         angle_deg(canonicalize(V_valid[:, order[k]]), vt_rel))
                     for k in range(min(6, len(order)))]
        best_in_top6 = min(topK_angs)

        print(f"Piece {p:02d}  {d_gt:<8.1f} {d_rel:<8.1f} {d_top:<8.1f} {ang_gt:<9.2f} {ang_rel:<9.2f} "
              f"{best_ang:<10.2f} {d_top:<9.1f} {costs[order[0]]:<10.5f} | top6 best: {best_in_top6:.2f} deg")

if __name__ == "__main__":
    main()
