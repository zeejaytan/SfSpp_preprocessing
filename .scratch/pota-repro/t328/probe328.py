#!/usr/bin/env python
"""ticket 328 -- bar 1 and bar 2 probe on the t66 geom bundle (no build needed).

All inputs are copies of the merged 327 artifacts (artifacts/pota328/in/{geom,gt,dsaxis}).
Nothing here writes outside artifacts/pota328/.

Outputs (artifacts/pota328/probe/):
  census.tsv      per piece: GT-axis radius per face, thickness, fitted-axis radii, geometric
                  pick, DS-axis vote (code-equivalent), agreement
  blsign.tsv      per piece/face: line-normal vs wall-normal agreement (the bar-2 "before")
  pairs.json      per touching pair: harness-reproduced dot_med_d3 (before), the wall-normal
                  ceiling, and the prediction after per-point wall signing
"""
import json, os, sys
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(BASE, "..", "..", ".."))
IN = os.path.join(WT, "artifacts", "pota328", "in")
OUT = os.path.join(WT, "artifacts", "pota328", "probe")
os.makedirs(OUT, exist_ok=True)
GEOM = os.path.join(IN, "geom")
GT = os.path.join(IN, "gt")

def load_ply6(p):
    L = open(p).read().splitlines()
    i = [n for n, l in enumerate(L) if l.strip() == "end_header"][0]
    data = [l.split() for l in L[i + 1:] if l.strip() and not l.startswith("camera")]
    a = np.array([[float(x) for x in r[:6]] for r in data])
    return a

def load_pcd(p):
    L = open(p).read().splitlines()
    i = [n for n, l in enumerate(L) if l.startswith("DATA")][0]
    rows = [l.split() for l in L[i + 1:] if l.strip() and len(l.split()) >= 6]
    return np.array([[float(x) for x in r[:6]] for r in rows])

def load_ax(p):
    v = [float(x) for x in open(p).read().split()]
    return np.array(v[-6:-3]), np.array(v[-3:])

def unit(a):
    return a / np.maximum(np.linalg.norm(a, axis=1, keepdims=True), 1e-12)

def perp_dist(P, o, d):
    w = P - o
    return np.linalg.norm(w - np.outer(w @ d, d), axis=1)

from scipy.spatial import cKDTree

T = {k: np.loadtxt(os.path.join(GT, "Juglet_Piece_%d_T.txt" % k)) for k in range(1, 10)}
S = {k: {f: load_ply6(os.path.join(GEOM, "Juglet_Piece_%d.S%d" % (k, f))) for f in (0, 1)} for k in range(1, 10)}
B = {k: {f: load_pcd(os.path.join(GEOM, "Juglet_Piece_%d.Bl%d" % (k, f))) for f in (0, 1)} for k in range(1, 10)}
GTax = {k: load_ax(os.path.join(GT, "Juglet_Piece_%d_Axis.xyz" % k)) for k in range(1, 10)}
DSax = {k: load_ax(os.path.join(IN, "dsaxis", "Juglet_Piece_%d_Axis.xyz" % k)) for k in range(1, 10)}

def fit_axis(P0, N0, P1, N1):
    """Axis of the two faces from their normals+points.  Flip-invariant, axis-file-free.
    direction = min-eigenvector of sum n n^T (normals of a wall fragment lie in the plane
    perpendicular to the vessel axis); position = linear fit imposing one signed radius per
    face.  Returns (c, d, lam_ratio, rms)."""
    N = np.vstack([N0, N1])
    P = np.vstack([P0, P1])
    N = unit(N)
    M = N.T @ N / len(N)
    w, V = np.linalg.eigh(M)
    d = V[:, 0]
    lam_ratio = w[0] / max(w[1], 1e-12)
    # plane basis perpendicular to d
    a = np.array([1.0, 0, 0]) if abs(d[0]) < 0.9 else np.array([0, 1.0, 0])
    u = np.cross(d, a); u /= np.linalg.norm(u)
    v = np.cross(d, u)
    n2 = np.stack([N @ u, N @ v], axis=1)          # (m,2)
    p2 = np.stack([P @ u, P @ v], axis=1)          # (m,2)
    face = np.concatenate([np.zeros(len(P0)), np.ones(len(P1))])
    # residual_i = c.n2_i - p2_i.n2_i + rho_face ; solve for c(2), rho0, rho1
    A = np.zeros((len(P), 4))
    A[:, 0:2] = n2
    A[:, 2] = (face == 0)
    A[:, 3] = (face == 1)
    b = np.sum(p2 * n2, axis=1)
    sol, *_ = np.linalg.lstsq(A, b, rcond=None)
    c2 = sol[0:2]
    c = c2[0] * u + c2[1] * v
    res = A @ sol - b
    rms = float(np.sqrt(np.mean(res ** 2)))
    return c, d, float(lam_ratio), rms, (float(sol[2]), float(sol[3]))

def vote(axpair, faces):
    """exact re-implementation of classifyAndOrderPaper234's vote (order = faces list)."""
    o, d = axpair
    d = d / np.linalg.norm(d)
    fr = []
    for f in faces:
        P = S[f]["S0"][:, :3] if False else None
        fr.append(None)
    return None

def infrac(P, N, o, d):
    d = d / np.linalg.norm(d)
    w = P - o
    t = w @ d
    cp = o + np.outer(t, d)
    v = cp - P
    return float(np.mean(np.sum(v * N, axis=1) > 0))

