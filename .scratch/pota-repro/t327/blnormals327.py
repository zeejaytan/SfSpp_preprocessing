#!/usr/bin/env python
"""ticket 327 bar 4 support -- breakline normal convention on the t66 bundle.

For each piece, Bl0 and Bl1 (the two walks' lines): fraction of normals pointing outward from the
GT axis (dot(n, rhat) > 0) and the mean signed dot. If the two walks wrote opposite conventions,
the pair gate dt>0.7 can only pass for one slot per piece.
"""
import os
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(BASE, "..", "..", ".."))
GEOM = os.path.join(WT, "artifacts", "pota327", "geom")
GT = os.path.join(WT, "artifacts", "pota327", "gt")

def load_pcd(p):
    L = open(p).read().splitlines()
    i = [n for n, l in enumerate(L) if l.startswith("DATA")][0]
    rows = [l.split() for l in L[i + 1:] if l.strip() and len(l.split()) >= 6]
    return np.array([[float(x) for x in r[:6]] for r in rows])

def load_ax(p):
    v = [float(x) for x in open(p).read().split()]
    return np.array(v[-6:-3]), np.array(v[-3:])

print("piece  Bl0 n  frac_out  mean_dot | Bl1 n  frac_out  mean_dot | Bl1-vs-Bl0 sign")
for k in range(1, 10):
    b0 = load_pcd(os.path.join(GEOM, f"Juglet_Piece_{k}.Bl0"))
    b1 = load_pcd(os.path.join(GEOM, f"Juglet_Piece_{k}.Bl1"))
    o, d = load_ax(os.path.join(GT, f"Juglet_Piece_{k}_Axis.xyz"))
    d = d / np.linalg.norm(d)
    def stat(B):
        P, N = B[:, :3], B[:, 3:6]
        w = P - o; perp = w - np.outer(w @ d, d)
        rh = perp / np.maximum(np.linalg.norm(perp, axis=1), 1e-9)[:, None]
        s = np.sum(N * rh, axis=1)
        return len(P), float(np.mean(s > 0)), float(np.mean(s))
    n0, f0, m0 = stat(b0)
    n1, f1, m1 = stat(b1)
    # nearest-neighbour normal agreement between the two loops (do they face the same way?)
    P1, N1 = b1[:, :3], b1[:, 3:6]
    ds = []
    for i in range(0, len(b0), max(1, len(b0) // 200)):
        j = int(np.argmin(np.linalg.norm(P1 - b0[i, :3], axis=1)))
        ds.append(float(np.dot(b0[i, 3:6], N1[j])))
    print(f"{k:5d} {n0:6d} {f0:9.3f} {m0:+8.3f} | {n1:6d} {f1:9.3f} {m1:+8.3f} | {np.median(ds):+.3f}")
