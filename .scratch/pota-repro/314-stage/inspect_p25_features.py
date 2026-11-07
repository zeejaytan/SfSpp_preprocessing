import os
import sys
import numpy as np

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_313")

from sfs_axes.normalized import compute_normalized_residual, centroid_distance
from sfs_axes.io_axes import read_axes, direction_angle_deg
from sfs_axes.potsac import patch_gap_deg

stem = "Pot_E_Piece_25"
s0_path = f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz"
s1_path = f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz"
rel_path = f"{CORPUS}/Axes/{stem}_Axis.xyz"
gt_path = f"{CORPUS}/Ground Truth Axes/{stem}_Axis.xyz"

C0 = np.loadtxt(s0_path, usecols=range(6)).T
C1 = np.loadtxt(s1_path, usecols=range(6)).T
C = np.concatenate([C0, C1], axis=1)

rel = read_axes(rel_path)
v_rel = rel[:, 0].copy()
if v_rel[2] < 0: v_rel[:3] = -v_rel[:3]

# In inspect_close_basins:
# basin 1: cand with ang_rel = 3.23 deg
# let's find basin 1 and the 26.88 deg decoy
from sfs_axes.potsac import _cluster_union, effective_step
from sfs_axes.pottmann import compute_pottmann_axis

Cd = C[:, ::effective_step(C.shape[1], 10)]
nd = Cd.shape[1]

all_cands = []
for seed in range(10):
    rng = np.random.default_rng(seed)
    for _ in range(1000):
        kidx = rng.choice(nd, 6, replace=False)
        Cs = Cd[:, kidx].copy()
        mCs = Cs[:3, :].mean(axis=1)
        Cs[:3, :] -= mCs[:, None]
        scale = float(np.mean(np.abs(Cs)))
        if scale < 1e-8: continue
        Cs[:3, :] /= scale
        try:
            vt = compute_pottmann_axis(Cs)
            vt[3:6] = vt[3:6] * scale + mCs
            vt[3:6] -= (vt[:3] @ vt[3:6]) * vt[:3]
            all_cands.append(vt)
        except Exception: pass

V = np.column_stack(all_cands)
reps, sizes = _cluster_union(V)

for j in range(reps.shape[1]):
    cand = reps[:, j]
    ang_rel = direction_angle_deg(cand[:3], v_rel[:3])
    if ang_rel < 5.0 or (25.0 < ang_rel < 30.0):
        d = centroid_distance(cand, C)
        a = cand[:3] / np.linalg.norm(cand[:3])
        mean_ax = np.mean(np.abs(a @ C[3:6, :]))
        gap = patch_gap_deg(cand, C)
        err0 = compute_normalized_residual(cand, C0)[0, :]
        err1 = compute_normalized_residual(cand, C1)[0, :]
        from sfs_axes.robust import apply_robustifier, robustifier_huber
        c0 = float(np.mean(apply_robustifier(robustifier_huber, err0, None)))
        c1 = float(np.mean(apply_robustifier(robustifier_huber, err1, None)))
        print(f"basin {j:2d} (size {sizes[j]:3d}): ang_rel={ang_rel:5.2f}deg | d={d:5.1f}mm | mean_ax={mean_ax:.3f} | gap={gap:5.1f}deg | c0={c0:.6f}, c1={c1:.6f}, max={max(c0,c1):.6f}")
