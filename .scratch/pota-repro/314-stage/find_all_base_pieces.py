import os
import glob
import numpy as np

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"

def read_axis(path):
    lines = [l.strip().split() for l in open(path) if l.strip()]
    axes = []
    for l in lines:
        axes.append(np.r_[[float(x) for x in l[3:6]], [float(x) for x in l[:3]]])
    return np.column_stack(axes)

# Let's inspect every piece in Corpus and check which pieces are genuinely near the axis (d < 25 mm)
all_axes = sorted(glob.glob(f"{CORPUS}/Axes/*_Axis.xyz"))
print(f"Total pieces in corpus: {len(all_axes)}")

base_pieces = []
wall_pieces = []

for ax_path in all_axes:
    fn = os.path.basename(ax_path)
    stem = fn[:-len("_Axis.xyz")]
    s0_path = f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz"
    s1_path = f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz"
    if not os.path.isfile(s0_path) or not os.path.isfile(s1_path):
        continue
    s0 = np.loadtxt(s0_path, usecols=range(6)).T
    s1 = np.loadtxt(s1_path, usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)
    C_cent = np.mean(C[:3, :], axis=1)

    axes = read_axis(ax_path)
    min_d = min(np.linalg.norm(np.cross(C_cent - axes[3:6, k], axes[:3, k]/np.linalg.norm(axes[:3, k]))) for k in range(axes.shape[1]))
    
    if min_d < 25.0:
        base_pieces.append((stem, min_d, axes.shape[1]))
    else:
        wall_pieces.append((stem, min_d, axes.shape[1]))

print(f"\nPieces with at least one released axis having d < 25 mm ({len(base_pieces)} pieces):")
for stem, d, K in base_pieces:
    print(f"  {stem:20s}: d_min={d:5.2f} mm (K={K})")
