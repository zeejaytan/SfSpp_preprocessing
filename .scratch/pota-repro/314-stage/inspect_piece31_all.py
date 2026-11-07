import os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from test_pipeline_clean_7pieces import canonicalize
from sfs_axes.normalized import centroid_distance, worst_wall_normalized_cost, DEFAULT_CLEARANCE_MM
from sfs_axes.pottmann import compute_pottmann_axis
from sfs_axes.potsac import _cluster_union, effective_step
from sfs_axes.io_axes import read_axes, direction_angle_deg

stem = "Pot_E_Piece_31"
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

print(f"Total basins for Piece 31: {reps.shape[1]}")
for j in range(reps.shape[1]):
    cand = reps[:, j]
    d_c = centroid_distance(cand, C)
    a_cand = cand[:3] / np.linalg.norm(cand[:3])
    mean_ax = np.mean(np.abs(a_cand @ C[3:6, :]))
    
    ang = direction_angle_deg(cand[:3], v_gt[:3])
    for r_i in range(rel_ax.shape[1]):
        ang_r = direction_angle_deg(cand[:3], canonicalize(rel_ax[:, r_i])[:3])
        if ang_r < ang: ang = ang_r
        
    c = worst_wall_normalized_cost(cand, s0, s1, min_clearance_mm=0.0)
    status = "TRUE (<10deg)" if ang <= 10.0 else "DECOY"
    if ang <= 12.0 or sizes[j] > 10:
        print(f"Basin {j:2d}: ang={ang:5.2f}deg | d={d_c:5.1f}mm | cost={c:.6f} | size={sizes[j]:3d} | mean_ax={mean_ax:.3f} [{status}]")

