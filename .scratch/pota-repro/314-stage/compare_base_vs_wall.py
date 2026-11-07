import os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"

pieces = [
    ("Pot_A_Piece_01", True),
    ("Pot_B_Piece_01", True),
    ("Pot_C_Piece_03", True),
    ("Pot_D_Piece_22", True),
    ("Pot_D_Piece_32", True),
    ("Pot_E_Piece_34", True),
    ("Pot_E_Piece_03", False),
    ("Pot_E_Piece_23", False),
    ("Pot_E_Piece_24", False),
    ("Pot_E_Piece_25", False),
    ("Pot_E_Piece_26", False),
    ("Pot_E_Piece_28", False),
    ("Pot_E_Piece_31", False),
]

for stem, is_base in pieces:
    s0_p = f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz"
    s1_p = f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz"
    if not os.path.exists(s0_p): continue
    s0 = np.loadtxt(s0_p, usecols=range(6)).T
    s1 = np.loadtxt(s1_p, usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)
    P = C[:3, :]
    N = C[3:6, :]

    # Center at centroid
    P_c = P - P.mean(axis=1, keepdims=True)
    # PCA on points
    cov_P = np.cov(P_c)
    eigvals_P, eigvecs_P = np.linalg.eigh(cov_P)
    
    # Sort descending
    idx = np.argsort(eigvals_P)[::-1]
    eigvals_P = eigvals_P[idx]
    
    # Aspect ratio of the sherd in 3D:
    # A wall piece is a curved strip: length (L), width (W), thickness (T).
    # A base piece that covers the bottom center is a 2D disk: radius R in x and y (L ~ W), thickness T.
    ratio_12 = eigvals_P[0] / eigvals_P[1]
    ratio_23 = eigvals_P[1] / eigvals_P[2]
    
    # Check normal clustering:
    # A base piece has a flat floor where normals are tightly clustered in ONE direction.
    # What fraction of normals point within 15 deg of the dominant normal?
    # Dominant normal = mean of surface 0 normals:
    mean_n0 = s0[3:6, :].mean(axis=1)
    mean_n0 /= np.linalg.norm(mean_n0)
    dot0 = np.abs(mean_n0 @ s0[3:6, :])
    frac_flat0 = np.mean(dot0 > np.cos(np.radians(15.0)))
    
    mean_n1 = s1[3:6, :].mean(axis=1)
    mean_n1 /= np.linalg.norm(mean_n1)
    dot1 = np.abs(mean_n1 @ s1[3:6, :])
    frac_flat1 = np.mean(dot1 > np.cos(np.radians(15.0)))
    
    print(f"{stem:15s} (Base={is_base}): eigvals={np.round(eigvals_P, 1)}, L/W={ratio_12:.2f}, W/T={ratio_23:.2f}, flat0={frac_flat0:.2f}, flat1={frac_flat1:.2f}")
