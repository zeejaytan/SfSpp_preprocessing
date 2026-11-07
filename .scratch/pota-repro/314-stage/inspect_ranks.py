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

for p in [3, 24, 25, 26, 31]:
    stem = f"Pot_E_Piece_{p:02d}"
    s0_path = f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz"
    s1_path = f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz"
    rel_path = f"{CORPUS}/Axes/{stem}_Axis.xyz"
    gt_path = f"{CORPUS}/Ground Truth Axes/{stem}_Axis.xyz"
    if not os.path.isfile(gt_path): gt_path = rel_path

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

    # Let's see all basins with clearance >= 25 and mean_ax <= 0.50
    valid_reps = []
    for j in range(reps.shape[1]):
        cand = reps[:, j]
        d_c = centroid_distance(cand, C)
        a = cand[:3] / np.linalg.norm(cand[:3])
        mean_ax = np.mean(np.abs(a @ C[3:6, :]))
        if d_c >= 25.0 and d_c <= 250.0 and mean_ax <= 0.50:
            valid_reps.append(cand)

    V_valid = np.column_stack(valid_reps)
    print(f"\n================ Piece {p:02d} ({V_valid.shape[1]} valid basins) ================")
    
    # refine each valid basin on Cd
    basins = []
    for j in range(V_valid.shape[1]):
        cand = V_valid[:, j]
        v_ref = refine_axis_normalized(cand, Cd, max_iters=50, tolerance=1e-3)
        d_ref = centroid_distance(v_ref, C)
        a_ref = v_ref[:3] / np.linalg.norm(v_ref[:3])
        mean_ax_ref = np.mean(np.abs(a_ref @ C[3:6, :]))
        cost_C = worst_wall_normalized_cost(v_ref, C0, C1, min_clearance_mm=25.0)
        c0 = worst_wall_normalized_cost(v_ref, C0, None, min_clearance_mm=25.0)
        c1 = worst_wall_normalized_cost(v_ref, C1, None, min_clearance_mm=25.0)
        ang_gt = angle_deg(v_ref, v_gt)
        ang_rel = angle_deg(v_ref, v_rel)
        if p == 31 and rel_ax.shape[1] > 2:
            ang_rel2 = angle_deg(v_ref, canonicalize(rel_ax[:, 2]))
        else:
            ang_rel2 = 999.0

        basins.append({
            "v": v_ref, "d": d_ref, "mean_ax": mean_ax_ref,
            "cost": cost_C, "c0": c0, "c1": c1,
            "ang_gt": ang_gt, "ang_rel": ang_rel, "ang_rel2": ang_rel2
        })

    # Sort by min angle to GT/rel
    basins_by_ang = sorted(basins, key=lambda b: min(b["ang_gt"], b["ang_rel"], b["ang_rel2"]))
    print("--- 3 closest to GT/rel: ---")
    for b in basins_by_ang[:3]:
        print(f"  ang_gt={b['ang_gt']:5.1f} | ang_rel={b['ang_rel']:5.1f} | ang_rel2={b['ang_rel2']:5.1f} | d={b['d']:5.1f}mm | mean_ax={b['mean_ax']:.2f} | cost={b['cost']:.5f} (c0={b['c0']:.5f}, c1={b['c1']:.5f})")

    # Sort by cost
    basins_by_cost = sorted(basins, key=lambda b: b["cost"])
    print("--- 3 lowest cost: ---")
    for b in basins_by_cost[:3]:
        print(f"  cost={b['cost']:.5f} (c0={b['c0']:.5f}, c1={b['c1']:.5f}) | d={b['d']:5.1f}mm | mean_ax={b['mean_ax']:.2f} | ang_gt={b['ang_gt']:5.1f} | ang_rel={b['ang_rel']:5.1f} | ang_rel2={b['ang_rel2']:5.1f}")
