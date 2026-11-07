import pickle, numpy as np, sys
with open("/data/gpfs/projects/punim2657/sfs_preprocessing/work_314/stage_a_data.pkl", "rb") as f:
    d = pickle.load(f)
print("P03 cands count:", len(d[3]['angs']))
for i in range(len(d[3]['angs'])):
    if d[3]['angs'][i] <= 10.0:
        print(f"Cand {i:2d}: ang={d[3]['angs'][i]:.2f}deg | cost={d[3]['costs'][i]:.6f} | size={d[3]['sizes'][i]} | d={d[3]['d'][i]:.1f}mm")
