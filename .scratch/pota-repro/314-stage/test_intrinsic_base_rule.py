import glob, os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from sfs_axes.io_axes import read_axes

def is_intrinsic_base(s0, s1):
    C = np.concatenate([s0, s1], axis=1)
    P = C[:3, :]
    N = C[3:6, :]
    # A base piece contains a flat floor:
    # A large portion of points have normals pointing in almost the same direction (floor normal n_f).
    # Let's find the dominant normal direction:
    cov_N = np.cov(N)
    w_N, v_N = np.linalg.eigh(cov_N)
    n_dom = v_N[:, 2] # largest eigenvector
    
    # Check what fraction of points have |N . n_dom| > 0.90
    axial = np.abs(n_dom @ N)
    frac_flat = float(np.mean(axial > 0.90))
    
    # Check circular symmetry in the plane orthogonal to n_dom
    ref = np.array([1.0, 0.0, 0.0])
    if abs(np.dot(ref, n_dom)) > 0.9: ref = np.array([0.0, 1.0, 0.0])
    u = ref - np.dot(ref, n_dom) * n_dom
    u /= np.linalg.norm(u)
    v = np.cross(n_dom, u)
    
    # Project points onto floor plane
    c_pt = np.mean(P, axis=1)
    dp = P - c_pt[:, None]
    x_proj = u @ dp
    y_proj = v @ dp
    r_floor = np.sqrt(x_proj**2 + y_proj**2)
    
    # Check max radius and aspect ratio of point spread in the floor plane
    cov_2d = np.cov(np.vstack([x_proj, y_proj]))
    w_2d, _ = np.linalg.eigh(cov_2d)
    ratio_2d = float(np.max(w_2d) / (np.min(w_2d) + 1e-6))
    max_r = float(np.max(r_floor))
    
    return frac_flat, ratio_2d, max_r

print("=== Checking intrinsic base test across all 163 pieces ===")
false_positives = []
false_negatives = []

for pdir in sorted(glob.glob(f"{CORPUS}/Axes/*_Axis.xyz")):
    stem = os.path.basename(pdir).replace("_Axis.xyz", "")
    s0_p = f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz"
    s1_p = f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz"
    if not os.path.exists(s0_p): continue
    s0 = np.loadtxt(s0_p, usecols=range(6)).T
    s1 = np.loadtxt(s1_p, usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)
    
    axes = read_axes(pdir)
    c_pt = C[:3].mean(axis=1)
    min_d = 999.0
    for k in range(axes.shape[1]):
        a = axes[:3, k] / np.linalg.norm(axes[:3, k])
        p0 = axes[3:6, k]
        d = np.linalg.norm(np.cross(c_pt - p0, a))
        if d < min_d: min_d = d
    gt_is_base = min_d < 25.0
    
    frac_flat, ratio_2d, max_r = is_intrinsic_base(s0, s1)
    
    # Print for Pot E pieces
    if "Pot_E" in stem:
        print(f"{stem}: gt_base={gt_is_base} (d={min_d:.1f}mm), frac_flat={frac_flat:.2f}, ratio_2d={ratio_2d:.2f}, max_r={max_r:.1f}mm")
