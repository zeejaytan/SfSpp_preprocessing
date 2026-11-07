import os
import sys
import numpy as np

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_313")

from sfs_axes.pottmann import compute_pottmann_axis
from sfs_axes.normalized import refine_axis_normalized, worst_wall_normalized_cost, centroid_distance
from sfs_axes.io_axes import read_axes, direction_angle_deg
from sfs_axes.potsac import effective_step

stem = "Pot_E_Piece_03"
s0_path = f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz"
s1_path = f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz"
rel_path = f"{CORPUS}/Axes/{stem}_Axis.xyz"
gt_path = f"{CORPUS}/Ground Truth Axes/{stem}_Axis.xyz"

C0 = np.loadtxt(s0_path, usecols=range(6)).T
C1 = np.loadtxt(s1_path, usecols=range(6)).T
C = np.concatenate([C0, C1], axis=1)

rel = read_axes(rel_path)
gt = read_axes(gt_path)
v_rel = rel[:, 0].copy()
if v_rel[2] < 0: v_rel[:3] = -v_rel[:3]
v_gt = gt[:, 0].copy()
if v_gt[2] < 0: v_gt[:3] = -v_gt[:3]

Cd = C[:, ::effective_step(C.shape[1], 10)]
nd = Cd.shape[1]

# Find the draw with seed 0..20 that produced ang_rel = 0.1
for seed in range(20):
    rng = np.random.default_rng(seed)
    for draw_idx in range(1000):
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
            ang_rel = direction_angle_deg(vt[:3], v_rel[:3])
            d = centroid_distance(vt, C)
            if ang_rel < 1.0 and d >= 25.0:
                print(f"Seed {seed} draw {draw_idx}: ang_rel={ang_rel:.2f}, d={d:.2f}")
                print(f"  vt={vt}")
                # Now trace refine_axis_normalized with verbose=True
                vt_ref = refine_axis_normalized(vt, Cd, max_iters=50, tolerance=1e-3, verbose=True)
                ang_ref = direction_angle_deg(vt_ref[:3], v_rel[:3])
                d_ref = centroid_distance(vt_ref, C)
                print(f"  Result: ang_ref={ang_ref:.2f}, d_ref={d_ref:.2f}")
                sys.exit(0)
        except Exception: pass
