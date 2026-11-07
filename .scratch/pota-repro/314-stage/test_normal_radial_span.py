import os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from sfs_axes.io_axes import read_axes

def check_normal_radial_span(stem, cand):
    s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
    s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)
    
    a = cand[:3] / np.linalg.norm(cand[:3])
    N = C[3:6, :]
    
    # Project normals onto plane perpendicular to a:
    N_rad = N - a[:, None] * (a @ N)[None, :]
    norm_N_rad = np.linalg.norm(N_rad, axis=0)
    
    # Consider points where normal has significant radial component
    valid = norm_N_rad > 0.1
    if np.sum(valid) < 50:
        print(f"{stem}: too few radial normals ({np.sum(valid)})")
        return 0.0
    
    N_valid = N_rad[:, valid] / norm_N_rad[None, valid]
    
    ref = np.array([1.0, 0.0, 0.0])
    if abs(np.dot(ref, a)) > 0.9: ref = np.array([0.0, 1.0, 0.0])
    u = ref - np.dot(ref, a) * a
    u /= np.linalg.norm(u)
    v = np.cross(a, u)
    
    x = u @ N_valid
    y = v @ N_valid
    angles = np.sort(np.arctan2(y, x))
    gaps = np.diff(angles)
    wrap = 2 * np.pi - (angles[-1] - angles[0])
    max_gap = np.max(np.append(gaps, wrap))
    span_deg = 360.0 - np.degrees(max_gap)
    print(f"{stem}: normal radial span = {span_deg:.1f} deg (max_gap={np.degrees(max_gap):.1f}deg)")
    return span_deg

print("=== True Base Pieces ===")
check_normal_radial_span("Pot_A_Piece_01", read_axes(f"{CORPUS}/Axes/Pot_A_Piece_01_Axis.xyz")[:, 0])
check_normal_radial_span("Pot_B_Piece_01", read_axes(f"{CORPUS}/Axes/Pot_B_Piece_01_Axis.xyz")[:, 0])
check_normal_radial_span("Pot_C_Piece_03", read_axes(f"{CORPUS}/Axes/Pot_C_Piece_03_Axis.xyz")[:, 0])
check_normal_radial_span("Pot_E_Piece_34", read_axes(f"{CORPUS}/Axes/Pot_E_Piece_34_Axis.xyz")[:, 2])

print("\n=== Wall Pieces with Perpendicular Decoy ===")
s0 = np.loadtxt(f"{CORPUS}/Surfaces/Pot_E_Piece_03_Surface_0.xyz", usecols=range(6)).T
a_decoy = np.array([0.002, -0.828, 0.560])
cand = np.r_[a_decoy, s0[:3].mean(axis=1)]
check_normal_radial_span("Pot_E_Piece_03", cand)

s0 = np.loadtxt(f"{CORPUS}/Surfaces/Pot_E_Piece_26_Surface_0.xyz", usecols=range(6)).T
n_mean = s0[3:6, :].mean(axis=1)
cand26 = np.r_[n_mean, s0[:3].mean(axis=1)]
check_normal_radial_span("Pot_E_Piece_26", cand26)
