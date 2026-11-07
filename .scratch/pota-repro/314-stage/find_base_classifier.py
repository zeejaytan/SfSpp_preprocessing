import glob, os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from sfs_axes.io_axes import read_axes

# Ground truth: is_base = has any released axis with d < 25mm
all_data = []
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
    is_base = (min_d < 25.0)
    
    # Feature 1: PCA eigenvalues of points P
    P = C[:3, :] - c_pt[:, None]
    w_P = np.sort(np.linalg.eigvalsh(np.cov(P)))[::-1]
    
    # Feature 2: PCA eigenvalues of normals N
    cov_N = np.cov(C[3:6, :])
    w_N = np.sort(np.linalg.eigvalsh(cov_N))[::-1]
    
    # Feature 3: Normal angular spread on s0 and s1 separately
    # For a cylindrical wall piece, normals fan out in one plane (the circumferential circle).
    # For a base floor, normals on s0 are almost constant (pointing in one direction).
    mean_n0 = np.mean(s0[3:6, :], axis=1); mean_n0 /= np.linalg.norm(mean_n0)
    dev0 = np.degrees(np.arccos(np.clip(np.abs(mean_n0 @ s0[3:6, :]), 0.0, 1.0)))
    std_ang0 = float(np.std(dev0))
    mean_ang0 = float(np.mean(dev0))
    
    mean_n1 = np.mean(s1[3:6, :], axis=1); mean_n1 /= np.linalg.norm(mean_n1)
    dev1 = np.degrees(np.arccos(np.clip(np.abs(mean_n1 @ s1[3:6, :]), 0.0, 1.0)))
    std_ang1 = float(np.std(dev1))
    mean_ang1 = float(np.mean(dev1))

    # Feature 4: What is the curvature?
    # Cylinder has one principal curvature ~ 1/R (0.01 to 0.02) and one ~ 0.
    # A base floor has BOTH principal curvatures ~ 0 (it is flat)!
    
    # Feature 5: Look at Pottmann SAC attraction basins!
    # On a wall piece, how many draws produce candidate axes with d in [40, 120] mm?
    # On a base piece, how many draws produce candidate axes with d < 25 mm?
    
    all_data.append({
        'stem': stem, 'is_base': is_base, 'min_d': min_d,
        'w_P': w_P, 'w_N': w_N,
        'mean_ang0': mean_ang0, 'std_ang0': std_ang0,
        'mean_ang1': mean_ang1, 'std_ang1': std_ang1,
    })

print(f"Total pieces: {len(all_data)}")
print("=== Base pieces with mean_ang0 / std_ang0 ===")
for d in all_data:
    if d['is_base']:
        print(f"{d['stem']:18s}: mean_ang0={d['mean_ang0']:4.1f}, std0={d['std_ang0']:4.1f} | mean_ang1={d['mean_ang1']:4.1f}, std1={d['std_ang1']:4.1f} | w_N={np.round(d['w_N'], 3)}")

print("\n=== Pot E pieces with mean_ang0 / std_ang0 ===")
for d in all_data:
    if "Pot_E" in d['stem'] and not d['is_base']:
        print(f"{d['stem']:18s}: mean_ang0={d['mean_ang0']:4.1f}, std0={d['std_ang0']:4.1f} | mean_ang1={d['mean_ang1']:4.1f}, std1={d['std_ang1']:4.1f} | w_N={np.round(d['w_N'], 3)}")
