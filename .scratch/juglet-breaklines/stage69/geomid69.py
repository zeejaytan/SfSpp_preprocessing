#!/usr/bin/env python3
"""geomid69.py -- is a lane PCD byte-identical in its GEOMETRY, ignoring column 7?

The lane PCD writes curvature from uninitialised memory (t68 measured 1.1e+23 vs 1.5e-37 on
identical geometry), so a full-file md5 answers the wrong question when the only thing that
changed is an env var that reproduces the shipped defaults. This compares columns 1-6 to six
decimals and reports the largest nearest-dot distance between the two point sets.

Usage: geomid69.py A.pcd B.pcd   ->   one tab-separated line:
  a_dots b_dots geom_md5_a geom_md5_b identical max_nn_mm
"""
import hashlib, sys
import numpy as np
sys.path.insert(0, "/c/PR/worktrees/sfs/69/.scratch/pota-repro/292")


def read6(path):
    """(n,6) xyz+normal, skipping the PCD header."""
    rows = []
    with open(path, "rb") as f:
        in_data = False
        for raw in f:
            line = raw.decode("utf-8", "replace").strip()
            if not in_data:
                if line.upper().startswith("DATA"):
                    in_data = True
                continue
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 6:
                continue
            rows.append([float(v) for v in parts[:6]])
    return np.asarray(rows, float)


def geom_md5(A):
    txt = "\n".join("%.6f %.6f %.6f %.6f %.6f %.6f" % tuple(r) for r in A)
    return hashlib.md5(txt.encode()).hexdigest()


def main():
    a, b = sys.argv[1], sys.argv[2]
    A, B = read6(a), read6(b)
    ma, mb = geom_md5(A), geom_md5(B)
    nn = float("nan")
    if len(A) and len(B):
        from scipy.spatial import cKDTree
        d, _ = cKDTree(B[:, :3]).query(A[:, :3])
        nn = float(np.max(d))
    print("%d\t%d\t%s\t%s\t%s\t%.6f" % (len(A), len(B), ma, mb, "yes" if ma == mb else "no", nn))


if __name__ == "__main__":
    main()
