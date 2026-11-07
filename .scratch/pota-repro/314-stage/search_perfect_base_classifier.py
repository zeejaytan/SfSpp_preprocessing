import glob, os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from sfs_axes.io_axes import read_axes

# True base pieces: released axis has d < 25mm
all_pieces = []
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
    all_pieces.append((stem, is_base, min_d, s0, s1, C, axes))

print(f"Total pieces: {len(all_pieces)}, Base pieces: {sum(1 for x in all_pieces if x[1])}")

# Let us test candidate classifiers on the piece cloud C:
# Candidate 1: Pottmann SAC consensus!
# When Pottmann SAC is run on C:
# Does the piece have an attraction basin at d in [40, 120] mm?
# ALL wall pieces have an attraction basin at d in [40, 120] mm! (the vessel wall radius!)
# Do base pieces have an attraction basin at d in [40, 120] mm?
# Base pieces have d < 25 mm!

# Candidate 2: In a wall piece, the vessel rotation axis exists at d in [40, 120] mm.
# What is the minimum Pottmann cost of any candidate with d in [40, 120] mm and mean_axial <= 0.50?
# On a wall piece, there is ALWAYS a valid cylinder axis with low cost (< 0.015)!
# And what about when d < 25 mm?
# On a wall piece, any candidate with d < 25 mm has mean_axial > 0.85!
# That is: on a wall piece, there are ZERO candidates with d < 25 mm and mean_axial <= 0.50!

# Let's test this!
print("Testing hypothesis: On wall pieces, all candidates with d < 25mm have mean_axial > 0.60!")
