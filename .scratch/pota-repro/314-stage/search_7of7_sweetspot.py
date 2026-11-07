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

print("Searching sweet spot for ALL 7 PIECES...")
for r_thresh in [75.0, 78.0, 80.0, 82.0, 85.0]:
    for r_w in [0.00005, 0.0001, 0.00015, 0.0002]:
        for ax_w in [0.0005, 0.001, 0.0015, 0.002, 0.0025, 0.003, 0.004, 0.005]:
            for alpha in [0.10, 0.12, 0.13, 0.14, 0.15, 0.16]:
                for dedup in [8.0, 10.0, 12.0, 15.0]:
                    passed = []
                    for p in failing:
                        d = data[p]
                        costs = d['costs']
                        sizes = d['sizes']
                        d_c = d['d']
                        mean_ax = d['mean_ax']
                        angs = d['angs']
                        
                        r_pen = np.where(d_c > r_thresh, r_w * (d_c - r_thresh)**2, np.where(d_c < 40.0, 0.01 * (40.0 - d_c), 0.0))
                        ax_pen = ax_w * mean_ax
                        score = (costs + r_pen + ax_pen) / (sizes ** alpha)
                        order = np.argsort(score)
                        
                        mat = pairwise_angs[p]
                        deduped_idx = []
                        for idx in order:
                            if not any(mat[idx, kept] < dedup for kept in deduped_idx):
                                deduped_idx.append(idx)
                                
                        top2 = deduped_idx[:2]
                        if min(angs[top2]) <= 10.0:
                            passed.append(p)
                            
                    if len(passed) == 7:
                        print(f"!!! FOUND 7/7 PASS !!! r_thresh={r_thresh}, r_w={r_w}, ax_w={ax_w}, alpha={alpha}, dedup={dedup}")
                        for p in failing:
                            d = data[p]
                            costs = d['costs']
                            sizes = d['sizes']
                            d_c = d['d']
                            mean_ax = d['mean_ax']
                            angs = d['angs']
                            r_pen = np.where(d_c > r_thresh, r_w * (d_c - r_thresh)**2, np.where(d_c < 40.0, 0.01 * (40.0 - d_c), 0.0))
                            ax_pen = ax_w * mean_ax
                            score = (costs + r_pen + ax_pen) / (sizes ** alpha)
                            order = np.argsort(score)
                            mat = pairwise_angs[p]
                            deduped_idx = []
                            for idx in order:
                                if not any(mat[idx, kept] < dedup for kept in deduped_idx):
                                    deduped_idx.append(idx)
                            top2 = deduped_idx[:2]
                            print(f"  Piece {p:02d}: top2 angs = {[round(angs[i], 2) for i in top2]}")
                        sys.exit(0)

print("Sweep completed without 7/7.")
