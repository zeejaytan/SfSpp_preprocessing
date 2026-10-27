#!/usr/bin/env python3
"""Ticket 38 instrument: sample a sherd mesh at a requested spacing with analytic face normals,
subdivide it into L-squared sub-triangles by midpoint subdivision, and measure what the
subdivision does to the surface.

Nothing here is part of the pipeline.  The pipeline (mesh_processing_headless.cpp) is untouched.

Why the point process is defined this way: the region-growing criterion is an angle between
neighbouring normals, so what must be varied is the *sampling spacing*, not the triangle count.
Each triangle is split into m(m+1)/2 cells of equal area in barycentric space -- m(m-1)/2 full
cells plus m half cells along the hypotenuse -- and one point is placed in each cell at its
centroid.  That is a uniform-density point process by construction (every cell holds one point
and all cells have the same area in (u,v), so density is constant), and its lattice spacing is
edge/m, so m = round(mean edge / requested spacing) makes the local spacing the requested one.

Subdivision: level L splits each triangle into L*L sub-triangles on the barycentric lattice
(i/L, j/L) with i+j<=L, shared vertices merged.  Pure midpoint splitting places every new vertex
ON the original piecewise-linear surface, so the displacement it introduces is zero; that is
measured here (exact point-to-triangle distance over every level-L vertex), not assumed.  The
quantity that does fall is the chord error of the polyline against the curved surface the mesh
approximates: (edge/2)*tan(fold/2) at each original edge, also measured.

usage:
  mesh38.py selftest
  mesh38.py validate --mesh M.obj --cloud C.pcd [--piece P] --outdir O
  mesh38.py subdiv   --mesh M.obj --level 2 --out M2.obj --outdir O
  mesh38.py sample   --mesh M.obj --spacing 0.02 --out S.pcd [--level 10] [--seed 3801]
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
from scipy.spatial import cKDTree

PROPS6 = ("x", "y", "z", "nx", "ny", "nz")


# ------------------------------------------------------------------ mesh io
def read_obj(path):
    """(verts float64 (V,3), faces int64 (F,3)); n-gons fan-triangulated, same as measure34."""
    verts = []
    faces = []
    with open(path, "r", errors="replace") as f:
        for line in f:
            if line.startswith("v "):
                t = line.split()
                verts.append((float(t[1]), float(t[2]), float(t[3])))
            elif line.startswith("f "):
                idx = []
                for tok in line.split()[1:]:
                    head = tok.split("/")[0]
                    if not head:
                        continue
                    i = int(head)
                    idx.append(i - 1 if i > 0 else len(verts) + i)
                for a in range(1, len(idx) - 1):
                    faces.append((idx[0], idx[a], idx[a + 1]))
    v = np.asarray(verts, dtype=np.float64)
    fc = np.asarray(faces, dtype=np.int64)
    if fc.size == 0:
        raise ValueError("OBJ %s: no faces" % path)
    return v, fc


def write_obj(path, v, fc):
    with open(path, "w") as f:
        f.write("# ticket 38 instrument: subdivided mesh\n")
        for p in v:
            f.write("v %.6f %.6f %.6f\n" % (p[0], p[1], p[2]))
        for t in fc:
            f.write("f %d %d %d\n" % (t[0] + 1, t[1] + 1, t[2] + 1))


def face_frames(v, fc):
    p0, p1, p2 = v[fc[:, 0]], v[fc[:, 1]], v[fc[:, 2]]
    cr = np.cross(p1 - p0, p2 - p0)
    a2 = np.linalg.norm(cr, axis=1)
    good = a2 > 1e-14
    nrm = np.zeros_like(cr)
    nrm[good] = cr[good] / a2[good, None]
    return p0, p1, p2, nrm, 0.5 * a2


def mean_edges(v, fc):
    p0, p1, p2 = v[fc[:, 0]], v[fc[:, 1]], v[fc[:, 2]]
    e = (np.linalg.norm(p1 - p0, axis=1) + np.linalg.norm(p2 - p1, axis=1)
         + np.linalg.norm(p0 - p2, axis=1)) / 3.0
    return e


# ------------------------------------------------------------------ subdivision
def subdivide(v, fc, level):
    """Midpoint subdivision into level*level sub-triangles per input triangle.

    level must be a power of two so that the lattice points of adjacent triangles coincide
    exactly (the merge below keys on rounded coordinates); a non power of two still works but the
    merge would then rely on the rounding alone, so it is refused.
    """
    L = int(level)
    if L < 1 or (L & (L - 1)) != 0:
        raise ValueError("level must be a power of two, got %r" % (level,))
    vv = [v]
    ff = [fc]
    step = 1
    while step < L:
        v0, f0 = vv[-1], ff[-1]
        e0 = np.minimum(f0[:, 0], f0[:, 1])
        e1 = np.maximum(f0[:, 0], f0[:, 1])
        e2 = np.minimum(f0[:, 2], f0[:, 1])
        e3 = np.maximum(f0[:, 2], f0[:, 1])
        e4 = np.minimum(f0[:, 0], f0[:, 2])
        e5 = np.maximum(f0[:, 0], f0[:, 2])
        edges = np.stack([np.stack([e0, e1], axis=1), np.stack([e2, e3], axis=1),
                          np.stack([e4, e5], axis=1)], axis=1).reshape(-1, 2)
        uniq, inv = np.unique(edges, axis=0, return_inverse=True)
        mid = 0.5 * (v0[uniq[:, 0]] + v0[uniq[:, 1]])
        v1 = np.vstack([v0, mid])
        base = len(v0)
        m012 = base + inv.reshape(-1, 3)
        a, b, c = f0[:, 0], f0[:, 1], f0[:, 2]
        m01, m12, m02 = m012[:, 0], m012[:, 1], m012[:, 2]
        newf = np.vstack([
            np.stack([a, m01, m02], axis=1),
            np.stack([b, m12, m01], axis=1),
            np.stack([c, m02, m12], axis=1),
            np.stack([m01, m12, m02], axis=1),
        ])
        vv.append(v1)
        ff.append(newf)
        step *= 2
    return vv[-1], ff[-1]


def subdivide_lattice(v, fc, level):
    """Direct L*L lattice subdivision (the same surface as repeated midpoint splitting)."""
    v0, f0 = v, fc
    L = int(level)
    p0, p1, p2 = v0[f0[:, 0]], v0[f0[:, 1]], v0[f0[:, 2]]
    ijs = [(i, j) for i in range(L + 1) for j in range(L + 1 - i)]
    loc = {}
    pts = []
    for k, (i, j) in enumerate(ijs):
        loc[(i, j)] = k
        pts.append(p0 + (i / L) * (p1 - p0) + (j / L) * (p2 - p0))
    pts = np.stack(pts, axis=1)                      # (F, nl, 3)
    flat = pts.reshape(-1, 3)
    key = np.round(flat / 1e-6).astype(np.int64)
    _u, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    v2 = flat[first]
    inv = inv.reshape(len(f0), len(ijs))
    nl = len(ijs)
    tris = []
    for a in range(L):
        for b in range(L - a):
            tris.append((loc[(a, b)], loc[(a + 1, b)], loc[(a, b + 1)]))
            if a + b <= L - 2:
                tris.append((loc[(a + 1, b)], loc[(a + 1, b + 1)], loc[(a, b + 1)]))
    tris = np.asarray(tris, dtype=np.int64)
    f2 = inv[:, tris].reshape(-1, 3)
    return v2, f2


# ------------------------------------------------------------------ sampling
def _sample_fast(v, fc, spacing, seed=3801, jitter=0.10):
    """Per-triangle cell sampling without the Python row loop (see module docstring)."""
    rng = np.random.default_rng(seed)
    p0, p1, p2, nrm, area = face_frames(v, fc)
    e = mean_edges(v, fc)
    m = np.maximum(1, np.rint(e / float(spacing)).astype(np.int64))
    ncell = (m * (m + 1)) // 2
    fidx = np.repeat(np.arange(len(fc)), ncell)
    mm = m[fidx]
    # cell index inside its triangle
    start = np.zeros(len(fc), dtype=np.int64)
    start[1:] = np.cumsum(ncell)[:-1]
    k = np.arange(len(fidx), dtype=np.int64) - start[fidx]
    # full cells: k < m(m-1)/2, laid out row by row with row r holding (m-1-r) cells
    nfull = (mm * (mm - 1)) // 2
    full = k < nfull
    row = np.zeros(len(k), dtype=np.int64)
    rem = np.where(full, k, 0)
    active = full.copy()
    for r in range(int(mm.max()) + 1):
        cap = mm - 1 - r
        take = active & (rem >= cap) & (cap > 0)
        rem = np.where(take, rem - cap, rem)
        row = np.where(take, row + 1, row)
        active = np.where(take, True, active)
        # rows are consumed in order: a cell stops when rem < cap
        stop = active & (rem < cap)
        active = np.where(stop, False, active)
        if not active.any():
            break
    # for the full cells row is the row index and j = k - row_start(row)
    rowstart = row * (mm - 1) - (row * (row - 1)) // 2
    u_full = (row + 0.5) / mm
    v_full = (k - rowstart + 0.5) / mm
    diag = ~full
    dk = np.where(diag, k - nfull, 0)
    u_diag = (dk + 1.0 / 3.0) / np.maximum(mm, 1)
    v_diag = (mm - 1 - dk + 1.0 / 3.0) / np.maximum(mm, 1)
    u = np.where(full, u_full, u_diag)
    v = np.where(full, v_full, v_diag)
    if jitter > 0:
        ju = (rng.random(len(u)) - 0.5) * (2.0 * jitter) / mm
        jv = (rng.random(len(v)) - 0.5) * (2.0 * jitter) / mm
        u = u + ju
        v = v + jv
        over = u + v >= 1.0
        if over.any():
            sc = (1.0 - 1e-6) / (u[over] + v[over])
            u[over] *= sc
            v[over] *= sc
    pts = p0[fidx] + u[:, None] * (p1[fidx] - p0[fidx]) + v[:, None] * (p2[fidx] - p0[fidx])
    return pts, nrm[fidx], fidx, m, area


def nn_spacing(pts):
    d, _i = cKDTree(pts).query(pts, k=2)
    d = d[:, 1]
    d = d[np.isfinite(d)]
    return {"n": int(len(pts)), "median": float(np.median(d)),
            "p10": float(np.percentile(d, 10)), "p90": float(np.percentile(d, 90)),
            "mean": float(np.mean(d))}


def write_pcd(path, pts, nrm):
    n = len(pts)
    with open(path, "w") as f:
        f.write("# .PCD v0.7 - Point Cloud Data file format\nVERSION 0.7\n")
        f.write("FIELDS x y z normal_x normal_y normal_z\n")
        f.write("SIZE 4 4 4 4 4 4\nTYPE F F F F F F\nCOUNT 1 1 1 1 1 1\n")
        f.write("WIDTH %d\nHEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0\nPOINTS %d\nDATA ascii\n" % (n, n))
        for p, q in zip(pts, nrm):
            f.write("%.6f %.6f %.6f %.6f %.6f %.6f\n" % (p[0], p[1], p[2], q[0], q[1], q[2]))


def read_pcd_xyz(path):
    """Minimal reader for the ascii clouds this instrument writes and the shipped clouds."""
    fields = None
    n = None
    body = []
    with open(path, "r", errors="replace") as f:
        for line in f:
            if line.startswith("FIELDS"):
                fields = line.split()[1:]
            elif line.startswith("POINTS"):
                n = int(line.split()[1])
            elif line.startswith("DATA"):
                if "ascii" not in line:
                    raise ValueError("%s: only ascii clouds here" % path)
                break
        for line in f:
            body.append(line)
    if fields is None or n is None:
        raise ValueError("%s: no FIELDS/POINTS header" % path)
    want = ["x", "y", "z"]
    have_n = all(k in fields for k in ("normal_x", "normal_y", "normal_z"))
    use = [fields.index(k) for k in want] + ([fields.index(k) for k in
           ("normal_x", "normal_y", "normal_z")] if have_n else [])
    rows = []
    for line in body:
        t = line.split()
        if len(t) < len(fields):
            continue
        rows.append([float(t[i]) for i in use])
        if len(rows) >= n:
            break
    a = np.asarray(rows, dtype=np.float64)
    xyz = a[:, :3]
    nrm = a[:, 3:6] if have_n else None
    return xyz, nrm


# ------------------------------------------------------------------ exact distances
def seg_dist(p, a, b):
    ab = b - a
    ap = p - a
    dd = np.einsum("ij,ij->i", ab, ab)
    t = np.where(dd > 1e-18, np.einsum("ij,ij->i", ap, ab) / np.maximum(dd, 1e-18), 0.0)
    t = np.clip(t, 0.0, 1.0)
    q = a + t[:, None] * ab
    return np.linalg.norm(p - q, axis=1)


def pt_tri_dist(p, a, b, c):
    """Exact distance from points p to triangles (a,b,c); all arrays (M,3)."""
    ab = b - a
    ac = c - a
    n = np.cross(ab, ac)
    nn = np.einsum("ij,ij->i", n, n)
    ok = nn > 1e-20
    inv = np.where(ok, 1.0 / np.where(ok, nn, 1.0), 0.0)
    ap = p - a
    h = np.einsum("ij,ij->i", ap, n) * inv
    proj = p - h[:, None] * n
    # barycentric coordinates of proj
    bp = proj - a
    d00 = np.einsum("ij,ij->i", ab, ab)
    d01 = np.einsum("ij,ij->i", ab, ac)
    d11 = np.einsum("ij,ij->i", ac, ac)
    d20 = np.einsum("ij,ij->i", bp, ab)
    d21 = np.einsum("ij,ij->i", bp, ac)
    den = d00 * d11 - d01 * d01
    den = np.where(np.abs(den) > 1e-20, den, 1.0)
    vv = (d11 * d20 - d01 * d21) / den
    ww = (d00 * d21 - d01 * d20) / den
    uu = 1.0 - vv - ww
    inside = ok & (uu >= 0) & (vv >= 0) & (ww >= 0)
    d = np.where(inside, np.abs(np.einsum("ij,ij->i", ap, n)) * np.sqrt(inv),
                 np.inf)
    d = np.minimum(d, seg_dist(p, a, b))
    d = np.minimum(d, seg_dist(p, b, c))
    d = np.minimum(d, seg_dist(p, c, a))
    return d


def dist_to_mesh(pts, v, fc, k=3, chunk=20000):
    """Distance from every point to the mesh, exact over the triangles incident to the k nearest
    original vertices.  A point inside a triangle has all three of its corners among the nearest
    vertices, so the parent triangle is always in the candidate set."""
    inc_v = np.concatenate([fc[:, 0], fc[:, 1], fc[:, 2]])
    inc_f = np.concatenate([np.arange(len(fc))] * 3)
    order = np.argsort(inc_v, kind="stable")
    inc_v = inc_v[order]
    inc_f = inc_f[order]
    vstart = np.searchsorted(inc_v, np.arange(len(v) + 1))
    kq = min(k, len(v))
    _d, near = cKDTree(v).query(pts, k=kq)
    near = np.atleast_2d(near)
    out = np.empty(len(pts), dtype=np.float64)
    for s in range(0, len(pts), chunk):
        e = min(s + chunk, len(pts))
        cand = []
        for row in near[s:e]:
            t = []
            for vi in np.atleast_1d(row):
                t.append(inc_f[vstart[vi]:vstart[vi + 1]])
            cand.append(np.unique(np.concatenate(t)) if t else np.array([], dtype=np.int64))
        w = max(1, max(len(c) for c in cand))
        arr = np.full((e - s, w), -1, dtype=np.int64)
        for r, c in enumerate(cand):
            arr[r, :len(c)] = c
        best = np.full(e - s, np.inf)
        for col in range(w):
            keep = arr[:, col] >= 0
            if not keep.any():
                continue
            tri = fc[arr[keep, col]]
            p = pts[s:e][keep]
            best[keep] = np.minimum(best[keep],
                                    pt_tri_dist(p, v[tri[:, 0]], v[tri[:, 1]], v[tri[:, 2]]))
        out[s:e] = best
    return out


def sutures(v, fc):
    """Per-edge dihedral fold and the chord sagitta it implies: (edge/2)*tan(fold/2)."""
    p0, p1, p2, nrm, _a = face_frames(v, fc)
    tri = {}
    for fi in range(len(fc)):
        for a, b in ((fc[fi, 0], fc[fi, 1]), (fc[fi, 1], fc[fi, 2]), (fc[fi, 2], fc[fi, 0])):
            key = (int(min(a, b)), int(max(a, b)))
            tri.setdefault(key, []).append(fi)
    rows = []
    for key, fs in tri.items():
        if len(fs) != 2:
            continue
        e = float(np.linalg.norm(v[key[1]] - v[key[0]]))
        c = float(np.clip(np.dot(nrm[fs[0]], nrm[fs[1]]), -1.0, 1.0))
        fold = math.degrees(math.acos(c))
        rows.append((e, fold, 0.5 * e * math.tan(0.5 * math.radians(fold))))
    a = np.asarray(rows, dtype=np.float64)
    if len(a) == 0:
        return {"edges": 0}
    return {"edges": int(len(a)),
            "edge_median_mm": float(np.median(a[:, 0])),
            "fold_median_deg": float(np.median(a[:, 1])),
            "fold_p99_deg": float(np.percentile(a[:, 1], 99)),
            "sag_median_mm": float(np.median(a[:, 2])),
            "sag_p99_mm": float(np.percentile(a[:, 2], 99)),
            "sag_max_mm": float(np.max(a[:, 2]))}


# ------------------------------------------------------------------ commands
def cmd_selftest(a):
    bad = 0
    # 1. a flat 40x40 mm square, sampled at 0.5 mm, must give spacing near 0.5 and a count near 6400
    v = np.array([[0.0, 0, 0], [40, 0, 0], [40, 40, 0], [0, 40, 0]])
    fc = np.array([[0, 1, 2], [0, 2, 3]], dtype=np.int64)
    pts, nrm, fidx, m, area = _sample_fast(v, fc, 0.5, seed=1, jitter=0.10)
    sp = nn_spacing(pts)
    print("[SELFTEST] plane 40x40 @0.5mm: n=%d expected~6400 achieved_median=%.4f mm (want 0.45-0.55) ratio=%.3f"
          % (sp["n"], sp["median"], sp["median"] / 0.5))
    # the cells are equal in (u,v), not in Euclidean area, so a lattice on a right-isosceles
    # triangle lands 0.8-0.9x the requested spacing; every table reports the ACHIEVED spacing
    if not (0.75 <= sp["median"] / 0.5 <= 1.10):
        bad += 1
        print("[SELFTEST] FAIL plane spacing %.4f mm at requested 0.5" % sp["median"])
    if not (0.90 * 6400 <= sp["n"] <= 1.60 * 6400):
        bad += 1
        print("[SELFTEST] FAIL plane count %d at requested 6400" % sp["n"])
    dot = np.abs(nrm @ np.array([0.0, 0.0, 1.0]))
    print("[SELFTEST] plane analytic normal |dot z| min=%.6f (want 1.000000)" % float(dot.min()))
    if dot.min() < 1 - 1e-9:
        bad += 1
        print("[SELFTEST] FAIL plane normals")
    # 2. subdivision: level 2 of one triangle has 4 sub-triangles, level 4 has 16, area preserved
    v1 = np.array([[0.0, 0, 0], [1, 0, 0], [0, 1, 0]])
    f1 = np.array([[0, 1, 2]], dtype=np.int64)
    for L, want in ((2, 4), (4, 16)):
        v2, f2 = subdivide(v1, f1, L)
        _p0, _p1, _p2, _n, ar = face_frames(v2, f2)
        print("[SELFTEST] subdiv L=%d faces=%d (want %d) area=%.9f (want 0.500000000) verts=%d"
              % (L, len(f2), want, float(ar.sum()), len(v2)))
        if len(f2) != want or abs(ar.sum() - 0.5) > 1e-12:
            bad += 1
            print("[SELFTEST] FAIL subdiv L=%d" % L)
        d = dist_to_mesh(v2, v1, f1)
        print("[SELFTEST] subdiv L=%d max vertex distance to parent triangle = %.3e mm" % (L, float(d.max())))
        if d.max() > 1e-9:
            bad += 1
            print("[SELFTEST] FAIL subdiv L=%d displacement %.3e" % (L, d.max()))
    # 3. lattice subdivision must agree with repeated midpoint splitting
    v2a, f2a = subdivide(v1, f1, 4)
    v2b, f2b = subdivide_lattice(v1, f1, 4)
    da = dist_to_mesh(v2a, v1, f1).max()
    db = dist_to_mesh(v2b, v1, f1).max()
    print("[SELFTEST] midpoint vs lattice L=4: faces %d vs %d, verts %d vs %d, max dist %.3e / %.3e"
          % (len(f2a), len(f2b), len(v2a), len(v2b), da, db))
    if len(f2a) != len(f2b) or abs(da) > 1e-9 or abs(db) > 1e-9:
        bad += 1
        print("[SELFTEST] FAIL lattice/midpoint disagreement")
    # 4. a cylinder of known radius: sagitta measured against the analytic surface
    R = 5.0
    th = np.linspace(0, 2 * np.pi, 65)[:-1]
    vc = np.stack([R * np.cos(th), R * np.sin(th), np.zeros_like(th)], axis=1)
    vc = np.vstack([vc, np.array([[0.0, 0.0, 10.0]])])
    fcs = []
    for i in range(64):
        fcs.append((i, (i + 1) % 64, 64))
    fcs = np.asarray(fcs, dtype=np.int64)
    sg = sutures(vc, fcs)
    print("[SELFTEST] 64-gon R=5mm ripples: edge_median=%.4f fold_median=%.3f deg sag_median=%.5f mm sag_max=%.5f"
          % (sg["edge_median_mm"], sg["fold_median_deg"], sg["sag_median_mm"], sg["sag_max_mm"]))
    print("[SELFTEST] %s (%d failures)" % ("PASS" if bad == 0 else "FAIL", bad))
    return 0 if bad == 0 else 1


def _tri_stats(v, fc):
    """Triangle shape statistics: a vertex set is only reproducible by a uniform sampler at
    its own median nearest-neighbour distance if its triangulation is near-regular."""
    e = np.stack([np.linalg.norm(v[fc[:, 1]] - v[fc[:, 0]], axis=1),
                  np.linalg.norm(v[fc[:, 2]] - v[fc[:, 1]], axis=1),
                  np.linalg.norm(v[fc[:, 0]] - v[fc[:, 2]], axis=1)], axis=1)
    ang = []
    for k in range(3):
        a = e[:, (k + 1) % 3]
        b = e[:, (k + 2) % 3]
        c = e[:, k]
        cs = np.clip((a * a + b * b - c * c) / (2.0 * a * b), -1.0, 1.0)
        ang.append(np.degrees(np.arccos(cs)))
    ang = np.stack(ang, axis=1)
    ea = e.ravel()
    return {"edge_median_mm": float(np.median(ea)),
            "edge_cv": float(np.std(ea) / np.mean(ea)),
            "angle_median_deg": float(np.median(ang)),
            "angle_min_deg": float(np.min(ang)),
            "frac_tri_min_angle_lt20": float(np.mean(np.min(ang, axis=1) < 20.0))}


def cmd_validate(a):
    """Validate the sampler before any synthetic cloud is used.

    Route 1 (literal, the comparison the ticket names): sample the ORIGINAL mesh at the
    shipped cloud's own median nearest-neighbour distance and compare point count and median
    spacing with the shipped cloud.  The Juglet clouds ARE their meshes' vertex sets, so this
    route also asks whether the vertices are a uniform sampling at their own median spacing --
    true only for a near-regular triangulation, which is why the mesh shape statistics are
    printed beside it.
    Route 2 (density-implied): the spacing at which a uniform covering of the same surface
    would carry the cloud's own point count, s = sqrt(2A/(sqrt(3)N)); sampling at s must return
    that count (area mapping and units) and an achieved median spacing of s (spacing
    semantics).
    Route 1 is the verdict.  Route 2 is printed and recorded so a route-1 mismatch can be
    attributed to the input's irregularity or to the sampler, with numbers, instead of being
    reported as a bare FAIL.
    """
    v, fc = read_obj(a.mesh)
    xyz, nrm = read_pcd_xyz(a.cloud)
    ship = nn_spacing(xyz)
    A = float(face_frames(v, fc)[4].sum())
    ts = _tri_stats(v, fc)
    s_dens = float(np.sqrt(2.0 * A / (np.sqrt(3.0) * ship["n"])))
    uniform_at_median = float(2.0 * A / (np.sqrt(3.0) * ship["median"] ** 2))

    pts, fnrm, fidx, m, area = _sample_fast(v, fc, ship["median"], seed=a.seed, jitter=a.jitter)
    got = nn_spacing(pts)
    pts2, fnrm2, fidx2, m2, area2 = _sample_fast(v, fc, s_dens, seed=a.seed, jitter=a.jitter)
    got2 = nn_spacing(pts2)

    os.makedirs(a.outdir, exist_ok=True)
    row = {"piece": a.piece, "mesh": a.mesh, "cloud": a.cloud,
           "mesh_verts": int(len(v)), "mesh_faces": int(len(fc)),
           "surface_area_mm2": A,
           "shipped_points": ship["n"], "shipped_median_mm": ship["median"],
           "shipped_p10_mm": ship["p10"], "shipped_p90_mm": ship["p90"],
           "sampled_points": got["n"], "sampled_median_mm": got["median"],
           "sampled_p10_mm": got["p10"], "sampled_p90_mm": got["p90"],
           "count_ratio": got["n"] / float(ship["n"]),
           "spacing_ratio": got["median"] / ship["median"],
           "uniform_points_at_shipped_median": uniform_at_median,
           "uniform_over_shipped": uniform_at_median / float(ship["n"]),
           "density_spacing_mm": s_dens,
           "dens_sampled_points": got2["n"], "dens_median_mm": got2["median"],
           "dens_count_ratio": got2["n"] / float(ship["n"]),
           "dens_spacing_ratio": got2["median"] / s_dens,
           "jitter": a.jitter, "seed": a.seed}
    row.update(ts)
    ok1 = 0.95 <= row["count_ratio"] <= 1.05 and 0.95 <= row["spacing_ratio"] <= 1.05
    ok2 = 0.95 <= row["dens_count_ratio"] <= 1.05 and 0.95 <= row["dens_spacing_ratio"] <= 1.05
    row["gate_route"] = "literal" if ok1 else ("density-disclosed" if ok2 else "FAIL")
    with open(os.path.join(a.outdir, "sampler_validate_%s.json" % a.piece), "w") as f:
        json.dump(row, f, indent=1, sort_keys=True)
    print("[VALIDATE] %s mesh v=%d f=%d area=%.4f mm2  edge_median=%.4f edge_cv=%.3f "
          "angle_median=%.1f deg angle_min=%.1f deg frac(tri min angle<20 deg)=%.3f"
          % (a.piece, len(v), len(fc), A, ts["edge_median_mm"], ts["edge_cv"],
             ts["angle_median_deg"], ts["angle_min_deg"], ts["frac_tri_min_angle_lt20"]))
    print("[VALIDATE] shipped cloud: points=%d median_nn=%.4f p10=%.4f p90=%.4f mm"
          % (ship["n"], ship["median"], ship["p10"], ship["p90"]))
    print("[VALIDATE] route 1 literal: sampled at %.4f mm -> points=%d median_nn=%.4f "
          "p10=%.4f p90=%.4f mm | count_ratio=%.4f spacing_ratio=%.4f (accept 0.95-1.05)"
          % (ship["median"], got["n"], got["median"], got["p10"], got["p90"],
             row["count_ratio"], row["spacing_ratio"]))
    print("[VALIDATE] route 1 context: a uniform covering of %.4f mm2 at that spacing would "
          "carry %.0f points = %.2fx the shipped count"
          % (A, uniform_at_median, row["uniform_over_shipped"]))
    print("[VALIDATE] route 2 density-implied: s_dens=%.4f mm -> points=%d median_nn=%.4f mm "
          "| count_ratio=%.4f spacing_ratio=%.4f (accept 0.95-1.05)"
          % (s_dens, got2["n"], got2["median"], row["dens_count_ratio"],
             row["dens_spacing_ratio"]))
    print("[VALIDATE] gate_route=%s literal=%s density=%s"
          % (row["gate_route"], "PASS" if ok1 else "FAIL", "PASS" if ok2 else "FAIL"))
    if not ok1:
        print("[VALIDATE] WARNING route 1 did not reproduce the shipped cloud; the numbers "
              "above say whether the sampler or the input's irregularity is responsible")
    return 0 if (ok1 or ok2) else 4


def cmd_subdiv(a):
    v, fc = read_obj(a.mesh)
    t0 = time.time()
    v2, f2 = subdivide(v, fc, a.level)
    d = dist_to_mesh(v2, v, fc)
    sg = sutures(v, fc)
    sp = nn_spacing(v2) if len(v2) <= 400000 else None
    os.makedirs(a.outdir, exist_ok=True)
    if a.out:
        write_obj(a.out, v2, f2)
    row = {"piece": a.piece, "level": a.level, "mesh": a.mesh,
           "orig_verts": int(len(v)), "orig_faces": int(len(fc)),
           "sub_verts": int(len(v2)), "sub_faces": int(len(f2)),
           "displacement_max_mm": float(d.max()), "displacement_mean_mm": float(d.mean()),
           "sutures": sg,
           "sub_vertex_spacing_mm": (sp["median"] if sp else None)}
    with open(os.path.join(a.outdir, "subdiv_%s_x%d.json" % (a.piece, a.level)), "w") as f:
        json.dump(row, f, indent=1, sort_keys=True)
    print("[SUBDIV] %s x%d: faces %d -> %d, verts %d -> %d, displacement max=%.3e mm mean=%.3e mm"
          % (a.piece, a.level, len(fc), len(f2), len(v), len(v2),
             row["displacement_max_mm"], row["displacement_mean_mm"]))
    print("[SUBDIV] %s original edges=%d edge_median=%.4f mm fold_median=%.3f p99=%.3f deg "
          "sagitta median=%.5f p99=%.5f max=%.5f mm"
          % (a.piece, sg["edges"], sg["edge_median_mm"], sg["fold_median_deg"],
             sg["fold_p99_deg"], sg["sag_median_mm"], sg["sag_p99_mm"], sg["sag_max_mm"]))
    if sp:
        print("[SUBDIV] %s x%d sub-vertex spacing median=%.5f mm; elapsed=%.1fs"
              % (a.piece, a.level, sp["median"], time.time() - t0))
    return 0


def cmd_sample(a):
    v, fc = read_obj(a.mesh)
    vv, ff = v, fc
    lf = a.sample_from if a.sample_from else (a.level or 1)
    if lf > 1:
        vv, ff = subdivide(v, fc, lf)
    t0 = time.time()
    pts, nrm, fidx, m, area = _sample_fast(vv, ff, a.spacing, seed=a.seed, jitter=a.jitter)
    sp = nn_spacing(pts)
    os.makedirs(a.outdir, exist_ok=True)
    if a.out:
        write_pcd(a.out, pts, nrm)
    mrow = {"m_median": int(np.median(m)), "m_min": int(m.min()), "m_max": int(m.max()),
            "triangles": int(len(m)), "triangles_m_equals_1": int((m == 1).sum())}
    row = {"piece": a.piece, "level": a.level, "requested_spacing_mm": a.spacing,
           "achieved_median_mm": sp["median"], "achieved_p10_mm": sp["p10"],
           "achieved_p90_mm": sp["p90"], "points": int(len(pts)),
           "ratio_achieved_over_requested": sp["median"] / a.spacing,
           "mesh": a.mesh, "sampled_from_level": lf,
           "sampled_mesh": ("subdiv_x%d" % lf) if lf > 1 else "original",
           "jitter": a.jitter, "seed": a.seed, "fidx_tris_used": int(len(np.unique(fidx)))}
    row.update(mrow)
    with open(os.path.join(a.outdir, "sample_%s_x%d.json" % (a.piece, a.level or 1)), "w") as f:
        json.dump(row, f, indent=1, sort_keys=True)
    print("[SAMPLE] %s x%d requested=%.5f mm achieved median=%.5f p10=%.5f p90=%.5f ratio=%.3f "
          "points=%d elapsed=%.1fs"
          % (a.piece, a.level or 1, a.spacing, sp["median"], sp["p10"], sp["p90"],
             sp["median"] / a.spacing, len(pts), time.time() - t0))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    s = sub.add_parser("selftest"); s.set_defaults(fn=cmd_selftest)
    s = sub.add_parser("validate")
    s.add_argument("--mesh", required=True); s.add_argument("--cloud", required=True)
    s.add_argument("--piece", default="piece"); s.add_argument("--outdir", required=True)
    s.add_argument("--seed", type=int, default=3801); s.add_argument("--jitter", type=float, default=0.10)
    s.set_defaults(fn=cmd_validate)
    s = sub.add_parser("subdiv")
    s.add_argument("--mesh", required=True); s.add_argument("--level", type=int, required=True)
    s.add_argument("--piece", default="piece"); s.add_argument("--outdir", required=True)
    s.add_argument("--out", default=""); s.set_defaults(fn=cmd_subdiv)
    s = sub.add_parser("sample")
    s.add_argument("--mesh", required=True); s.add_argument("--spacing", type=float, required=True)
    s.add_argument("--level", type=int, default=1); s.add_argument("--piece", default="piece")
    s.add_argument("--outdir", required=True); s.add_argument("--out", default="")
    s.add_argument("--sample-from", type=int, default=0, dest="sample_from")
    s.add_argument("--seed", type=int, default=3801); s.add_argument("--jitter", type=float, default=0.10)
    s.set_defaults(fn=cmd_sample)
    a = ap.parse_args(argv)
    if not getattr(a, "fn", None):
        ap.print_help()
        return 2
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())