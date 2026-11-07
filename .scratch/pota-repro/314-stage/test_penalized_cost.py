import os
import sys
import numpy as np

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_313")

from sfs_axes.normalized import compute_normalized_residual, centroid_distance
from sfs_axes.io_axes import read_axes, direction_angle_deg
from scipy.optimize import least_squares

stem = "Pot_E_Piece_03"
s0_path = f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz"
s1_path = f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz"
rel_path = f"{CORPUS}/Axes/{stem}_Axis.xyz"

C0 = np.loadtxt(s0_path, usecols=range(6)).T
C1 = np.loadtxt(s1_path, usecols=range(6)).T
C = np.concatenate([C0, C1], axis=1)

rel = read_axes(rel_path)
v_rel = rel[:, 0].copy()
if v_rel[2] < 0: v_rel[:3] = -v_rel[:3]

Cd = C[:, ::10]

# Initial draw: ang_rel=0.65 deg
vt_init = np.array([-0.79665711, 0.44132265, 0.41300334, 184.85500248, -23.29305711, 381.46375714])

def cost_with_axial_prior(vt, C0, C1, axial_max=0.50, r_min=40.0, r_max=120.0):
    a = vt[:3] / np.linalg.norm(vt[:3])
    p0 = vt[3:6] - (vt[3:6] @ a) * a
    
    # Normalized residual
    err0 = compute_normalized_residual(vt, C0)[0, :]
    err1 = compute_normalized_residual(vt, C1)[0, :]
    
    from sfs_axes.robust import apply_robustifier, robustifier_huber
    c0 = float(np.mean(apply_robustifier(robustifier_huber, err0, None)))
    c1 = float(np.mean(apply_robustifier(robustifier_huber, err1, None)))
    cost = max(c0, c1)
    
    # Axial penalty
    mean_ax = float(np.mean(np.abs(a @ C[3:6, :])))
    if mean_ax > axial_max:
        cost += 100.0 * (mean_ax - axial_max) ** 2
        
    # Clearance penalty
    d = centroid_distance(vt, C)
    if d < 25.0:
        cost += 1000.0 * (25.0 - d) ** 2
    elif d > 200.0:
        cost += 0.001 * (d - 120.0) ** 2
    elif d < r_min:
        cost += 0.01 * (r_min - d)
    elif d > r_max:
        cost += 0.0005 * (d - r_max) ** 2
    return cost, mean_ax, d

print("Initial draw:")
c_init, ax_init, d_init = cost_with_axial_prior(vt_init, C0, C1)
print(f"  cost={c_init:.6f}, mean_ax={ax_init:.3f}, d={d_init:.2f}mm, ang_rel={direction_angle_deg(vt_init[:3], v_rel[:3]):.2f}deg")

print("Released axis:")
c_rel, ax_rel, d_rel = cost_with_axial_prior(v_rel, C0, C1)
print(f"  cost={c_rel:.6f}, mean_ax={ax_rel:.3f}, d={d_rel:.2f}mm")

print("Refined axis from trace_bad_step (ang_rel=39.33 deg):")
vt_bad = np.array([-0.61248083, 0.40798226, 0.67727192, 137.24075133, 40.59013222, 99.55949666])
c_bad, ax_bad, d_bad = cost_with_axial_prior(vt_bad, C0, C1)
print(f"  cost={c_bad:.6f}, mean_ax={ax_bad:.3f}, d={d_bad:.2f}mm")
