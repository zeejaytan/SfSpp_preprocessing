#!/usr/bin/env python3
"""ang310.py -- prototype: per-seed written-line angles for Pot A Piece 08.

Reads the 308a per-seed axis files and the released file; prints, per seed, every
written line's angle (deg, unsigned) to each released line, so the good axis can be
identified from the data rather than assumed.
"""
import os, sys, glob
import numpy as np

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
R = "/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0532_d330469_t308a-axes/out/pota"

def read_axes(p):
    a = np.loadtxt(p, ndmin=2)
    if a.shape[0] == 1:
        a = a.reshape(1, -1)
    return a.T          # (6, K) direction first

def ang(u, v):
    u = u / np.linalg.norm(u); v = v / np.linalg.norm(v)
    return float(np.degrees(np.arccos(min(1.0, abs(float(u @ v))))))

rel = read_axes(os.path.join(CORPUS, "Axes", "Pot_A_Piece_08_Axis.xyz"))
print("released K=%d" % rel.shape[1])
for seed in range(8):
    p = os.path.join(R, "paper_s%d" % seed, "Pot_A_Piece_08_Axis.xyz")
    a = read_axes(p)
    rows = []
    for k in range(a.shape[1]):
        rows.append(" ".join("%.2f" % ang(a[0:3, k], rel[0:3, j]) for j in range(rel.shape[1])))
    print("s%d K=%d  dir=(%s)  pos=(%s)" % (seed, a.shape[1], rows,
          " ".join("%.1f" % np.linalg.norm(a[3:6, k]) for k in range(a.shape[1]))))
