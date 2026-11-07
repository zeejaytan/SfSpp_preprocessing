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

seen_fails = set()
for min_size in [1, 5]:
    for r_thresh in [75.0, 80.0, 85.0, 90.0]:
        for r_w in [0.0, 0.0001, 0.0005, 0.001]:
            for ax_w in [0.0, 0.002, 0.005]:
                for alpha in [0.10, 0.12, 0.14]:
                    for dedup in [8.0, 10.0, 12.0, 15.0]:
                        passed = []
                        failed = []
                        for p in failing:
                            d = data[p]
                            costs = d['costs']
                            sizes = d['sizes']
                            d_c = d['d']
                            mean_ax = d['mean_ax']
                            angs = d['angs']
                            
                            valid = sizes >= min_size
                            if not np.any(valid): valid = np.ones(len(sizes), dtype=bool)
                            c_sub = costs[valid]
                            s_sub = sizes[valid]
                            dc_sub = d_c[valid]
                            ma_sub = mean_ax[valid]
                            idx_map = np.where(valid)[0]
                            
                            r_pen = np.where(dc_sub > r_thresh, r_w * (dc_sub - r_thresh)**2, np.where(dc_sub < 40.0, 0.01 * (40.0 - dc_sub), 0.0))
                            ax_pen = ax_w * ma_sub
                            score = (c_sub + r_pen + ax_pen) / (s_sub ** alpha)
                            order = np.argsort(score)
                            
                            mat = pairwise_angs[p]
                            deduped_idx = []
                            for idx in order:
                                orig_i = idx_map[idx]
                                if not any(mat[orig_i, kept] < dedup for kept in deduped_idx):
                                    deduped_idx.append(orig_i)
                                    
                            top2 = deduped_idx[:2]
                            if min(angs[top2]) <= 10.0:
                                passed.append(p)
                            else:
                                failed.append(p)
                                
                        if len(passed) == 6:
                            fail_p = failed[0]
                            if fail_p not in seen_fails:
                                seen_fails.add(fail_p)
                                print(f"Passed 6/7, single failing piece is: Piece {fail_p:02d} (min_size={min_size}, r_thresh={r_thresh}, r_w={r_w}, ax_w={ax_w}, alpha={alpha}, dedup={dedup})")
