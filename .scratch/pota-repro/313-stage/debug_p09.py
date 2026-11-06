import numpy as np, os
from sfs_axes.pottmann import compute_pottmann_axis
from sfs_axes.potsac import _cluster_union, effective_step
from sfs_axes.normalized import centroid_distance, worst_wall_normalized_cost, refine_axis_normalized, DEFAULT_CLEARANCE_MM
from sfs_axes.io_axes import direction_angle_deg, read_axes
from check_ref_drift import load_surface

CORPUS = '/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp'
s0 = load_surface(f'{CORPUS}/Surfaces/Pot_E_Piece_09_Surface_0.xyz')
s1 = load_surface(f'{CORPUS}/Surfaces/Pot_E_Piece_09_Surface_1.xyz')
C = np.concatenate([s0, s1], axis=1)
n = C.shape[1]
step = 10
Cd = C[:, ::step]
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
        except Exception:
            pass

V = np.column_stack(all_cands)
reps, sizes = _cluster_union(V)

valid_reps = []
for j in range(reps.shape[1]):
    cand = reps[:, j]
    d_c = centroid_distance(cand, C)
    if d_c < 25.0 or d_c > 105.0:
        continue
    a_cand = cand[:3] / np.linalg.norm(cand[:3])
    mean_axial = np.mean(np.abs(a_cand @ C[3:6, :]))
    if mean_axial > 0.6:
        continue
    valid_reps.append(cand)

V_valid = np.column_stack(valid_reps)
costs = [worst_wall_normalized_cost(V_valid[:, j], s0, s1, min_clearance_mm=25.0) for j in range(V_valid.shape[1])]
order = np.argsort(costs)

# Take up to 32 basins for refinement
V_pool = V_valid[:, order[:32]]
refined = []
for j in range(V_pool.shape[1]):
    orig_cand = V_pool[:, j]
    orig_cost = worst_wall_normalized_cost(orig_cand, s0, s1, min_clearance_mm=0.0)
    v_ref = refine_axis_normalized(orig_cand, C, max_iters=50, tolerance=1e-3)
    d_ref = centroid_distance(v_ref, C)
    ref_cost = worst_wall_normalized_cost(v_ref, s0, s1, min_clearance_mm=0.0)
    if 25.0 <= d_ref <= 105.0 and ref_cost <= orig_cost * 1.05:
        refined.append(v_ref)
    else:
        refined.append(orig_cand)

V_ref = np.column_stack(refined)
reps_final, _ = _cluster_union(V_ref)
scores_final = [worst_wall_normalized_cost(reps_final[:, j], s0, s1, min_clearance_mm=25.0) for j in range(reps_final.shape[1])]
order_final = np.argsort(scores_final)

top6 = reps_final[:, order_final[:6]]
gt = read_axes(f'{CORPUS}/Ground Truth Axes/Pot_E_Piece_09_Axis.xyz')
rel = read_axes(f'{CORPUS}/Axes/Pot_E_Piece_09_Axis.xyz')

print(f"Final K = {top6.shape[1]}")
for k in range(top6.shape[1]):
    c = top6[:, k]
    d = centroid_distance(c, C)
    print(f"cand {k}: cost={scores_final[order_final[k]]:.5f} gt={direction_angle_deg(c[:3], gt[:3, 0]):.2f} rel={direction_angle_deg(c[:3], rel[:3, 0]):.2f} d={d:.1f}")
