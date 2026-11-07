import os, sys, numpy as np
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"

from sfs_axes.normalized import centroid_distance
from sfs_axes.io_axes import read_axes

stem = "Pot_E_Piece_03"
s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
C = np.concatenate([s0, s1], axis=1)

# Let's take the decoy axis from task-589:
# Rank 0: ang=79.18deg | d= 11.7mm | mean_ax=0.898
# Let's see why is_base_fragment returned True:
from sfs_axes.normalized import is_base_fragment

# Let's find this decoy in Pottmann draws
from sfs_axes.potsac import run_potsac_union
axes = run_potsac_union(s0, s1, max_candidates=6, normalized=True)
cand = axes[:, 0]
print("Candidate 0:")
print("pos:", cand[3:6], "dir:", cand[:3])
print("d_c:", centroid_distance(cand, C))
a = cand[:3] / np.linalg.norm(cand[:3])
print("mean_axial:", np.mean(np.abs(a @ C[3:6, :])))
print("is_base_fragment:", is_base_fragment(C, cand))

# Trace inside is_base_fragment:
p0 = cand[3:6] - (cand[3:6] @ a) * a
P = C[:3, :]
N = C[3:6, :]
dp = P - p0[:, None]
z = a @ dp
r_vec = dp - a[:, None] * z[None, :]
r = np.linalg.norm(r_vec, axis=0)
near = r < 25.0
num_near = int(np.sum(near))
axial_normals = np.abs(a @ N[:, near])
mean_ax_near = float(np.mean(axial_normals))
z_extent = float(np.max(z) - np.min(z))
z_extent_near = float(np.max(z[near]) - np.min(z[near]))

print(f"num_near: {num_near}")
print(f"mean_ax_near: {mean_ax_near:.3f}")
print(f"z_extent (whole cloud): {z_extent:.1f} mm")
print(f"z_extent_near (near points): {z_extent_near:.1f} mm")
