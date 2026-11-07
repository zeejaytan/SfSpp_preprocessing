import glob, os, sys, numpy as np
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_313")
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
from sfs_axes.io_axes import read_axes

print("=== Pot E: centroid distance to GT axis for all pieces ===")
for p in range(1, 35):
    stem = f"Pot_E_Piece_{p:02d}"
    gt_p = f"{CORPUS}/Ground Truth Axes/{stem}_Axis.xyz"
    if not os.path.exists(gt_p): continue
    s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
    s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)
    c_pt = C[:3].mean(axis=1)
    
    gt = np.loadtxt(gt_p)
    a = gt[3:6] / np.linalg.norm(gt[3:6])
    p0 = gt[:3]
    d = np.linalg.norm(np.cross(c_pt - p0, a))
    
    # Also check whole-sherd mean axial normal for GT axis
    mean_ax = np.mean(np.abs(a @ C[3:6, :]))
    
    print(f"Piece {p:02d}: d_GT = {d:5.1f} mm, mean_axial_GT = {mean_ax:.3f}")
