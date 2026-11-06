import os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, ".")
from check_ref_drift import load_surface, read_axis
from sfs_axes.normalized import centroid_distance

for p in [3, 9, 23, 24, 25, 26, 27, 28, 29, 31]:
    stem = f"Pot_E_Piece_{p:02d}"
    s0_path = os.path.join(CORPUS, "Surfaces", f"{stem}_Surface_0.xyz")
    s1_path = os.path.join(CORPUS, "Surfaces", f"{stem}_Surface_1.xyz")
    gt_path = os.path.join(CORPUS, "Ground Truth Axes", f"{stem}_Axis.xyz")
    C0 = load_surface(s0_path)
    C1 = load_surface(s1_path)
    C = np.concatenate([C0, C1], axis=1)
    gt_axes = read_axis(gt_path)
    vt_gt = gt_axes[:, 0].copy()
    a_gt = vt_gt[:3] / np.linalg.norm(vt_gt[:3])
    
    # Check mean(|n . a_gt|)
    N = C[3:6, :]
    axial_gt = np.mean(np.abs(a_gt @ N))
    d_gt = centroid_distance(vt_gt, C)
    print(f"Piece {p:02d}: d_gt={d_gt:.2f} mm, mean(|n . a_gt|)={axial_gt:.3f}")
