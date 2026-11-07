import os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from test_pipeline_clean_7pieces import run_clean_potsac, canonicalize, r_prior
from sfs_axes.normalized import centroid_distance, worst_wall_normalized_cost
from sfs_axes.io_axes import read_axes, direction_angle_deg

for p in [3, 24, 26, 31]:
    stem = f"Pot_E_Piece_{p:02d}"
    s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
    s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
    C = np.concatenate([s0, s1], axis=1)
    
    rel_ax = read_axes(f"{CORPUS}/Axes/{stem}_Axis.xyz")
    gt_path = f"{CORPUS}/Ground Truth Axes/{stem}_Axis.xyz"
    gt_ax = read_axes(gt_path) if os.path.isfile(gt_path) else rel_ax
    v_gt = canonicalize(gt_ax[:, 0])
    
    axes = run_clean_potsac(s0, s1, max_candidates=6)
    print(f"\n================ Piece {p:02d} ================")
    for k in range(axes.shape[1]):
        cand = axes[:, k]
        d = centroid_distance(cand, C)
        a = cand[:3] / np.linalg.norm(cand[:3])
        mean_ax = np.mean(np.abs(a @ C[3:6, :]))
        c = worst_wall_normalized_cost(cand, s0, s1, min_clearance_mm=0.0)
        pen = r_prior(d)
        
        min_ang = direction_angle_deg(cand[:3], v_gt[:3])
        for r_idx in range(rel_ax.shape[1]):
            v_rel_k = canonicalize(rel_ax[:, r_idx])
            ang_k = direction_angle_deg(cand[:3], v_rel_k[:3])
            if ang_k < min_ang: min_ang = ang_k
        print(f"Rank {k}: ang={min_ang:5.2f}deg | d={d:5.1f}mm | cost={c:.6f} | pen={pen:.6f} | mean_ax={mean_ax:.3f}")
