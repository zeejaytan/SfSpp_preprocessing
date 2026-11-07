import glob, os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from sfs_axes.io_axes import read_axes
from sfs_axes.normalized import centroid_distance

# Collect all true base pieces: pieces where released axis has d < 25mm
true_base_items = []
for pdir in sorted(glob.glob(f"{CORPUS}/Axes/*_Axis.xyz")):
    stem = os.path.basename(pdir).replace("_Axis.xyz", "")
    s0_p = f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz"
    s1_p = f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz"
    if not os.path.exists(s0_p): continue
    s0 = np.loadtxt(s0_p, usecols=range(6)).T
    s1 = np.loadtxt(s1_p, usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)
    c_pt = C[:3].mean(axis=1)
    axes = read_axes(pdir)
    for k in range(axes.shape[1]):
        vt = axes[:, k]
        a = vt[:3] / np.linalg.norm(vt[:3])
        d = np.linalg.norm(np.cross(c_pt - vt[3:6], a))
        if d < 25.0:
            true_base_items.append((stem, C, s0, s1, vt, d))

# Collect perpendicular decoys on Pot E pieces
AXES313 = "/data/gpfs/projects/punim2657/SfSpp/runs/20261106-1316_fe906ab_t313a-axes/out/axes313"
decoy_items = []
for p in range(1, 32):
    stem = f"Pot_E_Piece_{p:02d}"
    ax_p = f"{AXES313}/{stem}_Axis.xyz"
    if not os.path.exists(ax_p): continue
    axes = read_axes(ax_p)
    s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
    s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)
    c_pt = C[:3].mean(axis=1)
    for k in range(axes.shape[1]):
        vt = axes[:, k]
        a = vt[:3] / np.linalg.norm(vt[:3])
        d = np.linalg.norm(np.cross(c_pt - vt[3:6], a))
        mean_ax = np.mean(np.abs(a @ C[3:6, :]))
        if d < 25.0 and mean_ax > 0.70:
            decoy_items.append((f"{stem}_k{k}", C, s0, s1, vt, d))

print(f"True base items: {len(true_base_items)}")
print(f"Decoy items: {len(decoy_items)}")

# Let's inspect features for true bases vs decoys
def extract_features(C, s0, s1, vt):
    a = vt[:3] / np.linalg.norm(vt[:3])
    p0 = vt[3:6] - (vt[3:6] @ a) * a
    P = C[:3, :]
    N = C[3:6, :]
    dp = P - p0[:, None]
    z = a @ dp
    r_vec = dp - a[:, None] * z[None, :]
    r = np.linalg.norm(r_vec, axis=0)
    
    # 1. Near points (r < 25mm)
    near = r < 25.0
    num_near = int(np.sum(near))
    mean_ax_near = float(np.mean(np.abs(a @ N[:, near]))) if num_near > 0 else 0.0
    
    # 2. Far points (r > 35mm)
    far = r > 35.0
    num_far = int(np.sum(far))
    mean_ax_far = float(np.mean(np.abs(a @ N[:, far]))) if num_far > 0 else 0.0
    
    # 3. Ratio of radial spread: max_r / (d + 1e-3)
    max_r = float(np.max(r))
    
    # 4. Azimuthal span of ALL points around the axis
    u = np.array([1.0, 0.0, 0.0])
    if abs(u @ a) > 0.9: u = np.array([0.0, 1.0, 0.0])
    u = u - (u @ a) * a; u /= np.linalg.norm(u)
    v = np.cross(a, u)
    th = np.arctan2(v @ r_vec, u @ r_vec)
    th_s = np.sort(np.degrees(th) % 360.0)
    gap = np.max(np.diff(np.r_[th_s, th_s[0] + 360.0]))
    all_span = 360.0 - gap
    
    # 5. Thickness along a: max(z) - min(z)
    z_span = float(np.max(z) - np.min(z))
    
    # 6. Plane curvature:
    # How much does z vary as a function of r?
    # On a flat base floor, z does not depend on r!
    # On a wall piece pierced perpendicularly, z ~ r^2 / (2R) in one direction!
    return {
        'num_near': num_near, 'mean_ax_near': mean_ax_near,
        'num_far': num_far, 'mean_ax_far': mean_ax_far,
        'max_r': max_r, 'all_span': all_span, 'z_span': z_span
    }

print("\n--- TRUE BASES ---")
for item in true_base_items[:12]:
    stem, C, s0, s1, vt, d = item
    f = extract_features(C, s0, s1, vt)
    print(f"{stem:18s} (d={d:4.1f}): near={f['num_near']:4d}, ax_near={f['mean_ax_near']:.2f}, far={f['num_far']:4d}, ax_far={f['mean_ax_far']:.2f}, max_r={f['max_r']:4.1f}, span={f['all_span']:5.1f}, z_span={f['z_span']:4.1f}")

print("\n--- DECOYS ON POT E ---")
for item in decoy_items[:12]:
    stem, C, s0, s1, vt, d = item
    f = extract_features(C, s0, s1, vt)
    print(f"{stem:18s} (d={d:4.1f}): near={f['num_near']:4d}, ax_near={f['mean_ax_near']:.2f}, far={f['num_far']:4d}, ax_far={f['mean_ax_far']:.2f}, max_r={f['max_r']:4.1f}, span={f['all_span']:5.1f}, z_span={f['z_span']:4.1f}")

