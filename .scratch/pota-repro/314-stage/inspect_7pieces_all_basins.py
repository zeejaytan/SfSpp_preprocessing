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

    print(f"\n=================== Piece {p:02d} ({len(all_cands)} draws -> {reps.shape[1]} basins) ===================")
    rows = []
    for j in range(reps.shape[1]):
        cand = reps[:, j]
        d_c = centroid_distance(cand, C)
        a = cand[:3] / np.linalg.norm(cand[:3])
        mean_ax = np.mean(np.abs(a @ C[3:6, :]))
        err0 = compute_normalized_residual(cand, s0)[0, :]
        err1 = compute_normalized_residual(cand, s1)[0, :]
        c0 = float(np.mean(apply_robustifier(robustifier_huber, err0, None)))
        c1 = float(np.mean(apply_robustifier(robustifier_huber, err1, None)))
        cost = max(c0, c1)

        ang_gt = direction_angle_deg(cand[:3], v_gt[:3])
        ang_rel = direction_angle_deg(cand[:3], v_rel[:3])
        ang_rel2 = direction_angle_deg(cand[:3], v_rel2[:3]) if v_rel2 is not None else 999.0
        best_ang = min(ang_gt, ang_rel, ang_rel2)

        rows.append({
            "idx": j, "cand": cand, "d": d_c, "size": sizes[j],
            "cost": cost, "mean_ax": mean_ax, "ang": best_ang,
            "ang_gt": ang_gt, "ang_rel": ang_rel
        })

    # Filter to physical candidates: d >= 25.0 (for wall) and d <= 120.0 and mean_ax <= 0.50
    # For Piece 31: d can be anything if base, but line 2 has d=71.5
    valid_rows = [r for r in rows if (r["d"] >= 25.0 or p == 31) and r["d"] <= 120.0 and r["mean_ax"] <= 0.50]
    
    # Sort by cost alone
    valid_rows.sort(key=lambda x: x["cost"])
    print(f"--- Top 10 by normalized cost alone (filtered 25 <= d <= 120, mean_ax <= 0.50): ---")
    for rank, r in enumerate(valid_rows[:10]):
        status = "TRUE (<10deg)" if r["ang"] <= 10.0 else "DECOY"
        print(f"  Rank {rank:2d} | Basin {r['idx']:3d} | size={r['size']:4d} | d={r['d']:5.1f}mm | mean_ax={r['mean_ax']:.3f} | cost={r['cost']:.6f} | ang={r['ang']:5.2f}deg [{status}]")

    # Let's see where the true axes (< 10 deg) are located:
    true_rows = [r for r in valid_rows if r["ang"] <= 10.0]
    print(f"  Total true basins in pool: {len(true_rows)}")
    for r in true_rows[:5]:
        print(f"    -> True Basin {r['idx']:3d}: size={r['size']:4d}, d={r['d']:5.1f}mm, cost={r['cost']:.6f}, ang={r['ang']:.2f}deg")
