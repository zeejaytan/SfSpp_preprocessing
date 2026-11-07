import os, sys, pickle, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")

from sfs_axes.pottmann import compute_pottmann_axis
from sfs_axes.potsac import _cluster_union, effective_step
from sfs_axes.normalized import (
    centroid_distance,
    refine_axis_normalized,
    worst_wall_normalized_cost,
    DEFAULT_CLEARANCE_MM
)
from sfs_axes.io_axes import read_axes, direction_angle_deg

def canonicalize(vt):
    vt = np.asarray(vt, dtype=float).copy()
    if vt[2] < 0: vt[:3] = -vt[:3]
    return vt

failing = [3, 23, 24, 25, 26, 28, 31]
data = {}

print("Precomputing basins and refinement for all 7 pieces...")
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
    
    # Filter out wall punctures d < 25 or mean_ax > 0.50
    valid_reps = []
    valid_sizes = []
    for j in range(reps.shape[1]):
        cand = reps[:, j]
        d_c = centroid_distance(cand, C)
        a_cand = cand[:3] / np.linalg.norm(cand[:3])
        mean_ax = np.mean(np.abs(a_cand @ C[3:6, :]))
        if d_c < DEFAULT_CLEARANCE_MM or d_c > 250.0 or mean_ax > 0.50:
            continue
        valid_reps.append(cand)
        valid_sizes.append(sizes[j])
        
    V_valid = np.column_stack(valid_reps)
    v_sizes = np.array(valid_sizes)
    
    # Pre-refine the top 35 candidates by raw cost
    raw_costs = [worst_wall_normalized_cost(V_valid[:, j], s0, s1, min_clearance_mm=0.0) for j in range(V_valid.shape[1])]
    top_idx = np.argsort(raw_costs)[:35]
    
    refined_cands = []
    ref_costs = []
    ref_sizes = []
    ref_d = []
    ref_mean_ax = []
    ref_angs = []
    
    for j in top_idx:
        orig_cand = V_valid[:, j]
        orig_cost = raw_costs[j]
        v_ref = refine_axis_normalized(orig_cand, C, max_iters=20, tolerance=1e-3)
        drift = direction_angle_deg(v_ref[:3], orig_cand[:3])
        d_ref = centroid_distance(v_ref, C)
        a_ref = v_ref[:3] / np.linalg.norm(v_ref[:3])
        mean_ax_ref = np.mean(np.abs(a_ref @ C[3:6, :]))
        ref_c = worst_wall_normalized_cost(v_ref, s0, s1, min_clearance_mm=0.0)
        
        cand_final = v_ref if (drift <= 8.0 and (DEFAULT_CLEARANCE_MM <= d_ref <= 250.0 and mean_ax_ref <= 0.50) and ref_c <= orig_cost) else orig_cand
        c_final = worst_wall_normalized_cost(cand_final, s0, s1, min_clearance_mm=0.0)
        d_final = centroid_distance(cand_final, C)
        a_final = cand_final[:3] / np.linalg.norm(cand_final[:3])
        mean_ax_final = np.mean(np.abs(a_final @ C[3:6, :]))
        
        ang = direction_angle_deg(cand_final[:3], v_gt[:3])
        for r_i in range(rel_ax.shape[1]):
            ang_r = direction_angle_deg(cand_final[:3], canonicalize(rel_ax[:, r_i])[:3])
            if ang_r < ang: ang = ang_r
            
        refined_cands.append(cand_final)
        ref_costs.append(c_final)
        ref_sizes.append(v_sizes[j])
        ref_d.append(d_final)
        ref_mean_ax.append(mean_ax_final)
        ref_angs.append(ang)
        
    data[p] = {
        'cands': np.column_stack(refined_cands),
        'costs': np.array(ref_costs),
        'sizes': np.array(ref_sizes),
        'd': np.array(ref_d),
        'mean_ax': np.array(ref_mean_ax),
        'angs': np.array(ref_angs)
    }

out_path = "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314/stage_a_data.pkl"
with open(out_path, "wb") as f:
    pickle.dump(data, f)
print(f"Data cached successfully to {out_path}!")
