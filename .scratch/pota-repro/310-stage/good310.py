#!/usr/bin/env python3
"""good310.py -- write the reference 'good axis' for Piece 08 from the 308a files.

The good axis is DEFINED by the data: the one line present in exactly the three
seeds that seated Pot A 8/8 + 15/15 (308 seeds 1, 4, 5) and absent from the five
that did not. This script finds that line by consensus among those seeds' written
files and writes it position-first (the corpus axis convention), for scoring only
-- it is never an input to any rule under test.

Output: good310.xyz (K x 6, position-first) + a printed warrant (each line's angle
to the released lines and to the others).
"""
import os, sys, itertools
import numpy as np
sys.path.insert(0, "/tmp/t310")
from sfs_axes.io_axes import read_axes, direction_angle_deg, write_axes

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
RUN = "/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0532_d330469_t308a-axes/out/pota"
SEATED = (1, 4, 5)

rel = read_axes(os.path.join(CORPUS, "Axes", "Pot_A_Piece_08_Axis.xyz"))
files = {s: read_axes(os.path.join(RUN, "paper_s%d" % s, "Pot_A_Piece_08_Axis.xyz"))
         for s in SEATED}

def ang(a, b):
    return direction_angle_deg(a[0:3], b[0:3])

# lines of the three seated seeds that agree within 2 deg with all the others
cand = []
for s in SEATED:
    for k in range(files[s].shape[1]):
        v = files[s][:, k]
        if all(any(ang(v, files[t][:, j]) < 2.0 for j in range(files[t].shape[1]))
               for t in SEATED if t != s):
            cand.append((s, k, v))

print("consensus lines across the seated seeds (2 deg):")
for s, k, v in cand:
    print("  seed %d line %d | vs released: %s | pos %.4f %.4f %.4f" %
          (s, k, " ".join("%.3f" % ang(v, rel[:, j]) for j in range(rel.shape[1])),
           v[3], v[4], v[5]))
print("pairwise angles:")
for (s1, k1, v1), (s2, k2, v2) in itertools.combinations(cand, 2):
    print("  s%d.%d vs s%d.%d = %.4f deg" % (s1, k1, s2, k2, ang(v1, v2)))

V = np.column_stack([v for _s, _k, v in cand])
write_axes("/tmp/good310.xyz", V)
print("wrote /tmp/good310.xyz K=%d" % V.shape[1])
# also the mean direction as a single reference, for a stable label
d = np.mean(V[0:3, :] / np.linalg.norm(V[0:3, :], axis=0), axis=1)
d = d / np.linalg.norm(d)
print("mean direction", " ".join("%.10f" % x for x in d))
