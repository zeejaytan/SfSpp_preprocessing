import glob, os, sys, numpy as np
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_313")
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
from sfs_axes.io_axes import read_axes

def check_base_geometry(X, vt, r_thresh=25.0):
    a = vt[:3] / np.linalg.norm(vt[:3])
    p0 = vt[3:6] - (vt[3:6] @ a) * a
    P = X[:3, :]
    N = X[3:6, :]
    dp = P - p0[:, None]
    z = a @ dp
    r_vec = dp - a[:, None] * z[None, :]
    r = np.linalg.norm(r_vec, axis=0)
    
    near = r < r_thresh
    num_near = int(np.sum(near))
    if num_near < 50:
        return False, num_near, 0.0, 0.0
    
    axial_normals = np.abs(a @ N[:, near])
    mean_axial = float(np.mean(axial_normals))
    
    # Compute azimuthal span
    # Pick a reference vector orthogonal to a
    ref = np.array([1.0, 0.0, 0.0])
    if abs(np.dot(ref, a)) > 0.9:
        ref = np.array([0.0, 1.0, 0.0])
    u = ref - np.dot(ref, a) * a
    u /= np.linalg.norm(u)
    v = np.cross(a, u)
    
    r_near = r_vec[:, near]
    x_proj = u @ r_near
    y_proj = v @ r_near
    angles = np.sort(np.arctan2(y_proj, x_proj))  # in [-pi, pi]
    
    # max gap between adjacent angles
    gaps = np.diff(angles)
    wrap_gap = 2 * np.pi - (angles[-1] - angles[0])
    all_gaps = np.append(gaps, wrap_gap)
    max_gap_deg = np.degrees(np.max(all_gaps))
    span_deg = 360.0 - max_gap_deg
    
    is_base = (num_near >= 80 and mean_axial >= 0.70 and span_deg >= 160.0)
    return is_base, num_near, mean_axial, span_deg

print("=== Testing TRUE base pieces with released axes ===")
true_bases = [
    ("Pot_A_Piece_01", 0),
    ("Pot_B_Piece_01", 0),
    ("Pot_C_Piece_03", 0),
    ("Pot_D_Piece_22", 0),
    ("Pot_D_Piece_32", 0),
    ("Pot_E_Piece_34", 2),
]
for stem, line_idx in true_bases:
    s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
    s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)
    axes = read_axes(f"{CORPUS}/Axes/{stem}_Axis.xyz")
    vt = axes[:, line_idx]
    is_base, num_near, mean_ax, span = check_base_geometry(C, vt)
    print(f"{stem} line {line_idx}: is_base={is_base} (near={num_near}, mean_ax={mean_ax:.3f}, span={span:5.1f}deg)")

print("\n=== Testing WALL pieces with DECOY axes from axes313 ===")
AXES313 = "/data/gpfs/projects/punim2657/SfSpp/runs/20261106-1316_fe906ab_t313a-axes/out/axes313"
for p in [3, 23, 24, 25, 26, 28, 31]:
    stem = f"Pot_E_Piece_{p:02d}"
    s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
    s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)
    ax_p = f"{AXES313}/{stem}_Axis.xyz"
    if not os.path.exists(ax_p): continue
    axes = read_axes(ax_p)
    for k in range(axes.shape[1]):
        vt = axes[:, k]
        # check distance
        d = np.linalg.norm(np.cross(C[:3].mean(axis=1) - vt[3:6], vt[:3]/np.linalg.norm(vt[:3])))
        if d < 25.0:
            is_base, num_near, mean_ax, span = check_base_geometry(C, vt)
            print(f"{stem} line {k} (d={d:.1f}mm): is_base={is_base} (near={num_near}, mean_ax={mean_ax:.3f}, span={span:5.1f}deg)")
