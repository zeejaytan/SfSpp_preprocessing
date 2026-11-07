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

# Let's see: what if we also filter out small basins size < min_size?
for min_size in [1, 3, 5, 8, 10]:
    for r_thresh in [75.0, 78.0, 80.0, 85.0, 90.0]:
        for r_w in [0.0, 0.00005, 0.0001, 0.0002, 0.0005, 0.001]:
            for ax_w in [0.0, 0.001, 0.002, 0.003, 0.004, 0.005]:
                for alpha in [0.08, 0.10, 0.12, 0.14, 0.16]:
                    for dedup in [8.0, 10.0, 12.0, 15.0]:
                        passed = []
                        for p in failing:
                            d = data[p]
                            costs = d['costs']
                            sizes = d['sizes']
                            d_c = d['d']
                            mean_ax = d['mean_ax']
                            angs = d['angs']
                            
                            valid = sizes >= min_size
                            if not np.any(valid):
                                valid = np.ones(len(sizes), dtype=bool)
                                
                            c_sub = costs[valid]
                            s_sub = sizes[valid]
                            dc_sub = d_c[valid]
                            ma_sub = mean_ax[valid]
                            ang_sub = angs[valid]
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
                                
                        if len(passed) == 7:
                            print(f"\n=======================================================")
                            print(f"!!! SUCCESS: 7/7 PASSED TOP 2 (<10 deg) !!!")
                            print(f"min_size={min_size}, r_thresh={r_thresh}, r_w={r_w}, ax_w={ax_w}, alpha={alpha}, dedup={dedup}")
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
                                print(f"Piece {p:02d}:")
                                for rank, idx in enumerate(top2):
                                    st = "TRUE" if angs[idx] <= 10.0 else "DECOY"
                                    print(f"  Rank {rank}: ang={angs[idx]:5.2f}deg | d={d_c[idx]:5.1f}mm | cost={costs[idx]:.6f} | size={sizes[idx]:3d} [{st}]")
                            sys.exit(0)

print("Sweep finished.")
