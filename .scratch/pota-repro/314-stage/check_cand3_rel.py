import os, sys, pickle, numpy as np
sys.path.insert(0, "/data/gpfs/projects/punim2657/sfs_preprocessing/work_314")
from sfs_axes.io_axes import read_axes, direction_angle_deg

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
gt = read_axes(f"{CORPUS}/Ground Truth Axes/Pot_E_Piece_31_Axis.xyz")
rel = read_axes(f"{CORPUS}/Axes/Pot_E_Piece_31_Axis.xyz")

with open("/data/gpfs/projects/punim2657/sfs_preprocessing/work_314/stage_a_data.pkl", "rb") as f:
    data = pickle.load(f)

cands = data[31]['cands']

cand3 = cands[:, 3]
cand10 = cands[:, 10]
cand1 = cands[:, 1]
cand2 = cands[:, 2]

print("Cand 3 (d=78.6mm):")
print("  ang to GT:", direction_angle_deg(cand3[:3], gt[:3, 0]))
print("  ang to rel[0]:", direction_angle_deg(cand3[:3], rel[:3, 0]))
print("  ang to rel[1]:", direction_angle_deg(cand3[:3], rel[:3, 1]))
print("  ang to rel[2]:", direction_angle_deg(cand3[:3], rel[:3, 2]))

print("\nCand 10 (d=70.3mm):")
print("  ang to GT:", direction_angle_deg(cand10[:3], gt[:3, 0]))
print("  ang to rel[2]:", direction_angle_deg(cand10[:3], rel[:3, 2]))

print("\nCand 1 (d=74.2mm):")
print("  ang to GT:", direction_angle_deg(cand1[:3], gt[:3, 0]))
print("  ang to rel[2]:", direction_angle_deg(cand1[:3], rel[:3, 2]))

print("\nCand 2 (d=79.3mm):")
print("  ang to GT:", direction_angle_deg(cand2[:3], gt[:3, 0]))
print("  ang to rel[2]:", direction_angle_deg(cand2[:3], rel[:3, 2]))

a1 = cand1[:3] / np.linalg.norm(cand1[:3])
a10 = cand10[:3] / np.linalg.norm(cand10[:3])
print("Angle Cand 1 to Cand 10:", np.degrees(np.arccos(np.clip(abs(np.dot(a1, a10)), 0, 1))))
