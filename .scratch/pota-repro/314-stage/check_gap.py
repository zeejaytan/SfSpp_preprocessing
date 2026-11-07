import os, sys, numpy as np
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_313")
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"

from sfs_axes.potsac import patch_gap_deg
from sfs_axes.io_axes import read_axes

stem = "Pot_E_Piece_03"
s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
C = np.concatenate([s0, s1], axis=1)

# Let's test patch gap on GT axis vs decoy axis
gt = np.loadtxt(f"{CORPUS}/Ground Truth Axes/{stem}_Axis.xyz")
vt_gt = np.r_[gt[3:6], gt[:3]]
gap_gt = patch_gap_deg(vt_gt, C)
print(f"Piece 03 GT patch gap: {gap_gt:.1f} deg")
