import os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from sfs_axes.normalized import refine_axis_normalized, worst_wall_normalized_cost, centroid_distance
from sfs_axes.io_axes import read_axes, direction_angle_deg
from test_pipeline_clean_7pieces import canonicalize

stem = "Pot_E_Piece_31"
s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
C = np.concatenate([s0, s1], axis=1)

gt = read_axes(f"{CORPUS}/Ground Truth Axes/{stem}_Axis.xyz")
v_gt = canonicalize(gt[:, 0])

import pickle
with open("/data/gpfs/projects/punim2657/sfs_preprocessing/work_314/stage_a_data.pkl", "rb") as f:
    data = pickle.load(f)

cand10 = data[31]['cands'][:, 10]
a = cand10[:3] / np.linalg.norm(cand10[:3])
p0 = cand10[3:6] - (cand10[3:6] @ a) * a

dp = C[:3, :] - p0[:, None]
r = np.linalg.norm(dp - a[:, None] * (a @ dp)[None, :], axis=0)

# Filter out points near the axis (the base floor r < 35 mm)
wall_mask = r > 35.0
C_wall = C[:, wall_mask]
print(f"Total points: {C.shape[1]}, Wall points (r > 35mm): {C_wall.shape[1]}")

print("Cand 10 raw:")
print(f"  ang={direction_angle_deg(cand10[:3], v_gt[:3]):.2f}deg, cost={worst_wall_normalized_cost(cand10, s0, s1, min_clearance_mm=0.0):.6f}")

v_ref = refine_axis_normalized(cand10, C_wall, max_iters=20, tolerance=1e-3)
drift = direction_angle_deg(v_ref[:3], cand10[:3])
ang_ref = direction_angle_deg(v_ref[:3], v_gt[:3])
c_ref = worst_wall_normalized_cost(v_ref, s0, s1, min_clearance_mm=0.0)
print("Cand 10 refined on wall points:")
print(f"  ang={ang_ref:.2f}deg, cost={c_ref:.6f}, drift={drift:.2f}deg")
