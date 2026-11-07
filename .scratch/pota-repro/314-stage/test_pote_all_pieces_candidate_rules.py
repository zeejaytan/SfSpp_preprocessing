import glob, os, sys, numpy as np
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_313")
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"

from sfs_axes.pottmann import compute_pottmann_axis
from sfs_axes.normalized import (
    compute_normalized_residual,
    refine_axis_normalized,
    worst_wall_normalized_cost,
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

print("=== Running Pot E pieces with candidate filtering & radius ranking ===")

for p in range(1, 35):
    stem = f"Pot_E_Piece_{p:02d}"
    s0_p = f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz"
    s1_p = f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz"
    if not os.path.exists(s0_p): continue
    s0 = np.loadtxt(s0_p, usecols=range(6)).T
    s1 = np.loadtxt(s1_p, usecols=range(6)).T
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

    valid_reps = []
    for j in range(reps.shape[1]):
        cand = reps[:, j]
        d_c = centroid_distance(cand, C)
        a = cand[:3] / np.linalg.norm(cand[:3])
        mean_ax = np.mean(np.abs(a @ C[3:6, :]))
        # Rules:
        # 1. Enforce d >= 25.0 mm on wall pieces.
        if d_c < 25.0:
            continue
        # 2. Reject whole-sherd mean axial normal > 0.50
        if mean_ax > 0.50:
            continue
        # 3. Reject d > 200.0 mm
        if d_c > 200.0:
            continue
        valid_reps.append(cand)

    if not valid_reps:
        valid_reps = [reps[:, 0]]

    V_valid = np.column_stack(valid_reps)

    # Score before refinement:
    # Prioritize physical radius band [40, 120] over d > 120
    def r_penalty(d):
        if d < 40.0: return 0.01 * (40.0 - d)
        elif d > 120.0: return 0.001 * (d - 120.0) ** 2
        return 0.0

    scores = []
    for j in range(V_valid.shape[1]):
        cand = V_valid[:, j]
        d_c = centroid_distance(cand, C)
        err0 = compute_normalized_residual(cand, s0)[0, :]
        err1 = compute_normalized_residual(cand, s1)[0, :]
        c0 = float(np.mean(apply_robustifier(robustifier_huber, err0, None)))
        c1 = float(np.mean(apply_robustifier(robustifier_huber, err1, None)))
        cost = max(c0, c1) + r_penalty(d_c)
        scores.append(cost)

    order = np.argsort(scores)
    V_top = V_valid[:, order[:32]]

    # Refine top survivors
    refined = []
    for j in range(V_top.shape[1]):
        orig_cand = V_top[:, j]
        orig_cost = worst_wall_normalized_cost(orig_cand, s0, s1, min_clearance_mm=25.0)
        v_ref = refine_axis_normalized(orig_cand, C, max_iters=50, tolerance=1e-3)
        d_ref = centroid_distance(v_ref, C)
        a_ref = v_ref[:3] / np.linalg.norm(v_ref[:3])
        mean_ax_ref = np.mean(np.abs(a_ref @ C[3:6, :]))
        ref_cost = worst_wall_normalized_cost(v_ref, s0, s1, min_clearance_mm=25.0)

        if 25.0 <= d_ref <= 200.0 and mean_ax_ref <= 0.50 and ref_cost <= orig_cost * 1.05:
            refined.append(v_ref)
        else:
            refined.append(orig_cand)

    V_ref = np.column_stack(refined)
    reps2, sizes2 = _cluster_union(V_ref)

    # Score refined
    final_scored = []
    for j in range(reps2.shape[1]):
        cand = reps2[:, j]
        d_c = centroid_distance(cand, C)
        a = cand[:3] / np.linalg.norm(cand[:3])
        mean_ax = np.mean(np.abs(a @ C[3:6, :]))
        if d_c < 25.0 or d_c > 200.0 or mean_ax > 0.50:
            continue
        err0 = compute_normalized_residual(cand, s0)[0, :]
        err1 = compute_normalized_residual(cand, s1)[0, :]
        c0 = float(np.mean(apply_robustifier(robustifier_huber, err0, None)))
        c1 = float(np.mean(apply_robustifier(robustifier_huber, err1, None)))
        cost = max(c0, c1) + r_penalty(d_c)
        
        # Check angle to all released lines and GT
        min_ang = direction_angle_deg(cand[:3], v_gt[:3])
        for k in range(rel_ax.shape[1]):
            v_rel_k = canonicalize(rel_ax[:, k])
            ang_k = direction_angle_deg(cand[:3], v_rel_k[:3])
            if ang_k < min_ang: min_ang = ang_k

        final_scored.append({"cand": cand, "cost": cost, "d": d_c, "ang": min_ang})

    final_scored.sort(key=lambda x: x["cost"])
    top = final_scored[:3]
    best_ang_top2 = min(top[0]["ang"], top[1]["ang"] if len(top) > 1 else 999.0)
    passed = best_ang_top2 <= 10.0
    status = "PASS" if passed else "FAIL"
    top_str = ", ".join([f"R{r}: {x['ang']:.1f}deg (d={x['d']:.0f}mm)" for r, x in enumerate(top)])
    print(f"Piece {p:02d} [{status}]: {top_str}")
