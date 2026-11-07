import os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from sfs_axes.io_axes import read_axes

def check_revolution_symmetry(stem, line_idx=0):
    s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
    s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)
    P = C[:3, :]
    
    axes = read_axes(f"{CORPUS}/Axes/{stem}_Axis.xyz")
    cand = axes[:, line_idx]
    a = cand[:3] / np.linalg.norm(cand[:3])
    p0 = cand[3:6] - (cand[3:6] @ a) * a
    
    dp = P - p0[:, None]
    z = a @ dp
    r = np.linalg.norm(dp - a[:, None] * z[None, :], axis=0)
    
    # Check circularity at height slices
    # Divide z into 10 bins
    z_min, z_max = np.percentile(z, 5), np.percentile(z, 95)
    bins = np.linspace(z_min, z_max, 11)
    
    # For each slice, compute std(r) / mean(r)
    r_cvs = []
    for b in range(10):
        in_bin = (z >= bins[b]) & (z < bins[b+1])
        if np.sum(in_bin) > 50:
            rb = r[in_bin]
            cv = np.std(rb) / (np.mean(rb) + 1e-6)
            r_cvs.append(cv)
    
    mean_cv = np.mean(r_cvs) if r_cvs else 999.0
    print(f"{stem} (line {line_idx}): z_extent={z_max-z_min:.1f}mm, mean circularity CV={mean_cv:.3f}")

print("=== True Base Piece (Pot A Piece 01) ===")
check_revolution_symmetry("Pot_A_Piece_01", 0)

print("\n=== True Base Piece (Pot B Piece 01) ===")
check_revolution_symmetry("Pot_B_Piece_01", 0)

print("\n=== Wall Piece (Pot E Piece 03) with Perpendicular Decoy ===")
# Let's test with the perpendicular decoy
from sfs_axes.potsac import run_potsac_union
s0 = np.loadtxt(f"{CORPUS}/Surfaces/Pot_E_Piece_03_Surface_0.xyz", usecols=range(6)).T
s1 = np.loadtxt(f"{CORPUS}/Surfaces/Pot_E_Piece_03_Surface_1.xyz", usecols=range(6)).T
C = np.concatenate([s0, s1], axis=1)
Cd = C[:, ::10]
P = C[:3, :]
# A perpendicular decoy:
a_decoy = np.array([0.002, -0.828, 0.560])
a_decoy /= np.linalg.norm(a_decoy)
p0_decoy = C[:3].mean(axis=1)

dp = P - p0_decoy[:, None]
z = a_decoy @ dp
r = np.linalg.norm(dp - a_decoy[:, None] * z[None, :], axis=0)
z_min, z_max = np.percentile(z, 5), np.percentile(z, 95)
bins = np.linspace(z_min, z_max, 11)
r_cvs = []
for b in range(10):
    in_bin = (z >= bins[b]) & (z < bins[b+1])
    if np.sum(in_bin) > 50:
        rb = r[in_bin]
        cv = np.std(rb) / (np.mean(rb) + 1e-6)
        r_cvs.append(cv)
mean_cv_decoy = np.mean(r_cvs)
print(f"Pot_E_Piece_03 (decoy): z_extent={z_max-z_min:.1f}mm, mean circularity CV={mean_cv_decoy:.3f}")
