import glob, os, sys, numpy as np
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_313")
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
from sfs_axes.io_axes import read_axes

print("=== All pieces across corpus with ANY released axis d < 25mm ===")
for ax_file in sorted(glob.glob(f"{CORPUS}/Axes/*_Axis.xyz")):
    stem = os.path.basename(ax_file).replace("_Axis.xyz", "")
    s0_p = f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz"
    s1_p = f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz"
    if not os.path.exists(s0_p): continue
    s0 = np.loadtxt(s0_p, usecols=range(6)).T
    s1 = np.loadtxt(s1_p, usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)
    c_pt = C[:3].mean(axis=1)
    
    axes = read_axes(ax_file)
    for k in range(axes.shape[1]):
        a = axes[:3, k] / np.linalg.norm(axes[:3, k])
        p0 = axes[3:6, k]
        d = np.linalg.norm(np.cross(c_pt - p0, a))
        if d < 25.0:
            print(f"{stem} (line {k}): d = {d:.2f} mm")
