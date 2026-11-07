import os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from test_pipeline_clean_7pieces import canonicalize, r_prior
from sfs_axes.normalized import centroid_distance, worst_wall_normalized_cost
from sfs_axes.io_axes import read_axes, direction_angle_deg
from optimize_stage_a_ranking import data

alpha = 0.14
ax_w = 0.005
r_w = 0.0
dedup = 15.0

print(f"=== CHECKING 7 PIECES WITH BEST CONFIG (alpha={alpha}, ax_w={ax_w}, dedup={dedup}) ===")
for p in [3, 23, 24, 25, 26, 28, 31]:
    d = data[p]
    costs = d['costs']
    sizes = d['sizes']
    d_c = d['d']
    mean_ax = d['mean_ax']
    angs = d['angs']
    cands = d['cands']
    
    r_pen = np.where(d_c > 90.0, r_w * (d_c - 90.0)**2, np.where(d_c < 40.0, 0.01 * (40.0 - d_c), 0.0))
    ax_pen = ax_w * mean_ax
    
    score = (costs + r_pen + ax_pen) / (sizes ** alpha)
    order = np.argsort(score)
    
    # Dedup
    deduped_idx = []
    for idx in order:
        c_curr = cands[:, idx]
        if not any(direction_angle_deg(c_curr[:3], cands[:3, kept]) < dedup for kept in deduped_idx):
            deduped_idx.append(idx)
            
    print(f"\nPiece {p:02d}:")
    for rank, idx in enumerate(deduped_idx[:4]):
        ang = angs[idx]
        status = "TRUE (<10deg)" if ang <= 10.0 else "DECOY"
        print(f"  Rank {rank}: ang={ang:5.2f}deg | d={d_c[idx]:5.1f}mm | cost={costs[idx]:.6f} | size={sizes[idx]:4d} | mean_ax={mean_ax[idx]:.3f} [{status}]")
