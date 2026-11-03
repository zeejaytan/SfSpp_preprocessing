#!/usr/bin/env python3
"""diag69.py -- why do the estimators land far from GT on a corpus pot where the released
axis is 2 deg from truth?  Reads ONE piece and prints the geometry that decides it."""
import sys
import numpy as np

C = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
pot, piece = sys.argv[1], int(sys.argv[2])

def surf(k):
    a = np.loadtxt("%s/Surfaces/Pot_%s_Piece_%02d_Surface_%d.xyz" % (C, pot, piece, k),
                   usecols=(0, 1, 2, 3, 4, 5))
    return a.T

def ax(path):
    return np.atleast_2d(np.loadtxt(path, ndmin=2))[0]

gt = ax("%s/Ground Truth Axes/Pot_%s_Piece_%02d_Axis.xyz" % (C, pot, piece))
rel = ax("%s/Axes/Pot_%s_Piece_%02d_Axis.xyz" % (C, pot, piece))
d = gt[3:6] / np.linalg.norm(gt[3:6])
print("GT  dir %s  point %s" % (np.round(d, 4), np.round(gt[0:3], 2)))
print("rel dir %s  point %s" % (np.round(rel[3:6], 4), np.round(rel[0:3], 2)))

for k in (0, 1):
    S = surf(k)
    n = S[3:6].T
    nn = np.linalg.norm(n, axis=1)
    n = n / np.maximum(nn[:, None], 1e-12)
    cosd = np.abs(n @ d)
    x = S[0:3].T
    r = np.linalg.norm(x - gt[0:3] - np.outer((x - gt[0:3]) @ d, d), axis=1)
    print("S%d n=%6d  |n|=%.4f..%.4f  |n.d| median %.3f p10 %.3f p90 %.3f  "
          "frac |n.d|<0.3: %.2f  radius med %.2f mm  bbox %s" % (
              k, S.shape[1], nn.min(), nn.max(), np.median(cosd),
              np.percentile(cosd, 10), np.percentile(cosd, 90), (cosd < 0.3).mean(),
              np.median(r), np.round(x.max(0) - x.min(0), 1)))
    # how many points sit far from the axis (rim / flat) vs on the wall
    print("     radius percentiles 5/25/50/75/95: %s" % np.round(
        np.percentile(r, [5, 25, 50, 75, 95]), 2))
