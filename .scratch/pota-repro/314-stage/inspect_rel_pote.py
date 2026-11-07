import os
import numpy as np

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"

def read_axis(path):
    lines = [l.strip().split() for l in open(path) if l.strip()]
    axes = []
    for l in lines:
        axes.append(np.r_[[float(x) for x in l[3:6]], [float(x) for x in l[:3]]])
    return np.column_stack(axes)

for p in range(1, 32):
    stem = f"Pot_E_Piece_{p:02d}"
    s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
    s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)
    C_cent = np.mean(C[:3, :], axis=1)

    rel_path = f"{CORPUS}/Axes/{stem}_Axis.xyz"
    rel_ax = read_axis(rel_path)
    
    print(f"Piece {p:02d} (rel K={rel_ax.shape[1]}):")
    for k in range(rel_ax.shape[1]):
        a = rel_ax[:3, k] / np.linalg.norm(rel_ax[:3, k])
        p0 = rel_ax[3:6, k]
        d = np.linalg.norm(np.cross(C_cent - p0, a))
        mean_ax = np.mean(np.abs(a @ C[3:6, :]))
        print(f"  line {k}: d={d:6.2f} mm | mean_axial={mean_ax:.3f} | a={np.round(a, 3)}")
