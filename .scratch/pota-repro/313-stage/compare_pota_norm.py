#!/usr/bin/env python3
"""Compare candidate ranking on Pot A: normalized vs unnormalized cost."""
import os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, ".")

from sfs_axes.pottmann import compute_pottmann_axis
from sfs_axes.normalized import centroid_distance, worst_wall_normalized_cost, DEFAULT_CLEARANCE_MM
from sfs_axes.potsac import _cluster_union, effective_step, _worst_surface_cost, refine_axis
from sfs_axes.io_axes import direction_angle_deg
from check_ref_drift import load_surface, read_axis

def canonicalize(vt):
    vt = np.asarray(vt, dtype=float).copy()
    if vt[2] < 0: vt[:3] = -vt[:3]
    return vt

for p in range(1, 9):
    stem = f"Pot_A_Piece_{p:02d}"
    s0 = load_surface(os.path.join(CORPUS, "Surfaces", f"{stem}_Surface_0.xyz"))
    s1 = load_surface(os.path.join(CORPUS, "Surfaces", f"{stem}_Surface_1.xyz"))
    C = np.concatenate([s0, s1], axis=1)
    rel = read_axis(os.path.join(CORPUS, "Axes", f"{stem}_Axis.xyz"))
    gt = read_axis(os.path.join(CORPUS, "Ground Truth Axes", f"{stem}_Axis.xyz"))
    vt_rel = rel[:, 0]
    
    n = C.shape[1]
    step = effective_step(n, 10)
    Cd = C[:, ::step]
    
    cand = []
    for seed in range(10):
        rng = np.random.default_rng(seed)
        for _ in range(100):
            kidx = rng.choice(Cd.shape[1], 6, replace=False)
            Cs = Cd[:, kidx].copy()
            mCs = Cs[:3, :].mean(axis=1)
            Cs[:3, :] -= mCs[:, None]
            scale = float(np.mean(np.abs(Cs)))
            if scale < 1e-8: continue
            Cs[:3, :] /= scale
            try:
                vt = compute_pottmann_axis(Cs)
                vt[3:6] = vt[3:6] * scale + mCs
                vt[3:6] -= (vt[:3] @ vt[3:6]) * vt[:3]
                cand.append(vt)
            except Exception:
                pass
                
    V = np.column_stack(cand)
    reps, sizes = _cluster_union(V)
    
    # Cost under unnormalized worst surface
    cost_unnorm = [_worst_surface_cost(reps[:, j], s0, s1) for j in range(reps.shape[1])]
    order_unnorm = np.argsort(cost_unnorm)
    best_unnorm = min([direction_angle_deg(reps[:3, order_unnorm[k]], vt_rel[:3]) for k in range(min(6, len(order_unnorm)))])
    
    # Cost under normalized worst wall
    cost_norm = [worst_wall_normalized_cost(reps[:, j], s0, s1, min_clearance_mm=0.0) for j in range(reps.shape[1])]
    order_norm = np.argsort(cost_norm)
    best_norm = min([direction_angle_deg(reps[:3, order_norm[k]], vt_rel[:3]) for k in range(min(6, len(order_norm)))])
    
    print(f"Pot A Piece {p:02d}: best_unnorm_top6={best_unnorm:.2f} deg | best_norm_top6={best_norm:.2f} deg")
