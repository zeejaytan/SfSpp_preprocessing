import os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, ".")
from check_ref_drift import load_surface, read_axis
from sfs_axes.normalized import centroid_distance

stem = "Pot_A_Piece_01"
s0 = load_surface(os.path.join(CORPUS, "Surfaces", f"{stem}_Surface_0.xyz"))
s1 = load_surface(os.path.join(CORPUS, "Surfaces", f"{stem}_Surface_1.xyz"))
C = np.concatenate([s0, s1], axis=1)
rel = read_axis(os.path.join(CORPUS, "Axes", f"{stem}_Axis.xyz"))
vt = rel[:, 0]
a = vt[:3] / np.linalg.norm(vt[:3])
p0 = vt[3:6] - (vt[3:6] @ a) * a
P = C[:3, :]
N = C[3:6, :]
dp = P - p0[:, None]
r = np.linalg.norm(dp - a[:, None] * (a @ dp)[None, :], axis=0)

print(f"Pot A Piece 01: total points {P.shape[1]}")
print(f"min r = {np.min(r):.2f} mm, p10 r = {np.percentile(r, 10):.2f} mm, max r = {np.max(r):.2f} mm")
near = r < 20.0
print(f"Points near axis (r < 20mm): {np.sum(near)}")
print(f"Axial component |n . a| of near points: mean={np.mean(np.abs(a @ N[:, near])):.3f}")
