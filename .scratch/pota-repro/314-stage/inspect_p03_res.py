import os, sys, numpy as np
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_313")
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"

from sfs_axes.normalized import compute_normalized_residual, centroid_distance
from sfs_axes.io_axes import read_axes, direction_angle_deg
from sfs_axes.robust import apply_robustifier, robustifier_huber

stem = "Pot_E_Piece_03"
s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
C = np.concatenate([s0, s1], axis=1)

gt = np.loadtxt(f"{CORPUS}/Ground Truth Axes/{stem}_Axis.xyz")
vt_gt = np.r_[gt[3:6], gt[:3]]

# Let's inspect residual distribution on Surface 0 vs Surface 1
err0_gt = compute_normalized_residual(vt_gt, s0)[0, :]
err1_gt = compute_normalized_residual(vt_gt, s1)[0, :]
c0_gt = float(np.mean(apply_robustifier(robustifier_huber, err0_gt, None)))
c1_gt = float(np.mean(apply_robustifier(robustifier_huber, err1_gt, None)))
print(f"Piece 03 GT: c0={c0_gt:.6f}, c1={c1_gt:.6f}, worst={max(c0_gt, c1_gt):.6f}, mean={(c0_gt+c1_gt)/2:.6f}")
