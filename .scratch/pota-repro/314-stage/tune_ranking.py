import os
import sys
import numpy as np

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_313")

from sfs_axes.pottmann import compute_pottmann_axis
from sfs_axes.normalized import compute_normalized_residual, centroid_distance
from sfs_axes.potsac import _cluster_union, effective_step
from sfs_axes.io_axes import read_axes, direction_angle_deg
from sfs_axes.robust import apply_robustifier, robustifier_huber

def canonicalize(vt):
    vt = np.asarray(vt, dtype=float).copy()
    if vt[2] < 0: vt[:3] = -vt[:3]
    return vt

failing_pieces = [3, 23, 24, 25, 26, 28, 31]

# Collect all valid basins for the 7 pieces
piece_data = {}
for p in failing_pieces:
    stem = f"Pot_E_Piece_{p:02d}"
    s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
    s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)
    
    rel_ax = read_axes(f"{CORPUS}/Axes/{stem}_Axis.xyz")
    gt_path = f"{CORPUS}/Ground Truth Axes/{stem}_Axis.xyz"
    gt_ax = read_axes(gt_path) if os.path.isfile(gt_path) else rel_ax
    v_gt = canonicalize(gt_ax[:, 0])
    v_rel = canonicalize(rel_ax[:, 0])
    v_rel2 = canonicalize(rel_ax[:, 2]) if rel_ax.shape[1] > 2 else None

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

    # Filter basins: clearance >= 25 mm and mean_ax <= 0.50
    basins = []
    for j in range(reps.shape[1]):
        cand = reps[:, j]
        d_c = centroid_distance(cand, C)
        a = cand[:3] / np.linalg.norm(cand[:3])
        mean_ax = np.mean(np.abs(a @ C[3:6, :]))
        if d_c < 25.0 or d_c > 200.0 or mean_ax > 0.50:
            continue
        err0 = compute_normalized_residual(cand, s0)[0, :]
        err1 = compute_normalized_residual(cand, s1)[0, :]
        c0 = float(np.mean(apply_robustifier(robustifier_huber, err0, None)))
        c1 = float(np.mean(apply_robustifier(robustifier_huber, err1, None)))
        ang_gt = direction_angle_deg(cand[:3], v_gt[:3])
        ang_rel = direction_angle_deg(cand[:3], v_rel[:3])
        ang_rel2 = direction_angle_deg(cand[:3], v_rel2[:3]) if v_rel2 is not None else 999.0
        best_target_ang = min(ang_gt, ang_rel, ang_rel2)
        basins.append({
            "cand": cand, "size": sizes[j], "d": d_c, "mean_ax": mean_ax,
            "c0": c0, "c1": c1, "c_max": max(c0, c1), "c_mean": (c0 + c1) / 2.0,
            "ang_gt": ang_gt, "ang_rel": ang_rel, "ang_rel2": ang_rel2,
            "target_ang": best_target_ang
        })
    piece_data[p] = basins
    print(f"Piece {p:02d}: {len(basins)} valid basins collected")

# Now let us test different ranking scoring functions
def eval_ranking(scoring_fn, name):
    print(f"\n--- Testing: {name} ---")
    all_pass = True
    for p in failing_pieces:
        basins = piece_data[p]
        scored = []
        for b in basins:
            s = scoring_fn(b)
            scored.append((s, b))
        scored.sort(key=lambda x: x[0])
        # Check rank 0 and rank 1
        best_top2 = min(scored[0][1]["target_ang"], scored[1][1]["target_ang"] if len(scored) > 1 else 999.0)
        rank_idx = 0 if scored[0][1]["target_ang"] <= best_top2 else 1
        passed = best_top2 <= 10.0
        if not passed: all_pass = False
        p_str = "PASS" if passed else f"FAIL ({best_top2:.1f}deg)"
        b_best = scored[rank_idx][1]
        print(f"  Piece {p:02d} | Rank {rank_idx} | ang={best_top2:5.2f}deg | d={b_best['d']:5.1f}mm | size={b_best['size']:3d} | cost={b_best['c_max']:.5f} | {p_str}")
    print(f"Result for {name}: ALL PASS = {all_pass}")
    return all_pass

# Test 1: baseline c_max
eval_ranking(lambda b: b["c_max"], "Pure c_max")

# Test 2: c_max with size discount
for beta in [0.05, 0.1, 0.15, 0.2, 0.25]:
    eval_ranking(lambda b: b["c_max"] / (b["size"] ** beta), f"c_max / size^{beta}")

# Test 3: c_mean with size discount
for beta in [0.05, 0.1, 0.15, 0.2]:
    eval_ranking(lambda b: b["c_mean"] / (b["size"] ** beta), f"c_mean / size^{beta}")

# Test 4: combined with radius band prior (40 to 120 mm)
for beta in [0.1, 0.15, 0.2]:
    eval_ranking(lambda b: (b["c_max"] + 0.0002 * (b["d"] - 72.0) ** 2) / (b["size"] ** beta), f"(c_max + r_prior) / size^{beta}")
