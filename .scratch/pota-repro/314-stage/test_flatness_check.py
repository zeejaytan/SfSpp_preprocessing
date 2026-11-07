import os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from sfs_axes.io_axes import read_axes

def check_near_patch_flatness(stem, cand):
    s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
    s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)
    
    a = cand[:3] / np.linalg.norm(cand[:3])
    p0 = cand[3:6] - (cand[3:6] @ a) * a
    P = C[:3, :]
    N = C[3:6, :]
    dp = P - p0[:, None]
    z = a @ dp
    r = np.linalg.norm(dp - a[:, None] * z[None, :], axis=0)
    near = r < 25.0
    
    P_near = P[:, near]
    N_near = N[:, near]
    
    # Check curvature / flatness of P_near:
    # Fit plane to P_near
    c_near = P_near.mean(axis=1)
    cov = np.cov(P_near - c_near[:, None])
    w, v = np.linalg.eigh(cov)
    # The smallest eigenvalue w[0] corresponds to the normal of the patch
    patch_thickness = np.sqrt(w[0])
    
    # Angular spread of normals on the near patch:
    # On a flat base floor, all normals point along the axis.
    # What is the max angle between normals on the patch?
    dots = np.abs(a @ N_near)
    min_dot = np.min(dots)
    max_ang_deg = np.degrees(np.arccos(np.clip(min_dot, 0.0, 1.0)))
    
    print(f"{stem:15s}: near pts={np.sum(near):5d}, patch_thickness={patch_thickness:4.2f}mm, max_ang_deg={max_ang_deg:4.1f}deg")

print("=== True Base Pieces with GT/Rel Axis ===")
check_near_patch_flatness("Pot_A_Piece_01", read_axes(f"{CORPUS}/Axes/Pot_A_Piece_01_Axis.xyz")[:, 0])
check_near_patch_flatness("Pot_B_Piece_01", read_axes(f"{CORPUS}/Axes/Pot_B_Piece_01_Axis.xyz")[:, 0])
check_near_patch_flatness("Pot_C_Piece_03", read_axes(f"{CORPUS}/Axes/Pot_C_Piece_03_Axis.xyz")[:, 0])
check_near_patch_flatness("Pot_E_Piece_34", read_axes(f"{CORPUS}/Axes/Pot_E_Piece_34_Axis.xyz")[:, 2])

print("\n=== Wall Pieces with Perpendicular Decoy Axis ===")
for p in [3, 23, 24, 25, 26, 28, 31]:
    stem = f"Pot_E_Piece_{p:02d}"
    s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
    C = s0
    # Mean normal of Surface 0 as candidate direction
    n_mean = C[3:6, :].mean(axis=1)
    n_mean /= np.linalg.norm(n_mean)
    c_pt = C[:3, :].mean(axis=1)
    cand = np.r_[n_mean, c_pt]
    check_near_patch_flatness(stem, cand)
