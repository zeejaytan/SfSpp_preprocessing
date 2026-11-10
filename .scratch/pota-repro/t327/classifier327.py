#!/usr/bin/env python
"""ticket 327 bar 2 -- the classifier's input, per piece.

The rule (mesh_processing_headless.cpp:3688-3750 at fab76f5) is: for each of the two faces,
inFrac = fraction of points whose normal points back toward the *configured* axis line
(v = cp - pp, cp = projection of pp on the axis; inFrac counts v.dot(n) > 0).  The vote
satA/satB then names face 0 or face 1 as interior, and the mesh stage renames Surface_0 to
Breakline_0 downstream.  So the rule has exactly one data input: the axis file.

This script evaluates inFrac twice per piece -- once with the axis the t66 cell actually
staged (Dataset/Axes/Juglet, our September PotSAC fit), once with the GT axis -- on the same
exported surfaces, and reports the vote each time.
"""
import json, os
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(BASE, "..", "..", ".."))
GEOM = os.path.join(WT, "artifacts", "pota327", "geom")
GTD = os.path.join(WT, "artifacts", "pota327", "gt")
DSD = os.path.join(WT, "artifacts", "pota327", "dsaxis")
OUT = os.path.join(WT, "artifacts", "pota327")

def load_ply(p):
    L = open(p).read().splitlines()
    i = [n for n, l in enumerate(L) if l == "end_header"][0]
    rows = [l.split() for l in L[i + 1:] if l.strip() and len(l.split()) >= 6]
    return np.array([[float(x) for x in r[:6]] for r in rows])

def load_ax6(p):
    v = [float(x) for x in open(p).read().split()]
    return np.array(v[:3]), np.array(v[3:6])          # the binary reads the FIRST six

def load_axgt(p):
    v = [float(x) for x in open(p).read().split()]
    return np.array(v[-6:-3]), np.array(v[-3:])

def in_frac(P, N, o, d):
    w = P - o
    t = w @ d
    cp = o + np.outer(t, d)
    v = cp - P
    return float(np.mean(np.sum(v * N, axis=1) > 0))

def vote(f0, n0, f1, n1):
    satA = f0 * n0 + (1.0 - f1) * n1
    satB = (1.0 - f0) * n0 + f1 * n1
    return satA, satB, ("face0" if satA >= satB else "face1")

rows = []
for k in range(1, 10):
    s0 = load_ply(os.path.join(GEOM, f"Juglet_Piece_{k}.S0"))
    s1 = load_ply(os.path.join(GEOM, f"Juglet_Piece_{k}.S1"))
    od, dd = load_ax6(os.path.join(DSD, f"Juglet_Piece_{k}_Axis.xyz"))
    og, dg = load_axgt(os.path.join(GTD, f"Juglet_Piece_{k}_Axis.xyz"))
    dd /= np.linalg.norm(dd); dg /= np.linalg.norm(dg)
    c = np.vstack([s0[:, :3], s1[:, :3]]).mean(0)
    # how far the DS line is from the GT line at the piece
    # direction angle (acute)
    ang = float(np.degrees(np.arccos(min(1.0, abs(dd @ dg)))))
    # perpendicular distance between the lines measured at the piece centroid:
    # distance from c to each line, and the offset perpendicular to dg
    def dist_line(p, o, d):
        w = p - o; return float(np.linalg.norm(w - (w @ d) * d))
    lat_ds = dist_line(c, od, dd)
    lat_gt = dist_line(c, og, dg)

    f0d, f1d = in_frac(s0[:, :3], s0[:, 3:6], od, dd), in_frac(s1[:, :3], s1[:, 3:6], od, dd)
    f0g, f1g = in_frac(s0[:, :3], s0[:, 3:6], og, dg), in_frac(s1[:, :3], s1[:, 3:6], og, dg)
    aD = vote(f0d, len(s0), f1d, len(s1))
    aG = vote(f0g, len(s0), f1g, len(s1))
    rows.append(dict(piece=k, ang_deg=ang, lat_ds_mm=lat_ds, lat_gt_mm=lat_gt,
                     inFrac_S0_ds=f0d, inFrac_S1_ds=f1d, satA_ds=aD[0], satB_ds=aD[1], interior_ds=aD[2],
                     inFrac_S0_gt=f0g, inFrac_S1_gt=f1g, satA_gt=aG[0], satB_gt=aG[1], interior_gt=aG[2],
                     n_S0=len(s0), n_S1=len(s1)))

json.dump(rows, open(os.path.join(OUT, "classifier_bar2.json"), "w"), indent=1)
print("piece  ang(DS,GT)  off_DS  off_GT | inFrac_ds S0/S1  ->interior | inFrac_gt S0/S1  ->interior")
for r in rows:
    print(f"{r['piece']:5d} {r['ang_deg']:10.1f} {r['lat_ds_mm']:7.2f} {r['lat_gt_mm']:7.2f} | "
          f"{r['inFrac_S0_ds']:6.3f}/{r['inFrac_S1_ds']:6.3f}  {r['interior_ds']:6s}   | "
          f"{r['inFrac_S0_gt']:6.3f}/{r['inFrac_S1_gt']:6.3f}  {r['interior_gt']:6s}")

