#!/usr/bin/env python3
"""Evaluate Pot E with full physical clearance window [25.0, 105.0] mm and decoy filter."""

import os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, ".")

from sfs_axes.pottmann import compute_pottmann_axis
from sfs_axes.normalized import centroid_distance, worst_wall_normalized_cost, DEFAULT_CLEARANCE_MM
from sfs_axes.potsac import _cluster_union, effective_step
from sfs_axes.io_axes import direction_angle_deg
from check_ref_drift import load_surface, read_axis

def canonicalize(vt):
    vt = np.asarray(vt, dtype=float).copy()
    if vt[2] < 0: vt[:3] = -vt[:3]
    return vt

def angle_deg(v1, v2):
    a1 = v1[:3] / np.linalg.norm(v1[:3])
    a2 = v2[:3] / np.linalg.norm(v2[:3])
    cos = np.clip(abs(float(np.dot(a1, a2))), 0.0, 1.0)
    return float(np.degrees(np.arccos(cos)))

MAX_CLEARANCE_MM = 105.0

def run_piece(p):
    stem = f"Pot_E_Piece_{p:02d}"
    s0_path = os.path.join(CORPUS, "Surfaces", f"{stem}_Surface_0.xyz")
    s1_path = os.path.join(CORPUS, "Surfaces", f"{stem}_Surface_1.xyz")
    rel_path = os.path.join(CORPUS, "Axes", f"{stem}_Axis.xyz")
    gt_path = os.path.join(CORPUS, "Ground Truth Axes", f"{stem}_Axis.xyz")

    if not os.path.isfile(s0_path): return None

    C0 = load_surface(s0_path)
    C1 = load_surface(s1_path)
    C = np.concatenate([C0, C1], axis=1)
    N = C[3:6, :]

    rel_axes = read_axis(rel_path)
    gt_axes = read_axis(gt_path) if os.path.isfile(gt_path) else rel_axes
    vt_gt = canonicalize(gt_axes[:, 0])
    vt_rel = canonicalize(rel_axes[:, 0])

    n = C.shape[1]
    step = effective_step(n, 10)
    Cd = C[:, ::step]
    nd = Cd.shape[1]

    all_cands = []
    for seed in range(10):
        rng = np.random.default_rng(seed)
        for _ in range(1000):
            kidx = rng.choice(nd, 6, replace=False)
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
                all_cands.append(vt)
            except Exception:
                pass

    V = np.column_stack(all_cands)
    reps, sizes = _cluster_union(V)

    # Filter candidate basins:
    # 1. Physical clearance window: 25.0 <= d(C, L) <= 105.0 mm
    # 2. Axial normal <= 0.6
    valid_reps = []
    for j in range(reps.shape[1]):
        cand = reps[:, j]
        d_c = centroid_distance(cand, C)
        if d_c < DEFAULT_CLEARANCE_MM or d_c > MAX_CLEARANCE_MM:
            continue
        a_cand = cand[:3] / np.linalg.norm(cand[:3])
        mean_axial = np.mean(np.abs(a_cand @ N))
        if mean_axial > 0.6:
            continue
        valid_reps.append(cand)

    if not valid_reps:
        valid_reps = [reps[:, 0]]

    V_valid = np.column_stack(valid_reps)
    costs = [worst_wall_normalized_cost(V_valid[:, j], C0, C1, min_clearance_mm=DEFAULT_CLEARANCE_MM)
             for j in range(V_valid.shape[1])]
    order = np.argsort(costs)

    top = canonicalize(V_valid[:, order[0]])
    ang_top_gt = angle_deg(top, vt_gt)
    ang_top_rel = angle_deg(top, vt_rel)

    top3_angs = [min(angle_deg(canonicalize(V_valid[:, order[k]]), vt_gt),
                     angle_deg(canonicalize(V_valid[:, order[k]]), vt_rel))
                 for k in range(min(3, len(order)))]
    top6_angs = [min(angle_deg(canonicalize(V_valid[:, order[k]]), vt_gt),
                     angle_deg(canonicalize(V_valid[:, order[k]]), vt_rel))
                 for k in range(min(6, len(order)))]

    return dict(
        p=p,
        K=min(6, len(order)),
        ang_top=min(ang_top_gt, ang_top_rel),
        best_top3=min(top3_angs),
        best_top6=min(top6_angs),
        d_top=centroid_distance(top, C),
        d_gt=centroid_distance(vt_gt, C)
    )

print(f"{'Piece':<8} {'K':<4} {'Ang_Top':<10} {'Best_Top3':<10} {'Best_Top6':<10} {'d_Top(mm)':<10} {'d_GT(mm)':<10}")
print("-" * 75)
failing_10 = [3, 9, 23, 24, 25, 26, 27, 28, 29, 31]
all_res = []
for p in range(1, 35):
    r = run_piece(p)
    if r is None: continue
    all_res.append(r)
    mark = " *" if p in failing_10 else ""
    print(f"Piece {r['p']:02d}{mark:<2} {r['K']:<4} {r['ang_top']:<10.2f} {r['best_top3']:<10.2f} "
          f"{r['best_top6']:<10.2f} {r['d_top']:<10.1f} {r['d_gt']:<10.1f}", flush=True)

print("\n=== SUMMARY OVER 34 PIECES ===")
top1_under_10 = sum(1 for r in all_res if r['ang_top'] <= 10.0)
top3_under_10 = sum(1 for r in all_res if r['best_top3'] <= 10.0)
top6_under_10 = sum(1 for r in all_res if r['best_top6'] <= 10.0)
print(f"Top 1 (K=1) <= 10 deg: {top1_under_10}/34 ({top1_under_10/34*100:.1f}%)")
print(f"Top 3 (K=3) <= 10 deg: {top3_under_10}/34 ({top3_under_10/34*100:.1f}%)")
print(f"Top 6 (K=6) <= 10 deg: {top6_under_10}/34 ({top6_under_10/34*100:.1f}%)")

f10_res = [r for r in all_res if r['p'] in failing_10]
f10_top1 = sum(1 for r in f10_res if r['ang_top'] <= 10.0)
f10_top3 = sum(1 for r in f10_res if r['best_top3'] <= 10.0)
f10_top6 = sum(1 for r in f10_res if r['best_top6'] <= 10.0)
print(f"Failing 10: K=1 <= 10 deg: {f10_top1}/10; K=3 <= 10 deg: {f10_top3}/10; K=6 <= 10 deg: {f10_top6}/10")
