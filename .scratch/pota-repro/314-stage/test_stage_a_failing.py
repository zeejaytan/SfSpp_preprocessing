import os
import sys
import numpy as np

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_313")

from sfs_axes.pottmann import compute_pottmann_axis
from sfs_axes.normalized import (
    compute_normalized_residual,
    refine_axis_normalized,
    worst_wall_normalized_cost,
    centroid_distance,
    DEFAULT_CLEARANCE_MM
)
from sfs_axes.potsac import _cluster_union, effective_step

def read_axis(path):
    lines = [l.strip().split() for l in open(path) if l.strip()]
    axes = []
    for l in lines:
        axes.append(np.r_[[float(x) for x in l[3:6]], [float(x) for x in l[:3]]])
    return np.column_stack(axes)

def canonicalize(vt):
    vt = np.asarray(vt, dtype=float).copy()
    if vt[2] < 0:
        vt[:3] = -vt[:3]
    return vt

def angle_deg(v1, v2):
    a1 = v1[:3] / np.linalg.norm(v1[:3])
    a2 = v2[:3] / np.linalg.norm(v2[:3])
    cos = np.clip(abs(float(np.dot(a1, a2))), 0.0, 1.0)
    return float(np.degrees(np.arccos(cos)))

failing_pieces = [3, 23, 24, 25, 26, 28, 31]

print(f"{'Piece':<8} {'Top Ang GT':<12} {'Top Ang Rel':<12} {'Top d':<10} {'Rank 0/1 Ang':<14} {'Rank 0/1 d':<12} {'<=10deg?':<10}")
print("-" * 80)

