import numpy as np, sys
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from sfs_axes.normalized import is_base_fragment, centroid_distance
from sfs_axes.potsac import run_potsac_union

s0 = np.loadtxt("/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Surfaces/Pot_E_Piece_03_Surface_0.xyz", usecols=range(6)).T
s1 = np.loadtxt("/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Surfaces/Pot_E_Piece_03_Surface_1.xyz", usecols=range(6)).T
C = np.concatenate([s0, s1], axis=1)

axes = run_potsac_union(s0, s1, max_candidates=6, normalized=True)
bad = axes[:, 0]
print("bad cand d:", centroid_distance(bad, C))
print("is_base_fragment(C, bad):", is_base_fragment(C, bad))

# Check why is_base_fragment returned what it did:
vt = bad
a = vt[0:3] / np.linalg.norm(vt[0:3])
p0 = vt[3:6] - (vt[3:6] @ a) * a
P = C[0:3, :]
N = C[3:6, :]
dp = P - p0[:, None]
z = a @ dp
r_vec = dp - a[:, None] * z[None, :]
r = np.linalg.norm(r_vec, axis=0)
near = r < 25.0
print("near count:", np.sum(near))
axial_normals = np.abs(a @ N[:, near])
print("mean axial normals:", np.mean(axial_normals))

ref = np.array([1.0, 0.0, 0.0])
if abs(np.dot(ref, a)) > 0.9: ref = np.array([0.0, 1.0, 0.0])
u = ref - np.dot(ref, a) * a
u /= np.linalg.norm(u)
v = np.cross(a, u)
r_near = r_vec[:, near]
x_proj = u @ r_near
y_proj = v @ r_near
angles = np.sort(np.arctan2(y_proj, x_proj))
gaps = np.diff(angles)
wrap_gap = 2 * np.pi - (angles[-1] - angles[0])
max_gap = np.max(np.append(gaps, wrap_gap))
span_deg = 360.0 - np.degrees(max_gap)
print("azimuthal span:", span_deg)
z_extent = float(np.max(z) - np.min(z))
print("z_extent:", z_extent)
