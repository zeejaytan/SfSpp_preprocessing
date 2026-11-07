import os
import sys
import numpy as np

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_313")

from sfs_axes.pottmann import compute_pottmann_axis
from sfs_axes.normalized import (
    compute_normalized_residual,
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

def score_candidate(vt, C0, C1, C, r_min=40.0, r_max=120.0, axial_max=0.50):
    a = vt[:3] / np.linalg.norm(vt[:3])
    p0 = vt[3:6] - (vt[3:6] @ a) * a
    
    err0 = compute_normalized_residual(vt, C0)[0, :]
    err1 = compute_normalized_residual(vt, C1)[0, :]
    c0 = float(np.mean(apply_robustifier(robustifier_huber, err0, None)))
    c1 = float(np.mean(apply_robustifier(robustifier_huber, err1, None)))
    cost = max(c0, c1)

    mean_ax = float(np.mean(np.abs(a @ C[3:6, :])))
    if mean_ax > axial_max:
        cost += 100.0 * (mean_ax - axial_max) ** 2

    d = centroid_distance(vt, C)
    if d < 25.0:
        cost += 1000.0 * (25.0 - d) ** 2
    elif d > 200.0:
        cost += 0.001 * (d - 120.0) ** 2
    elif d < r_min:
        cost += 0.01 * (r_min - d)
    elif d > r_max:
        cost += 0.0005 * (d - r_max) ** 2

    return cost, mean_ax, d

failing_pieces = [3, 23, 24, 25, 26, 28, 31]

print(f"{'Piece':<8} {'Rank':<6} {'Ang_GT':<10} {'Ang_Rel':<10} {'Ang_Rel2':<10} {'d':<10} {'mean_ax':<10} {'cost':<12} {'<=10deg?'}")
print("-" * 90)

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

    # Filter out obvious perpendicular slicing decoys (d < 25 or mean_ax > 0.50)
    valid_reps = []
    for j in range(reps.shape[1]):
        cand = reps[:, j]
        d_c = centroid_distance(cand, C)
        a = cand[:3] / np.linalg.norm(cand[:3])
        mean_ax = np.mean(np.abs(a @ C[3:6, :]))
        if d_c < 25.0 or mean_ax > 0.50:
            continue
        valid_reps.append(cand)

    if not valid_reps:
        valid_reps = [reps[:, 0]]

    V_valid = np.column_stack(valid_reps)

    # Score each candidate using score_candidate
    cands_scored = []
    for j in range(V_valid.shape[1]):
        cand = V_valid[:, j]
        cost, mean_ax, d = score_candidate(cand, C0, C1, C)
        ang_gt = direction_angle_deg(cand[:3], v_gt[:3])
        ang_rel = direction_angle_deg(cand[:3], v_rel[:3])
        ang_rel2 = direction_angle_deg(cand[:3], v_rel2[:3]) if v_rel2 is not None else 999.0
        cands_scored.append({
            "vt": cand, "cost": cost, "mean_ax": mean_ax, "d": d,
            "ang_gt": ang_gt, "ang_rel": ang_rel, "ang_rel2": ang_rel2
        })

    cands_scored.sort(key=lambda x: x["cost"])

    for rank in range(min(3, len(cands_scored))):
        c = cands_scored[rank]
        best_ang = min(c["ang_gt"], c["ang_rel"], c["ang_rel2"])
        pass_str = "PASS" if best_ang <= 10.0 else ""
        print(f"Piece {p:02d} | Rank {rank} | {c['ang_gt']:8.2f} | {c['ang_rel']:8.2f} | {c['ang_rel2']:8.2f} | {c['d']:6.1f}mm | {c['mean_ax']:8.3f} | {c['cost']:10.6f} | {pass_str}")
