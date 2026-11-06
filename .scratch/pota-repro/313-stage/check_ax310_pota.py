import os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
AX310 = "/data/gpfs/projects/punim2657/SfSpp/runs/20261105-1215_1a6f16e_t310b3-timing/out/axes310"
sys.path.insert(0, ".")
from check_ref_drift import read_axis
from sfs_axes.io_axes import direction_angle_deg

for p in range(1, 9):
    stem = f"Pot_A_Piece_{p:02d}"
    ax = read_axis(os.path.join(AX310, f"{stem}_Axis.xyz"))
    rel = read_axis(os.path.join(CORPUS, "Axes", f"{stem}_Axis.xyz"))
    gt = read_axis(os.path.join(CORPUS, "Ground Truth Axes", f"{stem}_Axis.xyz"))
    ang_rel = direction_angle_deg(ax[:3, 0], rel[:3, 0])
    ang_gt = direction_angle_deg(ax[:3, 0], gt[:3, 0])
    print(f"Pot A Piece {p:02d}: lines={ax.shape[1]}, line0 to rel={ang_rel:.2f} deg, line0 to gt={ang_gt:.2f} deg")
