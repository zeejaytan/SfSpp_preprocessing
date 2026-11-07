import os
import sys
import numpy as np

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_313")

from sfs_axes.normalized import worst_wall_normalized_cost, centroid_distance

s0_path = f"{CORPUS}/Surfaces/Pot_E_Piece_03_Surface_0.xyz"
s1_path = f"{CORPUS}/Surfaces/Pot_E_Piece_03_Surface_1.xyz"
rel_path = f"{CORPUS}/Axes/Pot_E_Piece_03_Axis.xyz"

C0 = np.loadtxt(s0_path, usecols=range(6)).T
C1 = np.loadtxt(s1_path, usecols=range(6)).T
C = np.concatenate([C0, C1], axis=1)

rel = [float(x) for x in open(rel_path).read().split()]
# p0x p0y p0z ax ay az
vt_rel = np.r_[rel[3:6], rel[:3]]
vt_rel[:3] /= np.linalg.norm(vt_rel[:3])
vt_rel[3:6] -= (vt_rel[:3] @ vt_rel[3:6]) * vt_rel[:3]

cost_rel = worst_wall_normalized_cost(vt_rel, C0, C1, min_clearance_mm=25.0)
mean_ax_rel = np.mean(np.abs(vt_rel[:3] @ C[3:6, :]))
d_rel = centroid_distance(vt_rel, C)

print(f"Piece 03 Released Axis: cost={cost_rel:.6f}, d={d_rel:.2f}mm, mean_ax={mean_ax_rel:.3f}")
