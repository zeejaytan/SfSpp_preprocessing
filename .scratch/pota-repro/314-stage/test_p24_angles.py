import os, sys, pickle, numpy as np
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from sfs_axes.io_axes import direction_angle_deg

with open("/data/gpfs/projects/punim2657/sfs_preprocessing/work_314/stage_a_data.pkl", "rb") as f:
    data = pickle.load(f)

d = data[24]
cands = d['cands']
angs = d['angs']
print("Pairwise angles between top decoys and true on Piece 24:")
print("cand 7 to cand 1:", direction_angle_deg(cands[:3, 7], cands[:3, 1]))
print("cand 7 to cand 2:", direction_angle_deg(cands[:3, 7], cands[:3, 2]))
print("cand 1 to cand 2:", direction_angle_deg(cands[:3, 1], cands[:3, 2]))
print("cand 7 to cand 10:", direction_angle_deg(cands[:3, 7], cands[:3, 10]))
print("cand 1 to cand 10:", direction_angle_deg(cands[:3, 1], cands[:3, 10]))
