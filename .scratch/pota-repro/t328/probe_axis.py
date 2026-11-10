#!/usr/bin/env python
"""ticket 328 -- bar-1 prototype: fit the piece's own axis from its normals (every normal line
of a surface of revolution meets the axis), then decide interior/exterior by radius.

Flip-invariant (a line through p with +-n is the same line), axis-file-free (nothing but the
piece's own points and normals).  Validated against the GT axis for evidence only.
"""
import json, os
import numpy as np
from scipy.spatial import cKDTree
from scipy.optimize import least_squares

BASE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(BASE, "..", "..", ".."))
IN = os.path.join(WT, "artifacts", "pota328", "in")
OUT = os.path.join(WT, "artifacts", "pota328", "probe")
GEOM, GT = os.path.join(IN, "geom"), os.path.join(IN, "gt")

def load_ply6(p):
    L = open(p).read().splitlines()
    i = [n for n, l in enumerate(L) if l.strip() == "end_header"][0]
    d = [l.split() for l in L[i + 1:] if l.strip() and not l.startswith("camera")]
    return np.array([[float(x) for x in r[:6]] for r in d])

def load_pcd(p):
    L = open(p).read().splitlines()
    i = [n for n, l in enumerate(L) if l.startswith("DATA")][0]
    d = [l.split() for l in L[i + 1:] if l.strip() and len(l.split()) >= 6]
    return np.array([[float(x) for x in r[:6]] for r in d])

def load_ax(p):
    v = [float(x) for x in open(p).read().split()]
    return np.array(v[-6:-3]), np.array(v[-3:])

def unit(a):
    return a / np.maximum(np.linalg.norm(a, axis=1, keepdims=True), 1e-12)

def perp(P, o, d):
    w = P - o
    return np.linalg.norm(w - np.outer(w @ d, d), axis=1)

def line_axis_res(P, N, c, d):
    """per point: distance from the normal line (P,N) to the axis line (c,d)."""
    A = P - c
    A = A - np.outer(A @ d, d)                  # transverse part of p-c
    nt = N - np.outer(N @ d, d)                 # transverse part of n
    nn = np.sum(nt * nt, axis=1)
    ok = nn > 1e-8
    r = np.linalg.norm(A, axis=1)
    s = np.zeros(len(P))
    s[ok] = -np.sum(A[ok] * nt[ok], axis=1) / nn[ok]
    res = np.linalg.norm(A + np.outer(s, np.ones(3)) * nt, axis=1)
    return res

def fit_axis_lines(P, N, nstart=12, seed=7):
    rng = np.random.default_rng(seed)
    if len(P) > 1200:
        idx = rng.choice(len(P), 1200, replace=False)
        P = P[idx]; N = N[idx]
    P = P.copy(); N = unit(N)
    m = P.mean(axis=0)
    P = P - m
    best = None
    dirs = []
    for k in range(nstart):
        v = rng.normal(size=3); dirs.append(v / np.linalg.norm(v))
    # a few structured starts too
    for v in ([0, 0, 1], [1, 0, 0], [0, 1, 0]):
        dirs.append(np.array(v, float))
    # coarse grid over the sphere as well
    for th in np.linspace(0, np.pi, 5):
        for ph in np.linspace(0, 2 * np.pi, 8, endpoint=False):
            dirs.append(np.array([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)]))
    for d0 in dirs:
        d0 = d0 / np.linalg.norm(d0)
        a = np.array([1.0, 0, 0]) if abs(d0[0]) < 0.9 else np.array([0, 1.0, 0])
        u = np.cross(d0, a); u /= np.linalg.norm(u)
        v = np.cross(d0, u)
        # algebraic start for c: solve for transverse offset that minimises the median residual
        # cheap: start at the transverse centroid of P
        c0 = np.zeros(3)
        def unpack(p):
            dd = d0 + p[0] * u + p[1] * v
            dd = dd / np.linalg.norm(dd)
            cc = c0 + p[2] * u + p[3] * v + p[4] * d0
            return cc, dd
        def fun(p):
            cc, dd = unpack(p)
            return line_axis_res(P, N, cc, dd)
        r = least_squares(fun, np.zeros(5), method="trf", loss="soft_l1", f_scale=0.5,
                          max_nfev=120, xtol=1e-10, ftol=1e-10)
        cost = np.median(np.abs(r.fun))
        if best is None or cost < best[0]:
            best = (cost, r.x, d0, u, v, c0)
    cost, x, d0, u, v, c0 = best
    dd = d0 + x[0] * u + x[1] * v; dd /= np.linalg.norm(dd)
    cc = c0 + x[2] * u + x[3] * v + x[4] * d0 + m
    return cc, dd, float(cost)

S = {k: {f: load_ply6(os.path.join(GEOM, "Juglet_Piece_%d.S%d" % (k, f))) for f in (0, 1)} for k in range(1, 10)}
GTax = {k: load_ax(os.path.join(GT, "Juglet_Piece_%d_Axis.xyz" % k)) for k in range(1, 10)}

rows = []
for k in range(1, 10):
    P = np.vstack([S[k][0][:, :3], S[k][1][:, :3]])
    N = np.vstack([S[k][0][:, 3:6], S[k][1][:, 3:6]])
    c, d, cost = fit_axis_lines(P, N)
    g0, gd = GTax[k]; gd = gd / np.linalg.norm(gd)
    ang = float(np.degrees(np.arccos(min(1.0, abs(float(d @ gd))))))
    # distance between the two lines
    w = g0 - c
    dist = float(np.linalg.norm(w - (w @ gd) * gd - ((w @ d)) * d + ((w @ gd) * gd) * 0)) if False else None
    # line-line distance between (c,d) and (g0,gd)
    nn = np.cross(d, gd)
    if np.linalg.norm(nn) > 1e-6:
        dist = abs(float((g0 - c) @ nn) / np.linalg.norm(nn))
    else:
        dist = float(np.linalg.norm((g0 - c) - ((g0 - c) @ gd) * gd))
    r = {f: float(np.median(perp(S[k][f][:, :3], c, d))) for f in (0, 1)}
    rg = {f: float(np.median(perp(S[k][f][:, :3], g0, gd))) for f in (0, 1)}
    thick = float(np.median(cKDTree(S[k][1][:, :3]).query(S[k][0][:, :3], k=1)[0]))
    dr = r[1] - r[0]
    pick = 0 if dr > 0 else 1
    true_int = 0 if rg[0] < rg[1] else 1
    rows.append(dict(piece=k, ang=round(ang, 2), dist=round(dist, 3), cost=round(cost, 3),
                     r0=round(r[0], 3), r1=round(r[1], 3), dr=round(dr, 3), thick=round(thick, 3),
                     pick=pick, true_int=true_int, ok=pick == true_int,
                     decisive=bool(abs(dr) > 0.5 * thick)))
    print("piece %d | fit vs GT axis: angle %5.2f deg, line distance %5.3f mm, median resid %5.3f | r %7.3f %7.3f dr %+6.3f | t %5.3f | pick %d true %d %-3s decisive %s" % (
        k, ang, dist, cost, r[0], r[1], dr, thick, pick, true_int, "OK" if pick == true_int else "FAIL", rows[-1]["decisive"]))

json.dump(rows, open(os.path.join(OUT, "axis_geom.json"), "w"), indent=1)
