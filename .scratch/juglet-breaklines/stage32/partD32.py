#!/usr/bin/env python3
"""Ticket 32 part D -- the growth's fragmentation, run with ticket 28's replica.

replica234.py (stage28, verified against the pipeline's own rung-2 sidecars) is
imported, not rewritten: pcl_curvature, grow, normalised_f32 and read_rung2_ply are
called as they are.  grow_members below is a copy of replica234.grow with one added
line (the member index list); the selftest asserts the two return the same region
sizes on real rung-2 clouds.

Arms: J (the nine mesh-derived Juglet clouds at native density), PA_025 (Pot A 07,
0.25 mm), and the ticket-30 rung-2 dumps (B = the shipped 0.6 mm Juglet cloud, E = the
native Juglet cloud the pipeline grew, PA = the shipped Pot A 07 cloud) which are the
only copy of the shipped-density clouds and the only way to reproduce ticket 28's
recorded anchors.
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy.spatial import cKDTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import io32
import partA32 as PA
import replica29 as R
import replica234 as R234
import analyse30 as A30

THETA = 3.4
KAPPA = 1.0
NB = 10
FLOORS = (50, 40, 30, 20, 10)
COVER_MM = 2.0

ANCHOR = {("B", "Juglet_Piece_2"): {"regions": 661, "largest": 36, "fail_angle": 4703},
          ("B", "Juglet_Piece_3"): {"regions": 825, "survivors_50": [169, 99]},
          ("B", "Juglet_Piece_5"): {"regions": 1467, "survivors_50": [679]},
          ("B", "Juglet_Piece_7"): {"regions": 1951,
                                    "survivors_50": [326, 263, 77, 68, 65]},
          ("PA", "Pot_A_Piece_07"): {"regions": 1276,
                                     "survivors_50": [3093, 2850, 203, 170, 134,
                                                      120, 73, 71]}}
E_ROWS = {"Juglet_Piece_2": {"npts": 2565, "regions": 1798, "largest": 30},
          "Juglet_Piece_3": {"npts": 3486, "regions": 2308, "largest": 284},
          "Juglet_Piece_5": {"npts": 6208, "regions": 3572, "largest": 757},
          "Juglet_Piece_7": {"npts": 8421, "regions": 4054, "largest": 1162}}


def grow_members(xyz, nrm, curv, nb, theta_deg, kappa):
    """replica234.grow, plus the member index list per region."""
    n = xyz.shape[0]
    pts = xyz.astype(np.float64)
    tree = cKDTree(pts)
    nu = R234.normalised_f32(nrm)
    kq = min(int(nb) + 1, n)
    claimed = np.zeros(n, dtype=bool)
    regions = []
    for sd in np.argsort(curv, kind="stable"):
        sd = int(sd)
        if claimed[sd]:
            continue
        claimed[sd] = True
        reg = [sd]
        front = [sd]
        level = {sd: 0}
        fh = 0
        st = {"pops": 0, "tests": 0, "fail_curv": 0, "fail_angle": 0,
              "skip_self": 0, "skip_claimed": 0, "joined": 0}
        depth = 0
        while fh < len(front):
            cf = front[fh]
            fh += 1
            st["pops"] += 1
            _, nbrs = tree.query(pts[cf], k=kq)
            cur_n = nu[cf]
            for cand in np.atleast_1d(nbrs):
                cand = int(cand)
                if cand == cf:
                    st["skip_self"] += 1
                    continue
                if claimed[cand]:
                    st["skip_claimed"] += 1
                    continue
                st["tests"] += 1
                if curv[cand] >= kappa:
                    st["fail_curv"] += 1
                    continue
                if R234.angle_deg(cur_n, nu[cand]) > theta_deg:
                    st["fail_angle"] += 1
                    continue
                claimed[cand] = True
                st["joined"] += 1
                reg.append(cand)
                front.append(cand)
                lv = level[cf] + 1
                level[cand] = lv
                if lv > depth:
                    depth = lv
        st.update({"size": len(reg), "seed": sd, "seed_curv": float(curv[sd]),
                   "max_depth": depth, "members": np.asarray(reg, dtype=np.int64)})
        regions.append(st)
    return regions, nu


def mesh_angles_all(pts, nrm, verts, vnorm, tree):
    """Per-point folded angle (deg) between the cloud normal and the nearest mesh vertex
    normal -- analyse30.mesh_floor's arithmetic, returned per point."""
    _d, idx = tree.query(pts, k=1, workers=-1)
    a = R.normalised_f32(np.asarray(nrm, dtype=np.float32))
    b = R.normalised_f32(vnorm[idx])
    dot = (a[:, 0] * b[:, 0] + a[:, 1] * b[:, 1] + a[:, 2] * b[:, 2]).astype(np.float32)
    dot = np.where(dot < -1.0, np.float32(-1.0), dot).astype(np.float32)
    dot = np.where(dot > 1.0, np.float32(1.0), dot).astype(np.float32)
    return np.degrees(np.arccos(np.abs(dot).astype(np.float64)))


