#!/usr/bin/env python3
"""Inspect why refinement drifts."""
import os, sys
import numpy as np

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, ".")
from sfs_axes.normalized import compute_normalized_residual, centroid_distance
from sfs_axes.io_axes import direction_angle_deg

def load_surface(path):
    a = np.loadtxt(path, usecols=(0, 1, 2, 3, 4, 5), ndmin=2)
    return np.asarray(a, dtype=float).T

def read_axis(path):
    lines = [line.strip().split() for line in open(path) if line.strip()]
    axes = []
    for l in lines:
        p0 = [float(x) for x in l[:3]]
        a = [float(x) for x in l[3:6]]
        axes.append(np.r_[a, p0])
    return np.column_stack(axes)

for p in [3, 9, 23, 26, 27]:
    stem = f"Pot_E_Piece_{p:02d}"
    s0_path = os.path.join(CORPUS, "Surfaces", f"{stem}_Surface_0.xyz")
    s1_path = os.path.join(CORPUS, "Surfaces", f"{stem}_Surface_1.xyz")
    rel_path = os.path.join(CORPUS, "Axes", f"{stem}_Axis.xyz")
    gt_path = os.path.join(CORPUS, "Ground Truth Axes", f"{stem}_Axis.xyz")

    C0 = load_surface(s0_path)
    C1 = load_surface(s1_path)
    C = np.concatenate([C0, C1], axis=1)

    rel_axes = read_axis(rel_path)
    gt_axes = read_axis(gt_path) if os.path.isfile(gt_path) else rel_axes
    vt_gt = gt_axes[:, 0].copy()
    if vt_gt[2] < 0: vt_gt[:3] = -vt_gt[:3]

    from sfs_axes.normalized import refine_axis_normalized
    vt_ref = refine_axis_normalized(vt_gt, C, max_iters=100, tolerance=1e-9)

    d_gt = centroid_distance(vt_gt, C)
    d_ref = centroid_distance(vt_ref, C)
    ang = direction_angle_deg(vt_ref[:3], vt_gt[:3])
    
    # What are the residuals at vt_gt vs vt_ref?
    e_gt = compute_normalized_residual(vt_gt, C)[0, :]
    e_ref = compute_normalized_residual(vt_ref, C)[0, :]
    
    print(f"Piece {p:02d}: ang={ang:.2f} deg, d_gt={d_gt:.2f} mm, d_ref={d_ref:.2f} mm | "
          f"mean(|e_gt|)={np.mean(np.abs(e_gt)):.5f}, mean(|e_ref|)={np.mean(np.abs(e_ref)):.5f}")
