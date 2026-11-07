import os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from test_pipeline_clean_7pieces import canonicalize, r_prior
from sfs_axes.normalized import centroid_distance, worst_wall_normalized_cost
from sfs_axes.io_axes import read_axes, direction_angle_deg

# Let's inspect Piece 31's top basins directly
stem = "Pot_E_Piece_31"
s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
C = np.concatenate([s0, s1], axis=1)

rel_ax = read_axes(f"{CORPUS}/Axes/{stem}_Axis.xyz")
gt_path = f"{CORPUS}/Ground Truth Axes/{stem}_Axis.xyz"
gt_ax = read_axes(gt_path) if os.path.isfile(gt_path) else rel_ax
v_gt = canonicalize(gt_ax[:, 0])

# Run quick test of ranking formulas on Piece 31
# We know the candidates:
# Decoy A: ang=15.08, d=78.6, cost=0.019108, size=14, mean_ax=0.096
# Decoy B: ang=34.16, d=79.3, cost=0.017139, size=5, mean_ax=0.134
# Decoy C: ang=38.28, d=73.2, cost=0.020379, size=18, mean_ax=0.346
# True C: ang=6.59, d=70.3, cost=0.020444, size=16, mean_ax=0.331
# True D: ang=6.37, d=74.2, cost=0.017489, size=1, mean_ax=0.360

# Notice: True D has cost = 0.017489, ang = 6.37 deg!
# Why did True D not get refined? Because size = 1!
# What about Basin 38: cost = 0.020444, ang = 6.59 deg!
# Why did Decoy B (cost=0.017139, size=5) beat Basin 38?
# Because Decoy B had cost 0.017139 vs 0.020444!
# And what was Decoy B? ang = 34.16 deg!

# Let's inspect Decoy B vs Basin 38:
# Does Decoy B have different residual distribution?
# Or does LM refinement on Basin 38 reduce its cost?
# Let's check!
from sfs_axes.normalized import refine_axis_normalized
# Let's refine Basin 38:
from inspect_piece31_all import reps, sizes
cand38 = reps[:, 38]
print("Basin 38 before refinement:")
print(f"ang={direction_angle_deg(cand38[:3], v_gt[:3]):.2f}, cost={worst_wall_normalized_cost(cand38, s0, s1, min_clearance_mm=0.0):.6f}")

v_ref38 = refine_axis_normalized(cand38, C, max_iters=50, tolerance=1e-5)
print("Basin 38 after refinement:")
print(f"ang={direction_angle_deg(v_ref38[:3], v_gt[:3]):.2f}, cost={worst_wall_normalized_cost(v_ref38, s0, s1, min_clearance_mm=0.0):.6f}, drift={direction_angle_deg(v_ref38[:3], cand38[:3]):.2f}")
