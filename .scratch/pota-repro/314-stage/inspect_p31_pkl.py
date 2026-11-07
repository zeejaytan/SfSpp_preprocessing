import os, sys, pickle, numpy as np
with open("/data/gpfs/projects/punim2657/sfs_preprocessing/work_314/stage_a_data.pkl", "rb") as f:
    data = pickle.load(f)

d = data[31]
angs = d['angs']
costs = d['costs']
sizes = d['sizes']
d_c = d['d']
mean_ax = d['mean_ax']
cands = d['cands']

print("=== ALL CANDIDATES IN DATA[31] ===")
for j in range(len(angs)):
    status = "TRUE (<10deg)" if angs[j] <= 10.0 else "DECOY"
    print(f"Cand {j:2d}: ang={angs[j]:5.2f}deg | d={d_c[j]:5.1f}mm | cost={costs[j]:.6f} | size={sizes[j]:3d} | mean_ax={mean_ax[j]:.3f} [{status}]")
