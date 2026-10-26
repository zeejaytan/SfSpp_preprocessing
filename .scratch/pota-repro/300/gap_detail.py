#!/usr/bin/env python
"""Ticket 300: which sheet each boundary loop of Pot C 01 lies on, how wide the opening is,
and how far it sits from the sherd's break face (crease where the sheets meet the wall)."""
import json
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree

ROOT = Path(r"C:/PR/SfSpp_preprocessing/artifacts/pota300")
IN = ROOT / "inputs" / "stage"
CORPUS = IN / "corpus"
OUT = ROOT / "geom"


def load_obj(path):
    vs, fs = [], []
    with open(path, "r", errors="ignore") as fh:
        for line in fh:
            if line.startswith("v "):
                vs.append([float(x) for x in line.split()[1:4]])
            elif line.startswith("f "):
                idx = [int(tok.split("/")[0]) for tok in line.split()[1:]]
                for k in range(1, len(idx) - 1):
                    fs.append([idx[0], idx[k], idx[k + 1]])
    return np.asarray(vs, float), np.asarray(fs, np.int64) - 1


def load_axis(path):
    a = np.loadtxt(path).ravel()
    return a[:3], a[3:6] / np.linalg.norm(a[3:6])


def load_xyz(path):
    return np.loadtxt(path, usecols=(0, 1, 2))


def boundary_loops(V, F):
    cnt = defaultdict(int)
    for tri in F:
        for a, b in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
            cnt[(min(a, b), max(a, b))] += 1
    bedges = {(a, b) for (a, b), c in cnt.items() if c == 1}
    adj = defaultdict(set)
    for a, b in bedges:
        adj[a].add(b)
        adj[b].add(a)
    used, loops = set(), []
    for a, b in sorted(bedges):
        if a in used:
            continue
        loop = [a]; used.add(a)
        cur, prev = b, a
        closed = True
        while cur != a:
            if cur in used:
                closed = False
                break
            loop.append(cur); used.add(cur)
            nxt = [x for x in adj[cur] if x != prev and x not in used] or [x for x in adj[cur] if x != prev]
            if not nxt:
                closed = False
                break
            prev, cur = cur, nxt[0]
        loops.append((loop, closed))
    out = []
    for lp, closed in loops:
        P = V[np.asarray(lp)]
        per = float(np.linalg.norm(np.diff(np.vstack([P, P[:1]]), axis=0), axis=1).sum())
        out.append({"idx": lp, "P": P, "n_verts": len(lp), "perimeter_mm": per, "closed": closed})
    return sorted(out, key=lambda r: -r["perimeter_mm"])


def crease_vertices(V, F, deg=55.0):
    """vertices on an edge whose two faces fold by more than deg: where a sheet meets the break wall"""
    edge_faces = defaultdict(list)
    for fi, tri in enumerate(F):
        for a, b in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
            edge_faces[(min(a, b), max(a, b))].append(fi)
    n = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]])
    nn = np.linalg.norm(n, axis=1, keepdims=True)
    nn[nn == 0] = 1.0
    n = n / nn
    c = np.cos(np.radians(deg))
    verts = set()
    for (a, b), fl in edge_faces.items():
        if len(fl) == 2 and float(n[fl[0]] @ n[fl[1]]) < c:
            verts.add(a); verts.add(b)
    return np.asarray(sorted(verts))


V, F = load_obj(CORPUS / "Mesh" / "Pot_C_Piece_01_Mesh_DS.obj")
axis = load_axis(IN / "axes" / "Pot_C_Piece_01_Axis.xyz")
S0 = load_xyz(IN / "prep_geom" / "Pot_C_Piece_01.S0.xyz")   # our classify step: Surface_0 = interior
S1 = load_xyz(IN / "prep_geom" / "Pot_C_Piece_01.S1.xyz")

def radius(V, axis):
    o, d = axis
    rel = V - o
    t = rel @ d
    return np.linalg.norm(rel - np.outer(t, d), axis=1), t

r_all, t_all = radius(V, axis)
loops = boundary_loops(V, F)
crease = crease_vertices(V, F)
tS0, tS1, tCr = cKDTree(S0), cKDTree(S1), cKDTree(V[crease])

rep = {"crease": {"n_verts": int(len(crease)), "frac_of_mesh": round(len(crease) / len(V), 3),
                 "deg_threshold": 55.0},
       "loops": []}
for k, lp in enumerate(loops):
    P = lp["P"]
    r, t = radius(P, axis)
    d0, _ = tS0.query(P, k=1)
    d1, _ = tS1.query(P, k=1)
    dd, _ = tCr.query(P, k=1)
    # best-fit plane, then the opening's two principal extents
    c = P.mean(0)
    _, _, vt = np.linalg.svd(P - c, full_matrices=False)
    Q = (P - c) @ vt[:2].T
    rep["loops"].append({
        "rank": k,
        "n_verts": lp["n_verts"], "closed": bool(lp["closed"]),
        "perimeter_mm": round(lp["perimeter_mm"], 2),
        "centroid": [round(float(x), 2) for x in c],
        "radius_to_axis_mm": {"median": round(float(np.median(r)), 2),
                              "range": [round(float(r.min()), 2), round(float(r.max()), 2)]},
        "dist_to_S0_interior_mm": {"median": round(float(np.median(d0)), 2),
                                   "p90": round(float(np.quantile(d0, 0.9)), 2)},
        "dist_to_S1_exterior_mm": {"median": round(float(np.median(d1)), 2),
                                   "p90": round(float(np.quantile(d1, 0.9)), 2)},
        "lies_on": "interior(S0)" if np.median(d0) < np.median(d1) else "exterior(S1)",
        "dist_to_break_crease_mm": {"min": round(float(dd.min()), 2),
                                    "median": round(float(np.median(dd)), 2)},
        "opening_mm": {"major": round(float(np.ptp(Q[:, 0])), 2), "minor": round(float(np.ptp(Q[:, 1])), 2)},
        "idx": lp["idx"],
    })

# gap width across the loop for the two big ones
for rec in rep["loops"][:2]:
    P = loops[rec["rank"]]["P"]
    n = len(P)
    d = np.min(np.vstack([np.linalg.norm(P - np.roll(P, k, axis=0), axis=1)
                          for k in (n // 8, n // 4, n // 2)]), axis=0)
    rec["across_the_opening_mm"] = {"min": round(float(d.min()), 2),
                                    "median": round(float(np.median(d)), 2)}
    rec.pop("idx"); rep["loops"][rec["rank"] + 1].pop("idx", None) if False else None

# the sherd's own size, for scale
rep["sherd"] = {"bbox_mm": [round(float(x), 2) for x in np.ptp(V, axis=0)],
                "n_verts": int(len(V)), "n_faces": int(len(F)),
                "n_boundary_loops": len(loops)}
for rec in rep["loops"]:
    rec.pop("idx", None)
(OUT / "gap_detail.json").write_text(json.dumps(rep, indent=1))
print(json.dumps(rep, indent=1))
