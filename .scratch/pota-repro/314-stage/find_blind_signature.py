import glob, os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from sfs_axes.io_axes import read_axes

# Let's inspect all pieces across all pots in the corpus:
# For each piece, we know whether its GT/released axis has d < 25mm.
# Let's find a blind geometric feature of the piece cloud C that separates d < 25mm pieces from d >= 25mm pieces!

data = []
for pdir in sorted(glob.glob(f"{CORPUS}/Axes/*_Axis.xyz")):
    stem = os.path.basename(pdir).replace("_Axis.xyz", "")
    s0_p = f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz"
    s1_p = f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz"
    if not os.path.exists(s0_p): continue
    s0 = np.loadtxt(s0_p, usecols=range(6)).T
    s1 = np.loadtxt(s1_p, usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)
    
    # GT / released distance
    axes = read_axes(pdir)
    c_pt = C[:3].mean(axis=1)
    min_d = 999.0
    for k in range(axes.shape[1]):
        a = axes[:3, k] / np.linalg.norm(axes[:3, k])
        p0 = axes[3:6, k]
        d = np.linalg.norm(np.cross(c_pt - p0, a))
        if d < min_d: min_d = d
    is_base = min_d < 25.0
    
    # Geometric features of cloud C:
    # 1. Bounding box / PCA dimensions
    P = C[:3, :] - c_pt[:, None]
    cov_P = np.cov(P)
    w_P, _ = np.linalg.eigh(cov_P)
    w_P = np.sort(w_P)[::-1]
    
    # 2. Normal distribution
    N0 = s0[3:6, :]
    cov_N0 = np.cov(N0)
    w_N0, v_N0 = np.linalg.eigh(cov_N0)
    w_N0 = np.sort(w_N0)[::-1]

    data.append((stem, is_base, min_d, w_P, w_N0))

print(f"Total pieces analyzed: {len(data)}")
base_pieces = [x for x in data if x[1]]
wall_pieces = [x for x in data if not x[1]]
print(f"Base pieces (d < 25mm): {len(base_pieces)}")
print(f"Wall pieces (d >= 25mm): {len(wall_pieces)}")
