import os, sys, pickle, numpy as np
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from sfs_axes.io_axes import direction_angle_deg

with open("/data/gpfs/projects/punim2657/sfs_preprocessing/work_314/stage_a_data.pkl", "rb") as f:
    data = pickle.load(f)

failing = [3, 23, 24, 25, 26, 28, 31]

pairwise_angs = {}
for p in failing:
    cands = data[p]['cands']
    N = cands.shape[1]
    mat = np.zeros((N, N))
    for i in range(N):
        for j in range(i+1, N):
            a = direction_angle_deg(cands[:3, i], cands[:3, j])
            mat[i, j] = a
            mat[j, i] = a
    pairwise_angs[p] = mat

# Let's test Piece 24 and Piece 31 specifically:
print("Testing combined configs on P24 and P31:")
for r_thresh in [100.0, 110.0, 120.0]:
    for r_w in [0.0005, 0.001, 0.002]:
        for ax_w in [0.001, 0.002, 0.003, 0.004, 0.005]:
            for alpha in [0.10, 0.12, 0.14]:
                for dedup in [10.0, 11.0, 12.0, 13.0, 14.0]:
                    p24_pass = False
                    p31_pass = False
                    
                    # Check P24
                    d = data[24]
                    r_pen = np.where(d['d'] > r_thresh, r_w * (d['d'] - r_thresh)**2, np.where(d['d'] < 40.0, 0.01 * (40.0 - d['d']), 0.0))
                    score = (d['costs'] + r_pen + ax_w * d['mean_ax']) / (d['sizes'] ** alpha)
                    order = np.argsort(score)
                    mat = pairwise_angs[24]
                    deduped = []
                    for idx in order:
                        if not any(mat[idx, kept] < dedup for kept in deduped):
                            deduped.append(idx)
                    if min(d['angs'][deduped[:2]]) <= 10.0:
                        p24_pass = True
                        
                    # Check P31
                    d = data[31]
                    r_pen = np.where(d['d'] > r_thresh, r_w * (d['d'] - r_thresh)**2, np.where(d['d'] < 40.0, 0.01 * (40.0 - d['d']), 0.0))
                    score = (d['costs'] + r_pen + ax_w * d['mean_ax']) / (d['sizes'] ** alpha)
                    order = np.argsort(score)
                    mat = pairwise_angs[31]
                    deduped = []
                    for idx in order:
                        if not any(mat[idx, kept] < dedup for kept in deduped):
                            deduped.append(idx)
                    if min(d['angs'][deduped[:2]]) <= 10.0:
                        p31_pass = True
                        
                    if p24_pass and p31_pass:
                        print(f"BOTH P24 and P31 PASS! r_thresh={r_thresh}, r_w={r_w}, ax_w={ax_w}, alpha={alpha}, dedup={dedup}")
