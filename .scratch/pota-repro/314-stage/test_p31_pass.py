import os, sys, pickle, numpy as np
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from sfs_axes.io_axes import direction_angle_deg

with open("/data/gpfs/projects/punim2657/sfs_preprocessing/work_314/stage_a_data.pkl", "rb") as f:
    data = pickle.load(f)

# Let's check Piece 31 with r_w > 0:
d = data[31]
costs = d['costs']
sizes = d['sizes']
d_c = d['d']
mean_ax = d['mean_ax']
angs = d['angs']
cands = d['cands']

print("Checking Piece 31 ranking for different parameters:")
for r_thresh in [100.0, 110.0, 120.0]:
    for r_w in [0.0005, 0.001, 0.002]:
        for alpha in [0.0, 0.04, 0.08, 0.10, 0.12, 0.14]:
            for ax_w in [0.0, 0.005, 0.010]:
                r_pen = np.where(d_c > r_thresh, r_w * (d_c - r_thresh)**2, np.where(d_c < 40.0, 0.01 * (40.0 - d_c), 0.0))
                ax_pen = ax_w * mean_ax
                score = (costs + r_pen + ax_pen) / (sizes ** alpha)
                order = np.argsort(score)
                deduped = []
                for idx in order:
                    c_curr = cands[:, idx]
                    if not any(direction_angle_deg(c_curr[:3], cands[:3, kept]) < 12.0 for kept in deduped):
                        deduped.append(idx)
                top2 = deduped[:2]
                min_ang = min(angs[top2])
                if min_ang <= 10.0:
                    print(f"P31 PASS! r_thresh={r_thresh}, r_w={r_w}, alpha={alpha}, ax_w={ax_w} -> Top2 angs: {[round(angs[i], 2) for i in top2]}")
