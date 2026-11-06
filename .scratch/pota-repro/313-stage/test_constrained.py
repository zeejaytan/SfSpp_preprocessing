#!/usr/bin/env python3
"""Test refined with clearance penalty in least squares."""
import os, sys, numpy as np
from scipy.optimize import least_squares

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, ".")
from sfs_axes.normalized import compute_normalized_residual, centroid_distance, worst_wall_normalized_cost
from sfs_axes.io_axes import direction_angle_deg
from check_ref_drift import load_surface, read_axis

def canonicalize(vt):
    vt = np.asarray(vt, dtype=float).copy()
    if vt[2] < 0: vt[:3] = -vt[:3]
    return vt

def refine_constrained(vt_initial, X, min_d=25.0):
    vt = np.asarray(vt_initial, dtype=float).reshape(6)
    a0 = vt[:3] / np.linalg.norm(vt[:3])
    p0 = vt[3:6] - (vt[3:6] @ a0) * a0
    C = np.mean(X[:3, :], axis=1)
    N = X[3:6, :]

    def res(params):
        v = params.copy()
        norm_v = np.linalg.norm(v[:3])
        if norm_v < 1e-12:
            return np.ones(X.shape[1] + 2) * 1e3
        a = v[:3] / norm_v
        p = v[3:6] - (v[3:6] @ a) * a
        v_can = np.r_[a, p]
        
        # 1. Normalized normal residual
        e = compute_normalized_residual(v_can, X, with_jacobian=False)[0, :]
        
        # 2. Clearance penalty
        d = float(np.linalg.norm(np.cross(C - p, a)))
        if d < min_d:
            pen_d = 20.0 * (min_d - d)
        else:
            pen_d = 0.0
            
        # 3. Decoy perpendicular penalty: vessel walls should have |n . a| <= 0.6
        mean_axial = float(np.mean(np.abs(a @ N)))
        if mean_axial > 0.6:
            pen_a = 50.0 * (mean_axial - 0.6)
        else:
            pen_a = 0.0
            
        return np.r_[e, pen_d, pen_a]

    out = least_squares(res, np.r_[a0, p0], loss='huber', f_scale=0.1, max_nfev=150)
    v_opt = out.x.copy()
    v_opt[:3] /= np.linalg.norm(v_opt[:3])
    v_opt[3:6] -= (v_opt[3:6] @ v_opt[:3]) * v_opt[:3]
    return canonicalize(v_opt)

# Test on all 10 pieces starting from GT
pieces = [3, 9, 23, 24, 25, 26, 27, 28, 29, 31]
for p in pieces:
    stem = f"Pot_E_Piece_{p:02d}"
    s0_path = os.path.join(CORPUS, "Surfaces", f"{stem}_Surface_0.xyz")
    s1_path = os.path.join(CORPUS, "Surfaces", f"{stem}_Surface_1.xyz")
    gt_path = os.path.join(CORPUS, "Ground Truth Axes", f"{stem}_Axis.xyz")
    C0 = load_surface(s0_path)
    C1 = load_surface(s1_path)
    C = np.concatenate([C0, C1], axis=1)
    gt_axes = read_axis(gt_path)
    vt_gt = canonicalize(gt_axes[:, 0])

    v_ref = refine_constrained(vt_gt, C, min_d=25.0)
    ang = direction_angle_deg(v_ref[:3], vt_gt[:3])
    d_gt = centroid_distance(vt_gt, C)
    d_ref = centroid_distance(v_ref, C)
    print(f"Piece {p:02d}: ang={ang:.2f} deg, d_gt={d_gt:.1f} mm, d_ref={d_ref:.1f} mm")
