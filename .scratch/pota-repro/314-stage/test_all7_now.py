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

max_pass = 0
best_stat = None

for r_thresh in [75.0, 80.0, 85.0, 90.0, 100.0, 110.0, 120.0]:
    for r_w in [0.0, 0.0001, 0.0003, 0.0005, 0.001, 0.002]:
        for alpha in np.linspace(0.0, 0.30, 31):
            for dedup in [8.0, 10.0, 12.0, 15.0, 18.0, 20.0]:
                passed = []
                for p in failing:
                    d = data[p]
                    costs = d['costs']
                    sizes = d['sizes']
                    d_c = d['d']
                    angs = d['angs']
                    
                    r_pen = np.where(d_c > r_thresh, r_w * (d_c - r_thresh)**2, np.where(d_c < 40.0, 0.01 * (40.0 - d_c), 0.0))
                    score = (costs + r_pen) / (sizes ** alpha)
                    order = np.argsort(score)
                    
                    mat = pairwise_angs[p]
                    deduped_idx = []
                    for idx in order:
                        if not any(mat[idx, kept] < dedup for kept in deduped_idx):
                            deduped_idx.append(idx)
                            
                    top2 = deduped_idx[:2]
                    if min(angs[top2]) <= 10.0:
                        passed.append(p)
                        
                if len(passed) > max_pass:
                    max_pass = len(passed)
                    best_stat = (len(passed), passed, r_thresh, r_w, alpha, dedup)
                    print(f"Passed {len(passed)}/7: pieces {passed} (r_thresh={r_thresh}, r_w={r_w}, alpha={alpha:.2f}, dedup={dedup})")

print(f"\nBest config: {best_stat}")
