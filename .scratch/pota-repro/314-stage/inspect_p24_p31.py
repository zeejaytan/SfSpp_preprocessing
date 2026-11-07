import os, sys, pickle, numpy as np
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from sfs_axes.io_axes import direction_angle_deg

with open("/data/gpfs/projects/punim2657/sfs_preprocessing/work_314/stage_a_data.pkl", "rb") as f:
    data = pickle.load(f)

for p in [24, 31]:
    d = data[p]
    costs = d['costs']
    sizes = d['sizes']
    d_c = d['d']
    mean_ax = d['mean_ax']
    angs = d['angs']
    cands = d['cands']
    
    print(f"\n================ PIECE {p} ================")
    # Print all candidates
    for i in range(len(angs)):
        status = "TRUE" if angs[i] <= 10.0 else "DECOY"
        print(f"cand {i:2d}: ang={angs[i]:5.2f}deg | d={d_c[i]:5.1f}mm | cost={costs[i]:.6f} | size={sizes[i]:3d} | mean_ax={mean_ax[i]:.3f} [{status}]")
