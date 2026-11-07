import os, sys, numpy as np
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_313")
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"

from sfs_axes.pottmann import compute_pottmann_axis
from sfs_axes.normalized import (
    compute_normalized_residual,
    centroid_distance,
)
from sfs_axes.potsac import _cluster_union, effective_step, patch_gap_deg
from sfs_axes.io_axes import read_axes, direction_angle_deg
from sfs_axes.robust import apply_robustifier, robustifier_huber

def canonicalize(vt):
    vt = np.asarray(vt, dtype=float).copy()
    if vt[2] < 0: vt[:3] = -vt[:3]
    return vt

failing = [3, 23, 24, 25, 26, 28, 31]

for p in failing:
    stem = f"Pot_E_Piece_{p:02d}"
    s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
    s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)

    rel_ax = read_axes(f"{CORPUS}/Axes/{stem}_Axis.xyz")
    gt_path = f"{CORPUS}/Ground Truth Axes/{stem}_Axis.xyz"
    gt_ax = read_axes(gt_path) if os.path.isfile(gt_path) else rel_ax
    v_gt = canonicalize(gt_ax[:, 0])

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

    print(f"\n=================== Piece {p:02d} ===================")
    for j in range(reps.shape[1]):
        cand = reps[:, j]
        d = centroid_distance(cand, C)
        a = cand[:3] / np.linalg.norm(cand[:3])
        mean_ax = np.mean(np.abs(a @ C[3:6, :]))
        if d < 25.0 or d > 120.0 or mean_ax > 0.50:
            continue
        err0 = compute_normalized_residual(cand, s0)[0, :]
        err1 = compute_normalized_residual(cand, s1)[0, :]
        c0 = float(np.mean(apply_robustifier(robustifier_huber, err0, None)))
        c1 = float(np.mean(apply_robustifier(robustifier_huber, err1, None)))
        cost = max(c0, c1)
        ratio_c = max(c0, c1) / (min(c0, c1) + 1e-6)

        min_ang = direction_angle_deg(cand[:3], v_gt[:3])
        for k in range(rel_ax.shape[1]):
            v_rel_k = canonicalize(rel_ax[:, k])
            ang_k = direction_angle_deg(cand[:3], v_rel_k[:3])
            if ang_k < min_ang: min_ang = ang_k

        if min_ang < 10.0 or sizes[j] > 100 or cost < 0.007:
            status = "TRUE (<10deg)" if min_ang < 10.0 else "DECOY"
            print(f"  Basin {j:3d} | size={sizes[j]:4d} | d={d:5.1f}mm | mean_ax={mean_ax:.3f} | cost={cost:.6f} (c0={c0:.6f}, c1={c1:.6f}, rat={ratio_c:.2f}) | ang={min_ang:5.2f}deg [{status}]")
