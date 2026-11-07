import pickle, numpy as np, sys
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
with open("/data/gpfs/projects/punim2657/sfs_preprocessing/work_314/stage_a_data.pkl", "rb") as f:
    d = pickle.load(f)
from test_mean_wall_cost import all_costs_mean, pairwise_angs
failing = [3, 23, 24, 25, 26, 28, 31]
for r_w in [0.0, 0.0001, 0.0002, 0.0005, 0.001]:
    passed = []
    for p in failing:
        costs = all_costs_mean[p]
        sizes = d[p]['sizes']
        d_c = d[p]['d']
        mean_ax = d[p]['mean_ax']
        angs = d[p]['angs']
        r_pen = np.where(d_c > 120.0, r_w * (d_c - 120.0)**2, np.where(d_c < 40.0, 0.01 * (40.0 - d_c), 0.0))
        score = (costs + r_pen + 0.002 * mean_ax) / (sizes ** 0.12)
        order = np.argsort(score)
        mat = pairwise_angs[p]
        deduped = []
        for idx in order:
            if not any(mat[idx, kept] < 15.0 for kept in deduped):
                deduped.append(idx)
        if min(angs[deduped[:2]]) <= 10.0:
            passed.append(p)
    print(f"r_w={r_w}: passed {len(passed)}/7: {passed}")
