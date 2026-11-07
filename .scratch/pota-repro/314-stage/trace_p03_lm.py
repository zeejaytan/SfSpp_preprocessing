import os
import sys
import numpy as np

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_313")

from sfs_axes.normalized import (
    compute_normalized_residual,
    worst_wall_normalized_cost,
    centroid_distance,
    DEFAULT_CLEARANCE_MM
)
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

print(f"Piece 03: GT vs Rel angle = {direction_angle_deg(v_gt[:3], v_rel[:3]):.2f} deg")

# Evaluate cost of v_rel and v_gt
c_rel = worst_wall_normalized_cost(v_rel, C0, C1, min_clearance_mm=25.0)
c_gt = worst_wall_normalized_cost(v_gt, C0, C1, min_clearance_mm=25.0)
d_rel = centroid_distance(v_rel, C)
d_gt = centroid_distance(v_gt, C)
m_rel = np.mean(np.abs(v_rel[:3] @ C[3:6, :]))
m_gt = np.mean(np.abs(v_gt[:3] @ C[3:6, :]))

print(f"Rel: cost={c_rel:.6f}, d={d_rel:.2f}mm, mean_ax={m_rel:.3f}")
print(f"GT : cost={c_gt:.6f}, d={d_gt:.2f}mm, mean_ax={m_gt:.3f}")

# Check step by step LM from v_rel
from sfs_axes.refine import cao_update_func, optimize_using_lm
from sfs_axes.robust import robustifier_huber

Cd = C[:, ::effective_step(C.shape[1], 10)]

def res_func(v):
    return compute_normalized_residual(v, Cd, with_jacobian=True)

# Run LM with verbose=True
print("\nRunning LM refinement from v_rel:")
v_cur = v_rel.copy()
for it in range(1, 15):
    v_next = optimize_using_lm(v_cur, res_func, cao_update_func, robustifier_huber, max_iters=1, func_tol=1e-7, verbose=False)[0]
    v_next[:3] /= np.linalg.norm(v_next[:3])
    v_next[3:6] -= (v_next[:3] @ v_next[3:6]) * v_next[:3]
    ang_to_rel = direction_angle_deg(v_next[:3], v_rel[:3])
    d_next = centroid_distance(v_next, C)
    m_next = np.mean(np.abs(v_next[:3] @ C[3:6, :]))
    c_next = worst_wall_normalized_cost(v_next, C0, C1, min_clearance_mm=25.0)
    print(f"  iter {it:2d}: ang_to_rel={ang_to_rel:5.2f}deg, d={d_next:5.2f}mm, mean_ax={m_next:.3f}, cost={c_next:.6f}")
    v_cur = v_next
