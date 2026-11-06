import os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, ".")
from check_ref_drift import read_axis
from sfs_axes.io_axes import direction_angle_deg

rel = read_axis(os.path.join(CORPUS, "Axes", "Pot_A_Piece_07_Axis.xyz"))
print(f"Piece 07 lines: {rel.shape[1]}")
if rel.shape[1] > 1:
    print(f"Line 0 vs Line 1 angle: {direction_angle_deg(rel[:3, 0], rel[:3, 1]):.2f} deg")
