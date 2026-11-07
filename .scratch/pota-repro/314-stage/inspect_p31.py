import numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
s0 = np.loadtxt(f"{CORPUS}/Surfaces/Pot_E_Piece_31_Surface_0.xyz", usecols=range(6)).T
s1 = np.loadtxt(f"{CORPUS}/Surfaces/Pot_E_Piece_31_Surface_1.xyz", usecols=range(6)).T
C = np.concatenate([s0, s1], axis=1)
print("Points bounds:")
print("X:", C[0].min(), C[0].max())
print("Y:", C[1].min(), C[1].max())
print("Z:", C[2].min(), C[2].max())
print("Mean pos:", C[:3].mean(axis=1))
print("Mean norm:", C[3:6].mean(axis=1))

# Check GT line
gt = np.loadtxt(f"{CORPUS}/Ground Truth Axes/Pot_E_Piece_31_Axis.xyz")
print("GT axis pos:", gt[:3], "dir:", gt[3:6])
a = gt[3:6] / np.linalg.norm(gt[3:6])
p0 = gt[:3]
d = np.linalg.norm(np.cross(C[:3].mean(axis=1) - p0, a))
print(f"d(C, GT) = {d:.2f} mm")

# Check Released lines
rel = np.loadtxt(f"{CORPUS}/Axes/Pot_E_Piece_31_Axis.xyz")
for i, r in enumerate(rel):
    ra = r[3:6] / np.linalg.norm(r[3:6])
    rp = r[:3]
    rd = np.linalg.norm(np.cross(C[:3].mean(axis=1) - rp, ra))
    cos_ang = abs(np.dot(a, ra))
    ang = np.degrees(np.arccos(min(1.0, cos_ang)))
    print(f"Rel line {i}: pos={rp}, dir={ra}, d={rd:.2f} mm, ang_to_GT={ang:.2f} deg")
