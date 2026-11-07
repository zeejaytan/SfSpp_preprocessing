import os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from sfs_axes.normalized import refine_axis_normalized, worst_wall_normalized_cost, centroid_distance
from sfs_axes.io_axes import read_axes, direction_angle_deg
from test_pipeline_clean_7pieces import canonicalize
from inspect_piece31_all import reps, sizes, C, s0, s1, v_gt

cand38 = reps[:, 38]
cand82 = reps[:, 82]

print("=== PIECE 31 BASIN 38 & 82 REFINEMENT INVESTIGATION ===")
print(f"Basin 38 raw: ang={direction_angle_deg(cand38[:3], v_gt[:3]):.2f}, cost={worst_wall_normalized_cost(cand38, s0, s1, min_clearance_mm=0.0):.6f}, d={centroid_distance(cand38, C):.1f}")
print(f"Basin 82 raw: ang={direction_angle_deg(cand82[:3], v_gt[:3]):.2f}, cost={worst_wall_normalized_cost(cand82, s0, s1, min_clearance_mm=0.0):.6f}, d={centroid_distance(cand82, C):.1f}")

for iters in [1, 2, 3, 5, 10]:
    v_ref38 = refine_axis_normalized(cand38, C, max_iters=iters, tolerance=1e-5)
    drift38 = direction_angle_deg(v_ref38[:3], cand38[:3])
    ang38 = direction_angle_deg(v_ref38[:3], v_gt[:3])
    c38 = worst_wall_normalized_cost(v_ref38, s0, s1, min_clearance_mm=0.0)
    print(f"Basin 38 iters={iters:2d}: ang={ang38:.2f}deg, cost={c38:.6f}, drift={drift38:.2f}deg")

for iters in [1, 2, 3, 5, 10]:
    v_ref82 = refine_axis_normalized(cand82, C, max_iters=iters, tolerance=1e-5)
    drift82 = direction_angle_deg(v_ref82[:3], cand82[:3])
    ang82 = direction_angle_deg(v_ref82[:3], v_gt[:3])
    c82 = worst_wall_normalized_cost(v_ref82, s0, s1, min_clearance_mm=0.0)
    print(f"Basin 82 iters={iters:2d}: ang={ang82:.2f}deg, cost={c82:.6f}, drift={drift82:.2f}deg")
