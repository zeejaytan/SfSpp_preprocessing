import os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"

def measure_patch_curvature(stem):
    s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
    P = s0[:3, :]
    N = s0[3:6, :]
    
    # Fit a plane P . n = d to the surface
    C = np.mean(P, axis=1)
    cov = np.cov(P - C[:, None])
    w, v = np.linalg.eigh(cov)
    n_plane = v[:, 0]  # smallest variance = normal to best-fit plane
    
    # Distances of points to the best-fit plane
    dist_plane = np.abs(n_plane @ (P - C[:, None]))
    max_dist = np.max(dist_plane)
    mean_dist = np.mean(dist_plane)
    
    # Normal angular deviation from plane normal
    ang_dev = np.degrees(np.arccos(np.clip(np.abs(n_plane @ N), 0.0, 1.0)))
    mean_ang_dev = np.mean(ang_dev)
    max_ang_dev = np.max(ang_dev)
    
    print(f"{stem:15s}: plane dist (mean={mean_dist:.2f}mm, max={max_dist:.2f}mm), norm dev (mean={mean_ang_dev:.1f}deg, max={max_ang_dev:.1f}deg)")

print("=== Base Pieces ===")
for b in ["Pot_A_Piece_01", "Pot_B_Piece_01", "Pot_C_Piece_03", "Pot_E_Piece_34"]:
    measure_patch_curvature(b)

print("\n=== Wall Pieces ===")
for w in ["Pot_E_Piece_03", "Pot_E_Piece_23", "Pot_E_Piece_24", "Pot_E_Piece_25", "Pot_E_Piece_26", "Pot_E_Piece_28", "Pot_E_Piece_31"]:
    measure_patch_curvature(w)
