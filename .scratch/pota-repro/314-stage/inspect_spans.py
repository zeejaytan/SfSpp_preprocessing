import os
import glob
import numpy as np

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"

def read_axis(path):
    lines = [l.strip().split() for l in open(path) if l.strip()]
    axes = []
    for l in lines:
        axes.append(np.r_[[float(x) for x in l[3:6]], [float(x) for x in l[:3]]])
    return np.column_stack(axes)

def check_piece(stem, ax):
    s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
    s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)
    
    a = ax[:3] / np.linalg.norm(ax[:3])
    p0 = ax[3:6] - (ax[3:6] @ a) * a
    P = C[:3, :]
    N = C[3:6, :]
    
    dp = P - p0[:, None]
    z = a @ dp
    r_vec = dp - a[:, None] * z[None, :]
    r = np.linalg.norm(r_vec, axis=0)
    
    # centroid distance
    C_cent = np.mean(P, axis=1)
    d_cent = np.linalg.norm(np.cross(C_cent - p0, a))
    
    # whole sherd mean axial
    mean_ax = np.mean(np.abs(a @ N))
    
    # azimuth span of near points (r < 25 mm)
    near = r < 25.0
    u = np.array([1.0, 0.0, 0.0])
    if abs(u @ a) > 0.9: u = np.array([0.0, 1.0, 0.0])
    u = u - (u @ a) * a; u /= np.linalg.norm(u)
    v = np.cross(a, u)
    
    if np.sum(near) > 20:
        th = np.arctan2(v @ r_vec[:, near], u @ r_vec[:, near])
        th_s = np.sort(np.degrees(th) % 360.0)
        gap = np.max(np.diff(np.r_[th_s, th_s[0] + 360.0]))
        span_near = 360.0 - gap
    else:
        span_near = 0.0
        
    # azimuth span of ALL points
    th_all = np.arctan2(v @ r_vec, u @ r_vec)
    th_all_s = np.sort(np.degrees(th_all) % 360.0)
    gap_all = np.max(np.diff(np.r_[th_all_s, th_all_s[0] + 360.0]))
    span_all = 360.0 - gap_all

    print(f"{stem:18s} | d_cent={d_cent:5.1f} | whole_ax={mean_ax:.2f} | near_pts={np.sum(near):4d} | near_span={span_near:5.1f} | all_span={span_all:5.1f}")

# Check genuine base pieces
print("=== Genuine Base Sherds with Released Axis ===")
check_piece("Pot_A_Piece_01", read_axis(f"{CORPUS}/Axes/Pot_A_Piece_01_Axis.xyz")[:, 0])
check_piece("Pot_B_Piece_01", read_axis(f"{CORPUS}/Axes/Pot_B_Piece_01_Axis.xyz")[:, 0])
check_piece("Pot_D_Piece_22", read_axis(f"{CORPUS}/Axes/Pot_D_Piece_22_Axis.xyz")[:, 0])
check_piece("Pot_D_Piece_28", read_axis(f"{CORPUS}/Axes/Pot_D_Piece_28_Axis.xyz")[:, 1])
check_piece("Pot_D_Piece_29", read_axis(f"{CORPUS}/Axes/Pot_D_Piece_29_Axis.xyz")[:, 0])
check_piece("Pot_D_Piece_30", read_axis(f"{CORPUS}/Axes/Pot_D_Piece_30_Axis.xyz")[:, 0])
check_piece("Pot_D_Piece_31", read_axis(f"{CORPUS}/Axes/Pot_D_Piece_31_Axis.xyz")[:, 0])
check_piece("Pot_D_Piece_32", read_axis(f"{CORPUS}/Axes/Pot_D_Piece_32_Axis.xyz")[:, 0])
check_piece("Pot_G_Piece_07", read_axis(f"{CORPUS}/Axes/Pot_G_Piece_07_Axis.xyz")[:, 0])
check_piece("Pot_I_Piece_25", read_axis(f"{CORPUS}/Axes/Pot_I_Piece_25_Axis.xyz")[:, 0])
check_piece("Pot_I_Piece_29", read_axis(f"{CORPUS}/Axes/Pot_I_Piece_29_Axis.xyz")[:, 0])
check_piece("Pot_I_Piece_30", read_axis(f"{CORPUS}/Axes/Pot_I_Piece_30_Axis.xyz")[:, 0])
check_piece("Pot_E_Piece_31", read_axis(f"{CORPUS}/Axes/Pot_E_Piece_31_Axis.xyz")[:, 0])
check_piece("Pot_E_Piece_31", read_axis(f"{CORPUS}/Axes/Pot_E_Piece_31_Axis.xyz")[:, 2])

print("\n=== Wall Sherds with True Released Axis ===")
check_piece("Pot_E_Piece_03", read_axis(f"{CORPUS}/Axes/Pot_E_Piece_03_Axis.xyz")[:, 0])
check_piece("Pot_E_Piece_23", read_axis(f"{CORPUS}/Axes/Pot_E_Piece_23_Axis.xyz")[:, 0])
check_piece("Pot_E_Piece_24", read_axis(f"{CORPUS}/Axes/Pot_E_Piece_24_Axis.xyz")[:, 0])
check_piece("Pot_E_Piece_25", read_axis(f"{CORPUS}/Axes/Pot_E_Piece_25_Axis.xyz")[:, 0])
check_piece("Pot_E_Piece_26", read_axis(f"{CORPUS}/Axes/Pot_E_Piece_26_Axis.xyz")[:, 0])
check_piece("Pot_E_Piece_28", read_axis(f"{CORPUS}/Axes/Pot_E_Piece_28_Axis.xyz")[:, 0])
