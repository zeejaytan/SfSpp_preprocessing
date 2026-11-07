import os, sys, numpy as np
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
from sfs_axes.io_axes import read_axes

true_bases = [
    ("Pot_A_Piece_01", 0),
    ("Pot_B_Piece_01", 0),
    ("Pot_C_Piece_03", 0),
    ("Pot_E_Piece_34", 2),
]

for stem, l_idx in true_bases:
    s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
    s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)
    axes = read_axes(f"{CORPUS}/Axes/{stem}_Axis.xyz")
    cand = axes[:, l_idx]
    a = cand[:3] / np.linalg.norm(cand[:3])
    p0 = cand[3:6] - (cand[3:6] @ a) * a
    P = C[:3, :]
    dp = P - p0[:, None]
    z = a @ dp
    r = np.linalg.norm(dp - a[:, None] * z[None, :], axis=0)
    near = r < 25.0
    z_near = z[near]
    z_ext_near = float(np.max(z_near) - np.min(z_near))
    print(f"{stem}: z_extent_near = {z_ext_near:.1f} mm")
