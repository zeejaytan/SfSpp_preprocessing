#!/usr/bin/env python3
"""probe310.py (v2) -- conventions fixed: files are POSITION-first (io_axes)."""
import os, sys
import numpy as np
sys.path.insert(0, "/tmp/t310")

from sfs_axes.io_surfaces import read_surfaces
from sfs_axes.io_axes import read_axes, direction_angle_deg
from sfs_axes.potsac import run_potsac, _huber_per_point
from sfs_axes.refine import refine_axis

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
RUN = "/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0532_d330469_t308a-axes/out/pota"

def ang(u, v):
    return direction_angle_deg(u, v)

def line_dist(a, b):
    """distance between two axis LINES (mm): |(p_b - p_a) . (d_a x d_b)| / |d_a x d_b|"""
    da = a[0:3] / np.linalg.norm(a[0:3]); db = b[0:3] / np.linalg.norm(b[0:3])
    c = np.cross(da, db); nc = np.linalg.norm(c)
    if nc < 1e-9:
        w = b[3:6] - a[3:6]
        return float(np.linalg.norm(w - (w @ da) * da))
    return float(abs((b[3:6] - a[3:6]) @ c) / nc)

C0, C1 = read_surfaces(os.path.join(CORPUS, "Surfaces"), "A", 8, truncate=False)
C = np.concatenate([C0, C1], axis=1)
print("n0=%d n1=%d n=%d" % (C0.shape[1], C1.shape[1], C.shape[1]), flush=True)

for seed in (0, 4):
    vt = run_potsac(C0, C1, rng=np.random.default_rng(seed))
    ref = read_axes(os.path.join(RUN, "paper_s%d" % seed, "Pot_A_Piece_08_Axis.xyz"))
    print("seed %d: ours K=%d ref K=%d" % (seed, vt.shape[1], ref.shape[1]))
    for k in range(min(vt.shape[1], ref.shape[1])):
        print("   line%d  ang=%.9f  dpos=%.9f" % (k, ang(vt[0:3, k], ref[0:3, k]),
              np.linalg.norm(vt[3:6, k] - ref[3:6, k])))

print("--- unique basins across the 8 seeds' files (5 deg)")
seen = []
for seed in range(8):
    ref = read_axes(os.path.join(RUN, "paper_s%d" % seed, "Pot_A_Piece_08_Axis.xyz"))
    for k in range(ref.shape[1]):
        v = ref[:, k]
        if all(ang(v[0:3], s[0:3]) > 5.0 for s in seen):
            seen.append(v)
            print("basin %d first at seed %d line %d" % (len(seen) - 1, seed, k))
B = np.column_stack(seen)
print("angle matrix (dir deg):")
for i in range(B.shape[1]):
    print("%2d  %s" % (i, " ".join("%6.2f" % ang(B[0:3, i], B[0:3, j]) for j in range(B.shape[1]))))
print("line-to-line distance matrix (mm):")
for i in range(B.shape[1]):
    print("%2d  %s" % (i, " ".join("%8.1f" % line_dist(B[:, i], B[:, j]) for j in range(B.shape[1]))))
rel = read_axes(os.path.join(CORPUS, "Axes", "Pot_A_Piece_08_Axis.xyz"))
print("vs released (dir deg | line mm):")
for i in range(B.shape[1]):
    print("%2d  %s" % (i, "  ".join("%.2f|%.1f" % (ang(B[0:3, i], rel[0:3, j]), line_dist(B[:, i], rel[:, j]))
                                    for j in range(rel.shape[1]))))
print("costs huber/pt  C0 / C1 / worst / all | refine(C0) ang, refine(C1) ang, cross ang")
for i in range(B.shape[1]):
    h0 = _huber_per_point(B[:, i], C0); h1 = _huber_per_point(B[:, i], C1)
    va = refine_axis(B[:, i], C0, 2, 300, 1e-9)
    vb = refine_axis(B[:, i], C1, 2, 300, 1e-9)
    print("%2d  %.4e %.4e %.4e %.4e | %6.2f %6.2f %6.2f" % (i, h0, h1, max(h0, h1),
          _huber_per_point(B[:, i], C), ang(B[0:3, i], va[0:3]), ang(B[0:3, i], vb[0:3]),
          ang(va[0:3], vb[0:3])))
