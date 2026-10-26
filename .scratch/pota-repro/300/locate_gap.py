#!/usr/bin/env python
"""Ticket 300: locate Pot C 01's scan gap on the mesh and measure it against the pot axis.

Reads the mesh, the pot axis and both Bl0 lines (ours and the authors'); writes nothing but
numbers.  Read-only.
"""
import json
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree

ROOT = Path(r"C:/PR/SfSpp_preprocessing/artifacts/pota300")
IN = ROOT / "inputs" / "stage"
CORPUS = IN / "corpus"
OUT = ROOT / "geom"
SLOTS = [1, 2, 3, 4]


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
    """Axis file is one line: origin x y z + unit direction dx dy dz."""
    a = np.loadtxt(path).ravel()
    assert a.size == 6, a.size
    return a[:3], a[3:6] / np.linalg.norm(a[3:6])


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
    used = set()
    loops = []
    for a, b in sorted(bedges):
        if a in used:
            continue
        loop = [a]
        used.add(a)
        cur, prev = b, a
        ok = True
        while cur != a:
            if cur in used:
                ok = False
                break
            loop.append(cur)
            used.add(cur)
            nxt = [x for x in adj[cur] if x != prev and x not in used]
            if not nxt:
                nxt = [x for x in adj[cur] if x != prev]
                ok = ok and bool(nxt)
            if not nxt:
                break
            prev, cur = cur, nxt[0]
        loops.append({"loop": loop, "closed": ok})
    out = []
    for rec in loops:
        lp = rec["loop"]
        P = V[np.asarray(lp)]
        per = float(np.linalg.norm(np.diff(np.vstack([P, P[:1]]), axis=0), axis=1).sum())
        out.append({"n_verts": len(lp), "perimeter_mm": per, "closed": rec["closed"],
                    "centroid": P.mean(0).tolist(), "bbox_mm": (P.max(0) - P.min(0)).tolist(),
                    "idx": lp, "P": P})
    return sorted(out, key=lambda r: -r["perimeter_mm"])


def axis_radius(V, axis):
    """radial distance to the piece axis (mm) and position along it"""
    origin, d = axis
    rel = V - origin
    t = rel @ d
    return np.linalg.norm(rel - np.outer(t, d), axis=1), t


rep = {}
V1, F1 = load_obj(CORPUS / "Mesh" / "Pot_C_Piece_01_Mesh_DS.obj")
A = load_axis(IN / "axes" / "Pot_C_Piece_01_Axis.xyz")
r_all, t_all = axis_radius(V1, A)
loops = boundary_loops(V1, F1)

rep["mesh"] = {"n_verts": int(len(V1)), "n_faces": int(len(F1)),
               "n_boundary_loops": len(loops),
               "loops": [{"n_verts": r["n_verts"], "perimeter_mm": round(r["perimeter_mm"], 3),
                          "closed": r["closed"],
                          "centroid": [round(c, 2) for c in r["centroid"]],
                          "bbox_mm": [round(c, 2) for c in r["bbox_mm"]]}
                         for r in loops[:10]]}

# the mesh is a solid: interior sheet at low radius, exterior at high radius, break face between
hist, edges = np.histogram(r_all, bins=40)
rep["radius_histogram"] = {"bins_mm": [round(float(e), 2) for e in edges],
                           "counts": [int(h) for h in hist]}

big = loops[0]
P = big["P"]
r_loop, _ = axis_radius(P, A)
rep["largest_hole"] = {
    "n_verts": big["n_verts"], "perimeter_mm": round(big["perimeter_mm"], 3), "closed": big["closed"],
    "bbox_mm": [round(c, 2) for c in big["bbox_mm"]],
    "radius_to_axis_mm": {"min": round(float(r_loop.min()), 2), "median": round(float(np.median(r_loop)), 2),
                          "max": round(float(r_loop.max()), 2)},
    "mesh_radius_to_axis_mm": {"p1": round(float(np.quantile(r_all, 0.01)), 2),
                               "median": round(float(np.median(r_all)), 2),
                               "p99": round(float(np.quantile(r_all, 0.99)), 2)},
}

# gap width: for each loop vertex, distance to the loop vertex K steps away (K = quarter of the loop)
n = big["n_verts"]
K = max(4, n // 4)
d = []
for k in (K // 2, K, K * 3 // 4):
    dd = np.linalg.norm(P - np.roll(P, k, axis=0), axis=1)
    d.append(dd)
d = np.min(np.vstack(d), axis=0)
rep["largest_hole"]["gap_width_mm"] = {"min": round(float(d.min()), 2),
                                       "median": round(float(np.median(d)), 2),
                                       "max": round(float(d.max()), 2),
                                       "how": "min over k in {n/8, n/4, 3n/8} of |p - p rolled by k|, then min/median across the loop"}

# does the hole reach the break face? compare the loop's radius to the two sheet modes,
# and measure the hole's distance to the sherd's outer skin (the silhouette of the piece).
rep["largest_hole"]["spans_sherd_thickness"] = bool(
    (r_loop.max() - r_loop.min()) > 0.5 * (np.quantile(r_all, 0.99) - np.quantile(r_all, 0.01)))

# our Bl0 and the authors' Bl0, in the mesh frame (the exported lines are in the mesh frame)
def load_pcd(path):
    """ASCII PCD: skip the header (FIELDS/VERSION/DATA...) and any '# start end label' comment."""
    rows = []
    seen_data = False
    with open(path, "r", errors="ignore") as fh:
        for line in fh:
            if not seen_data:
                if line.startswith("DATA"):
                    seen_data = True
                continue
            tok = line.split()
            if len(tok) >= 3:
                try:
                    rows.append([float(x) for x in tok[:3]])
                except ValueError:
                    pass
    return np.asarray(rows, float)

ours = load_pcd(IN / "prep_geom" / "Pot_C_Piece_01.Bl0.pcd")
auth = load_pcd(CORPUS / "Breaklines" / "Pot_C_Piece_01_Breakline_0.pcd")
tree_loop = cKDTree(P)
rep["bl0_vs_hole"] = {}
for name, X in (("ours_bl0", ours), ("auth_bl0", auth)):
    dl, _ = tree_loop.query(X, k=1)
    rep["bl0_vs_hole"][name] = {
        "n_dots": int(len(X)),
        "to_hole_mm": {"min": round(float(dl.min()), 2), "median": round(float(np.median(dl)), 2),
                       "max": round(float(dl.max()), 2)},
        "frac_within_2mm": round(float((dl < 2.0).mean()), 3),
        "frac_within_5mm": round(float((dl < 5.0).mean()), 3),
    }
rep["hole_loop_verts"] = P.tolist()

(OUT / "gap.json").write_text(json.dumps(rep, indent=1))
print(json.dumps({k: rep[k] for k in ("mesh", "largest_hole", "bl0_vs_hole")}, indent=1))
