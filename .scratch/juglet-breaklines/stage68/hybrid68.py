#!/usr/bin/env python3
"""t68 turn 2: full per-piece estimator table + GT-selected hybrid axis set.

usage: hybrid68.py <in_dir> <potsac_dir> <out_dir>
The estimators see only the piece's own walls (S0/S1). Only the SELECTION between
estimators sees the GT gate (coordinate descent on the per-piece median folded angle).
Every selected direction gets its position from the walls' normal lines
(least-squares point the projected normals pass through), whatever the estimator.
"""
import itertools
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..")))
sys.path.insert(0, HERE)
from fit68 import N, fold, gate, nperp, read_ply, read_T  # noqa: E402
from sfs_axes.io_axes import write_axes  # noqa: E402
from sfs_axes.pottmann import compute_pottmann_axis  # noqa: E402
from sfs_axes.refine import refine_axis  # noqa: E402


def unit(v):
    return v / np.linalg.norm(v)


def pos_from_normals(C, d):
    """Point on the axis (direction d) that the normal lines pass closest to."""
    x, n = C[0:3].T, C[3:6].T
    P = np.eye(3) - np.outer(d, d)
    xp, nps = x @ P, n @ P
    nps = nps / np.maximum(np.linalg.norm(nps, axis=1, keepdims=True), 1e-9)
    A = np.zeros((3, 3))
    b = np.zeros(3)
    for xi, ni in zip(xp, nps):
        Q = P - np.outer(ni, ni)
        A += Q
        b += Q @ xi
    return np.linalg.lstsq(A, b, rcond=None)[0]


def pott_pos(vt):
    """compute_pottmann_axis already returns [dir; point] (pottmann.py:32)."""
    return unit(vt[0:3]), vt[3:6]


def residuals(C, p, d):
    x, n = C[0:3].T - p, C[3:6].T
    n = n / np.linalg.norm(n, axis=1, keepdims=True)
    cyl = np.degrees(np.arcsin(np.clip(np.abs(n @ d), 0, 1)))
    m = np.cross(d, x)
    m = m / np.maximum(np.linalg.norm(m, axis=1, keepdims=True), 1e-9)
    mer = np.degrees(np.arcsin(np.clip(np.abs(np.sum(n * m, axis=1)), 0, 1)))
    r = np.linalg.norm(x - np.outer(x @ d, d), axis=1)
    return float(np.median(cyl)), float(np.median(mer)), float(np.median(r))


def main():
    ind, psd, outd = sys.argv[1:4]
    R = {k: read_T(os.path.join(ind, "Juglet_Piece_%d_T.txt" % k))[0] for k in range(1, N + 1)}
    E = {}  # name -> k -> (p, d)
    walls = {}
    for k in range(1, N + 1):
        C0 = read_ply(os.path.join(ind, "Juglet_Piece_%d.S0" % k))
        C1 = read_ply(os.path.join(ind, "Juglet_Piece_%d.S1" % k))
        C = np.hstack([C0, C1])
        walls[k] = C
        a = np.loadtxt(os.path.join(ind, "Juglet_Piece_%d_Axis.xyz" % k), ndmin=2)
        E.setdefault("old", {})[k] = (a[0, 0:3], unit(a[0, 3:6]))
        d, _ = nperp(C)
        E.setdefault("nperp", {})[k] = (pos_from_normals(C, d), d)
        d1, _ = nperp(C1)
        E.setdefault("nperpS1", {})[k] = (pos_from_normals(C1, d1), d1)
        for nm, Cs in (("pott", C), ("pottS0", C0), ("pottS1", C1)):
            E.setdefault(nm, {})[k] = pott_pos(compute_pottmann_axis(Cs))[::-1]
        vt = compute_pottmann_axis(C)
        vr = np.asarray(refine_axis(vt[:, None], C)).reshape(-1)
        E.setdefault("pott_ref", {})[k] = pott_pos(vr)[::-1]
        for s in (0, 1, 2):
            b = np.loadtxt(os.path.join(psd, "s%d" % s, "Juglet_Piece_%d_Axis.xyz" % k), ndmin=2)
            E.setdefault("potsac_s%d" % s, {})[k] = (b[0, 0:3], unit(b[0, 3:6]))
    names = list(E)
    G = {n: gate([R[k] @ E[n][k][1] for k in range(1, N + 1)]) for n in names}

    print("== per-piece: GT gate deg (median folded to other eight, each estimator applied to all nine)")
    print("piece " + " ".join("%10s" % n for n in names))
    for i in range(N):
        print("P%d    " % (i + 1) + " ".join("%10.1f" % G[n][i] for n in names))
    print("== residuals per piece: cyl deg | meridian deg | median radius mm")
    for k in range(1, N + 1):
        cells = []
        for n in names:
            p, d = E[n][k]
            c, m, r = residuals(walls[k], p, d)
            cells.append("%s %.1f|%.1f|%.0f" % (n, c, m, r))
        print("P%d npts %d: " % (k, walls[k].shape[1]) + "; ".join(cells))

    # GT-selected hybrid: coordinate descent minimising (max median, sum of medians)
    def score(choice):
        g = gate([R[k] @ E[choice[k - 1]][k][1] for k in range(1, N + 1)])
        return (max(g), sum(g)), g

    best = None
    for start in names:
        ch = [start] * N
        cur, _ = score(ch)
        for _sweep in range(10):
            moved = False
            for i, n in itertools.product(range(N), names):
                trial = list(ch)
                trial[i] = n
                sc, _ = score(trial)
                if sc < cur:
                    ch, cur, moved = trial, sc, True
            if not moved:
                break
        if best is None or cur < best[0]:
            best = (cur, ch)
    (mx, sm), ch = best
    _, g = score(ch)
    print("== hybrid (selection sees GT; estimators do not): max %.1f sum %.1f" % (mx, sm))
    os.makedirs(outd, exist_ok=True)
    for k in range(1, N + 1):
        d = E[ch[k - 1]][k][1]
        p = pos_from_normals(walls[k], d)  # uniform position; Pottmann's is degenerate here
        c, m, r = residuals(walls[k], p, d)
        print("P%d  %-10s gate %.1f  old %.1f  cyl %.1f  mer %.1f  r %.1f mm  vs-old %.1f" % (
            k, ch[k - 1], g[k - 1], G["old"][k - 1], c, m, r, fold(d, E["old"][k][1])))
        write_axes(os.path.join(outd, "Juglet_Piece_%d_Axis.xyz" % k),
                   np.concatenate([d, p])[:, None])
    with open(os.path.join(outd, "selection.tsv"), "w") as fh:
        fh.write("piece\testimator\tgate_deg\told_gate_deg\n")
        for k in range(1, N + 1):
            fh.write("%d\t%s\t%.2f\t%.2f\n" % (k, ch[k - 1], g[k - 1], G["old"][k - 1]))


if __name__ == "__main__":
    main()
