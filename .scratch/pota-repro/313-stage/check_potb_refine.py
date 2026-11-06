import os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, ".")

from sfs_axes.pottmann import compute_pottmann_axis
from sfs_axes.normalized import refine_axis_normalized, centroid_distance, worst_wall_normalized_cost
from sfs_axes.potsac import _cluster_union, effective_step
from sfs_axes.io_axes import direction_angle_deg
from check_ref_drift import load_surface, read_axis

for p in [6, 7, 9]:
    stem = f"Pot_B_Piece_{p:02d}"
    s0 = load_surface(os.path.join(CORPUS, "Surfaces", f"{stem}_Surface_0.xyz"))
    s1 = load_surface(os.path.join(CORPUS, "Surfaces", f"{stem}_Surface_1.xyz"))
    C = np.concatenate([s0, s1], axis=1)
    rel = read_axis(os.path.join(CORPUS, "Axes", f"{stem}_Axis.xyz"))
    vt_rel = rel[:, 0]
    
    n = C.shape[1]
    step = effective_step(n, 10)
    Cd = C[:, ::step]
    
    cand = []
    for seed in range(5):
        rng = np.random.default_rng(seed)
        for _ in range(500):
            kidx = rng.choice(Cd.shape[1], 6, replace=False)
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
                cand.append(vt)
            except Exception:
                pass
                
    V = np.column_stack(cand)
    reps, sizes = _cluster_union(V)
    
    # Check angle of reps before refinement
    angs_before = [direction_angle_deg(reps[:3, j], vt_rel[:3]) for j in range(reps.shape[1])]
    print(f"Pot B Piece {p:02d}: {reps.shape[1]} basins, min angle before refine: {min(angs_before):.2f} deg")
    
    # Refine reps
    refined = [refine_axis_normalized(reps[:, j], Cd, max_iters=50, tolerance=1e-3) for j in range(min(30, reps.shape[1]))]
    angs_after = [direction_angle_deg(r[:3], vt_rel[:3]) for r in refined]
    print(f"Pot B Piece {p:02d}: min angle after refine: {min(angs_after):.2f} deg")
