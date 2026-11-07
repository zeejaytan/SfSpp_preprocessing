import os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from sfs_axes.normalized import refine_axis_normalized, worst_wall_normalized_cost, centroid_distance
from sfs_axes.io_axes import read_axes, direction_angle_deg
from inspect_piece31_all import reps, sizes, C, s0, s1, v_gt

cand54 = reps[:, 54]
print("=== PIECE 31 BASIN 54 INVESTIGATION ===")
print(f"Basin 54 raw: ang={direction_angle_deg(cand54[:3], v_gt[:3]):.2f}, cost={worst_wall_normalized_cost(cand54, s0, s1, min_clearance_mm=0.0):.6f}, d={centroid_distance(cand54, C):.1f}, size={sizes[54]}")

v_ref54 = refine_axis_normalized(cand54, C, max_iters=20, tolerance=1e-3)
drift54 = direction_angle_deg(v_ref54[:3], cand54[:3])
ang54 = direction_angle_deg(v_ref54[:3], v_gt[:3])
c54 = worst_wall_normalized_cost(v_ref54, s0, s1, min_clearance_mm=0.0)
print(f"Basin 54 ref: ang={ang54:.2f}deg, cost={c54:.6f}, drift={drift54:.2f}deg")
