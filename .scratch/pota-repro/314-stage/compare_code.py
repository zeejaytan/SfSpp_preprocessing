import os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from sfs_axes.potsac import run_potsac_union
from test_pipeline_clean_7pieces import run_clean_potsac, canonicalize
from sfs_axes.io_axes import read_axes, direction_angle_deg

# Read the two functions line by line and find the divergence
stem = "Pot_E_Piece_03"
s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
gt = read_axes(f"{CORPUS}/Ground Truth Axes/{stem}_Axis.xyz")
v_gt = canonicalize(gt[:, 0])

# Inspect potsac.py around run_potsac_union:
import inspect
from sfs_axes import potsac
lines_union = inspect.getsource(potsac.run_potsac_union)
lines_clean = inspect.getsource(run_clean_potsac)

print("=== LINES IN RUN_POTSAC_UNION ===")
for i, line in enumerate(lines_union.splitlines()):
    if "reps" in line or "score" in line or "order" in line or "dedup" in line or "has_cyl" in line or "valid" in line or "refine" in line:
        print(f"union {i:3d}: {line}")

print("\n=== LINES IN RUN_CLEAN_POTSAC ===")
for i, line in enumerate(lines_clean.splitlines()):
    if "reps" in line or "score" in line or "order" in line or "dedup" in line or "has_cyl" in line or "valid" in line or "refine" in line:
        print(f"clean {i:3d}: {line}")
