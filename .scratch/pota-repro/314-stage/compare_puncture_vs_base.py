import os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from sfs_axes.io_axes import read_axes

def check_piece(stem, vt):
    s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
    s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)
    
    a = vt[:3] / np.linalg.norm(vt[:3])
    p0 = vt[3:6] - (vt[3:6] @ a) * a
    P = C[:3, :]
    N = C[3:6, :]
    
    dp = P - p0[:, None]
    z = a @ dp
    r = np.linalg.norm(dp - a[:, None] * z[None, :], axis=0)
    
    # 1. Radial distribution:
    # On a base floor, points exist all the way to r = 0 (the axis is in the interior of the floor)
    # What is the minimum radius of points to the axis?
    min_r = np.min(r)
    # What is the maximum radius of points to the axis?
    max_r = np.max(r)
    
    # 2. Thickness along the axis (delta z):
    # What is the extent of z for points near the axis (r < 20mm)?
    near = r < 20.0
    z_extent_near = (np.max(z[near]) - np.min(z[near])) if np.sum(near) > 0 else 0.0
    
    # 3. What is the surface normal variation in the radial direction?
    # In a surface of revolution, radial vector u_r = (p - p0)_perp / r.
    # What is n . u_r?
    r_vec = dp - a[:, None] * z[None, :]
    r_norm = r_vec / np.maximum(r[None, :], 1e-6)
    dot_n_ur = np.sum(N * r_norm, axis=0)
    
    # 4. What is the distance between Surface 0 and Surface 1 along the line of the axis?
    # In a wall piercing, the axis pierces through Surface 0 and Surface 1 at a single spot!
    # Let's find the point on Surface 0 closest to the axis line, and the point on Surface 1 closest to the axis line:
    dp0 = s0[:3, :] - p0[:, None]
    r0 = np.linalg.norm(dp0 - a[:, None] * (a @ dp0)[None, :], axis=0)
    p0_closest = s0[:3, np.argmin(r0)]
    
    dp1 = s1[:3, :] - p0[:, None]
    r1 = np.linalg.norm(dp1 - a[:, None] * (a @ dp1)[None, :], axis=0)
    p1_closest = s1[:3, np.argmin(r1)]
    
    # The physical thickness of the wall at the piercing point:
    wall_thickness_at_puncture = np.linalg.norm(p0_closest - p1_closest)
    
    # 5. On a genuine base: what is the distance between the center of Surface 0 and center of Surface 1 along the axis?
    # On a pot base, the bottom is a floor of thickness ~5-15mm.
    
    # 6. Look at the ratio: min_r / max_r, and area of the sherd:
    print(f"{stem:18s}: min_r={min_r:4.1f}mm, max_r={max_r:4.1f}mm, z_near={z_extent_near:4.1f}mm, thick={wall_thickness_at_puncture:4.1f}mm, near_pts={np.sum(near)}")

print("=== Genuine Base Sherds with Released Axis ===")
check_piece("Pot_A_Piece_01", read_axes(f"{CORPUS}/Axes/Pot_A_Piece_01_Axis.xyz")[:, 0])
check_piece("Pot_B_Piece_01", read_axes(f"{CORPUS}/Axes/Pot_B_Piece_01_Axis.xyz")[:, 0])
check_piece("Pot_C_Piece_03", read_axes(f"{CORPUS}/Axes/Pot_C_Piece_03_Axis.xyz")[:, 0])
check_piece("Pot_D_Piece_22", read_axes(f"{CORPUS}/Axes/Pot_D_Piece_22_Axis.xyz")[:, 0])
check_piece("Pot_E_Piece_34", read_axes(f"{CORPUS}/Axes/Pot_E_Piece_34_Axis.xyz")[:, 2])

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
            check_piece(stem, vt)
