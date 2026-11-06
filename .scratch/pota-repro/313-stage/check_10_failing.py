import numpy as np, os
from sfs_axes.io_axes import read_axes, direction_angle_deg
CORPUS = '/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp'
failing = [3, 9, 23, 24, 25, 26, 27, 28, 29, 31]
for p in failing:
    stem = f"Pot_E_Piece_{p:02d}"
    ax = read_axes(f"test_out3/axes313/{stem}_Axis.xyz")
    gt = read_axes(f"{CORPUS}/Ground Truth Axes/{stem}_Axis.xyz")
    rel = read_axes(f"{CORPUS}/Axes/{stem}_Axis.xyz")
    angs_gt = [direction_angle_deg(ax[:3, k], gt[:3, 0]) for k in range(ax.shape[1])]
    angs_rel = [direction_angle_deg(ax[:3, k], rel[:3, 0]) for k in range(ax.shape[1])]
    min_gt = min(angs_gt) if angs_gt else 999
    min_rel = min(angs_rel) if angs_rel else 999
    print(f"{stem}: K={ax.shape[1]} min_gt={min_gt:.1f} min_rel={min_rel:.1f} | gt={[round(a,1) for a in angs_gt]} | rel={[round(a,1) for a in angs_rel]}")
