import glob, os, sys, numpy as np
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_313")
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
from sfs_axes.io_axes import read_axes

true_bases = [
    ("Pot_A_Piece_01", 0),
    ("Pot_B_Piece_01", 0),
    ("Pot_C_Piece_03", 0),
    ("Pot_D_Piece_22", 0),
    ("Pot_D_Piece_32", 0),
    ("Pot_E_Piece_34", 2),
]

for stem, line_idx in true_bases:
    s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
    s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)
    axes = read_axes(f"{CORPUS}/Axes/{stem}_Axis.xyz")
    vt = axes[:, line_idx]
    a = vt[:3] / np.linalg.norm(vt[:3])
    whole_mean_ax = np.mean(np.abs(a @ C[3:6, :]))
    print(f"{stem} line {line_idx}: WHOLE-SHERD mean_axial = {whole_mean_ax:.3f}")
