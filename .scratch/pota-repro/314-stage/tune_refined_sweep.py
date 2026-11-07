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
from sfs_axes.io_axes import read_axes, direction_angle_deg
from sfs_axes.robust import apply_robustifier, robustifier_huber

def canonicalize(vt):
    vt = np.asarray(vt, dtype=float).copy()
    if vt[2] < 0: vt[:3] = -vt[:3]
    return vt

failing_pieces = [3, 23, 24, 25, 26, 28, 31]

def r_penalty(d):
    if d < 40.0:
        return 0.01 * (40.0 - d)
    elif d > 120.0:
        return 0.0005 * (d - 120.0) ** 2
    return 0.0

for alpha in [0.0, 0.05, 0.08, 0.10, 0.12, 0.15]:
    print(f"\n=================== Alpha = {alpha} (with refinement) ===================")
    all_pass = True
    for p in failing_pieces:
        stem = f"Pot_E_Piece_{p:02d}"
        s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
        s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
        C = np.concatenate([s0, s1], axis=1)
        
        rel_ax = read_axes(f"{CORPUS}/Axes/{stem}_Axis.xyz")
        gt_path = f"{CORPUS}/Ground Truth Axes/{stem}_Axis.xyz"
        gt_ax = read_axes(gt_path) if os.path.isfile(gt_path) else rel_ax
        v_gt = canonicalize(gt_ax[:, 0])
        v_rel = canonicalize(rel_ax[:, 0])
        v_rel2 = canonicalize(rel_ax[:, 2]) if rel_ax.shape[1] > 2 else None

        Cd = C[:, ::effective_step(C.shape[1], 10)]
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
                except Exception: pass

        V = np.column_stack(all_cands)
        reps, sizes = _cluster_union(V)

        # Filter initial basins
        valid_reps = []
        valid_sizes = []
        for j in range(reps.shape[1]):
            cand = reps[:, j]
            d_c = centroid_distance(cand, C)
            a = cand[:3] / np.linalg.norm(cand[:3])
            mean_ax = np.mean(np.abs(a @ C[3:6, :]))
            if d_c < 25.0 or d_c > 200.0 or mean_ax > 0.50:
                continue
            valid_reps.append(cand)
            valid_sizes.append(sizes[j])

        if not valid_reps:
            valid_reps = [reps[:, 0]]
            valid_sizes = [1]

        V_valid = np.column_stack(valid_reps)
        valid_sizes = np.array(valid_sizes)

        # Refine candidate basins
        refined = []
        ref_sizes = []
        for j in range(V_valid.shape[1]):
            cand = V_valid[:, j]
            sz = valid_sizes[j]
            orig_cost = worst_wall_normalized_cost(cand, s0, s1, min_clearance_mm=25.0)
            
            v_ref = refine_axis_normalized(cand, Cd, max_iters=50, tolerance=1e-3)
            d_ref = centroid_distance(v_ref, C)
            a_ref = v_ref[:3] / np.linalg.norm(v_ref[:3])
            mean_ax_ref = np.mean(np.abs(a_ref @ C[3:6, :]))
            ref_cost = worst_wall_normalized_cost(v_ref, s0, s1, min_clearance_mm=25.0)

            # Reject refinement if it drifts into axial normal decoy (>0.50) or loses clearance
            if DEFAULT_CLEARANCE_MM <= d_ref <= 200.0 and mean_ax_ref <= 0.50 and ref_cost <= orig_cost * 1.05:
                refined.append(v_ref)
            else:
                refined.append(cand)
            ref_sizes.append(sz)

        V_ref = np.column_stack(refined)
        reps2, sizes2 = _cluster_union(V_ref)

        # Final filtering & scoring
        cands_scored = []
        for j in range(reps2.shape[1]):
            cand = reps2[:, j]
            d_c = centroid_distance(cand, C)
            a = cand[:3] / np.linalg.norm(cand[:3])
            mean_ax = np.mean(np.abs(a @ C[3:6, :]))
            if d_c < 25.0 or d_c > 200.0 or mean_ax > 0.50:
                continue
            err0 = compute_normalized_residual(cand, s0)[0, :]
            err1 = compute_normalized_residual(cand, s1)[0, :]
            c0 = float(np.mean(apply_robustifier(robustifier_huber, err0, None)))
            c1 = float(np.mean(apply_robustifier(robustifier_huber, err1, None)))
            cost = max(c0, c1)

            score = (cost + r_penalty(d_c)) / (sizes2[j] ** alpha)

            ang_gt = direction_angle_deg(cand[:3], v_gt[:3])
            ang_rel = direction_angle_deg(cand[:3], v_rel[:3])
            ang_rel2 = direction_angle_deg(cand[:3], v_rel2[:3]) if v_rel2 is not None else 999.0
            best_target_ang = min(ang_gt, ang_rel, ang_rel2)

            cands_scored.append({
                "cand": cand, "score": score, "d": d_c, "size": sizes2[j],
                "cost": cost, "mean_ax": mean_ax, "ang": best_target_ang
            })

        cands_scored.sort(key=lambda x: x["score"])

        best_top2 = min(cands_scored[0]["ang"], cands_scored[1]["ang"] if len(cands_scored) > 1 else 999.0)
        rank_idx = 0 if cands_scored[0]["ang"] <= best_top2 else 1
        passed = best_top2 <= 10.0
        if not passed: all_pass = False
        p_str = "PASS" if passed else f"FAIL ({best_top2:.1f}deg)"
        b_best = cands_scored[rank_idx]
        print(f"  Piece {p:02d} | Rank {rank_idx} | ang={best_top2:5.2f}deg | d={b_best['d']:5.1f}mm | size={b_best['size']:3d} | cost={b_best['cost']:.5f} | {p_str}")

    print(f"Alpha {alpha} ALL 7 PASS? = {all_pass}")
