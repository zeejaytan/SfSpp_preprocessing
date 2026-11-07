import os, sys, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from sfs_axes.io_axes import direction_angle_deg
from optimize_stage_a_ranking import data

d = data[31]
costs = d['costs']
sizes = d['sizes']
d_c = d['d']
mean_ax = d['mean_ax']
angs = d['angs']
cands = d['cands']

print("=== ALL 25 REFINED CANDIDATES FOR PIECE 31 ===")
for j in range(len(costs)):
    status = "TRUE (<10deg)" if angs[j] <= 10.0 else "DECOY"
    print(f"Cand {j:2d}: ang={angs[j]:5.2f}deg | d={d_c[j]:5.1f}mm | cost={costs[j]:.6f} | size={sizes[j]:3d} | mean_ax={mean_ax[j]:.3f} [{status}]")
