import os, sys, pickle, numpy as np
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from sfs_axes.io_axes import direction_angle_deg

with open("/data/gpfs/projects/punim2657/sfs_preprocessing/work_314/stage_a_data.pkl", "rb") as f:
    data = pickle.load(f)

d = data[31]
costs = d['costs']
sizes = d['sizes']
d_c = d['d']
angs = d['angs']
cands = d['cands']

r_thresh = 75.0
r_w = 0.0001
alpha = 0.14
dedup = 8.0

r_pen = np.where(d_c > r_thresh, r_w * (d_c - r_thresh)**2, np.where(d_c < 40.0, 0.01 * (40.0 - d_c), 0.0))
score = (costs + r_pen) / (sizes ** alpha)
order = np.argsort(score)
deduped_idx = []
for idx in order:
    c_curr = cands[:, idx]
    if not any(direction_angle_deg(c_curr[:3], cands[:3, kept]) < dedup for kept in deduped_idx):
        deduped_idx.append(idx)

print("Piece 31 under Config B:")
for rank, idx in enumerate(deduped_idx[:4]):
    status = "TRUE" if angs[idx] <= 10.0 else "DECOY"
    print(f"Rank {rank}: cand {idx:2d} | ang={angs[idx]:5.2f}deg | d={d_c[idx]:5.1f}mm | cost={costs[idx]:.6f} | size={sizes[idx]:3d} [{status}]")
