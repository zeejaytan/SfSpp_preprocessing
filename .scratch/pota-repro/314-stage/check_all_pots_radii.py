import glob
import os
import numpy as np
import sys

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_313")
from sfs_axes.io_axes import read_axes

all_d = {}
for pdir in sorted(glob.glob(f"{CORPUS}/Axes/*_Axis.xyz")):
    stem = os.path.basename(pdir).replace("_Axis.xyz", "")
    pot = stem.split("_")[1]
    s0_p = f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz"
    s1_p = f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz"
    if not os.path.exists(s0_p):
        continue
    s0 = np.loadtxt(s0_p, usecols=range(6)).T
    s1 = np.loadtxt(s1_p, usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)
    c_pt = C[:3].mean(axis=1)
    
    axes = read_axes(pdir)
    for k in range(axes.shape[1]):
        ax = axes[:, k]
        a = ax[:3] / np.linalg.norm(ax[:3])
        p0 = ax[3:6]
        d = np.linalg.norm(np.cross(c_pt - p0, a))
        all_d.setdefault(pot, []).append((stem, k, d))

for pot, lst in sorted(all_d.items()):
    ds = [x[2] for x in lst]
    print(f"Pot {pot}: count={len(ds)}, min={min(ds):.1f}mm, max={max(ds):.1f}mm, median={np.median(ds):.1f}mm")
    above = [x for x in lst if x[2] > 150.0]
    if above:
        print(f"   > 150mm: {above}")
