#!/usr/bin/env python3
"""cover_cloud46.py — ticket 46's cloud-maker: an EVEN COVERING of a shipped mesh.

One Juglet piece per invocation. The mesh's own triangles are sampled on the surface at the
spacing the run already resolves (ticket 22's S) — mesh38.sample_at, level 1, NO subdivision —
and written as an ASCII PCD with normals, the layout the pipeline reads natively. The shipped
cloud is a dump of the mesh VERTEX list; this is a covering of the mesh SURFACE. Nothing else
changes: same mesh, same axis, same binary, no environment.

Gates (all mechanical, exit non-zero on failure, every number in the json):
  spacing  |achieved median - S| / S <= 1 pct            ticket 46 deliverable (1)
  surface  every sampled point <= 1e-3 mm from the mesh  ticket 46 deliverable (1)
           exact per-triangle distance over EVERY triangle (mesh38.dist_to_mesh_all), not the
           k-vertex shortcut: the Juglet meshes are long thin triangles, the shortcut can miss
           a sliver interior.
  record   shipped cloud points, covering points, ratio, md5, "no subdivision used".

Usage: python3 cover_cloud46.py --mesh M.obj --shipped-cloud C.pcd --spacing S \
           --piece Juglet_Piece_2 --out out.pcd --json rec.json [--seed 3801] [--jitter 0.10]
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mesh38  # noqa: E402


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def count_pcd_points(path):
    with open(path, "r", errors="replace") as f:
        for line in f:
            if line.startswith("POINTS"):
                return int(line.split()[1])
            if line.startswith("DATA"):
                break
    return -1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mesh", required=True)
    ap.add_argument("--shipped-cloud", default="", dest="shipped_cloud")
    ap.add_argument("--spacing", type=float, required=True)
    ap.add_argument("--piece", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--json", required=True)
    ap.add_argument("--seed", type=int, default=3801)
    ap.add_argument("--jitter", type=float, default=0.10)
    ap.add_argument("--spacing-tol", type=float, default=0.01, dest="spacing_tol")
    ap.add_argument("--surface-tol-mm", type=float, default=1e-3, dest="surface_tol_mm")
    a = ap.parse_args()

    v, fc = mesh38.read_obj(a.mesh)   # read_obj returns (verts, faces) only
    res = mesh38.sample_at(v, fc, a.spacing, seed=a.seed, jitter=a.jitter)
    pts, nrm = res["pts"], res["nrm"]
    mesh38.write_pcd(a.out, pts, nrm)

    achieved = res["sp"]["median"]
    sp_err = abs(achieved - a.spacing) / a.spacing
    d = mesh38.dist_to_mesh_all(pts, v, fc)
    cover = mesh38.covering_stats(v, fc, pts, a.spacing, seed=a.seed)

    shipped_points = count_pcd_points(a.shipped_cloud) if a.shipped_cloud else -1
    gate_sp = "PASS" if sp_err <= a.spacing_tol else "FAIL"
    gate_surf = "PASS" if float(np.max(d)) <= a.surface_tol_mm else "FAIL"
    gate = "PASS" if gate_sp == "PASS" and gate_surf == "PASS" else "FAIL"

    rec = {"piece": a.piece, "mesh": a.mesh, "mesh_md5": md5(a.mesh),
           "mesh_vertices": int(len(v)), "mesh_triangles": int(len(fc)),
           "shipped_cloud": a.shipped_cloud, "shipped_points": shipped_points,
           "out": a.out, "covering_md5": md5(a.out), "covering_points": int(len(pts)),
           "covering_over_shipped": (round(len(pts) / shipped_points, 3) if shipped_points > 0 else None),
           "spacing_requested_mm": a.spacing, "spacing_achieved_median_mm": achieved,
           "spacing_p10_mm": res["sp"]["p10"], "spacing_p90_mm": res["sp"]["p90"],
           "spacing_error_pct": round(100.0 * sp_err, 4),
           "ratio_achieved_over_requested": res["ratio_achieved_over_requested"],
           "voxel_mm": res["voxel_mm"], "iterations": res["iterations"],
           "gen_pitch_mm": res["gen_pitch_mm"], "gen_points": res["gen_points"],
           "gen_capped": bool(res["gen_capped"]),
           "area_mm2": res["area_mm2"],
           "points_per_mm2": round(len(pts) / res["area_mm2"], 4),
           "dist_to_mesh_median_mm": round(float(np.median(d)), 6),
           "dist_to_mesh_p99_mm": round(float(np.percentile(d, 99)), 6),
           "dist_to_mesh_max_mm": round(float(np.max(d)), 6),
           "cover_median_mm": cover["cover_median_mm"],
           "cover_p90_mm": cover["cover_p90_mm"], "cover_p99_mm": cover["cover_p99_mm"],
           "cover_max_mm": cover["cover_max_mm"],
           "cover_median_over_spacing": cover["cover_median_over_spacing"],
           "gate_spacing": gate_sp, "gate_surface": gate_surf, "gate": gate,
           "subdivision": "no subdivision used (level 1, mesh38.sample_at on the shipped triangles)",
           "seed": a.seed, "jitter": a.jitter,
           "tri_stats": {k: val for k, val in mesh38._tri_stats(v, fc).items()}}
    with open(a.json, "w") as f:
        json.dump(rec, f, indent=1, sort_keys=True)
    print("[COVER46] %s points %d (shipped %d) S=%.6f achieved=%.6f err=%.3f%% "
          "maxdist=%.6fmm gate=%s" % (a.piece, len(pts), shipped_points, a.spacing,
                                      achieved, 100 * sp_err, float(np.max(d)), gate))
    return 0 if gate == "PASS" else 4


if __name__ == "__main__":
    sys.exit(main())
