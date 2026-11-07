import os
import sys
import numpy as np

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"

def read_axis(path):
    lines = [l.strip().split() for l in open(path) if l.strip()]
    axes = []
    for l in lines:
        axes.append(np.r_[[float(x) for x in l[3:6]], [float(x) for x in l[:3]]])
    return np.column_stack(axes)

for pot in ["A", "B", "D", "E", "G", "I"]:
    for fn in sorted(os.listdir(os.path.join(CORPUS, "Axes"))):
        if not fn.startswith(f"Pot_{pot}_"):
            continue
        stem = fn[:-len("_Axis.xyz")]
        s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
        gt_path = f"{CORPUS}/Ground Truth Axes/{fn}"
        if not os.path.isfile(gt_path):
            gt_path = f"{CORPUS}/Axes/{fn}"
        ax = read_axis(gt_path)
        a = ax[:3, 0] / np.linalg.norm(ax[:3, 0])
        p0 = ax[3:6, 0]
        C = np.mean(s0[:3, :], axis=1)
        d = np.linalg.norm(np.cross(C - p0, a))
        if d < 35.0:
            print(f"{stem}: d_gt={d:.2f} mm")
