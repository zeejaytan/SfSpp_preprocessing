import glob, os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"

def analyze_piece_normals(stem):
    s0_p = f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz"
    s1_p = f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz"
    if not os.path.exists(s0_p): return
    s0 = np.loadtxt(s0_p, usecols=range(6)).T
    s1 = np.loadtxt(s1_p, usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)
    P = C[:3, :]
    N = C[3:6, :]
    
    # PCA on normals
    cov_N = np.cov(N)
    eigvals, eigvecs = np.linalg.eigh(cov_N)
    
    # If the surface is a cylinder (wall piece):
    # normals lie in a 2D circle/fan, so smallest eigenvalue is very small,
    # and the corresponding eigenvector is the cylinder axis direction a_cyl!
    a_cyl = eigvecs[:, 0]
    axial_cyl = np.abs(a_cyl @ N)
    
    # Distance from centroid to cylinder axis:
    # Cylinder axis passes through center of curvature
    # Let's check mean axial normal for a_cyl
    print(f"{stem}: eigvals_N = {np.round(eigvals, 4)}, mean(|a_cyl . N|) = {np.mean(axial_cyl):.3f}")

print("=== Base Pieces ===")
for b in ["Pot_A_Piece_01", "Pot_B_Piece_01", "Pot_C_Piece_03", "Pot_E_Piece_34"]:
    analyze_piece_normals(b)

print("\n=== Wall Pieces ===")
for w in ["Pot_E_Piece_03", "Pot_E_Piece_23", "Pot_E_Piece_24", "Pot_E_Piece_25", "Pot_E_Piece_26", "Pot_E_Piece_28", "Pot_E_Piece_31"]:
    analyze_piece_normals(w)
