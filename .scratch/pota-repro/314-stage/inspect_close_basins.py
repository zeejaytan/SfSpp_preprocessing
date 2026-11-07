import os
import sys
import numpy as np

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_313")

from sfs_axes.pottmann import compute_pottmann_axis
from sfs_axes.normalized import (
    compute_normalized_residual,
    centroid_distance,
    DEFAULT_CLEARANCE_MM
)
from sfs_axes.potsac import _cluster_union, effective_step
from sfs_axes.io_axes import read_axes, direction_angle_deg
from sfs_axes.robust import apply_robustifier, robustifier_huber

def canonicalize(vt):
    vt = np.asarray(vt, dtype=float).copy()
    if vt[2] < 0: vt[:3] = -vt[:3]
    return vt

for p in [3, 25, 26, 28]:
    stem = f"Pot_E_Piece_{p:02d}"
    s0_path = f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz"
    s1_path = f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz"
    rel_path = f"{CORPUS}/Axes/{stem}_Axis.xyz"
    gt_path = f"{CORPUS}/Ground Truth Axes/{stem}_Axis.xyz"
    if not os.path.isfile(gt_path): gt_path = rel_path

    C0 = np.loadtxt(s0_path, usecols=range(6)).T
    C1 = np.loadtxt(s1_path, usecols=range(6)).T
    C = np.concatenate([C0, C1], axis=1)

    rel_ax = read_axes(rel_path)
    gt_ax = read_axes(gt_path)
    v_gt = canonicalize(gt_ax[:, 0])
    v_rel = canonicalize(rel_ax[:, 0])

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

    # List all basins within 15 deg of GT or Rel
    print(f"\nPiece {p:02d} basins (total {reps.shape[1]} basins):")
    close_basins = []
    for j in range(reps.shape[1]):
        cand = reps[:, j]
        ang_gt = direction_angle_deg(cand[:3], v_gt[:3])
        ang_rel = direction_angle_deg(cand[:3], v_rel[:3])
        d = centroid_distance(cand, C)
        a = cand[:3] / np.linalg.norm(cand[:3])
        mean_ax = np.mean(np.abs(a @ C[3:6, :]))
        if min(ang_gt, ang_rel) < 25.0:
            close_basins.append((j, sizes[j], ang_gt, ang_rel, d, mean_ax, cand))

    close_basins.sort(key=lambda x: min(x[2], x[3]))
    for cb in close_basins[:8]:
        j, sz, ag, ar, d, ma, cand = cb
        # also compute cost
        err0 = compute_normalized_residual(cand, C0)[0, :]
        err1 = compute_normalized_residual(cand, C1)[0, :]
        c0 = float(np.mean(apply_robustifier(robustifier_huber, err0, None)))
        c1 = float(np.mean(apply_robustifier(robustifier_huber, err1, None)))
        cost = max(c0, c1)
        print(f"  basin {j:2d} (size {sz:3d}): ang_gt={ag:5.2f} | ang_rel={ar:5.2f} | d={d:5.1f}mm | mean_ax={ma:.3f} | cost={cost:.6f} (c0={c0:.6f}, c1={c1:.6f})")
