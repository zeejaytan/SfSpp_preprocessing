#!/usr/bin/env python
"""ticket 327 bar 1 -- nine-piece Juglet wall-side census, independent re-derivation.

Inputs (read-only): the t66 bundle's per-piece Surface_0/Surface_1 (PLY with normals) and
Breakline_0/Breakline_1 (PCD with normals); the GT key Dataset/Juglet_GT (T matrices + axes).
The GT axis is the oracle: it names which wall is the outer one, and is never an input to the
pipeline. No ORIG/GT point cloud is read anywhere.

Per piece it reports:
  - mean/median radius of S0 and S1 about the GT axis LINE (GT axis is already in the same
    frame as the t66 clouds: measured centroid->axis 2.4-16.3 mm and radii 11-17 mm, which a
    33 mm vessel requires; the T-applied hypotheses put the centroid 100-500 mm off),
  - per-wall loop point count, loop length and sampling density for Bl0/Bl1,
  - median distance of each breakline to S0 and to S1 (which surface it rides),
  - the assembly-frame inward normal test mean(n . rhat) with rhat pointing away from the axis
    (interior is negative), which is ticket 296's instrument and the census's second opinion.
"""
import json, os
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(BASE, "..", "..", ".."))
GEOM = os.path.join(WT, "artifacts", "pota327", "geom")
GT = os.path.join(WT, "artifacts", "pota327", "gt")
OUT = os.path.join(WT, "artifacts", "pota327")

def load_ply(p):
    L = open(p).read().splitlines()
    i = [n for n, l in enumerate(L) if l == "end_header"][0]
    rows = [l.split() for l in L[i + 1:] if l.strip() and len(l.split()) >= 6]
    return np.array([[float(x) for x in r[:6]] for r in rows])

def load_pcd(p):
    L = open(p).read().splitlines()
    i = [n for n, l in enumerate(L) if l.startswith("DATA")][0]
    rows = [l.split() for l in L[i + 1:] if l.strip() and len(l.split()) >= 6]
    return np.array([[float(x) for x in r[:6]] for r in rows])

def load_ax(p):
    v = [float(x) for x in open(p).read().split()]
    return np.array(v[-6:-3]), np.array(v[-3:])

def rad_line(P, o, d):
    w = P - o
    return np.linalg.norm(w - np.outer(w @ d, d), axis=1)

rows = []
for k in range(1, 10):
    s0 = load_ply(os.path.join(GEOM, f"Juglet_Piece_{k}.S0"))
    s1 = load_ply(os.path.join(GEOM, f"Juglet_Piece_{k}.S1"))
    b0 = load_pcd(os.path.join(GEOM, f"Juglet_Piece_{k}.Bl0"))
    b1 = load_pcd(os.path.join(GEOM, f"Juglet_Piece_{k}.Bl1"))
    o, d = load_ax(os.path.join(GT, f"Juglet_Piece_{k}_Axis.xyz"))
    d = d / np.linalg.norm(d)

    r0, r1 = rad_line(s0[:, :3], o, d), rad_line(s1[:, :3], o, d)
    # inward test: rhat points away from the axis
    def inmean(S):
        P = S[:, :3]; N = S[:, 3:6]
        w = P - o; perp = w - np.outer(w @ d, d)
        rh = perp / np.maximum(np.linalg.norm(perp, axis=1), 1e-9)[:, None]
        return float(np.mean(np.sum(N * rh, axis=1)))
    m0, m1 = inmean(s0), inmean(s1)

    def loop_stats(B):
        P = B[:, :3]
        seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
        L = float(seg.sum())
        nn = []
        for i in range(0, len(P), max(1, len(P) // 400)):
            dd = np.linalg.norm(P - P[i], axis=1)
            dd[i] = np.inf
            nn.append(dd.min())
        return len(P), L, (len(P) / L if L > 0 else 0.0), float(np.median(nn))

    n0, L0, dens0, nn0 = loop_stats(b0)
    n1, L1, dens1, nn1 = loop_stats(b1)

    def ride(B, S):
        P = B[:, :3]; Q = S[:, :3]
        idx = np.random.default_rng(0).choice(len(Q), size=min(len(Q), 3000), replace=False)
        Q = Q[idx]
        out = []
        for i in range(0, len(P), max(1, len(P) // 200)):
            out.append(np.linalg.norm(Q - P[i], axis=1).min())
        return float(np.median(out))

    d_b0_s0, d_b0_s1 = ride(b0, s0), ride(b0, s1)
    d_b1_s0, d_b1_s1 = ride(b1, s0), ride(b1, s1)

    rows.append(dict(piece=k, r_mean_S0=float(r0.mean()), r_mean_S1=float(r1.mean()),
                     r_med_S0=float(np.median(r0)), r_med_S1=float(np.median(r1)),
                     m_S0=m0, m_S1=m1,
                     side_S0="outer" if r0.mean() > r1.mean() else "inner",
                     n_S0=int(len(s0)), n_S1=int(len(s1)),
                     bl0_n=n0, bl0_len_mm=L0, bl0_dens=n0 / L0, bl0_nn_mm=nn0,
                     bl1_n=n1, bl1_len_mm=L1, bl1_dens=n1 / L1, bl1_nn_mm=nn1,
                     bl0_to_S0=d_b0_s0, bl0_to_S1=d_b0_s1,
                     bl1_to_S0=d_b1_s0, bl1_to_S1=d_b1_s1))

os.makedirs(OUT, exist_ok=True)
json.dump(rows, open(os.path.join(OUT, "census_bar1.json"), "w"), indent=1)
hdr = ("piece r_mean_S0 r_mean_S1 S0_is m_S0 m_S1 | S0pts S1pts | Bl0n Bl0len Bl0dens Bl0nn "
       "| Bl1n Bl1len Bl1dens Bl1nn | Bl0->S0 Bl0->S1 Bl1->S0 Bl1->S1")
print(hdr)
for r in rows:
    print(f"{r['piece']:5d} {r['r_mean_S0']:9.3f} {r['r_mean_S1']:9.3f} {r['side_S0']:5s} "
          f"{r['m_S0']:+7.3f} {r['m_S1']:+7.3f} | {r['n_S0']:6d} {r['n_S1']:6d} "
          f"| {r['bl0_n']:4d} {r['bl0_len_mm']:7.2f} {r['bl0_dens']:7.3f} {r['bl0_nn_mm']:6.3f} "
          f"| {r['bl1_n']:4d} {r['bl1_len_mm']:7.2f} {r['bl1_dens']:7.3f} {r['bl1_nn_mm']:6.3f} "
          f"| {r['bl0_to_S0']:6.3f} {r['bl0_to_S1']:6.3f} {r['bl1_to_S0']:6.3f} {r['bl1_to_S1']:6.3f}")
print("S0-OUTER:", [r["piece"] for r in rows if r["side_S0"] == "outer"])
print("Bl0 rides S0 (closer to S0 than S1):", [r["piece"] for r in rows if r["bl0_to_S0"] < r["bl0_to_S1"]])

