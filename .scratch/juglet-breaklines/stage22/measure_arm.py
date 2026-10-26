#!/usr/bin/env python3
"""ticket 22: pair statistics for every cell of the arm grid that wrote two surfaces.

usage: measure_arm.py <cellroot>   ->  <cellroot>/measure.tsv

Surface_0 is the interior face (classifyAndOrderPaper234 puts it there), Surface_1 the
exterior one; the question the ticket asks is whether the pair is two walls of one sherd
or one wall split in two, so every column is a pair statistic.

  n0, n1       points in Surface_0 / Surface_1
  share        share of Surface_1 points that coincide with a Surface_0 point when both
               are rounded to 0.001 mm -- a merged pair shares points, a wall pair does not
  mean_dot     dot product of the two mean normals, normalised. Two walls face opposite
               ways (near -1); one wall split in two keeps one direction (near +1)
  med_nn_mm    median distance from a Surface_1 point to its nearest Surface_0 point
  med_abs_dot  median |dot| between a Surface_1 normal and the normal of its nearest
               Surface_0 point
  frac_neg     share of Surface_1 points whose nearest Surface_0 normal points the other way
  med_off_mm   median |offset| of a Surface_1 point along its nearest Surface_0 normal
  bar          yes when mean_dot <= -0.9 and med_nn_mm >= 1.5 and share <= 0.05 (the
               ticket's wall-pair bar), no when it misses, NA when a surface is missing

The bar is a threshold on the numbers, not a verdict: nothing here decides an arm.
"""
import os
import sys

import numpy as np
from scipy.spatial import cKDTree


def load_ply(path):
    """vertex xyz + normals from a PCL ASCII PLY; other vertex properties are ignored."""
    with open(path, "rb") as fh:
        raw = fh.read()
    end = raw.index(b"end_header")
    header = raw[:end].decode("ascii", "replace").splitlines()
    n = 0
    fmt = "ascii"
    for line in header:
        parts = line.split()
        if len(parts) >= 3 and parts[0] == "element" and parts[1] == "vertex":
            n = int(parts[2])
        if parts[:2] == ["format", "binary_little_endian"]:
            fmt = "binary"
    if fmt != "ascii":
        raise SystemExit("%s: only ascii PLY is expected here, got %s" % (path, fmt))
    body = raw[end + len(b"end_header"):].splitlines()[1:n + 1]
    xyz = np.empty((len(body), 3))
    nrm = np.empty((len(body), 3))
    for i, line in enumerate(body):
        f = line.split()
        xyz[i] = [float(f[0]), float(f[1]), float(f[2])]
        nrm[i] = [float(f[3]), float(f[4]), float(f[5])]
    return xyz, nrm


def unit(v):
    ln = np.linalg.norm(v, axis=1, keepdims=True)
    ln[ln == 0] = 1.0
    return v / ln


def pair_stats(p0, n0, p1, n1):
    n0u = unit(n0)
    n1u = unit(n1)
    keys0 = set(map(tuple, np.round(p0, 3)))
    keys1 = np.round(p1, 3)
    shared = sum(1 for k in map(tuple, keys1) if k in keys0)
    m0 = n0u.mean(axis=0)
    m1 = n1u.mean(axis=0)
    den = np.linalg.norm(m0) * np.linalg.norm(m1)
    mean_dot = float(m0.dot(m1) / den) if den > 0 else float("nan")
    dist, idx = cKDTree(p0).query(p1, k=1, workers=-1)
    dot = np.einsum("ij,ij->i", n1u, n0u[idx])
    off = np.einsum("ij,ij->i", p1 - p0[idx], n0u[idx])
    return dict(
        n0=len(p0), n1=len(p1),
        share=shared / len(p1) if len(p1) else float("nan"),
        mean_dot=mean_dot,
        med_nn_mm=float(np.median(dist)),
        med_abs_dot=float(np.median(np.abs(dot))),
        frac_neg=float((dot < 0).mean()),
        med_off_mm=float(np.median(np.abs(off))),
    )


def main():
    root = sys.argv[1]
    cells = os.path.join(root, "cells.tsv")
    rows = []
    with open(cells) as fh:
        header = fh.readline().rstrip("\n").split("\t")
        for line in fh:
            f = line.rstrip("\n").split("\t")
            if len(f) < len(header):
                f += ["NA"] * (len(header) - len(f))
            rows.append(dict(zip(header, f)))
    cols = ["tag", "pot", "piece", "mesh_exit", "n0", "n1", "share", "mean_dot",
            "med_nn_mm", "med_abs_dot", "frac_neg", "med_off_mm", "bar"]
    out = os.path.join(root, "measure.tsv")
    with open(out, "w") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            base = os.path.join(root, "cells", r["tag"], r["pot"], r["piece"], "surfaces")
            f0 = os.path.join(base, r["piece"] + "_Surface_0.ply")
            f1 = os.path.join(base, r["piece"] + "_Surface_1.ply")
            if r.get("surf0") != "yes" or r.get("surf1") != "yes" or not (
                    os.path.exists(f0) and os.path.exists(f1)):
                vals = [r["tag"], r["pot"], r["piece"], r["mesh_exit"]] + ["NA"] * 8 + ["NA"]
                fh.write("\t".join(map(str, vals)) + "\n")
                continue
            p0, n0 = load_ply(f0)
            p1, n1 = load_ply(f1)
            if len(p0) == 0 or len(p1) == 0:
                vals = [r["tag"], r["pot"], r["piece"], r["mesh_exit"]] + ["NA"] * 8 + ["NA"]
                fh.write("\t".join(map(str, vals)) + "\n")
                continue
            s = pair_stats(p0, n0, p1, n1)
            bar = "yes" if (s["mean_dot"] <= -0.9 and s["med_nn_mm"] >= 1.5
                            and s["share"] <= 0.05) else "no"
            vals = [r["tag"], r["pot"], r["piece"], r["mesh_exit"],
                    s["n0"], s["n1"], "%.4f" % s["share"], "%.4f" % s["mean_dot"],
                    "%.4f" % s["med_nn_mm"], "%.4f" % s["med_abs_dot"],
                    "%.4f" % s["frac_neg"], "%.4f" % s["med_off_mm"], bar]
            fh.write("\t".join(map(str, vals)) + "\n")
            print("[MEASURE] %s %s %s dot=%.4f nn=%.3f share=%.4f bar=%s"
                  % (r["tag"], r["pot"], r["piece"], s["mean_dot"], s["med_nn_mm"],
                     s["share"], bar), flush=True)
    print("[MEASURE] wrote %s (%d rows)" % (out, len(rows)))


if __name__ == "__main__":
    main()
