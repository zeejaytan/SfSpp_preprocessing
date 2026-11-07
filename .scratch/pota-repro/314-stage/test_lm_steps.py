import os, sys, numpy as np
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_313")
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"

from sfs_axes.pottmann import compute_pottmann_axis
from sfs_axes.normalized import (
    compute_normalized_residual,
    refine_axis_normalized,
    worst_wall_normalized_cost,
    centroid_distance,
)
from sfs_axes.potsac import _cluster_union, effective_step
from sfs_axes.io_axes import read_axes, direction_angle_deg

def canonicalize(vt):
    vt = np.asarray(vt, dtype=float).copy()
    if vt[2] < 0: vt[:3] = -vt[:3]
    return vt

for p in [3, 28]:
    stem = f"Pot_E_Piece_{p:02d}"
    s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
    s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)

    rel_ax = read_axes(f"{CORPUS}/Axes/{stem}_Axis.xyz")
    gt_path = f"{CORPUS}/Ground Truth Axes/{stem}_Axis.xyz"
    gt_ax = read_axes(gt_path) if os.path.isfile(gt_path) else rel_ax
    v_gt = canonicalize(gt_ax[:, 0])

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
    
    print(f"\nPiece {p:02d}: testing all true basins with small-step LM refinement")
    for j in range(reps.shape[1]):
        cand = reps[:, j]
        ang = direction_angle_deg(cand[:3], v_gt[:3])
        if ang < 12.0:
            d = centroid_distance(cand, C)
            c = worst_wall_normalized_cost(cand, s0, s1, min_clearance_mm=25.0)
            print(f"  Basin {j}: ang={ang:.2f}deg, d={d:.1f}mm, size={sizes[j]}, cost={c:.6f}")
            # Try 5 iters of LM
            for it in [2, 5, 10, 20]:
                v_ref = refine_axis_normalized(cand, C, max_iters=it, tolerance=1e-3)
                ang_r = direction_angle_deg(v_ref[:3], v_gt[:3])
                d_r = centroid_distance(v_ref, C)
                c_r = worst_wall_normalized_cost(v_ref, s0, s1, min_clearance_mm=25.0)
                print(f"    -> LM {it:2d} iters: ang={ang_r:.2f}deg, d={d_r:.1f}mm, cost={c_r:.6f}")
