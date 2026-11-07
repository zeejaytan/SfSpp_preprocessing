import os, sys, numpy as np
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

def is_true_base_fragment(X, vt):
    """Clean intrinsic base classification (Ticket 314 Stage A)."""
    d_c = centroid_distance(vt, X)
    if d_c >= DEFAULT_CLEARANCE_MM:
        return False
    a = vt[:3] / np.linalg.norm(vt[:3])
    p0 = vt[3:6] - (vt[3:6] @ a) * a
    P = X[:3, :]
    N = X[3:6, :]
    dp = P - p0[:, None]
    z = a @ dp
    r = np.linalg.norm(dp - a[:, None] * z[None, :], axis=0)
    near = r < 25.0
    if np.sum(near) < 80:
        return False
    axial_normals = np.abs(a @ N[:, near])
    if np.mean(axial_normals) < 0.70:
        return False
    # Azimuthal span
    ref = np.array([1.0, 0.0, 0.0])
    if abs(np.dot(ref, a)) > 0.9: ref = np.array([0.0, 1.0, 0.0])
    u = ref - np.dot(ref, a) * a
    u /= np.linalg.norm(u)
    v = np.cross(a, u)
    r_near = (dp - a[:, None] * z[None, :])[:, near]
    x_proj = u @ r_near
    y_proj = v @ r_near
    angles = np.sort(np.arctan2(y_proj, x_proj))
    gaps = np.diff(angles)
    wrap_gap = 2 * np.pi - (angles[-1] - angles[0])
    max_gap = np.max(np.append(gaps, wrap_gap))
    span_deg = 360.0 - np.degrees(max_gap)
    if span_deg < 160.0:
        return False
    # Axial extent must exceed wall thickness (>= 15mm)
    z_extent = float(np.max(z) - np.min(z))
    if z_extent < 15.0:
        return False
    return True

failing = [3, 23, 24, 25, 26, 28, 31]

print("=== Running Clean Potsac on 7 Failing Pieces ===")

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

    # 1. Filter initial basins
    valid_reps = []
    valid_sizes = []
    for j in range(reps.shape[1]):
        cand = reps[:, j]
        d_c = centroid_distance(cand, C)
        base = is_true_base_fragment(C, cand)
        if not base and (d_c < DEFAULT_CLEARANCE_MM or d_c > 200.0):
            continue
        a = cand[:3] / np.linalg.norm(cand[:3])
        mean_ax = np.mean(np.abs(a @ C[3:6, :]))
        if not base and mean_ax > 0.50:
            continue
        valid_reps.append(cand)
        valid_sizes.append(sizes[j])

    if not valid_reps:
        valid_reps = [reps[:, 0]]
        valid_sizes = [1]

    V_valid = np.column_stack(valid_reps)
    valid_sizes = np.array(valid_sizes)

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
        # Consensus score
        score = cost / (valid_sizes[j] ** 0.10)
        scores.append(score)

    order = np.argsort(scores)
    V_top = V_valid[:, order[:32]]
    top_sizes = valid_sizes[order[:32]]

    # 2. Refine survivors with drift & physical constraints
    refined = []
    ref_sizes = []
    for j in range(V_top.shape[1]):
        orig_cand = V_top[:, j]
        orig_cost = worst_wall_normalized_cost(orig_cand, s0, s1, min_clearance_mm=25.0)
        v_ref = refine_axis_normalized(orig_cand, C, max_iters=20, tolerance=1e-3)
        drift = direction_angle_deg(v_ref[:3], orig_cand[:3])
        d_ref = centroid_distance(v_ref, C)
        base = is_true_base_fragment(C, v_ref)
        a_ref = v_ref[:3] / np.linalg.norm(v_ref[:3])
        mean_ax_ref = np.mean(np.abs(a_ref @ C[3:6, :]))
        ref_cost = worst_wall_normalized_cost(v_ref, s0, s1, min_clearance_mm=25.0)

        # Containment: reject refinement if it drifts > 8 deg or violates physical constraints
        if drift <= 8.0 and (base or (DEFAULT_CLEARANCE_MM <= d_ref <= 200.0 and mean_ax_ref <= 0.50)) and ref_cost <= orig_cost:
            refined.append(v_ref)
        else:
            refined.append(orig_cand)
        ref_sizes.append(top_sizes[j])

    V_ref = np.column_stack(refined)
    ref_sizes = np.array(ref_sizes)

    # 3. Final scoring & dedup
    final_scored = []
    for j in range(V_ref.shape[1]):
        cand = V_ref[:, j]
        d_c = centroid_distance(cand, C)
        base = is_true_base_fragment(C, cand)
        if not base and (d_c < DEFAULT_CLEARANCE_MM or d_c > 200.0):
            continue
        a = cand[:3] / np.linalg.norm(cand[:3])
        mean_ax = np.mean(np.abs(a @ C[3:6, :]))
        if not base and mean_ax > 0.50:
            continue
        err0 = compute_normalized_residual(cand, s0)[0, :]
        err1 = compute_normalized_residual(cand, s1)[0, :]
        c0 = float(np.mean(apply_robustifier(robustifier_huber, err0, None)))
        c1 = float(np.mean(apply_robustifier(robustifier_huber, err1, None)))
        cost = max(c0, c1) + r_penalty(d_c)
        score = cost / (ref_sizes[j] ** 0.10)

        min_ang = direction_angle_deg(cand[:3], v_gt[:3])
        for k in range(rel_ax.shape[1]):
            v_rel_k = canonicalize(rel_ax[:, k])
            ang_k = direction_angle_deg(cand[:3], v_rel_k[:3])
            if ang_k < min_ang: min_ang = ang_k

        final_scored.append({"cand": cand, "score": score, "cost": cost, "d": d_c, "size": ref_sizes[j], "ang": min_ang})

    final_scored.sort(key=lambda x: x["score"])

    # Dedup top candidates
    deduped = []
    for s in final_scored:
        is_dup = False
        for kept in deduped:
            if direction_angle_deg(s["cand"][:3], kept["cand"][:3]) < 10.0:
                is_dup = True
                break
        if not is_dup:
            deduped.append(s)

    top3 = deduped[:3]
    best_top2 = min([x["ang"] for x in top3[:2]])
    pass_top2 = best_top2 <= 10.0
    r0_str = f"R0: {top3[0]['ang']:.2f}deg (d={top3[0]['d']:.1f}mm, sz={top3[0]['size']})"
    r1_str = f"R1: {top3[1]['ang']:.2f}deg (d={top3[1]['d']:.1f}mm, sz={top3[1]['size']})" if len(top3) > 1 else ""
    r2_str = f"R2: {top3[2]['ang']:.2f}deg (d={top3[2]['d']:.1f}mm, sz={top3[2]['size']})" if len(top3) > 2 else ""
    print(f"Piece {p:02d} [{'PASS' if pass_top2 else 'FAIL'}]: {r0_str} | {r1_str} | {r2_str}")
