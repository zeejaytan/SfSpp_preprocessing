#!/usr/bin/env python3
"""ticket 23: what a written surface actually covers of its own piece.

A fragment and a wall must not read the same, so for every cell that wrote at least one
surface this records how much of that piece's own cloud the surface lies on:

  n0, n1        points in Surface_0 / Surface_1
  ext*_x/y/z    bounding-box extent of that surface in mm
  diag*         its bbox diagonal in mm
  cov*_2mm      fraction of the piece's cloud points within 2 mm of that surface
  cov_union_2mm the same for Surface_0 and Surface_1 together (two-surface cells only)

A coarse surface that is one wall of a sherd covers a wall's worth of cloud; one that is the
whole sherd covers more. The number is a description, not a threshold and not a verdict.

usage: coverage23.py <cellroot>   ->  <cellroot>/coverage23.tsv
"""
import os
import sys

import numpy as np
from scipy.spatial import cKDTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from measure_arm23 import load_ply, read_cells  # noqa: E402

CANON = "/data/gpfs/projects/punim2657/sfs_preprocessing"
CORP = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
MAXPTS = 60000


def cloud_path(pot, piece):
    if pot == "Pot_A":
        return os.path.join(CORP, "Point", "Pot_A", piece + "_Point.pcd")
    return os.path.join(CANON, "Dataset", "Point", pot, piece + "_Point.pcd")


def read_pcd_xyz(path, maxpts=MAXPTS):
    """xyz from an ASCII PCD, strided down to maxpts. Reads only; never writes."""
    with open(path, "rb") as fh:
        n = 0
        for line in fh:
            if line.startswith(b"POINTS"):
                n = int(line.split()[1])
            if line.startswith(b"DATA"):
                break
        body = fh.read().splitlines()
    stride = max(1, len(body) // maxpts)
    rows = body[::stride]
    out = np.empty((len(rows), 3))
    for i, line in enumerate(rows):
        f = line.split()
        out[i] = (float(f[0]), float(f[1]), float(f[2]))
    return out, n, stride


def extents(p):
    if len(p) == 0:
        return (float("nan"),) * 3 + (float("nan"),)
    d = p.max(axis=0) - p.min(axis=0)
    return float(d[0]), float(d[1]), float(d[2]), float(np.linalg.norm(d))


def cover(cloud, surfs):
    if not surfs:
        return float("nan")
    pts = np.vstack(surfs)
    d, _ = cKDTree(pts).query(cloud, k=1, workers=-1)
    return float((d <= 2.0).mean())


def main():
    root = sys.argv[1]
    rows = read_cells(os.path.join(root, "cells23.tsv"))
    cache = {}
    out = os.path.join(root, "coverage23.tsv")
    cols = ["tag", "pot", "piece", "outcome", "n_surf", "n0", "n1",
            "ext0_x", "ext0_y", "ext0_z", "diag0", "cov0_2mm",
            "ext1_x", "ext1_y", "ext1_z", "diag1", "cov1_2mm",
            "cov_union_2mm", "ncloud_total", "cloud_stride"]
    with open(out, "w") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            base = os.path.join(root, r["tag"], r["pot"], r["piece"], "surfaces")
            f0 = os.path.join(base, r["piece"] + "_Surface_0.ply")
            f1 = os.path.join(base, r["piece"] + "_Surface_1.ply")
            p0 = load_ply(f0)[0] if os.path.exists(f0) else None
            p1 = load_ply(f1)[0] if os.path.exists(f1) else None
            if p0 is None and p1 is None:
                fh.write("\t".join([r["tag"], r["pot"], r["piece"], r.get("outcome", "NA")] +
                                    ["NA"] * 16) + "\n")
                continue
            key = (r["pot"], r["piece"])
            if key not in cache:
                cache[key] = read_pcd_xyz(cloud_path(r["pot"], r["piece"]))
            cloud, ntot, stride = cache[key]
            e0 = extents(p0) if p0 is not None else (float("nan"),) * 4
            e1 = extents(p1) if p1 is not None else (float("nan"),) * 4
            c0 = cover(cloud, [p0]) if p0 is not None else float("nan")
            c1 = cover(cloud, [p1]) if p1 is not None else float("nan")
            cu = cover(cloud, [x for x in (p0, p1) if x is not None])
            vals = [r["tag"], r["pot"], r["piece"], r.get("outcome", "NA"),
                    int(p0 is not None) + int(p1 is not None),
                    len(p0) if p0 is not None else "NA", len(p1) if p1 is not None else "NA",
                    "%.2f" % e0[0], "%.2f" % e0[1], "%.2f" % e0[2], "%.2f" % e0[3], "%.4f" % c0,
                    "%.2f" % e1[0], "%.2f" % e1[1], "%.2f" % e1[2], "%.2f" % e1[3], "%.4f" % c1,
                    "%.4f" % cu, ntot, stride]
            fh.write("\t".join(map(str, vals)) + "\n")
            print("[COVER] %s %s %s surf=%s/%s cov0=%.4f cov1=%.4f union=%.4f diag0=%.1fmm"
                  % (r["tag"], r["pot"], r["piece"], r["surf0"], r["surf1"], c0, c1, cu, e0[3]),
                  flush=True)
    print("[COVER] wrote %s (%d rows)" % (out, len(rows)))


if __name__ == "__main__":
    main()
