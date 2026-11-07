import os, sys, numpy as np
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_313")
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"

from sfs_axes.pottmann import compute_pottmann_axis
from sfs_axes.normalized import (
    compute_normalized_residual,
    refine_axis_normalized,
    worst_wall_normalized_cost,
    centroid_distance,
)
from sfs_axes.potsac import _cluster_union, effective_step
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

    # Filter basins:
    valid_reps = []
    valid_sizes = []
    for j in range(reps.shape[1]):
        cand = reps[:, j]
        d = centroid_distance(cand, C)
        a = cand[:3] / np.linalg.norm(cand[:3])
        mean_ax = np.mean(np.abs(a @ C[3:6, :]))
        # Filter wall pieces: d >= 25.0 mm, d <= 120.0 mm, mean_ax <= 0.50
        if d < 25.0 or d > 120.0 or mean_ax > 0.50:
            continue
        valid_reps.append(cand)
        valid_sizes.append(sizes[j])

    V_valid = np.column_stack(valid_reps)
    valid_sizes = np.array(valid_sizes)

    # Refine with basin containment (drift <= 8.0 deg)
    refined = []
    for j in range(V_valid.shape[1]):
        orig_cand = V_valid[:, j]
        orig_cost = worst_wall_normalized_cost(orig_cand, s0, s1, min_clearance_mm=25.0)
        v_ref = refine_axis_normalized(orig_cand, C, max_iters=20, tolerance=1e-3)
        drift = direction_angle_deg(v_ref[:3], orig_cand[:3])
        d_ref = centroid_distance(v_ref, C)
        a_ref = v_ref[:3] / np.linalg.norm(v_ref[:3])
        mean_ax_ref = np.mean(np.abs(a_ref @ C[3:6, :]))
        ref_cost = worst_wall_normalized_cost(v_ref, s0, s1, min_clearance_mm=25.0)

        if drift <= 8.0 and 25.0 <= d_ref <= 120.0 and mean_ax_ref <= 0.50 and ref_cost <= orig_cost:
            refined.append(v_ref)
        else:
            refined.append(orig_cand)

    V_ref = np.column_stack(refined)
    
    # Score candidates using consensus support:
    scored = []
    for j in range(V_ref.shape[1]):
        cand = V_ref[:, j]
        d = centroid_distance(cand, C)
        err0 = compute_normalized_residual(cand, s0)[0, :]
        err1 = compute_normalized_residual(cand, s1)[0, :]
        c0 = float(np.mean(apply_robustifier(robustifier_huber, err0, None)))
        c1 = float(np.mean(apply_robustifier(robustifier_huber, err1, None)))
        cost = max(c0, c1)

        # Prioritize physical radius band [55, 85]
        dev_r = 0.0
        if d < 55.0: dev_r = (55.0 - d) ** 2
        elif d > 85.0: dev_r = (d - 85.0) ** 2

        score = (cost + 1e-4 * dev_r) / (valid_sizes[j] ** 0.12)

        min_ang = direction_angle_deg(cand[:3], v_gt[:3])
        for k in range(rel_ax.shape[1]):
            v_rel_k = canonicalize(rel_ax[:, k])
            ang_k = direction_angle_deg(cand[:3], v_rel_k[:3])
            if ang_k < min_ang: min_ang = ang_k

        scored.append({"cand": cand, "score": score, "cost": cost, "d": d, "size": valid_sizes[j], "ang": min_ang})

    scored.sort(key=lambda x: x["score"])

    # Dedup top candidates
    deduped = []
    for s in scored:
        is_dup = False
        for kept in deduped:
            if direction_angle_deg(s["cand"][:3], kept["cand"][:3]) < 10.0:
                is_dup = True
                break
        if not is_dup:
            deduped.append(s)

    top2 = deduped[:2]
    best_top2 = min([x["ang"] for x in top2])
    pass_top2 = best_top2 <= 10.0
    r0_str = f"R0: {top2[0]['ang']:.2f}deg (d={top2[0]['d']:.1f}mm, sz={top2[0]['size']})"
    r1_str = f"R1: {top2[1]['ang']:.2f}deg (d={top2[1]['d']:.1f}mm, sz={top2[1]['size']})" if len(top2) > 1 else ""
    print(f"Piece {p:02d} [{'PASS' if pass_top2 else 'FAIL'}]: {r0_str} | {r1_str}")
