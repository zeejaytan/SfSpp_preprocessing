import os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from sfs_axes.normalized import centroid_distance
from sfs_axes.io_axes import read_axes

stem = "Pot_E_Piece_31"
s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
C = np.concatenate([s0, s1], axis=1)

gt = read_axes(f"{CORPUS}/Ground Truth Axes/{stem}_Axis.xyz")
rel = read_axes(f"{CORPUS}/Axes/{stem}_Axis.xyz")

print("Centroid of Piece 31:", C[:3].mean(axis=1))
print("d(C, GT):", centroid_distance(gt[:, 0], C))
for i in range(rel.shape[1]):
    print(f"d(C, rel[{i}]):", centroid_distance(rel[:, i], C))
