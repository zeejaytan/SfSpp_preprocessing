import os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from sfs_axes.normalized import centroid_distance, normalized_huber_cost
from sfs_axes.io_axes import read_axes, direction_angle_deg
from inspect_p31_pkl import data

d = data[31]
cands = d['cands']
angs = d['angs']
costs = d['costs']
sizes = d['sizes']
d_c = d['d']

stem = "Pot_E_Piece_31"
s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T

print("=== DIAGNOSING PIECE 31 CANDIDATES ===")
# Inspect cand 3 (decoy 15.08), cand 2 (decoy 34.16), cand 9 (decoy 38.28), cand 10 (true 6.59)
for idx in [3, 2, 9, 10]:
    cand = cands[:, idx]
    c0 = normalized_huber_cost(cand, s0)
    c1 = normalized_huber_cost(cand, s1)
    
    # Radius profile along axis
    a = cand[:3] / np.linalg.norm(cand[:3])
    p0 = cand[3:6] - (cand[3:6] @ a) * a
    
    dp0 = s0[:3, :] - p0[:, None]
    z0 = a @ dp0
    r0 = np.linalg.norm(dp0 - a[:, None] * z0[None, :], axis=0)
    
    dp1 = s1[:3, :] - p0[:, None]
    z1 = a @ dp1
    r1 = np.linalg.norm(dp1 - a[:, None] * z1[None, :], axis=0)
    
    print(f"\nCandidate {idx:2d} (ang={angs[idx]:.2f}deg, d={d_c[idx]:.1f}mm, size={sizes[idx]}):")
    print(f"  cost S0={c0:.6f}, cost S1={c1:.6f}, max(c0,c1)={max(c0,c1):.6f}, diff=|c0-c1|={abs(c0-c1):.6f}")
    print(f"  r0 mean={np.mean(r0):.1f}mm, std={np.std(r0):.1f}mm, min={np.min(r0):.1f}, max={np.max(r0):.1f}")
    print(f"  r1 mean={np.mean(r1):.1f}mm, std={np.std(r1):.1f}mm, min={np.min(r1):.1f}, max={np.max(r1):.1f}")
    wall_thickness = np.abs(np.mean(r0) - np.mean(r1))
    print(f"  mean |r0 - r1| = {wall_thickness:.2f}mm")
