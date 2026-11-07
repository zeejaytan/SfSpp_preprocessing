import glob, os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from sfs_axes.io_axes import read_axes

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
    
    P = C[:3, :]
    N = C[3:6, :]
    
    # Check 1: Patch curvature along best-fit plane
    cov_P = np.cov(P - c_pt[:, None])
    w_P, v_P = np.linalg.eigh(cov_P)
    idx = np.argsort(w_P)[::-1]
    w_P = w_P[idx]
    v_P = v_P[:, idx]
    
    # Normal to dominant plane of the sherd
    n_dom = v_P[:, 2]
    # Check spread of points in the plane: ratio of eigenvalues
    # Base pieces: circular disc (w_P[0] / w_P[1] is close to 1.0)
    aspect_ratio = float(w_P[0] / (w_P[1] + 1e-6))
    
    # Check normals: on a wall piece, normals fan out in the cylinder arc.
    # The normal covariance has a clear 1D or 2D structure.
    # On a base piece with footring, normals point along n_dom on the floor, and perpendicular on footring.
    
    data.append((stem, is_base, min_d, aspect_ratio, w_P))

print("=== ALL PIECES: aspect ratio w_P[0] / w_P[1] ===")
base_ar = [x[3] for x in data if x[1]]
wall_ar = [x[3] for x in data if not x[1]]
print(f"Base aspect ratio: min={min(base_ar):.2f}, max={max(base_ar):.2f}, median={np.median(base_ar):.2f}")
print(f"Wall aspect ratio: min={min(wall_ar):.2f}, max={max(wall_ar):.2f}, median={np.median(wall_ar):.2f}")

# Look at Pot E pieces specifically:
print("\n=== Pot E pieces ===")
for x in data:
    if "Pot_E" in x[0]:
        print(f"  {x[0]}: is_base={x[1]} (min_d={x[2]:.1f}mm), aspect={x[3]:.2f}")
