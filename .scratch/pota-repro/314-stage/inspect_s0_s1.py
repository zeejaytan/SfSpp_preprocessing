import os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from sfs_axes.io_axes import read_axes

def check_surfaces(stem, vt):
    s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
    s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
    
    a = vt[:3] / np.linalg.norm(vt[:3])
    p0 = vt[3:6] - (vt[3:6] @ a) * a
    
    # Check mean axial on Surface 0 vs Surface 1
    mean_ax_s0 = np.mean(np.abs(a @ s0[3:6, :]))
    mean_ax_s1 = np.mean(np.abs(a @ s1[3:6, :]))
    
    # Check mean normal dot product: n0 . n1 at corresponding locations?
    # Or mean normal of s0 and mean normal of s1:
    m_n0 = np.mean(s0[3:6, :], axis=1)
    m_n1 = np.mean(s1[3:6, :], axis=1)
    
    dot_m = np.dot(m_n0, m_n1)
    
    # What is the distance between centroids of s0 and s1?
    c0 = np.mean(s0[:3, :], axis=1)
    c1 = np.mean(s1[:3, :], axis=1)
    dist_c = np.linalg.norm(c0 - c1)
    
    # What is the axial position of s0 vs s1 along the axis?
    z0 = a @ (c0 - p0)
    z1 = a @ (c1 - p0)
    dz = abs(z0 - z1)
    
    print(f"{stem:18s}: mean_ax_s0={mean_ax_s0:.3f}, mean_ax_s1={mean_ax_s1:.3f}, m_n0.m_n1={dot_m:.3f}, dist_c={dist_c:.2f}mm, dz={dz:.2f}mm")

print("=== Genuine Base Sherds with Released Axis ===")
check_surfaces("Pot_A_Piece_01", read_axes(f"{CORPUS}/Axes/Pot_A_Piece_01_Axis.xyz")[:, 0])
check_surfaces("Pot_B_Piece_01", read_axes(f"{CORPUS}/Axes/Pot_B_Piece_01_Axis.xyz")[:, 0])
check_surfaces("Pot_C_Piece_03", read_axes(f"{CORPUS}/Axes/Pot_C_Piece_03_Axis.xyz")[:, 0])
check_surfaces("Pot_D_Piece_22", read_axes(f"{CORPUS}/Axes/Pot_D_Piece_22_Axis.xyz")[:, 0])
check_surfaces("Pot_D_Piece_28", read_axes(f"{CORPUS}/Axes/Pot_D_Piece_28_Axis.xyz")[:, 1])
check_surfaces("Pot_D_Piece_32", read_axes(f"{CORPUS}/Axes/Pot_D_Piece_32_Axis.xyz")[:, 0])
check_surfaces("Pot_G_Piece_07", read_axes(f"{CORPUS}/Axes/Pot_G_Piece_07_Axis.xyz")[:, 0])
check_surfaces("Pot_I_Piece_25", read_axes(f"{CORPUS}/Axes/Pot_I_Piece_25_Axis.xyz")[:, 0])
check_surfaces("Pot_E_Piece_34", read_axes(f"{CORPUS}/Axes/Pot_E_Piece_34_Axis.xyz")[:, 2])

print("\n=== Perpendicular Decoys on Wall Pieces ===")
AXES313 = "/data/gpfs/projects/punim2657/SfSpp/runs/20261106-1316_fe906ab_t313a-axes/out/axes313"
for p in [3, 23, 24, 25, 26, 28, 31]:
    stem = f"Pot_E_Piece_{p:02d}"
    ax_p = f"{AXES313}/{stem}_Axis.xyz"
    if not os.path.exists(ax_p): continue
    axes = read_axes(ax_p)
    C = np.concatenate([np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T,
                        np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T], axis=1)
    c_pt = C[:3].mean(axis=1)
    for k in range(axes.shape[1]):
        vt = axes[:, k]
        a = vt[:3] / np.linalg.norm(vt[:3])
        d = np.linalg.norm(np.cross(c_pt - vt[3:6], a))
        if d < 25.0:
            print(f"Cand k={k}:")
            check_surfaces(stem, vt)
