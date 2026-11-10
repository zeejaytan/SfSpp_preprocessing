#!/usr/bin/env python
"""ticket 327 bar 4 support -- the five pairs, reconstructed locally, ctrl vs swap.

Placement verified against the harness's own gap_min (inv(T_y) T_x). Correspondence is
one-to-one by nearest neighbour with a 3 mm cut, which reproduces the harness's n_d3 and
dot_med_d3 on the ctrl run. Then the same computation runs on the swapped slot-0 assignment
(pieces 2,6,9 take Bl1) and reports which wall the matched points sit on.
"""
import json, os
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(BASE, "..", "..", ".."))
GEOM = os.path.join(WT, "artifacts", "pota327", "geom")
GT = os.path.join(WT, "artifacts", "pota327", "gt")
OUT = os.path.join(WT, "artifacts", "pota327", "swap")

def load_pcd(p):
    L = open(p).read().splitlines()
    i = [n for n, l in enumerate(L) if l.startswith("DATA")][0]
    rows = [l.split() for l in L[i + 1:] if l.strip() and len(l.split()) >= 6]
    return np.array([[float(x) for x in r[:6]] for r in rows])

def load_ax(k):
    v = [float(x) for x in open(os.path.join(GT, f"Juglet_Piece_{k}_Axis.xyz")).read().split()]
    return np.array(v[-6:-3]), np.array(v[-3:])

T = {k: np.loadtxt(os.path.join(GT, f"Juglet_Piece_{k}_T.txt")) for k in range(1, 10)}
L0 = {k: load_pcd(os.path.join(GEOM, f"Juglet_Piece_{k}.Bl0")) for k in range(1, 10)}
L1 = {k: load_pcd(os.path.join(GEOM, f"Juglet_Piece_{k}.Bl1")) for k in range(1, 10)}
SWAPPED = {2, 6, 9}

def slot0(k, swap):
    return L1[k] if (swap and k in SWAPPED) else L0[k]

def radial(k, P):
    o, d = load_ax(k)
    d = d / np.linalg.norm(d)
    w = P - o
    return np.linalg.norm(w - np.outer(w @ d, d), axis=1)

def pair(y, x, swap):
    A = slot0(y, swap)
    Bx = slot0(x, swap)
    M = np.linalg.inv(T[y]) @ T[x]
    B = np.hstack([(M @ np.hstack([Bx[:, :3], np.ones((len(Bx), 1))]).T).T,
                   (M[:3, :3] @ Bx[:, 3:6].T).T])
    P, N = A[:, :3], A[:, 3:6]
    out = []
    for i in range(len(B)):
        d = np.linalg.norm(P - B[i, :3], axis=1)
        j = int(np.argmin(d))
        out.append((float(d[j]), float(np.dot(N[j], B[i, 3:6])), j, i))
    out = [o for o in out if o[0] < 3.0]
    if not out:
        return dict(gap=float("nan"), n3=0, dot_med=float("nan"), neg=0, absdot_med=float("nan"),
                    rA=[], rB=[], tang=[])
    d = np.array([o[0] for o in out]); dt = np.array([o[1] for o in out])
    # tangent at the matched points (forward difference) for the angle between the two lines
    def tang(C, i):
        t = C[(i + 1) % len(C), :3] - C[i, :3]
        return t / max(np.linalg.norm(t), 1e-12)
    ang = []
    for _, _, j, i in out:
        ang.append(float(np.degrees(np.arccos(min(1.0, abs(np.dot(tang(A, j), tang(B, i))))))))
    ra = radial(y, np.array([P[o[2]] for o in out]))
    rb = radial(x, np.array([Bx[o[3], :3] for o in out]))
    def radsign(k, P, N):
        o, d = load_ax(k)
        d = d / np.linalg.norm(d)
        w = P - o
        rh = (w - np.outer(w @ d, d))
        rh = rh / np.maximum(np.linalg.norm(rh, axis=1), 1e-9)[:, None]
        return np.sum(N * rh, axis=1)
    sa = radsign(y, np.array([P[o[2]] for o in out]), np.array([N[o[2]] for o in out]))
    sb = radsign(x, np.array([Bx[o[3], :3] for o in out]), np.array([Bx[o[3], 3:6] for o in out]))
    return dict(gap=float(d.min()), n3=len(out), dot_med=float(np.median(dt)),
                neg=int(np.sum(dt < 0)), absdot_med=float(np.median(np.abs(dt))),
                rA=[float(v) for v in ra], rB=[float(v) for v in rb],
                radA=[round(float(v), 2) for v in sa], radB=[round(float(v), 2) for v in sb],
                tang=[round(a, 1) for a in ang])

touching = [(1, 2), (1, 4), (1, 8), (1, 9), (2, 5), (2, 9), (3, 5), (6, 7), (7, 9)]
res = {}
print("pair | ctrl gap n3 dot_med neg | swap gap n3 dot_med neg | |dot|med swap | tangent angle med (swap)")
for y, x in touching:
    c = pair(y, x, False)
    s = pair(y, x, True)
    res[f"{y}-{x}"] = dict(ctrl=c, swap=s)
    tmed = float(np.median([a for a in s["tang"]])) if s["tang"] else float("nan")
    print(f"{y}-{x} | {c['gap']:7.4f} {c['n3']:3d} {c['dot_med']:+7.3f} {c['neg']:3d} | "
          f"{s['gap']:7.4f} {s['n3']:3d} {s['dot_med']:+7.3f} {s['neg']:3d} | {s['absdot_med']:7.3f} | {tmed:7.1f}")
json.dump(res, open(os.path.join(OUT, "bar4_pairs_local.json"), "w"), indent=1)

print()
for y, x in [(1, 9), (6, 7)]:
    s = res[f"{y}-{x}"]["swap"]
    print(f"pair {y}-{x} swap: matched radii about the GT axis")
    print("  piece", y, ":", [round(v, 2) for v in s["rA"]])
    print("  piece", x, ":", [round(v, 2) for v in s["rB"]])
    print("  tangent angles deg:", s["tang"])
    print("  normal-vs-radial (outward +) A:", s["radA"])
    print("  normal-vs-radial (outward +) B:", s["radB"])