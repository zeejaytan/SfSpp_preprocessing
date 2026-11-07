import os, sys, pickle, numpy as np
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from sfs_axes.normalized import normalized_huber_cost, centroid_distance
from sfs_axes.io_axes import direction_angle_deg

with open("/data/gpfs/projects/punim2657/sfs_preprocessing/work_314/stage_a_data.pkl", "rb") as f:
    data = pickle.load(f)

# Compute both S0 and S1 costs for all candidates of all 7 pieces
failing = [3, 23, 24, 25, 26, 28, 31]
all_costs_mean = {}
all_costs_max = {}

print("Computing S0 and S1 costs for all candidates...")
for p in failing:
    stem = f"Pot_E_Piece_{p:02d}"
    s0 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_0.xyz", usecols=range(6)).T
    s1 = np.loadtxt(f"{CORPUS}/Surfaces/{stem}_Surface_1.xyz", usecols=range(6)).T
    cands = data[p]['cands']
    c_mean = []
    c_max = []
    for j in range(cands.shape[1]):
        cand = cands[:, j]
        c0 = normalized_huber_cost(cand, s0)
        c1 = normalized_huber_cost(cand, s1)
        c_mean.append(0.5 * (c0 + c1))
        c_max.append(max(c0, c1))
    all_costs_mean[p] = np.array(c_mean)
    all_costs_max[p] = np.array(c_max)

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

print("Testing mean wall cost across parameters...")
for min_size in [1, 5, 8]:
    for r_thresh in [80.0, 90.0, 100.0, 110.0, 120.0]:
        for r_w in [0.0, 0.0001, 0.0005, 0.001]:
            for ax_w in [0.0, 0.002, 0.003, 0.005]:
                for alpha in [0.10, 0.12, 0.14, 0.16]:
                    for dedup in [8.0, 10.0, 12.0, 15.0]:
                        passed = []
                        for p in failing:
                            d = data[p]
                            costs = all_costs_mean[p]
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
                                
                        if len(passed) == 7:
                            print(f"\n=======================================================")
                            print(f"!!! SUCCESS: 7/7 PASSED TOP 2 WITH MEAN WALL COST !!!")
                            print(f"min_size={min_size}, r_thresh={r_thresh}, r_w={r_w}, ax_w={ax_w}, alpha={alpha}, dedup={dedup}")
                            for p in failing:
                                d = data[p]
                                costs = all_costs_mean[p]
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

print("Mean wall cost sweep finished.")
