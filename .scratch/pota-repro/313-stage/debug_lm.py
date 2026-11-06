import os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, ".")
from check_ref_drift import load_surface, read_axis
from sfs_axes.normalized import refine_axis_normalized

stem = "Pot_E_Piece_27"
C0 = load_surface(os.path.join(CORPUS, "Surfaces", f"{stem}_Surface_0.xyz"))
C1 = load_surface(os.path.join(CORPUS, "Surfaces", f"{stem}_Surface_1.xyz"))
C = np.concatenate([C0, C1], axis=1)
gt_axes = read_axis(os.path.join(CORPUS, "Ground Truth Axes", f"{stem}_Axis.xyz"))
vt_gt = gt_axes[:, 0].copy()
if vt_gt[2] < 0: vt_gt[:3] = -vt_gt[:3]

refine_axis_normalized(vt_gt, C, max_iters=15, verbose=True)
