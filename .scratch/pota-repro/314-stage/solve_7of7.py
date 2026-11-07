import os, sys, pickle, numpy as np
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from sfs_axes.io_axes import direction_angle_deg

with open("/data/gpfs/projects/punim2657/sfs_preprocessing/work_314/stage_a_data.pkl", "rb") as f:
    data = pickle.load(f)

failing = [3, 23, 24, 25, 26, 28, 31]

print("=== CANDIDATES IN DATA FOR ALL 7 PIECES ===")
for p in failing:
    d = data[p]
    angs = d['angs']
    costs = d['costs']
    sizes = d['sizes']
    d_c = d['d']
    mean_ax = d['mean_ax']
    cands = d['cands']
    good = np.where(angs <= 10.0)[0]
    print(f"\nPiece {p:02d}: total {len(angs)} candidates, {len(good)} with ang <= 10 deg:")
    for idx in good:
        print(f"  cand {idx:2d}: ang={angs[idx]:5.2f}deg | d={d_c[idx]:5.1f}mm | cost={costs[idx]:.6f} | size={sizes[idx]:3d} | mean_ax={mean_ax[idx]:.3f}")

print("\n=== RUNNING SWEEP OVER RANKING PARAMETERS ===")
best_res = None
max_passed = 0

for alpha in np.linspace(0.05, 0.35, 31):
    for ax_w in [0.0, 0.002, 0.005, 0.010, 0.015, 0.020]:
        for r_w in [0.0, 0.0001, 0.0003, 0.0005, 0.001, 0.002]:
            for dedup in [8.0, 10.0, 12.0, 15.0]:
                n_pass = 0
                for p in failing:
                    d = data[p]
                    costs = d['costs']
                    sizes = d['sizes']
                    d_c = d['d']
                    mean_ax = d['mean_ax']
                    angs = d['angs']
                    cands = d['cands']
                    
                    r_pen = np.where(d_c > 120.0, r_w * (d_c - 120.0)**2, np.where(d_c < 40.0, 0.01 * (40.0 - d_c), 0.0))
                    ax_pen = ax_w * mean_ax
                    
                    score = (costs + r_pen + ax_pen) / (sizes ** alpha)
                    order = np.argsort(score)
                    
                    # Dedup
                    deduped_idx = []
                    for idx in order:
                        c_curr = cands[:, idx]
                        if not any(direction_angle_deg(c_curr[:3], cands[:3, kept]) < dedup for kept in deduped_idx):
                            deduped_idx.append(idx)
                            
                    # Check top 2
                    top2 = deduped_idx[:2]
                    min_ang = min(angs[top2])
                    if min_ang <= 10.0:
                        n_pass += 1
                        
                if n_pass > max_passed:
                    max_passed = n_pass
                    best_res = (alpha, ax_w, r_w, dedup)
                    print(f"NEW BEST: {max_passed}/7 passed with alpha={alpha:.3f}, ax_w={ax_w:.3f}, r_w={r_w:.4f}, dedup={dedup:.1f}")
                    if max_passed == 7: break
            if max_passed == 7: break
        if max_passed == 7: break
    if max_passed == 7: break

print(f"\nFinal Best Result: {max_passed}/7 pieces passed Top 2 with config {best_res}")