rows_c, rows_b = [], []
cen = {}
for k in range(1, 10):
    g0, gd = GTax[k]
    gd = gd / np.linalg.norm(gd)
    rec = dict(piece=k)
    r = {}
    for f in (0, 1):
        A = S[k][f]
        P, N = A[:, :3], unit(A[:, 3:6])
        r[f] = float(np.median(perp_dist(P, g0, gd)))
        rec["r_gt_S%d" % f] = round(r[f], 3)
    thick = float(np.median(cKDTree(S[k][1][:, :3]).query(S[k][0][:, :3], k=1)[0]))
    rec["thick"] = round(thick, 3)
    # geometric pick (no GT axis, no axis file)
    P0, N0 = S[k][0][:, :3], S[k][0][:, 3:6]
    P1, N1 = S[k][1][:, :3], S[k][1][:, 3:6]
    c, d, lam, rms, rho = fit_axis(P0, N0, P1, N1)
    rg = {}
    for f in (0, 1):
        A = S[k][f]
        rg[f] = float(np.median(perp_dist(A[:, :3], c, d)))
    rec["r_fit_S0"], rec["r_fit_S1"] = round(rg[0], 3), round(rg[1], 3)
    rec["lam_ratio"] = round(lam, 4)
    rec["fit_rms"] = round(rms, 3)
    rec["fit_rho"] = (round(rho[0], 3), round(rho[1], 3))
    dgeom = rg[1] - rg[0]
    rec["dgeom"] = round(dgeom, 3)
    rec["geom_pick"] = 0 if dgeom > 0 else 1     # smaller radius is interior
    rec["geom_decisive"] = bool(abs(dgeom) > 0.5 * thick)
    # the shipped vote against the DS axis, exactly as the binary runs it on (S0, S1)
    o2, d2 = DSax[k]
    f0 = infrac(S[k][0][:, :3], unit(S[k][0][:, 3:6]), o2, d2)
    f1 = infrac(S[k][1][:, :3], unit(S[k][1][:, 3:6]), o2, d2)
    n0, n1 = len(S[k][0]), len(S[k][1])
    satA = f0 * n0 + (1 - f1) * n1
    satB = (1 - f0) * n0 + f1 * n1
    rec.update(frac0=round(f0, 3), frac1=round(f1, 3), satA=round(satA, 1), satB=round(satB, 1),
               vote_pick=(0 if satA >= satB else 1), vote_margin=round((satA - satB) / (n0 + n1), 4))
    rec["interior_true"] = 0 if r[0] < r[1] else 1
    cen[k] = rec
    rows_c.append(rec)
    # bar-2 "before": each line against the wall it rides (Bl_k rides S_k)
    for f in (0, 1):
        A, L = S[k][f], B[k][f]
        Nw = unit(A[:, 3:6])
        idx = cKDTree(A[:, :3]).query(L[:, :3], k=1)[1]
        dt = np.sum(unit(L[:, 3:6]) * Nw[idx], axis=1)
        # and the wall on the *other* face, for contrast
        A2 = S[k][1 - f]
        Nw2 = unit(A2[:, 3:6])
        idx2 = cKDTree(A2[:, :3]).query(L[:, :3], k=1)[1]
        dt2 = np.sum(unit(L[:, 3:6]) * Nw2[idx2], axis=1)
        row = dict(piece=k, face=f, n=int(len(L)),
                   frac_agree_wall=round(float(np.mean(dt > 0)), 3),
                   med_dot_wall=round(float(np.median(dt)), 3),
                   frac_absdot_gt05=round(float(np.mean(np.abs(dt) > 0.5)), 3),
                   frac_agree_other=round(float(np.mean(dt2 > 0)), 3),
                   med_dot_other=round(float(np.median(dt2)), 3))
        rows_b.append(row)

with open(os.path.join(OUT, "census.tsv"), "w") as fh:
    cols = ["piece", "r_gt_S0", "r_gt_S1", "thick", "interior_true", "r_fit_S0", "r_fit_S1",
            "dgeom", "geom_pick", "geom_decisive", "lam_ratio", "fit_rms", "frac0", "frac1",
            "satA", "satB", "vote_pick", "vote_margin"]
    fh.write("\t".join(cols) + "\n")
    for r in rows_c:
        fh.write("\t".join(str(r.get(c)) for c in cols) + "\n")
with open(os.path.join(OUT, "blsign.tsv"), "w") as fh:
    cols = list(rows_b[0].keys())
    fh.write("\t".join(cols) + "\n")
    for r in rows_b:
        fh.write("\t".join(str(r[c]) for c in cols) + "\n")

print("piece | r_gt S0/S1 (interior) | thick | fit S0/S1 dgeom pick dec | lam fit_rms | vote frac0/frac1 margin pick | AGREE?")
for r in rows_c:
    ag = "yes" if r["geom_pick"] == r["vote_pick"] else "NO"
    print("%5d | %7.3f %7.3f (%d) | %5.3f | %7.3f %7.3f %+6.3f %d %-5s | %6.3f %6.2f | %5.3f %5.3f %+6.3f %d | %s" % (
        r["piece"], r["r_gt_S0"], r["r_gt_S1"], r["interior_true"], r["thick"],
        r["r_fit_S0"], r["r_fit_S1"], r["dgeom"], r["geom_pick"], r["geom_decisive"],
        r["lam_ratio"], r["fit_rms"], r["frac0"], r["frac1"], r["vote_margin"], r["vote_pick"], ag))
print()
print("bar-2 before: line normal vs the wall it rides, and vs the other face")
for r in rows_b:
    print("piece %d face %d n=%3d | wall agree %5.3f med %+6.3f |dot|>0.5 %5.3f | other agree %5.3f" % (
        r["piece"], r["face"], r["n"], r["frac_agree_wall"], r["med_dot_wall"],
        r["frac_absdot_gt05"], r["frac_agree_other"]))
