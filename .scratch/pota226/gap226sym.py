#!/usr/bin/env python3
"""POTA-226 symmetric min-gap (225 pattern) for R5 candidate steps.
Only missing numbers: P25@10, P25@8. Controls: P25@4p5 (expect 0.7906),
P27@8 (expect 5.2321) validate the pipeline."""
import numpy as np
from scipy.spatial import cKDTree
L221 = "/data/gpfs/projects/punim2657/pota221_ladder"
def L(thr, num):
    return (f"{L221}/thr_{thr}/Pot_D_Piece_{num}_Surface_0.xyz", f"{L221}/thr_{thr}/Pot_D_Piece_{num}_Surface_1.xyz")
JOBS = [
    ("P25,10",) + L("10", "25"),
    ("P25,8",) + L("8", "25"),
    ("P25,4p5",) + L("4p5", "25"),
    ("P27,8",) + L("8", "27"),
]
print("label,symmin,symmin_loc,s0_to_s1_min,s1_to_s0_min", flush=True)
for label, p0, p1 in JOBS:
    a = np.loadtxt(p0, usecols=(0, 1, 2))
    b = np.loadtxt(p1, usecols=(0, 1, 2))
    d01, i01 = cKDTree(b).query(a, k=1)
    d10, i10 = cKDTree(a).query(b, k=1)
    j01, j10 = int(np.argmin(d01)), int(np.argmin(d10))
    if d01[j01] <= d10[j10]:
        print(f"{label},{d01[j01]:.4f},S0[{a[j01,0]:.2f},{a[j01,1]:.2f},{a[j01,2]:.2f}],{d01[j01]:.4f},{d10[j10]:.4f}", flush=True)
    else:
        print(f"{label},{d10[j10]:.4f},S1[{b[j10,0]:.2f},{b[j10,1]:.2f},{b[j10,2]:.2f}],{d01[j01]:.4f},{d10[j10]:.4f}", flush=True)
print("GAP226-OK")
