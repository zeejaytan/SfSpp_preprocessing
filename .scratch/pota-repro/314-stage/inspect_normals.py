import os
import numpy as np

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"

stem = "Pot_E_Piece_31"
s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
C = np.concatenate([s0, s1], axis=1)

print("Piece 31 points:", C.shape[1])
# Normals distribution
N = C[3:6, :]
print("Mean normal:", np.mean(N, axis=1))
print("Std normal :", np.std(N, axis=1))

# Compare with wall pieces
for p in [3, 23, 24, 25, 26, 28]:
    stem = f"Pot_E_Piece_{p:02d}"
    s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
    s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
    Cw = np.concatenate([s0, s1], axis=1)
    Nw = Cw[3:6, :]
    print(f"Piece {p:02d} - Mean normal:", np.round(np.mean(Nw, axis=1), 3), "Std normal:", np.round(np.std(Nw, axis=1), 3))
