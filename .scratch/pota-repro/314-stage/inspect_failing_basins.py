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
from sfs_axes.potsac import _cluster_union, effective_step, is_base_sherd

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
    d_gt = centroid_distance(v_gt, C)
    d_rel = centroid_distance(v_rel, C)

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

    print(f"\n=======================================================")
    print(f"{stem}: GT d={d_gt:.1f}mm, Rel d={d_rel:.1f}mm | {V.shape[1]} draws -> {reps.shape[1]} basins")
    print(f"=======================================================")

    basin_info = []
    for j in range(reps.shape[1]):
        cand = reps[:, j]
        a = cand[:3] / np.linalg.norm(cand[:3])
        d_c = centroid_distance(cand, C)
        ang_gt = angle_deg(cand, v_gt)
        ang_rel = angle_deg(cand, v_rel)
        mean_ax = float(np.mean(np.abs(a @ C[3:6, :])))
        trojan = is_base_sherd(C, cand)
        
        # refine on Cd
        v_ref = refine_axis_normalized(cand, Cd, max_iters=50, tolerance=1e-3)
        a_ref = v_ref[:3] / np.linalg.norm(v_ref[:3])
        d_ref = centroid_distance(v_ref, C)
        ang_gt_ref = angle_deg(v_ref, v_gt)
        ang_rel_ref = angle_deg(v_ref, v_rel)
        mean_ax_ref = float(np.mean(np.abs(a_ref @ C[3:6, :])))
        cost_raw = worst_wall_normalized_cost(v_ref, C0, C1, min_clearance_mm=0.0)

        basin_info.append({
            "j": j, "size": sizes[j], "d_raw": d_c, "ang_gt_raw": ang_gt,
            "mean_ax_raw": mean_ax, "trojan": trojan,
            "v_ref": v_ref, "d_ref": d_ref, "ang_gt_ref": ang_gt_ref,
            "ang_rel_ref": ang_rel_ref, "mean_ax_ref": mean_ax_ref, "cost_raw": cost_raw
        })

    # Sort by ang_gt_ref to see where the good axes are
    basin_info_by_ang = sorted(basin_info, key=lambda x: min(x["ang_gt_ref"], x["ang_rel_ref"]))
    print("Top 5 closest to GT/Rel:")
    for b in basin_info_by_ang[:5]:
        print(f"  basin {b['j']:2d} (size {b['size']:3d}): ang_gt={b['ang_gt_ref']:5.1f} ang_rel={b['ang_rel_ref']:5.1f} d={b['d_ref']:5.1f} mean_ax={b['mean_ax_ref']:.2f} cost_raw={b['cost_raw']:.4f} trojan={b['trojan']}")

    # Sort by cost_raw without clearance filter
    basin_info_by_cost = sorted(basin_info, key=lambda x: x["cost_raw"])
    print("Top 5 lowest raw cost (no clearance):")
    for b in basin_info_by_cost[:5]:
        print(f"  basin {b['j']:2d} (size {b['size']:3d}): cost={b['cost_raw']:.4f} d={b['d_ref']:5.1f} mean_ax={b['mean_ax_ref']:.2f} ang_gt={b['ang_gt_ref']:5.1f} trojan={b['trojan']}")
