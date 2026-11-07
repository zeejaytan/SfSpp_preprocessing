import os
import numpy as np

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"

for p in [3, 23, 24, 25, 26, 28, 31]:
    stem = f"Pot_E_Piece_{p:02d}"
    s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
    N0 = s0[3:6, :]
    mean_N0 = np.mean(N0, axis=1)
    norm_mean = np.linalg.norm(mean_N0)
    print(f"Piece {p:02d} s0 - Mean normal: {np.round(mean_N0, 3)}, norm={norm_mean:.3f}")
