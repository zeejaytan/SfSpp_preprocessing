#!/usr/bin/env python3
"""Today's axis code over the two walls of one piece: sfs_axes (PotSAC).

Reads Surface_0/Surface_1 xyz (N x 6, mm + normals), applies the MATLAB-parity
equal-count truncation (io_surfaces.read_surfaces:truncate=True), runs
run_potsac, and writes the assembly-layout axis file (K x 6, position-first,
row 1 = lowest cost, io_axes.write_axes). SFS_SRC must point at the built
source tree so that "sfs_axes" is importable.

usage: potsac_axis.py --s0 A.xyz --s1 B.xyz --out Axis.xyz [--seed 0] [--step 10]
"""
import argparse
import sys

import numpy as np

sys.path.insert(0, __import__("os").environ["SFS_SRC"])
from sfs_axes.io_axes import write_axes          # noqa: E402
from sfs_axes.potsac import run_potsac          # noqa: E402


def load(path):
    arr = np.loadtxt(path, dtype=float)
    if arr.ndim == 1:
        arr = arr[None, :]
    return arr.T


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s0", required=True)
    ap.add_argument("--s1", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--step", type=int, default=10)
    a = ap.parse_args()
    C0, C1 = load(a.s0), load(a.s1)
    if C0.shape[0] != 6 or C1.shape[0] != 6:
        raise SystemExit("surfaces must be N x 6")
    m = min(C0.shape[1], C1.shape[1])          # read_surfaces.m:34-37 parity
    C0, C1 = C0[:, 0:m], C1[:, 0:m]
    print("[POTSAC] walls %d + %d points (truncated to %d each)" % (C0.shape[1], C1.shape[1], m))
    rng = np.random.default_rng(a.seed)
    vt = run_potsac(C0, C1, rng=rng, step=a.step, verbose=True)
    if vt.shape[1] < 1:
        raise SystemExit("no axis survived dedup")
    write_axes(a.out, vt)
    d, p = vt[0:3, 0], vt[3:6, 0]
    print("[POTSAC] K=%d seed=%d step=%d -> %s" % (vt.shape[1], a.seed, a.step, a.out))
    print("[POTSAC] best pos=[%.4f %.4f %.4f] dir=[%.6f %.6f %.6f]" % (p[0], p[1], p[2], d[0], d[1], d[2]))


if __name__ == "__main__":
    main()
