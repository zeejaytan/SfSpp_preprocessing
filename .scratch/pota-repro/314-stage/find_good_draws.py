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
)
from sfs_axes.potsac import effective_step

def read_axis(path):
    lines = [l.strip().split() for l in open(path) if l.strip()]
    axes = []
    for l in lines:
        axes.append(np.r_[[float(x) for x in l[3:6]], [float(x) for x in l[:3]]])
    return np.column_stack(axes)

def canonicalize(vt):
    vt = np.asarray(vt, dtype=float).copy()
    if vt[2] < 0: vt[:3] = -vt[:3]
    return vt

def angle_deg(v1, v2):
    a1 = v1[:3] / np.linalg.norm(v1[:3])
    a2 = v2[:3] / np.linalg.norm(v2[:3])
    cos = np.clip(abs(float(np.dot(a1, a2))), 0.0, 1.0)
    return float(np.degrees(np.arccos(cos)))

for p in [3, 23, 25, 31]:
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

    # Test raw Pottmann draws vs refinement
    good_draws = []
    for seed in range(20):
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
                ang_gt = angle_deg(vt, v_gt)
                ang_rel = angle_deg(vt, v_rel)
                d = centroid_distance(vt, C)
                if min(ang_gt, ang_rel) < 15.0 and d >= 25.0:
                    good_draws.append((vt, ang_gt, ang_rel, d))
            except Exception: pass

    print(f"\nPiece {p:02d}: found {len(good_draws)} raw draws with angle < 15 deg to GT/Rel and d >= 25mm")
    if good_draws:
        good_draws.sort(key=lambda x: min(x[1], x[2]))
        for g in good_draws[:5]:
            # test refining this draw
            vt_ref = refine_axis_normalized(g[0], Cd, max_iters=50, tolerance=1e-3)
            ang_ref_gt = angle_deg(vt_ref, v_gt)
            ang_ref_rel = angle_deg(vt_ref, v_rel)
            d_ref = centroid_distance(vt_ref, C)
            cost_ref = worst_wall_normalized_cost(vt_ref, C0, C1, min_clearance_mm=25.0)
            a_ref = vt_ref[:3] / np.linalg.norm(vt_ref[:3])
            mean_ax_ref = np.mean(np.abs(a_ref @ C[3:6, :]))
            print(f"  Draw: ang_gt={g[1]:5.1f} ang_rel={g[2]:5.1f} d={g[3]:5.1f} -> Refined: ang_gt={ang_ref_gt:5.1f} ang_rel={ang_ref_rel:5.1f} d={d_ref:5.1f} cost={cost_ref:.5f} mean_ax={mean_ax_ref:.2f}")
