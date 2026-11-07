import os
import sys
import numpy as np

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_313")

from sfs_axes.normalized import centroid_distance

def read_axis_file(path):
    lines = [l.strip().split() for l in open(path) if l.strip()]
    axes = []
    for l in lines:
        axes.append(np.r_[[float(x) for x in l[3:6]], [float(x) for x in l[:3]]])
    return np.column_stack(axes)

def azimuth_span(X, vt):
    # compute azimuth of points around axis vt
    a = vt[:3] / np.linalg.norm(vt[:3])
    p0 = vt[3:6] - (vt[3:6] @ a) * a
    P = X[:3, :]
    dp = P - p0[:, None]
    z = a @ dp
    r_vec = dp - a[:, None] * z[None, :]
    r = np.linalg.norm(r_vec, axis=0)
    
    # define orthonormal basis orthogonal to a
    u = np.array([1.0, 0.0, 0.0])
    if abs(u @ a) > 0.9:
        u = np.array([0.0, 1.0, 0.0])
    u = u - (u @ a) * a
    u /= np.linalg.norm(u)
    v = np.cross(a, u)
    
    # azimuth angles
    x_proj = u @ r_vec
    y_proj = v @ r_vec
    theta = np.arctan2(y_proj, x_proj)  # [-pi, pi]
    
    # check azimuth span by looking at largest gap
    th_sorted = np.sort(np.degrees(theta) % 360.0)
    gaps = np.diff(np.r_[th_sorted, th_sorted[0] + 360.0])
    max_gap = float(np.max(gaps))
    span_deg = 360.0 - max_gap
    return span_deg, np.std(r)

# Test on genuine base pieces
base_pieces = [
    ("Pot_A_Piece_01", f"{CORPUS}/Axes/Pot_A_Piece_01_Axis.xyz"),
    ("Pot_B_Piece_01", f"{CORPUS}/Axes/Pot_B_Piece_01_Axis.xyz"),
    ("Pot_D_Piece_22", f"{CORPUS}/Axes/Pot_D_Piece_22_Axis.xyz"),
    ("Pot_D_Piece_32", f"{CORPUS}/Axes/Pot_D_Piece_32_Axis.xyz"),
    ("Pot_E_Piece_31", f"{CORPUS}/Axes/Pot_E_Piece_31_Axis.xyz"),
]

print("=== Genuine Base Pieces with Released Axis ===")
for stem, ax_path in base_pieces:
    s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
    s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)
    ax = read_axis_file(ax_path)
    span_deg, r_std = azimuth_span(C, ax[:, 0])
    d_cent = centroid_distance(ax[:, 0], C)
    mean_ax = np.mean(np.abs((ax[:3, 0] / np.linalg.norm(ax[:3, 0])) @ C[3:6, :]))
    print(f"{stem}: d_cent={d_cent:5.1f}mm, span={span_deg:5.1f}deg, r_std={r_std:5.1f}mm, mean_ax={mean_ax:.2f}")

# Test on wall pieces with Trojan decoy vs true axis
print("\n=== Wall Pieces: Decoy vs True Axis ===")
wall_pieces = [
    "Pot_E_Piece_03", "Pot_E_Piece_23", "Pot_E_Piece_24", "Pot_E_Piece_25", "Pot_E_Piece_26", "Pot_E_Piece_28"
]
for stem in wall_pieces:
    s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
    s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)
    
    # Fake axis: pointing along mean normal at centroid
    C_cent = np.mean(C[:3, :], axis=1)
    N_mean = np.mean(C[3:6, :], axis=1)
    N_mean /= np.linalg.norm(N_mean)
    vt_decoy = np.r_[N_mean, C_cent]
    
    # True released axis
    rel_ax = read_axis_file(f"{CORPUS}/Axes/{stem}_Axis.xyz")
    vt_true = rel_ax[:, 0]
    
    span_decoy, r_std_decoy = azimuth_span(C, vt_decoy)
    d_decoy = centroid_distance(vt_decoy, C)
    mean_ax_decoy = np.mean(np.abs(N_mean @ C[3:6, :]))

    span_true, r_std_true = azimuth_span(C, vt_true)
    d_true = centroid_distance(vt_true, C)
    mean_ax_true = np.mean(np.abs((vt_true[:3]/np.linalg.norm(vt_true[:3])) @ C[3:6, :]))

    print(f"{stem}:")
    print(f"  Decoy: d={d_decoy:5.1f}mm, span={span_decoy:5.1f}deg, mean_ax={mean_ax_decoy:.2f}")
    print(f"  True : d={d_true:5.1f}mm, span={span_true:5.1f}deg, mean_ax={mean_ax_true:.2f}")
