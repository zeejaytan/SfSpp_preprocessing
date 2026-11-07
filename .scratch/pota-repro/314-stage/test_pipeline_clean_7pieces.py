import os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")

from sfs_axes.pottmann import compute_pottmann_axis
from sfs_axes.potsac import _cluster_union, effective_step, BASIN_REFINE_MAX
from sfs_axes.normalized import (
    centroid_distance,
    normalized_huber_cost,
    refine_axis_normalized,
    DEFAULT_CLEARANCE_MM
)
from sfs_axes.io_axes import read_axes, direction_angle_deg

def canonicalize(vt):
    vt = np.asarray(vt, dtype=float).copy()
    if vt[2] < 0: vt[:3] = -vt[:3]
    return vt

def r_prior(d):
    if d < 40.0:
        return 0.01 * (40.0 - d)
    elif d > 120.0:
        return 0.0005 * (d - 120.0) ** 2
    return 0.0

def run_clean_potsac(C0, C1=None, max_candidates=6):
    C = np.concatenate([C0, C1], axis=1) if C1 is not None else C0
    S1 = C1 if C1 is not None else C0
    
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
    
    # Check if piece has any valid cylinder wall basin
    has_cyl_wall = False
    for j in range(reps.shape[1]):
        cand = reps[:, j]
        d_c = centroid_distance(cand, C)
        a_cand = cand[:3] / np.linalg.norm(cand[:3])
        mean_ax = np.mean(np.abs(a_cand @ C[3:6, :]))
        if d_c >= DEFAULT_CLEARANCE_MM and mean_ax <= 0.50 and sizes[j] >= 5:
            has_cyl_wall = True
            break
            
    # Filter candidates
    valid_reps = []
    valid_sizes = []
    for j in range(reps.shape[1]):
        cand = reps[:, j]
        d_c = centroid_distance(cand, C)
        a_cand = cand[:3] / np.linalg.norm(cand[:3])
        mean_ax = np.mean(np.abs(a_cand @ C[3:6, :]))
        
        # If the piece is a wall piece:
        if has_cyl_wall:
            if d_c < DEFAULT_CLEARANCE_MM: continue
            if mean_ax > 0.50: continue
            if d_c > 250.0: continue
        else:
            # Base piece
            if d_c > 250.0: continue
            
        valid_reps.append(cand)
        valid_sizes.append(sizes[j])
        
    if not valid_reps:
        valid_reps = [reps[:, 0]]
        valid_sizes = [1]
        
    V_valid = np.column_stack(valid_reps)
    valid_sizes = np.array(valid_sizes)
    
    # Score initial candidates with mean wall cost
    scores = []
    for j in range(V_valid.shape[1]):
        cand = V_valid[:, j]
        d_c = centroid_distance(cand, C)
        c0 = normalized_huber_cost(cand, C0)
        c1 = normalized_huber_cost(cand, S1)
        c = 0.5 * (c0 + c1)
        pen = r_prior(d_c) if has_cyl_wall else 0.0
        a_cand = cand[:3] / np.linalg.norm(cand[:3])
        mean_ax = np.mean(np.abs(a_cand @ C[3:6, :]))
        ax_pen = 0.002 * mean_ax
        score = (c + pen + ax_pen) / (valid_sizes[j] ** 0.12)
        scores.append(score)
        
    order = np.argsort(scores, kind="stable")
    V = V_valid[:, order[:BASIN_REFINE_MAX]]
    surv_sizes = valid_sizes[order[:BASIN_REFINE_MAX]]
    
    # Constrained refinement
    refined = []
    ref_sizes = []
    for j in range(V.shape[1]):
        orig_cand = V[:, j]
        orig_cost = 0.5 * (normalized_huber_cost(orig_cand, C0) + normalized_huber_cost(orig_cand, S1))
        v_ref = refine_axis_normalized(orig_cand, C, max_iters=20, tolerance=1e-3)
        drift = direction_angle_deg(v_ref[:3], orig_cand[:3])
        d_ref = centroid_distance(v_ref, C)
        a_ref = v_ref[:3] / np.linalg.norm(v_ref[:3])
        mean_ax_ref = np.mean(np.abs(a_ref @ C[3:6, :]))
        ref_cost = 0.5 * (normalized_huber_cost(v_ref, C0) + normalized_huber_cost(v_ref, S1))
        
        if drift <= 8.0 and (not has_cyl_wall or (DEFAULT_CLEARANCE_MM <= d_ref <= 250.0 and mean_ax_ref <= 0.50)) and ref_cost <= orig_cost:
            refined.append(v_ref)
        else:
            refined.append(orig_cand)
        ref_sizes.append(surv_sizes[j])
        
    # Score refined candidates
    final_scored = []
    for j in range(len(refined)):
        cand = refined[j]
        d_c = centroid_distance(cand, C)
        c0 = normalized_huber_cost(cand, C0)
        c1 = normalized_huber_cost(cand, S1)
        c = 0.5 * (c0 + c1)
        pen = r_prior(d_c) if has_cyl_wall else 0.0
        a_cand = cand[:3] / np.linalg.norm(cand[:3])
        mean_ax = np.mean(np.abs(a_cand @ C[3:6, :]))
        ax_pen = 0.002 * mean_ax
        score = (c + pen + ax_pen) / (ref_sizes[j] ** 0.12)
        final_scored.append((score, cand))
        
    final_scored.sort(key=lambda x: x[0])
    
    # Deduplicate within 15 degrees
    deduped = []
    for sc, cand in final_scored:
        is_dup = False
        for kept in deduped:
            if direction_angle_deg(cand[:3], kept[:3]) < 15.0:
                is_dup = True
                break
        if not is_dup:
            deduped.append(cand)
            
    return np.column_stack(deduped[:max_candidates])

