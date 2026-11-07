import os
import sys
import numpy as np

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_313")

from sfs_axes.pottmann import compute_pottmann_axis
from sfs_axes.normalized import (
    compute_normalized_residual,
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

for weight in [0.0, 0.2, 0.3, 0.5]:
    print(f"\n=================== Basin size weight = {weight} ===================")
    all_pass = True
    for p in failing_pieces:
        stem = f"Pot_E_Piece_{p:02d}"
        s0_path = f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz"
        s1_path = f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz"
        rel_path = f"{CORPUS}/Axes/{stem}_Axis.xyz"
        gt_path = f"{CORPUS}/Ground Truth Axes/{stem}_Axis.xyz"
        if not os.path.isfile(gt_path): gt_path = rel_path

        C0 = np.loadtxt(s0_path, usecols=range(6)).T
        C1 = np.loadtxt(s1_path, usecols=range(6)).T
        C = np.concatenate([C0, C1], axis=1)

        rel_ax = read_axes(rel_path)
        gt_ax = read_axes(gt_path)
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

        # Filter: clearance >= 25 mm and mean_ax <= 0.50
        valid_idx = []
        for j in range(reps.shape[1]):
            cand = reps[:, j]
            d_c = centroid_distance(cand, C)
            a = cand[:3] / np.linalg.norm(cand[:3])
            mean_ax = np.mean(np.abs(a @ C[3:6, :]))
            if d_c >= 25.0 and d_c <= 200.0 and mean_ax <= 0.50:
                valid_idx.append(j)

        if not valid_idx:
            valid_idx = [0]

        max_size = max(sizes[j] for j in valid_idx)
        cands_scored = []
        for j in valid_idx:
            cand = reps[:, j]
            err0 = compute_normalized_residual(cand, C0)[0, :]
            err1 = compute_normalized_residual(cand, C1)[0, :]
            c0 = float(np.mean(apply_robustifier(robustifier_huber, err0, None)))
            c1 = float(np.mean(apply_robustifier(robustifier_huber, err1, None)))
            cost = max(c0, c1)
            
            d_c = centroid_distance(cand, C)
            # Physical vessel radius prior: center around 75 mm
            r_penalty = 0.0005 * (d_c - 75.0) ** 2
            
            # Combine cost with radius penalty and basin size
            score = (cost + r_penalty) / ((sizes[j] / max_size) ** weight)

            ang_gt = direction_angle_deg(cand[:3], v_gt[:3])
            ang_rel = direction_angle_deg(cand[:3], v_rel[:3])
            ang_rel2 = direction_angle_deg(cand[:3], v_rel2[:3]) if v_rel2 is not None else 999.0
            cands_scored.append({
                "cand": cand, "score": score, "d": d_c, "size": sizes[j],
                "ang_gt": ang_gt, "ang_rel": ang_rel, "ang_rel2": ang_rel2
            })

        cands_scored.sort(key=lambda x: x["score"])
        
        # Check top 2 candidates
        best_ang = min(cands_scored[0]["ang_gt"], cands_scored[0]["ang_rel"], cands_scored[0]["ang_rel2"])
        best_d = cands_scored[0]["d"]
        best_rank = 0
        if len(cands_scored) > 1:
            ang1 = min(cands_scored[1]["ang_gt"], cands_scored[1]["ang_rel"], cands_scored[1]["ang_rel2"])
            if ang1 < best_ang:
                best_ang = ang1
                best_d = cands_scored[1]["d"]
                best_rank = 1

        passed = best_ang <= 10.0
        if not passed: all_pass = False
        p_str = "PASS" if passed else f"FAIL ({best_ang:.1f}deg)"
        print(f"  Piece {p:02d} | Rank {best_rank} | Ang={best_ang:5.2f}deg | d={best_d:5.1f}mm | {p_str}")
    print(f"All 7 pieces pass? {all_pass}")
