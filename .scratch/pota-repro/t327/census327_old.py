#!/usr/bin/env python
"""ticket 327 bar 3 -- census of the pre-2026-10-31 Juglet bundles on the OLD clouds.

Two surviving old bundles are read (read-only copies under artifacts/pota327/old_t30 and old_t41):
  20261027-0659_cc9c6d9_t30-arm4-control-jug3p4  (2026-10-27, commit cc9c6d9)
  20261029-0017_bdbd8b8_t41-juglet               (2026-10-29, commit bdbd8b8, arm A/W = radius)
Both predate the 2026-10-31 cloud regeneration, so their inputs were the vertex dumps.
Same instrument as bar 1: mean radius of each surface about the piece's GT axis line, plus the
assembly-frame inward-normal test. Frame is checked by the centroid->axis offset (a 33 mm vessel
puts it at a few mm, as in bar 1).
"""
import json, os, glob
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(BASE, "..", "..", ".."))
GT = os.path.join(WT, "artifacts", "pota327", "gt")
OUT = os.path.join(WT, "artifacts", "pota327")

def load_ply(p):
    # PCL ASCII PLY: honour the element vertex count so the trailing camera block
    # (three 4x4 matrices = 48 numbers) is never mistaken for points.
    L = open(p).read().splitlines()
    i = [n for n, l in enumerate(L) if l == "end_header"][0]
    nvert = None
    for l in L[:i]:
        if l.startswith("element vertex"):
            nvert = int(l.split()[2])
    rows = [l.split() for l in L[i + 1:i + 1 + nvert] if l.strip()]
    return np.array([[float(x) for x in r[:6]] for r in rows])

def load_ax(p):
    v = [float(x) for x in open(p).read().split()]
    return np.array(v[-6:-3]), np.array(v[-3:])

def rad_line(P, o, d):
    w = P - o
    return np.linalg.norm(w - np.outer(w @ d, d), axis=1)

out = {}
for bundle, src in (("t30", "old_t30"), ("t41", "old_t41")):
    rows = []
    for f in sorted(glob.glob(os.path.join(WT, "artifacts", "pota327", src, "*Surface_0.ply"))):
        k = int(os.path.basename(f).split("_")[2])
        f1 = f.replace("Surface_0", "Surface_1")
        if not os.path.exists(f1):
            continue
        s0, s1 = load_ply(f), load_ply(f1)
        o, d = load_ax(os.path.join(GT, f"Juglet_Piece_{k}_Axis.xyz"))
        d = d / np.linalg.norm(d)
        r0, r1 = rad_line(s0[:, :3], o, d), rad_line(s1[:, :3], o, d)
        def inmean(S):
            P = S[:, :3]; N = S[:, 3:6]
            w = P - o; perp = w - np.outer(w @ d, d)
            rh = perp / np.maximum(np.linalg.norm(perp, axis=1), 1e-9)[:, None]
            return float(np.mean(np.sum(N * rh, axis=1)))
        c = np.vstack([s0[:, :3], s1[:, :3]]).mean(axis=0)
        w = c - o
        rows.append(dict(piece=k, r_mean_S0=float(r0.mean()), r_mean_S1=float(r1.mean()),
                         side_S0="outer" if r0.mean() > r1.mean() else "inner",
                         m_S0=inmean(s0), m_S1=inmean(s1),
                         n_S0=int(len(s0)), n_S1=int(len(s1)),
                         centroid_axis_mm=float(np.linalg.norm(w - (w @ d) * d)),
                         centroid_along_mm=float(w @ d),
                         frame_z_range=[float(np.concatenate([s0[:, 2], s1[:, 2]]).min()),
                                        float(np.concatenate([s0[:, 2], s1[:, 2]]).max())]))
    out[bundle] = rows

json.dump(out, open(os.path.join(OUT, "census_bar3_old.json"), "w"), indent=1)
for bundle, rows in out.items():
    print("==", bundle)
    print("piece r_mean_S0 r_mean_S1 S0_is m_S0 m_S1 n0 n1 centroid->axis along zrange")
    for r in rows:
        print(f"{r['piece']:5d} {r['r_mean_S0']:9.3f} {r['r_mean_S1']:9.3f} {r['side_S0']:5s} "
              f"{r['m_S0']:+7.3f} {r['m_S1']:+7.3f} {r['n_S0']:5d} {r['n_S1']:5d} "
              f"{r['centroid_axis_mm']:7.3f} {r['centroid_along_mm']:+8.3f} "
              f"[{r['frame_z_range'][0]:.2f},{r['frame_z_range'][1]:.2f}]")
    print("S0-OUTER:", [r["piece"] for r in rows if r["side_S0"] == "outer"])