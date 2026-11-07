import os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from sfs_axes.io_axes import read_axes

def analyze(stem, vt):
    s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
    s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)
    
    a = vt[:3] / np.linalg.norm(vt[:3])
    p0 = vt[3:6] - (vt[3:6] @ a) * a
    P = C[:3, :]
    N = C[3:6, :]
    
    dp = P - p0[:, None]
    z = a @ dp
    r_vec = dp - a[:, None] * z[None, :]
    r = np.linalg.norm(r_vec, axis=0)
    
    # 1. Look at the curvature of the surface perpendicular to a:
    # A wall piece is curved in ONE direction (circumferential), flat in orthogonal direction.
    # Let's project points onto plane perpendicular to a:
    u = np.array([1.0, 0.0, 0.0])
    if abs(u @ a) > 0.9: u = np.array([0.0, 1.0, 0.0])
    u = u - (u @ a) * a; u /= np.linalg.norm(u)
    v = np.cross(a, u)
    
    # For each point, its 2D coordinates in tangent plane:
    x_2d = u @ dp
    y_2d = v @ dp
    
    # Surface normal projection in 2D tangent plane:
    nx = u @ N
    ny = v @ N
    
    # In a cylindrical wall patch:
    # The normal tilts along one direction (the circumferential direction),
    # but NOT in the orthogonal direction (the cylinder axis direction)!
    # Let's find the covariance of (nx, ny):
    cov_n2d = np.cov(np.vstack([nx, ny]))
    eig_n2d = np.sort(np.linalg.eigvalsh(cov_n2d))[::-1]
    ratio_eig_n2d = eig_n2d[0] / (eig_n2d[1] + 1e-8)
    
    # In a circular base floor:
    # The floor is symmetric in x and y (or flat in all directions)!
    # So eig_n2d[0] and eig_n2d[1] are similar (ratio ~ 1.0 to 2.5)!
    # But in a cylindrical wall patch, normal ONLY tilts in circumferential direction!
    # So eig_n2d[0] >> eig_n2d[1] (ratio > 4.0 to 20.0)!
    
    # 2. Also look at Pottmann residual / curvature:
    # In a cylinder, how much does z vary as a quadratic function of 2D coordinates?
    
    print(f"{stem:18s}: eig_n2d={np.round(eig_n2d, 5)}, ratio={ratio_eig_n2d:5.2f}")

print("=== SET 1: TRUE BASE AXES ===")
true_bases = [
    ("Pot_A_Piece_01", 0),
    ("Pot_B_Piece_01", 0),
    ("Pot_C_Piece_03", 0),
    ("Pot_D_Piece_22", 0),
    ("Pot_D_Piece_28", 1),
    ("Pot_D_Piece_30", 0),
    ("Pot_D_Piece_32", 0),
    ("Pot_G_Piece_07", 0),
    ("Pot_I_Piece_25", 0),
    ("Pot_E_Piece_34", 2),
]
for stem, l_idx in true_bases:
    vt = read_axes(f"{CORPUS}/Axes/{stem}_Axis.xyz")[:, l_idx]
    analyze(stem, vt)

print("\n=== SET 2: PERPENDICULAR DECOYS ON WALL PIECES ===")
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
        mean_ax = np.mean(np.abs(a @ C[3:6, :]))
        if d < 25.0 and mean_ax > 0.80:
            print(f"Decoy {k} on {stem} (d={d:.1f}mm, mean_ax={mean_ax:.3f}):")
            analyze(stem, vt)
