#!/usr/bin/env python3
"""cover_cloud46.py — ticket 46's cloud-maker: an EVEN COVERING of a shipped mesh.

One Juglet piece per invocation. The mesh's own triangles are sampled on the surface at the
spacing the run already resolves (ticket 22's S) — mesh38.sample_at, level 1, NO subdivision —
and written as an ASCII PCD with normals, the layout the pipeline reads natively. The shipped
cloud is a dump of the mesh VERTEX list; this is a covering of the mesh SURFACE. Nothing else
changes: same mesh, same axis, same binary, no environment.

Gates (all mechanical, exit non-zero on failure, every number in the json):
  spacing  |achieved median - S| / S <= 1 pct            ticket 46 deliverable (1)
  surface  every checked point <= 1e-3 mm from the mesh  ticket 46 deliverable (1)
           the covering is PROJECTED onto the mesh after the voxel merge, so every point of the
           written cloud lies on a triangle; the gate measures that on the subsample below.
           exact per-triangle distance over EVERY triangle (mesh38.dist_to_mesh_all), not the
           k-vertex shortcut: the Juglet meshes are long thin triangles, the shortcut can miss
           a sliver interior.  Checked on a deterministic subsample (--surface-check-points,
           default 1000): the same exact test on all 20-30k covering points costs 10+ minutes a
           piece and the run has 9 pieces to cover.  The record says how many points were
           checked, so the claim never outruns the test.
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


def _closest_on_triangle(P, A, B, C):
    """Closest point on each triangle for each point (Ericson, vectorised, exact)."""
    AB = B - A; AC = C - A; AP = P - A
    BP = P - B; CP = P - C
    d1 = np.einsum("ij,ij->i", AB, AP); d2 = np.einsum("ij,ij->i", AC, AP)
    d3 = np.einsum("ij,ij->i", AB, BP); d4 = np.einsum("ij,ij->i", AC, BP)
    d5 = np.einsum("ij,ij->i", AB, CP); d6 = np.einsum("ij,ij->i", AC, CP)
    va = d3 * d6 - d5 * d4
    vb = d5 * d2 - d1 * d6
    vc = d1 * d4 - d3 * d2
    den = va + vb + vc
    safe = np.where(np.abs(den) < 1e-30, 1.0, den)
    v = vb / safe; w = vc / safe
    out = A + AB * v[:, None] + AC * w[:, None]
    m = (d1 <= 0) & (d2 <= 0); out[m] = A[m]
    m = (d3 >= 0) & (d4 <= d3); out[m] = B[m]
    m = (d6 >= 0) & (d5 <= d6); out[m] = C[m]
    m = (vc <= 0) & (d1 >= 0) & (d3 <= 0)
    if m.any():
        tt = d1[m] / np.where(np.abs(d1[m] - d3[m]) < 1e-30, 1.0, d1[m] - d3[m])
        out[m] = A[m] + AB[m] * tt[:, None]
    m = (vb <= 0) & (d2 >= 0) & (d6 <= 0)
    if m.any():
        tt = d2[m] / np.where(np.abs(d2[m] - d6[m]) < 1e-30, 1.0, d2[m] - d6[m])
        out[m] = A[m] + AC[m] * tt[:, None]
    m = (va <= 0) & ((d4 - d3) >= 0) & ((d5 - d6) >= 0)
    if m.any():
        num = d4[m] - d3[m]; den2 = num + (d5[m] - d6[m])
        tt = num / np.where(np.abs(den2) < 1e-30, 1.0, den2)
        out[m] = B[m] + (C[m] - B[m]) * tt[:, None]
    return out


def project_to_mesh(v, fc, pts, k=16):
    """Move every covering point onto the shipped mesh surface.

    The voxel merge that fixes the covering's spacing averages the generated points inside a
    voxel, so a merged point sits slightly inside the surface at a crease (0.03-0.11 mm,
    measured on the first attempt). Projecting the merged point back onto a nearby triangle
    makes every point lie exactly ON the shipped mesh -- which is what "an even covering of the
    mesh" means -- while moving it by less than half the spacing. Candidate triangles are the k
    nearest by centroid; a point on any candidate is on the surface, so the guarantee is exact
    even where the k nearest miss the global nearest.
    """
    from scipy.spatial import cKDTree
    A = v[fc[:, 0]]; B = v[fc[:, 1]]; C = v[fc[:, 2]]
    cen = (A + B + C) / 3.0
    kk = int(min(k, len(fc)))
    _, idx = cKDTree(cen).query(pts, k=kk)
    idx = np.atleast_2d(idx.reshape(len(pts), -1))
    best = np.full(len(pts), np.inf)
    out = pts.copy()
    for j in range(idx.shape[1]):
        cand = _closest_on_triangle(pts, A[idx[:, j]], B[idx[:, j]], C[idx[:, j]])
        dd = np.einsum("ij,ij->i", cand - pts, cand - pts)
        better = dd < best
        best[better] = dd[better]
        out[better] = cand[better]
    return out, float(np.sqrt(np.max(best)))


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
    ap.add_argument("--surface-check-points", type=int, default=1000, dest="surface_check_points")
    a = ap.parse_args()

    v, fc = mesh38.read_obj(a.mesh)   # read_obj returns (verts, faces) only
    # The spacing the covering finally HAS is the one measured after projection, so that is what
    # the gate reads. Projection pulls points onto the surface and shuffles them a little
    # (0.2-1.6 pct on the pieces seen so far), so when the post-projection spacing leaves the band
    # the sampler is asked again at the corrected spacing -- the request is solved, not rounded.
    res = mesh38.sample_at(v, fc, a.spacing, seed=a.seed, jitter=a.jitter)
    pts, moved = project_to_mesh(v, fc, res["pts"])
    nrm = res["nrm"]
    sp = mesh38.nn_spacing(pts)
    achieved = float(sp["median"])
    attempts = [{"ask_mm": a.spacing, "achieved_after_projection_mm": round(achieved, 6),
                 "points": int(len(pts)), "max_move_mm": round(moved, 6)}]
    for _ in range(2):
        err0 = abs(achieved - a.spacing) / a.spacing
        if err0 <= a.spacing_tol:
            break
        ask = a.spacing * (a.spacing / achieved)
        print("[COVER46] %s post-projection spacing %.6f is %.3f%% off; re-solving at %.6f"
              % (a.piece, achieved, 100.0 * err0, ask), flush=True)
        res = mesh38.sample_at(v, fc, ask, seed=a.seed, jitter=a.jitter)
        pts, moved = project_to_mesh(v, fc, res["pts"])
        nrm = res["nrm"]
        sp = mesh38.nn_spacing(pts)
        achieved = float(sp["median"])
        attempts.append({"ask_mm": round(ask, 6), "achieved_after_projection_mm": round(achieved, 6),
                         "points": int(len(pts)), "max_move_mm": round(moved, 6)})
    mesh38.write_pcd(a.out, pts, nrm)
    print("[COVER46] %s %d points on the mesh (largest move %.6f mm, %d attempts)"
          % (a.piece, len(pts), moved, len(attempts)), flush=True)
    sp_err = abs(achieved - a.spacing) / a.spacing
    print("[COVER46] %s sampled %d points at S=%.6f (achieved %.6f, %d triangles)"
          % (a.piece, len(pts), a.spacing, achieved, len(fc)), flush=True)

    nchk = int(min(len(pts), max(1, a.surface_check_points)))
    sidx = np.arange(len(pts))
    if nchk < len(pts):
        sidx = np.sort(np.random.RandomState(a.seed).choice(len(pts), nchk, replace=False))
    print("[COVER46] %s exact distance to every triangle on %d of %d points"
          % (a.piece, nchk, len(pts)), flush=True)
    d = mesh38.dist_to_mesh_all(pts[sidx], v, fc)
    print("[COVER46] %s distance max %.6f mm" % (a.piece, float(np.max(d))), flush=True)
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
           "spacing_p10_mm": sp["p10"], "spacing_p90_mm": sp["p90"],
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
           "surface_check_points": nchk,
           "surface_check": "exact distance to every triangle on a deterministic subsample (seed %d)" % a.seed,
           "projection": "voxel-merged covering projected onto the closest point of a nearby triangle (k=16 by centroid); every point lies on the shipped mesh",
           "project_max_move_mm": round(moved, 6),
           "spacing_attempts": attempts,
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
          "maxdist=%.6fmm on %d points gate=%s" % (a.piece, len(pts), shipped_points, a.spacing,
                                                   achieved, 100 * sp_err, float(np.max(d)), nchk, gate))
    return 0 if gate == "PASS" else 4


if __name__ == "__main__":
    sys.exit(main())
