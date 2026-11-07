import os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from sfs_axes.potsac import run_potsac_union
from test_pipeline_clean_7pieces import run_clean_potsac, canonicalize
from sfs_axes.io_axes import read_axes, direction_angle_deg

stem = "Pot_E_Piece_03"
s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
gt = read_axes(f"{CORPUS}/Ground Truth Axes/{stem}_Axis.xyz")
v_gt = canonicalize(gt[:, 0])

ax_union = run_potsac_union(s0, s1, max_candidates=6, normalized=True)
ax_clean = run_clean_potsac(s0, s1, max_candidates=6)

print("ax_union on Piece 03:")
for k in range(ax_union.shape[1]):
    print(f"  Rank {k}: ang={direction_angle_deg(ax_union[:3, k], v_gt[:3]):.2f}deg")

print("\nax_clean on Piece 03:")
for k in range(ax_clean.shape[1]):
    print(f"  Rank {k}: ang={direction_angle_deg(ax_clean[:3, k], v_gt[:3]):.2f}deg")