def load_cell(arm, piece, dataset, corpus, outdir, dump):
    if arm == "J":
        n = int(piece)
        p = PA.jug_paths(dataset, n)
        cl = io32.read_pcd(p["pcd"])
        mesh = p["objs"][0]
        ac = os.path.join(outdir, "cells", "A_J_%d.json" % n)
        if os.path.isfile(ac):
            with open(ac) as f:
                mesh = json.load(f).get("obj_chosen") or mesh
        return {"xyz": cl["xyz"], "nrm": cl["nrm"], "name": "Juglet_Piece_%d" % n,
                "src": p["pcd"], "md5": cl["md5"], "mesh": mesh}
    if arm == "PA_025":
        gp = os.path.join(outdir, "geom", "pa025", "Pot_A_Piece_%02d_025.npz" % int(piece))
        z = np.load(gp, allow_pickle=False)
        return {"xyz": np.asarray(z["xyz"], dtype=np.float64),
                "nrm": np.asarray(z["nrm"], dtype=np.float64),
                "name": "Pot_A_Piece_%02d" % int(piece), "src": gp,
                "md5": str(z["src_md5"]),
                "mesh": PA.pa_paths(corpus, int(piece))["obj"]}
    if arm in ("B", "E"):
        n = int(piece)
        nm = "Juglet_Piece_%d" % n
        ply = os.path.join(dump, arm, nm, "r2_clusters_premerge.ply")
        if not os.path.isfile(ply):
            raise SystemExit("[D32] missing rung-2 dump %s" % ply)
        xyz, nrm, _cid, _rsn, _pr = R234.read_rung2_ply(ply)
        mesh = PA.jug_paths(dataset, n)["objs"][0]
        ac = os.path.join(outdir, "cells", "A_J_%d.json" % n)
        if os.path.isfile(ac):
            with open(ac) as f:
                mesh = json.load(f).get("obj_chosen") or mesh
        return {"xyz": xyz.astype(np.float64), "nrm": nrm.astype(np.float64),
                "name": nm, "src": ply, "md5": io32.md5_file(ply), "mesh": mesh}
    if arm == "PA":
        ply = os.path.join(dump, "PA", "Pot_A_Piece_07", "r2_clusters_premerge.ply")
        if not os.path.isfile(ply):
            raise SystemExit("[D32] missing rung-2 dump %s" % ply)
        xyz, nrm, _cid, _rsn, _pr = R234.read_rung2_ply(ply)
        return {"xyz": xyz.astype(np.float64), "nrm": nrm.astype(np.float64),
                "name": "Pot_A_Piece_07", "src": ply, "md5": io32.md5_file(ply),
                "mesh": PA.pa_paths(corpus, 7)["obj"]}
    raise SystemExit("[D32] unknown arm %r" % arm)


