#!/usr/bin/env python3
"""Ticket 32 part A -- sherd extent, mesh area, and the vessel extent derived from GT.

One process per cell.  A cell writes out/cells/A_<arm>_<piece>.json; table32.py turns
the cells into sizes32.tsv and vessel32.tsv.  Nothing is measured here that is not
reported: extent is the bounding-box diagonal of the arm's own cloud (mm), area is the
sum of fan-triangulated face areas of the piece's own mesh (mm^2).
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy.spatial import cKDTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import io32

RECORDED_N = {1: 24294, 2: 2565, 3: 3493, 4: 3651, 5: 6211, 6: 5126, 7: 8421,
              8: 4479, 9: 2094}
MODES = ("Rp+t", "pR+t", "inv")
CELL_MM = 0.25
JUG_PIECES = list(range(1, 10))
PA_PIECES = list(range(1, 9))


def jug_paths(dataset, n):
    return {"pcd": os.path.join(dataset, "Point", "Juglet",
                                "Juglet_Piece_%d_Point.pcd" % n),
            "objs": [os.path.join(dataset, "Mesh", "Juglet",
                                  "Juglet_Piece_%d_Mesh.obj" % n),
                     os.path.join(dataset, "Mesh", "Juglet",
                                  "Juglet_Piece_0%d_Mesh.obj" % n)],
            "t": os.path.join(dataset, "Juglet_GT", "Juglet_Piece_%d_T.txt" % n)}


def pa_paths(corpus, nn):
    return {"pcd": os.path.join(corpus, "Point", "Pot_A",
                                "Pot_A_Piece_%02d_Point.pcd" % nn),
            "obj": os.path.join(corpus, "Mesh", "Pot_A_Piece_%02d_Mesh.obj" % nn),
            "t": os.path.join(corpus, "Ground Truth",
                              "Pot_A_Piece_%d_T.txt" % nn)}


def write_cell(outdir, name, obj):
    d = os.path.join(outdir, "cells")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name + ".json")
    with open(p, "w") as f:
        json.dump(obj, f, indent=1, sort_keys=True)
    print("[A32] wrote %s" % p)
    for k in sorted(obj):
        if isinstance(obj[k], (int, float, str)):
            print("[A32]   %s = %s" % (k, obj[k]))
    sys.stdout.flush()


def cell_juglet(dataset, n, outdir):
    p = jug_paths(dataset, n)
    cl = io32.read_pcd(p["pcd"])
    objs = []
    for op in p["objs"]:
        if not os.path.isfile(op):
            continue
        m = io32.read_obj(op)
        delta = None
        if m["verts"].shape[0] == cl["n_points"]:
            delta = float(np.max(np.linalg.norm(m["verts"] - cl["xyz"], axis=1)))
        objs.append({"path": op, "n_verts": int(m["verts"].shape[0]),
                     "n_faces": int(m["faces"]), "area_mm2": float(m["area_mm2"]),
                     "max_delta_vs_cloud_mm": delta, "md5": io32.md5_file(op)})
    chosen = None
    for o in objs:
        if o["max_delta_vs_cloud_mm"] is not None:
            chosen = o
            break
    rec = {"cell": "A_J_%d" % n, "arm": "J", "piece": "Juglet_Piece_%d" % n,
           "pcd": p["pcd"], "pcd_md5": cl["md5"], "pcd_data": cl["data"],
           "n_points": cl["n_points"], "header_points": cl["header_points"],
           "recorded_points": RECORDED_N[n],
           "count_matches_record": bool(cl["n_points"] == RECORDED_N[n]),
           "n_normals_zero": int(np.count_nonzero(
               np.linalg.norm(cl["nrm"], axis=1) == 0.0)) if cl["nrm"] is not None else -1,
           "objs": objs, "obj_chosen": chosen["path"] if chosen else None,
           "area_mm2": chosen["area_mm2"] if chosen else None,
           "extent_mm": io32.extent_mm(cl["xyz"]),
           "bbox_sides_mm": [float(x) for x in io32.bbox_sides(cl["xyz"])],
           "xyz_min": [float(x) for x in cl["xyz"].min(axis=0)],
           "xyz_max": [float(x) for x in cl["xyz"].max(axis=0)],
           "transform": p["t"]}
    write_cell(outdir, "A_J_%d" % n, rec)
    return rec


def cell_pota(corpus, arm, nn, outdir):
    p = pa_paths(corpus, nn)
    cl = io32.read_pcd(p["pcd"])
    m = io32.read_obj(p["obj"])
    xyz = cl["xyz"]
    nrm = cl["nrm"]
    sub = None
    if arm == "PA_025":
        sub = io32.voxel_subsample(xyz, CELL_MM)
        xyz = xyz[sub]
        nrm = None if nrm is None else nrm[sub]
        gd = os.path.join(outdir, "geom", "pa025")
        os.makedirs(gd, exist_ok=True)
        gp = os.path.join(gd, "Pot_A_Piece_%02d_025.npz" % nn)
        np.savez(gp, xyz=xyz, nrm=np.zeros((0, 3)) if nrm is None else nrm,
                 src=np.array(p["pcd"]), src_md5=np.array(cl["md5"]),
                 cell_mm=np.array(CELL_MM))
    rec = {"cell": "A_%s_%02d" % (arm, nn), "arm": arm,
           "piece": "Pot_A_Piece_%02d" % nn, "pcd": p["pcd"],
           "pcd_md5": cl["md5"], "pcd_data": cl["data"],
           "n_points_released": cl["n_points"], "header_points": cl["header_points"],
           "n_points": int(xyz.shape[0]),
           "n_points_subsampled": None if sub is None else int(sub.size),
           "subsample_cell_mm": None if sub is None else CELL_MM,
           "n_normals_zero": int(np.count_nonzero(
               np.linalg.norm(nrm, axis=1) == 0.0)) if nrm is not None else -1,
           "obj": p["obj"], "obj_md5": io32.md5_file(p["obj"]),
           "n_verts": int(m["verts"].shape[0]), "n_faces": int(m["faces"]),
           "area_mm2": float(m["area_mm2"]),
           "extent_mm": io32.extent_mm(xyz),
           "bbox_sides_mm": [float(x) for x in io32.bbox_sides(xyz)],
           "transform": p["t"]}
    write_cell(outdir, "A_%s_%02d" % (arm, nn), rec)
    return rec


def read_graph(path, n):
    g = []
    with open(path, "r", errors="replace") as fh:
        for line in fh:
            p = line.split()
            if len(p) >= n:
                g.append([int(float(x)) for x in p[:n]])
    if len(g) != n:
        raise SystemExit("[A32] graph %s has %d rows, expected %d" % (path, len(g), n))
    return np.asarray(g, dtype=np.int64)


def mate_stats(sets, graph, n_sample, rng):
    """Min distance from each piece to each other piece, and how the graph lines up."""
    trees = [cKDTree(s) for s in sets]
    d = np.full((len(sets), len(sets)), np.inf)
    for i in range(len(sets)):
        if n_sample is not None and sets[i].shape[0] > n_sample:
            qi = np.sort(rng.choice(sets[i].shape[0], size=n_sample, replace=False))
            q = sets[i][qi]
        else:
            q = sets[i]
        for j in range(len(sets)):
            if i == j:
                continue
            dd, _ = trees[j].query(q, k=1, workers=-1)
            d[i, j] = float(np.min(dd))
    iu = np.triu_indices(len(sets), 1)
    mate = graph[iu] > 0
    dm = d[iu]
    out = {"matrix_min_mm": [[None if not np.isfinite(x) else float(x) for x in row]
                             for row in d],
           "n_pairs": int(dm.size), "n_mates": int(mate.sum()),
           "mate_min_median_mm": float(np.median(dm[mate])) if mate.any() else None,
           "mate_min_max_mm": float(np.max(dm[mate])) if mate.any() else None,
           "nonmate_min_median_mm": float(np.median(dm[~mate])) if (~mate).any() else None,
           "nonmate_min_min_mm": float(np.min(dm[~mate])) if (~mate).any() else None,
           "n_pieces_whose_closest_is_a_mate": int(sum(
               1 for i in range(len(sets))
               if np.isfinite(d[i]).any() and graph[i, int(np.argmin(d[i]))] > 0)),
           "n_pieces": int(len(sets))}
    return out


def cell_vessel(corpus, dataset, pot, outdir, seed):
    rng = np.random.default_rng(seed)
    if pot == "Juglet":
        pieces = JUG_PIECES
        sets = []
        ts = []
        for n in pieces:
            p = jug_paths(dataset, n)
            sets.append(io32.read_pcd(p["pcd"])["xyz"])
            ts.append(io32.read_t(p["t"]))
        graph = read_graph(os.path.join(dataset, "Juglet_GT", "Juglet_simple_graph.txt"),
                           len(pieces))
        n_sample = None
        names = ["Juglet_Piece_%d" % n for n in pieces]
        gt_root = os.path.join(dataset, "Juglet_GT")
    else:
        pieces = PA_PIECES
        sets = []
        ts = []
        for nn in pieces:
            p = pa_paths(corpus, nn)
            sets.append(io32.read_pcd(p["pcd"])["xyz"])
            ts.append(io32.read_t(p["t"]))
        graph = read_graph(os.path.join(corpus, "Ground Truth", "Pot_A_simple_graph.txt"),
                           len(pieces))
        n_sample = 20000
        names = ["Pot_A_Piece_%02d" % nn for nn in pieces]
        gt_root = os.path.join(corpus, "Ground Truth")
    per_mode = {}
    placed = {}
    for mode in MODES:
        ps = []
        for s, T in zip(sets, ts):
            ps.append(io32.place(s, T, mode))
        union = np.vstack(ps)
        sides = io32.bbox_sides(union)
        per_mode[mode] = {"diag_mm": float(np.linalg.norm(sides)),
                          "sides_mm": [float(x) for x in sides],
                          "n_points_union": int(union.shape[0])}
        placed[mode] = ps
    sel = min(MODES, key=lambda m: per_mode[m]["diag_mm"])
    ms = mate_stats(placed[sel], graph, n_sample, rng)
    rec = {"cell": "A_VESSEL_%s" % pot, "arm": "VESSEL", "piece": "vessel_%s" % pot,
           "pot": pot, "pieces": names, "gt_root": gt_root,
           "n_pieces": len(names), "graph_md5": io32.md5_file(
               os.path.join(gt_root, "%s_simple_graph.txt" % pot)),
           "per_mode": per_mode, "mode_selected": sel,
           "mode_selected_by": "smallest union bbox diagonal (reported for all three)",
           "vessel_mm": per_mode[sel]["diag_mm"],
           "vessel_sides_mm": per_mode[sel]["sides_mm"],
           "mate_check": ms, "mate_sample": n_sample,
           "transform_md5": {nm: io32.md5_file(t) for nm, t in zip(
               names, [jug_paths(dataset, n)["t"] if pot == "Juglet"
                       else pa_paths(corpus, n)["t"] for n in pieces])}}
    write_cell(outdir, "A_VESSEL_%s" % pot, rec)
    return rec


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True)
    ap.add_argument("--piece", required=True)
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--seed", type=int, default=32)
    a = ap.parse_args(argv)
    if a.arm == "J":
        cell_juglet(a.dataset, int(a.piece), a.outdir)
    elif a.arm in ("PA_native", "PA_025"):
        cell_pota(a.corpus, a.arm, int(a.piece), a.outdir)
    elif a.arm == "VESSEL":
        cell_vessel(a.corpus, a.dataset, a.piece, a.outdir, a.seed)
    else:
        raise SystemExit("[A32] unknown arm %r" % a.arm)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