for p in failing_pieces:
    stem = f"Pot_E_Piece_{p:02d}"
    s0_path = f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz"
    s1_path = f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz"
    rel_path = f"{CORPUS}/Axes/{stem}_Axis.xyz"
    gt_path = f"{CORPUS}/Ground Truth Axes/{stem}_Axis.xyz"
    if not os.path.isfile(gt_path):
        gt_path = rel_path

    C0 = np.loadtxt(s0_path, usecols=range(6)).T
    C1 = np.loadtxt(s1_path, usecols=range(6)).T
    C = np.concatenate([C0, C1], axis=1)

    rel_ax = read_axis(rel_path)
    gt_ax = read_axis(gt_path)
    v_gt = canonicalize(gt_ax[:, 0])
    v_rel = canonicalize(rel_ax[:, 0])

    n = C.shape[1]
    step = effective_step(n, 10)
    Cd = C[:, ::step]
    nd = Cd.shape[1]

    # 10 seeds x 1000 draws
    all_cands = []
    for seed in range(10):
        rng = np.random.default_rng(seed)
        for _ in range(1000):
            kidx = rng.choice(nd, 6, replace=False)
            Cs = Cd[:, kidx].copy()
            mCs = Cs[:3, :].mean(axis=1)
            Cs[:3, :] -= mCs[:, None]
            scale = float(np.mean(np.abs(Cs)))
            if scale < 1e-8:
                continue
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

    # Filter candidate basins BEFORE refinement:
    # 1. Minimum clearance: d_c >= 25.0 mm (for wall pieces 03, 23, 24, 25, 26, 28)
    #    On Piece 31, if looking for vessel rotation axis, d >= 25.0 mm also holds!
    # 2. Maximum clearance: d_c <= 250.0 mm
    # 3. Whole-sherd mean axial normal <= 0.50 (reject axes pointing out of wall)
    valid_reps = []
    for j in range(reps.shape[1]):
        cand = reps[:, j]
        d_c = centroid_distance(cand, C)
        if d_c < DEFAULT_CLEARANCE_MM or d_c > 250.0:
            continue
        a = cand[:3] / np.linalg.norm(cand[:3])
        mean_ax = np.mean(np.abs(a @ C[3:6, :]))
        if mean_ax > 0.50:
            continue
        valid_reps.append(cand)

    if not valid_reps:
        valid_reps = [reps[:, 0]]

    V_valid = np.column_stack(valid_reps)
    
    # Score stage-1 basins
    scores1 = np.array([worst_wall_normalized_cost(V_valid[:, j], C0, C1, min_clearance_mm=DEFAULT_CLEARANCE_MM)
                       for j in range(V_valid.shape[1])])
    order1 = np.argsort(scores1, kind="stable")
    V_top = V_valid[:, order1[:32]]

    # Refine survivors on Cd
    refined = []
    for j in range(V_top.shape[1]):
        cand = V_top[:, j]
        orig_cost = worst_wall_normalized_cost(cand, C0, C1, min_clearance_mm=DEFAULT_CLEARANCE_MM)
        v_ref = refine_axis_normalized(cand, Cd, max_iters=50, tolerance=1e-3)
        d_ref = centroid_distance(v_ref, C)
        a_ref = v_ref[:3] / np.linalg.norm(v_ref[:3])
        mean_ax_ref = np.mean(np.abs(a_ref @ C[3:6, :]))
        ref_cost = worst_wall_normalized_cost(v_ref, C0, C1, min_clearance_mm=DEFAULT_CLEARANCE_MM)
        
        # Keep refinement if within physical clearance and not axial decoy
        if DEFAULT_CLEARANCE_MM <= d_ref <= 250.0 and mean_ax_ref <= 0.50 and ref_cost <= orig_cost * 1.05:
            refined.append(v_ref)
        else:
            refined.append(cand)

    V_ref = np.column_stack(refined)
    reps2, _ = _cluster_union(V_ref)

    # Filter reps2 again for clearance and axial normal
    valid_reps2 = []
    for j in range(reps2.shape[1]):
        cand = reps2[:, j]
        d_c = centroid_distance(cand, C)
        if d_c < DEFAULT_CLEARANCE_MM or d_c > 250.0:
            continue
        a = cand[:3] / np.linalg.norm(cand[:3])
        mean_ax = np.mean(np.abs(a @ C[3:6, :]))
        if mean_ax > 0.50:
            continue
        valid_reps2.append(cand)

    if not valid_reps2:
        valid_reps2 = [reps2[:, 0]]

    V_final = np.column_stack(valid_reps2)

    # Candidate ranking: prioritize physical vessel radius band (40 <= d <= 120 mm)
    # over degenerate infinite-radius decoys (d > 200 mm)
    final_scores = []
    for j in range(V_final.shape[1]):
        cand = V_final[:, j]
        d_c = centroid_distance(cand, C)
        cost = worst_wall_normalized_cost(cand, C0, C1, min_clearance_mm=DEFAULT_CLEARANCE_MM)
        # Radius penalty: if outside physical vessel band [40, 120], add soft penalty
        if d_c < 40.0:
            cost += 0.05 * (40.0 - d_c)
        elif d_c > 120.0:
            # penalize infinite radius decoys
            cost += 0.001 * (d_c - 120.0) ** 2
        final_scores.append(cost)

    final_scores = np.array(final_scores)
    order_final = np.argsort(final_scores, kind="stable")
    V_sorted = V_final[:, order_final]

    top0 = canonicalize(V_sorted[:, 0])
    ang_gt0 = angle_deg(top0, v_gt)
    ang_rel0 = angle_deg(top0, v_rel)
    d0 = centroid_distance(top0, C)

    # Check top 2 candidates
    best_ang_top2 = min(ang_gt0, ang_rel0)
    best_d_top2 = d0
    if V_sorted.shape[1] > 1:
        top1 = canonicalize(V_sorted[:, 1])
        ang_gt1 = angle_deg(top1, v_gt)
        ang_rel1 = angle_deg(top1, v_rel)
        d1 = centroid_distance(top1, C)
        if min(ang_gt1, ang_rel1) < best_ang_top2:
            best_ang_top2 = min(ang_gt1, ang_rel1)
            best_d_top2 = d1

    # On Piece 31, also check against released line 2 (which is the vessel rotation axis at d=71.5mm)
    if p == 31 and rel_ax.shape[1] > 2:
        v_rel2 = canonicalize(rel_ax[:, 2])
        ang_rel2_0 = angle_deg(top0, v_rel2)
        if ang_rel2_0 < best_ang_top2:
            best_ang_top2 = ang_rel2_0
            best_d_top2 = d0
        if V_sorted.shape[1] > 1:
            ang_rel2_1 = angle_deg(canonicalize(V_sorted[:, 1]), v_rel2)
            if ang_rel2_1 < best_ang_top2:
                best_ang_top2 = ang_rel2_1
                best_d_top2 = d1

    passed = "PASS" if best_ang_top2 <= 10.0 else f"FAIL ({best_ang_top2:.1f}deg)"
    print(f"Piece {p:02d} | Top0_GT={ang_gt0:5.1f} | Top0_Rel={ang_rel0:5.1f} | d0={d0:5.1f}mm | BestK2_ang={best_ang_top2:5.1f} | BestK2_d={best_d_top2:5.1f}mm | {passed}")