def cell(arm, piece, dataset, corpus, outdir, dump):
    c = load_cell(arm, piece, dataset, corpus, outdir, dump)
    xyz = np.ascontiguousarray(c["xyz"], dtype=np.float64)
    nrm = np.ascontiguousarray(c["nrm"], dtype=np.float64)
    n = int(xyz.shape[0])
    curv_k = max(10, min(50, n // 300))
    curv = R234.pcl_curvature(xyz, curv_k)
    regions, nu = grow_members(xyz, nrm, curv, NB, THETA, KAPPA)
    sizes = sorted((r["size"] for r in regions), reverse=True)
    fail_angle = int(sum(r["fail_angle"] for r in regions))
    fail_curv = int(sum(r["fail_curv"] for r in regions))
    largest = max(regions, key=lambda r: r["size"]) if regions else None
    m = A30.read_obj_normals(c["mesh"])
    mtree = cKDTree(m[0])
    ang_mesh = mesh_angles_all(xyz, nrm, m[0], m[1], mtree)
    rec = {"cell": "D_%s_%s" % (arm, piece), "arm": arm, "piece": c["name"],
           "src": c["src"], "md5": c["md5"], "mesh": c["mesh"],
           "mesh_md5": io32.md5_file(c["mesh"]), "n_points": n,
           "curv_k": int(curv_k), "theta_deg": THETA, "kappa": KAPPA, "nb": NB,
           "regions_before_floor": len(regions),
           "regions_per_point": len(regions) / float(n),
           "total_claimed": int(sum(sizes)),
           "largest_size": int(largest["size"]) if largest else None,
           "largest_frac_of_cloud": (largest["size"] / float(n)) if largest else None,
           "largest_depth": int(largest["max_depth"]) if largest else None,
           "n_ge_50": int(sum(1 for s in sizes if s >= 50)),
           "fail_angle_total": fail_angle, "fail_angle_per_point": fail_angle / float(n),
           "fail_curv_total": fail_curv, "n_zero_normals": int(
               np.count_nonzero(np.isnan(nu[:, 0]))),
           "sizes_head": sizes[:20], "floors": {}}
    for fl in FLOORS:
        surv = [r for r in regions if r["size"] >= fl]
        big = max(surv, key=lambda r: r["size"]) if surv else None
        row = {"floor": fl, "n_survive": len(surv),
               "largest_size": int(big["size"]) if big else None,
               "largest_frac_of_cloud": (big["size"] / float(n)) if big else None}
        if big is not None:
            mem = big["members"]
            mp = xyz[mem]
            dd, _ = cKDTree(mp).query(xyz, k=1, workers=-1)
            sides = io32.bbox_sides(mp)
            am = ang_mesh[mem]
            am = am[np.isfinite(am)]
            row.update({"extent_mm": float(np.linalg.norm(sides)),
                        "bbox_sides_mm": [float(x) for x in sides],
                        "coverage_2mm": float(np.mean(dd <= COVER_MM)),
                        "median_mesh_angle_deg": float(np.median(am)) if am.size else None,
                        "seed": int(big["seed"]), "depth": int(big["max_depth"])})
        rec["floors"]["%d" % fl] = row
        print("[D32] %s %s floor=%d survive=%d big=%s extent=%s cover=%s ang=%s"
              % (arm, c["name"], fl, row["n_survive"], row["largest_size"],
                 row.get("extent_mm"), row.get("coverage_2mm"),
                 row.get("median_mesh_angle_deg")))
        sys.stdout.flush()
    key = (arm, c["name"])
    if key in ANCHOR:
        a = ANCHOR[key]
        ok = True
        detail = {}
        if "regions" in a:
            detail["regions"] = [a["regions"], len(regions)]
            ok = ok and a["regions"] == len(regions)
        if "largest" in a:
            detail["largest"] = [a["largest"], int(largest["size"])]
            ok = ok and a["largest"] == int(largest["size"])
        if "fail_angle" in a:
            detail["fail_angle"] = [a["fail_angle"], fail_angle]
            ok = ok and a["fail_angle"] == fail_angle
        if "survivors_50" in a:
            got = sorted((r["size"] for r in regions if r["size"] >= 50),
                         reverse=True)
            detail["survivors_50"] = [a["survivors_50"], got]
            ok = ok and a["survivors_50"] == got
        rec["anchor"] = {"expected": a, "got": detail,
                         "verdict": "MATCH" if ok else "MISMATCH"}
        print("[D32] ANCHOR %s %s -> %s %s" % (arm, c["name"], rec["anchor"]["verdict"],
                                               json.dumps(detail)))
        sys.stdout.flush()
    elif arm == "E" and c["name"] in E_ROWS:
        e = E_ROWS[c["name"]]
        rec["e_row"] = {"expected": e, "got": {"npts": n, "regions": len(regions),
                                               "largest": int(largest["size"])}}
        print("[D32] E-ROW %s %s expected %s got %s"
              % (arm, c["name"], json.dumps(e), json.dumps(rec["e_row"]["got"])))
        sys.stdout.flush()
    d = os.path.join(outdir, "cells")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "D_%s_%s.json" % (arm, piece))
    with open(p, "w") as f:
        json.dump(rec, f, indent=1, sort_keys=True)
    print("[D32] wrote %s" % p)
    sys.stdout.flush()
    return rec


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True)
    ap.add_argument("--piece", required=True)
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--dump", default="")
    a = ap.parse_args(argv)
    cell(a.arm, a.piece, a.dataset, a.corpus, a.outdir, a.dump)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
