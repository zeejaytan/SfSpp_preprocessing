#!/usr/bin/env python3
"""Check candidate concordance across Pots B, D, G, I under normalized ranking."""
import os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, ".")

from sfs_axes.pottmann import compute_pottmann_axis
from sfs_axes.normalized import centroid_distance, worst_wall_normalized_cost, DEFAULT_CLEARANCE_MM
from sfs_axes.potsac import _cluster_union, effective_step
from sfs_axes.io_axes import direction_angle_deg
from check_ref_drift import load_surface, read_axis

def canonicalize(vt):
    vt = np.asarray(vt, dtype=float).copy()
    if vt[2] < 0: vt[:3] = -vt[:3]
    return vt

def angle_deg(v1, v2):
    a1 = v1[:3] / np.linalg.norm(v1[:3])
    a2 = v2[:3] / np.linalg.norm(v2[:3])
    cos = np.clip(abs(float(np.dot(a1, a2))), 0.0, 1.0)
    return float(np.degrees(np.arccos(cos)))

def is_base(X, vt):
    a = vt[:3] / np.linalg.norm(vt[:3])
    p0 = vt[3:6] - (vt[3:6] @ a) * a
    P = X[:3, :]
    N = X[3:6, :]
    dp = P - p0[:, None]
    r = np.linalg.norm(dp - a[:, None] * (a @ dp)[None, :], axis=0)
    near = r < 20.0
    if np.sum(near) < 50: return False
    axial = np.abs(a @ N[:, near])
    return bool(np.mean(axial) > 0.80)

MAX_CLEARANCE_MM = 105.0

for pot, num_p in [("B", 9), ("D", 29), ("G", 7), ("I", 27)]:
    print(f"\n=== POT {pot} ({num_p} pieces) ===")
    pieces_concordant = 0
    total_scored = 0
    for p in range(1, num_p + 1):
        stem = f"Pot_{pot}_Piece_{p:02d}"
        s0_path = os.path.join(CORPUS, "Surfaces", f"{stem}_Surface_0.xyz")
        s1_path = os.path.join(CORPUS, "Surfaces", f"{stem}_Surface_1.xyz")
        rel_path = os.path.join(CORPUS, "Axes", f"{stem}_Axis.xyz")
        if not (os.path.isfile(s0_path) and os.path.isfile(rel_path)):
            continue

        C0 = load_surface(s0_path)
        C1 = load_surface(s1_path)
        C = np.concatenate([C0, C1], axis=1)
        N = C[3:6, :]
        rel_axes = read_axis(rel_path)

        n = C.shape[1]
        step = effective_step(n, 10)
        Cd = C[:, ::step]
        nd = Cd.shape[1]

        all_cands = []
        for seed in range(5):  # 5 seeds for fast survey
            rng = np.random.default_rng(seed)
            for _ in range(500):
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
                except Exception:
                    pass

        V = np.column_stack(all_cands)
        reps, sizes = _cluster_union(V)

        valid_reps = []
        for j in range(reps.shape[1]):
            cand = reps[:, j]
            d_c = centroid_distance(cand, C)
            base = is_base(C, cand)
            if not base and (d_c < DEFAULT_CLEARANCE_MM or d_c > MAX_CLEARANCE_MM):
                continue
            a_cand = cand[:3] / np.linalg.norm(cand[:3])
            mean_axial = np.mean(np.abs(a_cand @ N))
            if not base and mean_axial > 0.6:
                continue
            valid_reps.append(cand)

        if not valid_reps:
            valid_reps = [reps[:, 0]]

        V_valid = np.column_stack(valid_reps)
        costs = [worst_wall_normalized_cost(V_valid[:, j], C0, C1, min_clearance_mm=(0.0 if is_base(C, V_valid[:, j]) else DEFAULT_CLEARANCE_MM))
                 for j in range(V_valid.shape[1])]
        order = np.argsort(costs)

        # Min angle to any released line in top 6
        min_ang = 999.0
        for k in range(min(6, len(order))):
            cand_k = canonicalize(V_valid[:, order[k]])
            for rel_idx in range(rel_axes.shape[1]):
                ang = angle_deg(cand_k, canonicalize(rel_axes[:, rel_idx]))
                if ang < min_ang: min_ang = ang

        total_scored += 1
        if min_ang <= 10.0:
            pieces_concordant += 1
        print(f"Pot {pot} Piece {p:02d}: best_top6_ang={min_ang:.2f} deg ({'<=10' if min_ang<=10 else '>10'})", flush=True)

    print(f"Pot {pot} Total Concordant: {pieces_concordant}/{total_scored} ({pieces_concordant/total_scored*100:.1f}%)")
