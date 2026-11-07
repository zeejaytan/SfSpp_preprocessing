import os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from sfs_axes.io_axes import read_axes

def check_curvature(stem, vt):
    s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
    s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)
    
    a = vt[:3] / np.linalg.norm(vt[:3])
    p0 = vt[3:6] - (vt[3:6] @ a) * a
    P = C[:3, :]
    N = C[3:6, :]
    
    dp = P - p0[:, None]
    z = a @ dp
    
    # 2D coordinates in plane perpendicular to a
    u = np.array([1.0, 0.0, 0.0])
    if abs(u @ a) > 0.9: u = np.array([0.0, 1.0, 0.0])
    u = u - (u @ a) * a; u /= np.linalg.norm(u)
    v = np.cross(a, u)
    x = u @ dp
    y = v @ dp
    r = np.sqrt(x**2 + y**2)
    
    # Near points r < 20mm
    near = r < 20.0
    if np.sum(near) < 50:
        print(f"{stem:18s}: too few near points ({np.sum(near)})")
        return
        
    x_n = x[near]
    y_n = y[near]
    z_n = z[near]
    
    # Fit quadratic surface to near points: z(x, y) = c0 + c1*x + c2*y + c3*x^2 + c4*x*y + c5*y^2
    # On a flat base floor, c3, c4, c5 are all ~ 0 (flat plane).
    # On a cylindrical wall piece, c3*x^2 + c4*x*y + c5*y^2 has one eigenvalue ~ 1/(2*R) ~ 0.007!
    # Let's fit second-order Taylor expansion:
    A = np.column_stack([np.ones_like(x_n), x_n, y_n, x_n**2, x_n*y_n, y_n**2])
    # Solve least squares
    coeff, _, _, _ = np.linalg.lstsq(A, z_n, rcond=None)
    
    # Hessian matrix of the quadratic form:
    H = np.array([[2*coeff[3], coeff[4]], [coeff[4], 2*coeff[5]]])
    eig_H = np.sort(np.linalg.eigvalsh(H))[::-1]
    
    # Max principal curvature
    max_curv = float(np.max(np.abs(eig_H)))
    
    print(f"{stem:18s}: eig_H = [{eig_H[0]:.6f}, {eig_H[1]:.6f}], max_curv = {max_curv:.6f}")

print("=== TRUE BASE AXES ===")
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
    check_curvature(stem, vt)

print("\n=== PERPENDICULAR DECOYS ON POT E WALL PIECES ===")
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
            print(f"Decoy k={k}:")
            check_curvature(stem, vt)
