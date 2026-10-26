#!/usr/bin/env python3
"""PCA bootstrap axis for one Juglet piece -- pass 1 only.

The mesh stage cannot write a surface before an axis exists
(mesh_processing_headless.cpp:2190 classify needs SFS_AXIS_FILE, the surfaces
are written at :2290), so pass 1 needs *an* axis to get two walls on disk.
This one is the cloud's centroid and first principal direction: good enough to
be a real ray through the piece, and nothing else. Its face labels are thrown
away and the final pass re-runs the stage with the PotSAC axis.

usage: boot_axis.py <cloud.pcd>   -> one line: px py pz dx dy dz
"""
import sys

import numpy as np


def read_xyz(path):
    rows = []
    with open(path) as fh:
        for ln in fh:
            s = ln.split()
            if len(s) >= 3 and not ln.startswith(("#", "VERSION", "FIELDS",
                                                 "SIZE", "TYPE", "COUNT", "WIDTH",
                                                 "HEIGHT", "VIEWPOINT", "POINTS",
                                                 "DATA")):
                try:
                    rows.append([float(x) for x in s[:3]])
                except ValueError:
                    pass
    return np.asarray(rows, dtype=float)


def main():
    pts = read_xyz(sys.argv[1])
    if pts.shape[0] < 10:
        raise SystemExit("too few points: %d" % pts.shape[0])
    c = pts.mean(axis=0)
    u, s, vt = np.linalg.svd(pts - c, full_matrices=False)
    d = vt[0] / np.linalg.norm(vt[0])
    print("%.6f %.6f %.6f %.9f %.9f %.9f" % (c[0], c[1], c[2], d[0], d[1], d[2]))


if __name__ == "__main__":
    main()