if __name__ == "__main__":
    failing = [3, 23, 24, 25, 26, 28, 31]
    print("=== TESTING CLEAN POTSAC ON 7 FAILING PIECES OF POT E ===")
    all_pass = True
    for p in failing:
        stem = f"Pot_E_Piece_{p:02d}"
        s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
        s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
        C = np.concatenate([s0, s1], axis=1)

        rel_ax = read_axes(f"{CORPUS}/Axes/{stem}_Axis.xyz")
        gt_path = f"{CORPUS}/Ground Truth Axes/{stem}_Axis.xyz"
        gt_ax = read_axes(gt_path) if os.path.isfile(gt_path) else rel_ax
        v_gt = canonicalize(gt_ax[:, 0])

        axes = run_clean_potsac(s0, s1, max_candidates=6)
        print(f"\nPiece {p:02d}: returned {axes.shape[1]} lines")
        min_top2 = 999.0
        for k in range(axes.shape[1]):
            cand = axes[:, k]
            d = centroid_distance(cand, C)
            a = cand[:3] / np.linalg.norm(cand[:3])
            mean_ax = np.mean(np.abs(a @ C[3:6, :]))

            min_ang = direction_angle_deg(cand[:3], v_gt[:3])
            for r_idx in range(rel_ax.shape[1]):
                v_rel_k = canonicalize(rel_ax[:, r_idx])
                ang_k = direction_angle_deg(cand[:3], v_rel_k[:3])
                if ang_k < min_ang: min_ang = ang_k

            if k < 2 and min_ang < min_top2:
                min_top2 = min_ang

            status = "TRUE (<10deg)" if min_ang <= 10.0 else "DECOY"
            print(f"  Rank {k}: ang={min_ang:5.2f}deg | d={d:5.1f}mm | mean_ax={mean_ax:.3f} [{status}]")

        passed = min_top2 <= 10.0
        if not passed: all_pass = False
        print(f"--> Piece {p:02d} Top 2: {'PASS' if passed else 'FAIL'} (best top2: {min_top2:.2f}deg)")

    print(f"\n=======================================================")
    print(f"ALL 7 PIECES PASS TOP 2 (<10 deg)? = {all_pass}")
    print(f"=======================================================")
