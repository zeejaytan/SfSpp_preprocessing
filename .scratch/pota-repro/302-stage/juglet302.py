#!/usr/bin/env python3
"""Ticket 302 gate 4a: Juglet axes from the corrected port (per-point cost).

Same protocol as t68 fit68.py: walls = t66 arm-U S0/S1 PLYs, truncated to the
shorter wall, step=1, line 1 kept, seeds 0..2. The gate metric is fit68's:
per-piece median folded angle to the other eight, directions mapped by GT R.
Reference numbers (t68 axes68 hybrid): median 12.31, p8 16.43, p9 23.83,
p3 10.78; old Dataset axes median ~26.8.
"""
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "sfs_axes")))

from sfs_axes.io_axes import write_axes  # noqa: E402
from sfs_axes.potsac import run_potsac  # noqa: E402

N = 9
SEEDS = (0, 1, 2)


def read_ply(path):
    with open(path) as fh:
        lines = fh.read().splitlines()
    nv = None
    for i, ln in enumerate(lines):
        if ln.startswith("element vertex"):
            nv = int(ln.split()[2])
        if ln.strip() == "end_header":
            body = lines[i + 1:i + 1 + nv]
            break
    a = np.array([[float(x) for x in r.split()[:6]] for r in body])
    return a.T


def read_T(path):
    v = np.array(open(path).read().split(), dtype=float)
    M = v[:12].reshape(3, 4)
    return M[:, :3], M[:, 3]


def fold(a, b):
    return float(np.degrees(np.arccos(np.clip(abs(a @ b), 0, 1))))


def gate(dirs_gt):
    return [float(np.median([fold(dirs_gt[i], dirs_gt[j])
                             for j in range(N) if j != i])) for i in range(N)]


def main(lanes, ds, outd):
    os.makedirs(outd, exist_ok=True)
    R, old = {}, {}
    for k in range(1, N + 1):
        R[k] = read_T(os.path.join(ds, "Juglet_GT", "Juglet_Piece_%d_T.txt" % k))[0]
        a = np.loadtxt(os.path.join(ds, "Axes", "Juglet",
                                    "Juglet_Piece_%d_Axis.xyz" % k), ndmin=2)[0]
        old[k] = a[3:6] / np.linalg.norm(a[3:6])
    est = {"old": dict(old)}
    for s in SEEDS:
        est["potsac302_s%d" % s] = {}
    for k in range(1, N + 1):
        C0 = read_ply(os.path.join(lanes, "Juglet_Piece_%d.S0" % k))
        C1 = read_ply(os.path.join(lanes, "Juglet_Piece_%d.S1" % k))
        m = min(C0.shape[1], C1.shape[1])
        for s in SEEDS:
            t0 = time.time()
            vt = run_potsac(C0[:, :m], C1[:, :m], rng=np.random.default_rng(s), step=1)
            d = vt[0:3, 0] / np.linalg.norm(vt[0:3, 0])
            est["potsac302_s%d" % s][k] = d
            if s == 0:
                write_axes(os.path.join(outd, "Juglet_Piece_%d_Axis.xyz" % k), vt[:, :1])
            print("P%d s%d K=%d vs_old=%.2f (%.1fs)"
                  % (k, s, vt.shape[1], fold(old[k], d), time.time() - t0), flush=True)
    print("\nGT gate: per-piece median folded angle (deg) to the other eight")
    names = list(est)
    G = {n: gate([R[k] @ est[n][k] for k in range(1, N + 1)]) for n in names}
    print("piece  " + "  ".join("%12s" % n for n in names))
    for i in range(N):
        print("P%d     " % (i + 1) + "  ".join("%12.2f" % G[n][i] for n in names))
    with open(os.path.join(outd, "gate302.tsv"), "w") as fh:
        fh.write("piece\t" + "\t".join(names) + "\n")
        for i in range(N):
            fh.write("P%d" % (i + 1) + "\t" + "\t".join("%.3f" % G[n][i] for n in names) + "\n")
    for n in names:
        g = np.array(G[n])
        print("%-12s median=%6.2f  worst=%6.2f" % (n, float(np.median(g)), float(g.max())))
    print("reference t68 hybrid: median 12.31  p3 10.78  p8 16.43  p9 23.83")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3]))
