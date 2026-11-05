#!/usr/bin/env python3
"""bspline309.py -- Ticket 309 variant V3: B-spline resampled surfaces.

The paper (sfspp-2502.13986v1.md:155) says: "B-Spline fitting is performed for each
cluster to refine surface boundaries and uniformly sample the point cloud." The repo
ships no MATLAB/Python code that does this on Surfaces/*.xyz (extract_axis_nurbs.m only
re-reads the same files), so V3 is our own implementation of that sentence, and is
labelled OURS everywhere:
  1. local frame per wall: PCA plane, (u,v) = the two largest axes;
  2. tensor-product cubic B-spline surface z = f(u,v) fitted to the scattered points
     (scipy SmoothBivariateSpline, smoothing s = n * tol^2, tol = 0.05 mm);
  3. uniform resample on a square (u,v) grid at the input's own mean spacing, keeping
     points inside the convex hull of (u,v), so the areal density is preserved;
  4. normals from the spline partials: n_local = (-f_u, -f_v, 1)/|.|, rotated back.
Writes Pot_X_Piece_NN_Surface_{0,1}.xyz (x y z nx ny nz) into --out, plus one row per
wall in v3.tsv: input n, output n, md5, median nearest-neighbour distance V3->V1 (mm),
and the input's own spacing.

usage: bspline309.py --corpus DIR --out DIR [--pieces A_07,...] [--tol 0.05]
"""
import argparse
import hashlib
import os

import numpy as np
from scipy.interpolate import SmoothBivariateSpline
from scipy.spatial import ConvexHull, cKDTree

PIECES = ["A_07", "D_17", "D_24", "D_30", "E_21", "E_31", "E_34",
          "F_07", "H_06", "H_09", "J_11", "J_13", "J_14"]


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def mean_spacing(P):
    """Median nearest-neighbour distance of a point set (mm), subsampled for speed."""
    idx = np.arange(P.shape[0])
    if P.shape[0] > 3000:
        idx = np.random.default_rng(0).choice(P.shape[0], 3000, replace=False)
    t = cKDTree(P)
    d, _ = t.query(P[idx], k=2)
    return float(np.median(d[:, 1]))


def resample_wall(P, tol=0.05):
    c = P.mean(axis=0)
    Q = P - c
    # PCA frame: u,v = two largest-variance axes
    _u, _s, Vt = np.linalg.svd(Q, full_matrices=False)
    e1, e2, e3 = Vt[0], Vt[1], Vt[2]
    u, v, w = Q @ e1, Q @ e2, Q @ e3
    spl = SmoothBivariateSpline(u, v, w, kx=3, ky=3, s=P.shape[0] * tol * tol)
    hull = ConvexHull(np.column_stack([u, v]))
    # grid at the input's own mean spacing
    d0 = mean_spacing(P)
    uu = np.arange(u.min(), u.max() + 0.5 * d0, d0)
    vv = np.arange(v.min(), v.max() + 0.5 * d0, d0)
    UU, VV = np.meshgrid(uu, vv)
    pts = np.column_stack([UU.ravel(), VV.ravel()])
    # keep grid points inside the convex hull (Delaunay-free edge test)
    A = hull.equations[:, :2]
    b = hull.equations[:, 2]
    inside = np.all(pts @ A.T + b <= 1e-9, axis=1)
    pts = pts[inside]
    if pts.shape[0] < 10:
        raise RuntimeError("resample produced %d points" % pts.shape[0])
    uu_, vv_ = pts[:, 0], pts[:, 1]
    ww_ = spl.ev(uu_, vv_)
    fu = spl.ev(uu_, vv_, dx=1, dy=0)
    fv = spl.ev(uu_, vv_, dx=0, dy=1)
    nl = np.column_stack([-fu, -fv, np.ones_like(fu)])
    nl /= np.linalg.norm(nl, axis=1, keepdims=True)
    # back to world: (u,v,w) basis is e1,e2,e3
    X = c + np.outer(uu_, e1) + np.outer(vv_, e2) + np.outer(ww_, e3)
    N = (np.outer(nl[:, 0], e1) + np.outer(nl[:, 1], e2) + np.outer(nl[:, 2], e3))
    N /= np.linalg.norm(N, axis=1, keepdims=True)
    return X, N, d0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--pieces", default=",".join(PIECES))
    ap.add_argument("--tol", type=float, default=0.05)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rows = [("piece", "wall", "n_in", "n_out", "spacing_mm", "md5_out",
             "nn_med_mm", "nn_p99_mm")]
    for pc in [p.strip() for p in a.pieces.split(",") if p.strip()]:
        pot, num = pc.split("_")
        for wall in (0, 1):
            src = os.path.join(a.corpus, "Surfaces",
                               "Pot_%s_Piece_%02d_Surface_%d.xyz" % (pot, int(num), wall))
            dst = os.path.join(a.out,
                               "Pot_%s_Piece_%02d_Surface_%d.xyz" % (pot, int(num), wall))
            P6 = np.loadtxt(src)
            P = P6[:, 0:3]
            try:
                X, N, d0 = resample_wall(P, a.tol)
            except Exception as exc:
                print("[V3] %s wall %d FAILED: %r" % (pc, wall, exc), flush=True)
                rows.append((pc, wall, P.shape[0], 0, d0 if 'd0' in dir() else "", "", "", ""))
                continue
            out = np.column_stack([X, N])
            np.savetxt(dst, out, fmt="%.6f")
            t = cKDTree(P)
            d, _ = t.query(X, k=1)
            rows.append((pc, wall, P.shape[0], X.shape[0], "%.4f" % d0, md5(dst),
                         "%.4f" % float(np.median(d)),
                         "%.4f" % float(np.percentile(d, 99))))
            print("[V3] %s wall %d n %d -> %d spacing %.3f mm  V3->V1 median %.3f mm"
                  % (pc, wall, P.shape[0], X.shape[0], d0, float(np.median(d))), flush=True)
    with open(os.path.join(a.out, "v3.tsv"), "w") as fh:
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    print("[V3] wrote %s" % a.out)


if __name__ == "__main__":
    main()
