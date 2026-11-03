#!/usr/bin/env python3
"""t68 Part A: estimate nine Juglet axes from each piece's own walls, gate vs GT.

usage: fit68.py <in_dir> <out_dir> [seeds]
in_dir : Juglet_Piece_N.S0/.S1 (t66 arm-U PLY), Juglet_Piece_N_Axis.xyz (old),
         Juglet_Piece_N_T.txt (GT, row-major 3x4 or 4x4 R|t)
Estimators:
  potsac : sfs_axes.run_potsac (port of the authors' MATLAB AxisExtraction,
           proven equal to MATLAB on Pot A, pota-repro ticket 05)
  nperp  : control -- direction minimising sum (n . d)^2 over both walls' normals
Gate: each piece's median folded angle to the other eight, directions mapped by GT R.
"""
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..")))
from sfs_axes.io_axes import write_axes  # noqa: E402
from sfs_axes.potsac import run_potsac  # noqa: E402

N = 9


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
    return a.T  # (6, n)


def read_axis(path):
    a = np.loadtxt(path, ndmin=2)[0]
    d = a[3:6] / np.linalg.norm(a[3:6])
    return a[0:3], d


def read_T(path):
    v = np.array(open(path).read().split(), dtype=float)
    M = v[:12].reshape(3, 4)
    return M[:, :3], M[:, 3]


def fold(a, b):
    return float(np.degrees(np.arccos(np.clip(abs(a @ b), 0, 1))))


def gate(dirs_gt):
    out = []
    for i in range(N):
        out.append(float(np.median([fold(dirs_gt[i], dirs_gt[j])
                                    for j in range(N) if j != i])))
    return out


def nperp(C):
    n = C[3:6].T
    n = n / np.linalg.norm(n, axis=1, keepdims=True)
    w, v = np.linalg.eigh(n.T @ n)
    return v[:, 0], float(w[0] / w.sum())


def radial_resid(C, p, d):
    x = C[0:3].T - p
    r = np.linalg.norm(x - np.outer(x @ d, d), axis=1)
    return float(np.median(r)), float(np.median(np.abs(r - np.median(r))))


def main():
    ind, outd = sys.argv[1], sys.argv[2]
    seeds = [int(s) for s in (sys.argv[3] if len(sys.argv) > 3 else "0").split(",")]
    os.makedirs(outd, exist_ok=True)
    R = {}
    old = {}
    for k in range(1, N + 1):
        R[k] = read_T(os.path.join(ind, "Juglet_Piece_%d_T.txt" % k))[0]
        old[k] = read_axis(os.path.join(ind, "Juglet_Piece_%d_Axis.xyz" % k))
    est = {"old": {k: old[k][1] for k in old}, "nperp": {}}
    rows = []
    for s in seeds:
        est["potsac_s%d" % s] = {}
    for k in range(1, N + 1):
        C0 = read_ply(os.path.join(ind, "Juglet_Piece_%d.S0" % k))
        C1 = read_ply(os.path.join(ind, "Juglet_Piece_%d.S1" % k))
        C = np.hstack([C0, C1])
        d, ev = nperp(C)
        est["nperp"][k] = d
        info = {"k": k, "n0": C0.shape[1], "n1": C1.shape[1], "nperp_ev": ev,
                "old_vs_nperp": fold(old[k][1], d)}
        for s in seeds:
            t0 = time.time()
            m = min(C0.shape[1], C1.shape[1])
            vt = run_potsac(C0[:, :m], C1[:, :m], rng=np.random.default_rng(s), step=1)
            dp, pp = vt[0:3, 0] / np.linalg.norm(vt[0:3, 0]), vt[3:6, 0]
            est["potsac_s%d" % s][k] = dp
            sd = os.path.join(outd, "s%d" % s)
            os.makedirs(sd, exist_ok=True)
            write_axes(os.path.join(sd, "Juglet_Piece_%d_Axis.xyz" % k), vt[:, :1])
            rr, rmad = radial_resid(C, pp, dp)
            info["s%d" % s] = (fold(old[k][1], dp), fold(d, dp), rr, rmad, vt.shape[1],
                               time.time() - t0)
        rows.append(info)
        print(info, flush=True)
    print("\nGT gate: per-piece median folded angle (deg) to the other eight")
    names = list(est)
    print("piece  " + "  ".join("%10s" % n for n in names))
    G = {n: gate([R[k] @ est[n][k] for k in range(1, N + 1)]) for n in names}
    for i in range(N):
        print("P%d     " % (i + 1) + "  ".join("%10.1f" % G[n][i] for n in names))
    for n in names:
        g = np.array(G[n])
        print("%-10s max %.1f  n<=10: %d  n>25: %d" % (n, g.max(), (g <= 10).sum(), (g > 25).sum()))


if __name__ == "__main__":
    main()
