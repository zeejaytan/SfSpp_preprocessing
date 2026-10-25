#!/usr/bin/env python3
"""measure297.py -- ticket 297: is the authors' chord on Pot D 22 Bl0 the better break edge?

Mesh-based, not cluster-based.  Everything is measured against the authors' own DS mesh,
which is the one object that is true whichever line is right.

Reads (nothing else):
  <run>/scripts/score292.py            its read_pcd, unchanged
  <run>/out/geom/repK/ours.Bl0.pcd     our line, repeat K
  <run>/out/geom/authors.Bl0.pcd       copy of the corpus authors' line
  <run>/out/geom/rep1/ours.S0.xyz      our interior face (cross-check of the face plane)
  <corpus>/Mesh/Pot_D_Piece_22_Mesh_DS.obj
  <corpus>/Surfaces/Pot_D_Piece_22_Surface_0.xyz, _1.xyz
  <corpus>/Breaklines/Pot_D_Piece_22_Breakline_0.pcd

Writes <run>/out/measure297.json; prints a human-readable report.

Usage:  measure297.py <run dir> [rep ...]
        measure297.py --selftest [run dir]     golden + synthetic test, no run needed
"""
import importlib.util
import json
import os
import sys

import numpy as np
from scipy.spatial import cKDTree

CORPUS = os.environ.get("SFS_CORPUS", "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp")
PIECE = "Pot_D_Piece_22"
POT = "Pot_D"
LANE = 0
REPS = ["rep1", "rep2", "rep3"]

# ---- pre-registered numbers, copied from the ticket before any measurement was made ----
R_FACE = 15.0                    # mm, disc around the stretch midpoint used to fit the face plane
R_FACE_MIN_PTS = 400
R_FACE_GROW = (1.0, 1.5, 2.0)    # multipliers tried in order until R_FACE_MIN_PTS is reached
MESH_NORMAL_SECTOR = 20.0        # deg, sector used for the mesh cross-check of the face normal
CONFIRM_CHORD_MM = 0.50
CONFIRM_CHORD_SHARE = 90.0
CONFIRM_TILT_DEG = 45.0
CONFIRM_TILT_SHARE = 70.0
REFUTE_FLOAT_MM = 1.0
REFUTE_FLOAT_LENGTH_SHARE = 50.0
REFUTE_FACE_TILT_DEG = 20.0
REFUTE_FACE_SHARE = 70.0
FACE_PLANE_MM = 1.0              # (d) "within 1 mm of the interior-face plane"
GATE = dict(runid="20261025-0340_0f8a4a4_p294-pictures", n_ours=125, n_auth=133,
            median=0.757, cov_ours=86.40, cov_auth=78.95, len_ours=223.007, len_auth=241.280,
            max_step=1.801, at_bar="no", theta=3.4)
BINS = [(float(a), float(a + 5)) for a in range(0, 90, 5)]


# ------------------------------------------------------------------ readers (294, verbatim)
def read_obj(path):
    V = []; F = []
    for line in open(path, "r", errors="ignore"):
        if line.startswith("v "):
            p = line.split()
            V.append((float(p[1]), float(p[2]), float(p[3])))
        elif line.startswith("f "):
            idx = [int(tok.split("/")[0]) - 1 for tok in line.split()[1:]]
            for k in range(1, len(idx) - 1):
                F.append((idx[0], idx[k], idx[k + 1]))
    return np.asarray(V, dtype=float), np.asarray(F, dtype=int)


def read_xyz_list(path):
    pts = []
    for line in open(path, "r", errors="ignore"):
        p = line.split()
        if len(p) >= 3:
            try:
                pts.append((float(p[0]), float(p[1]), float(p[2])))
            except ValueError:
                continue
    return np.asarray(pts, dtype=float)


def load_score(run):
    spec = importlib.util.spec_from_file_location("score292", os.path.join(run, "scripts", "score292.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------------ geometry (294, verbatim)
def dist_point_tri(P, A, B, C):
    """Vectorised closest distance from one point P to many triangles.  Ericson, regions."""
    AB = B - A; AC = C - A; AP = P - A
    d1 = (AB * AP).sum(1); d2 = (AC * AP).sum(1)
    BP = P - B; d3 = (AB * BP).sum(1); d4 = (AC * BP).sum(1)
    CP = P - C; d5 = (AB * CP).sum(1); d6 = (AC * CP).sum(1)
    va = d3 * d6 - d5 * d4; vb = d5 * d2 - d1 * d6; vc = d1 * d4 - d3 * d2
    denom = va + vb + vc
    denom = np.where(np.abs(denom) < 1e-20, 1e-20, denom)
    v = vb / denom; w = vc / denom
    out = np.empty((A.shape[0], 3))
    m = (d1 <= 0) & (d2 <= 0); out[m] = A[m]
    m = (d3 >= 0) & (d4 <= d3); out[m] = B[m]
    m = (d6 >= 0) & (d5 <= d6); out[m] = C[m]
    m = (vc <= 0) & (d1 >= 0) & (d3 <= 0); t = np.where((d1 - d3) == 0, 0, d1 / (d1 - d3)); out[m] = (A + t[:, None] * AB)[m]
    m = (vb <= 0) & (d2 >= 0) & (d6 <= 0); t = np.where((d2 - d6) == 0, 0, d2 / (d2 - d6)); out[m] = (A + t[:, None] * AC)[m]
    m = (va <= 0) & ((d4 - d3) >= 0) & ((d5 - d6) >= 0)
    t = np.where(((d4 - d3) + (d5 - d6)) == 0, 0, (d4 - d3) / ((d4 - d3) + (d5 - d6)))
    out[m] = (B + t[:, None] * (C - B))[m]
    m2 = ~((d1 <= 0) & (d2 <= 0)) & ~((d3 >= 0) & (d4 <= d3)) & ~((d6 >= 0) & (d5 <= d6)) & \
         ~((vc <= 0) & (d1 >= 0) & (d3 <= 0)) & ~((vb <= 0) & (d2 >= 0) & (d6 <= 0)) & \
         ~((va <= 0) & ((d4 - d3) >= 0) & ((d5 - d6) >= 0))
    out[m2] = (A + v[:, None] * AB + w[:, None] * AC)[m2]
    return out


def pts_to_mesh(pts, T1, T2, T3):
    """Closest distance from every point of pts to the triangle soup (mm)."""
    d = np.empty(len(pts), dtype=float)
    for k, p in enumerate(pts):
        Q = dist_point_tri(p, T1, T2, T3)
        d[k] = float(np.sqrt(((Q - p) ** 2).sum(1)).min())
    return d


def worst_stretch(ours, auth):
    """294's definition, verbatim (p294_render.py:91-119): the run of OUR dots further than
    2.0 mm from their line, chosen by the largest arc x mean gap."""
    dist, _ = cKDTree(auth).query(ours)
    thr = 2.0
    over = dist > thr
    if not over.any():
        thr = max(1.0, float(np.median(dist)) + 0.5)
        over = dist > thr
    best = None
    i = 0
    while i < len(over):
        if not over[i]:
            i += 1
            continue
        j = i
        while j + 1 < len(over) and over[j + 1]:
            j += 1
        seg = ours[i:j + 1]
        arc = float(np.linalg.norm(np.diff(seg, axis=0), axis=1).sum()) if len(seg) > 1 else 0.0
        key = arc * float(dist[i:j + 1].mean())
        if best is None or key > best[0]:
            best = (key, i, j)
        i = j + 1
    if best is None:
        k = int(np.argmax(dist))
        return k, k, float(dist[k]), 0.0, thr
    _, i, j = best
    seg = ours[i:j + 1]
    arc = float(np.linalg.norm(np.diff(seg, axis=0), axis=1).sum()) if len(seg) > 1 else 0.0
    return i, j, float(dist[i:j + 1].mean()), arc, thr


# ------------------------------------------------------------------ new machinery
def fit_plane(P):
    c = P.mean(0)
    Q = P - c
    _, V = np.linalg.eigh(Q.T @ Q / max(len(P), 1))
    n = V[:, 0]
    n = n / np.linalg.norm(n)
    rms = float(np.sqrt(((Q @ n) ** 2).mean()))
    return c, n, rms


def plane_basis(n):
    u = np.array([1.0, 0.0, 0.0])
    if abs(np.dot(u, n)) > 0.9:
        u = np.array([0.0, 1.0, 0.0])
    u = u - np.dot(u, n) * n
    u = u / np.linalg.norm(u)
    return u, np.cross(n, u)


def face_plane(points, mid, body_centroid, r=R_FACE):
    """Least-squares plane through the face points nearest the stretch, normal oriented away
    from the body centroid (i.e. pointing off the face into the interior air)."""
    d = np.linalg.norm(points - mid, axis=1)
    used = None
    for mult in R_FACE_GROW:
        R = r * mult
        sel = d <= R
        if int(sel.sum()) >= R_FACE_MIN_PTS:
            used = (R, sel)
            break
    if used is None:
        R = r * R_FACE_GROW[-1]
        sel = d <= R
        used = (R, sel)
    R, sel = used
    P = points[sel]
    if len(P) < 20:
        return None
    c, n, rms = fit_plane(P)
    if np.dot(n, c - body_centroid) < 0:
        n = -n
    return dict(centre=c, normal=n, rms=rms, n_pts=int(len(P)), radius=float(R))


def mesh_alignment(cen, nrm, area, mid, n_face, r=R_FACE):
    """Winding-agnostic check that the fitted face plane is a plane the mesh itself lies in:
    the share of local mesh area parallel to it, perpendicular to it, and steeper than 45 deg."""
    sel = np.linalg.norm(cen - mid, axis=1) <= r
    if int(sel.sum()) < 50:
        return None
    w = area[sel]
    tilt = tilted(nrm[sel], n_face)
    return dict(n_tris=int(sel.sum()), radius=float(r),
                parallel_area_share=round(100.0 * float(w[tilt <= MESH_NORMAL_SECTOR].sum() / w.sum()), 2),
                steeper_than_45_area_share=round(100.0 * float(w[tilt >= 45.0].sum() / w.sum()), 2),
                perpendicular_area_share=round(100.0 * float(w[tilt >= 90.0 - MESH_NORMAL_SECTOR].sum() / w.sum()), 2))


def tilted(nrm, n_face):
    return np.degrees(np.arccos(np.clip(np.abs(nrm @ n_face), 0.0, 1.0)))


def dist_stats(d, weights=None):
    d = np.asarray(d, dtype=float)
    if d.size == 0:
        return dict(n=0)
    s = dict(n=int(d.size),
             median=round(float(np.median(d)), 3),
             p95=round(float(np.percentile(d, 95)), 3),
             max=round(float(d.max()), 3),
             mean=round(float(d.mean()), 3))
    for thr in (0.25, 0.50, 1.0, 2.0):
        s["share_gt_%.2f" % thr] = round(100.0 * float((d > thr).mean()), 2)
    s["share_le_0.5"] = round(100.0 * float((d <= CONFIRM_CHORD_MM).mean()), 2)
    return s


def load_context(run):
    mesh_obj = os.path.join(CORPUS, "Mesh", PIECE + "_Mesh_DS.obj")
    if not os.path.exists(mesh_obj):
        mesh_obj = os.path.join(CORPUS, "Mesh", PIECE + "_Mesh.obj")
    verts, faces = read_obj(mesh_obj)
    T1 = verts[faces[:, 0]]; T2 = verts[faces[:, 1]]; T3 = verts[faces[:, 2]]
    nrm = np.cross(T2 - T1, T3 - T1)
    area = 0.5 * np.linalg.norm(nrm, axis=1)
    nrm = nrm / (np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-12)
    cen = (T1 + T2 + T3) / 3.0
    SC = load_score(run)
    auth = np.asarray(SC.read_pcd(os.path.join(run, "out", "geom", "authors.Bl0.pcd")), dtype=float)
    s0 = read_xyz_list(os.path.join(CORPUS, "Surfaces", PIECE + "_Surface_0.xyz"))
    s1 = read_xyz_list(os.path.join(CORPUS, "Surfaces", PIECE + "_Surface_1.xyz"))
    return dict(SC=SC, mesh_obj=mesh_obj, verts=verts, faces=faces, T1=T1, T2=T2, T3=T3,
                nrm=nrm, area=area, cen=cen, auth=auth, corp_s0=s0, corp_s1=s1)


def our_face(run, rep):
    p = os.path.join(run, "out", "geom", rep, "ours.S0.xyz")
    return read_xyz_list(p) if os.path.exists(p) else None


def analyse_rep(ctx, run, rep, keep_arrays=False):
    SC = ctx["SC"]
    T1, T2, T3 = ctx["T1"], ctx["T2"], ctx["T3"]
    auth = ctx["auth"]
    ours = np.asarray(SC.read_pcd(os.path.join(run, "out", "geom", rep, "ours.Bl0.pcd")), dtype=float)
    rec = dict(rep=rep, n_ours=int(len(ours)), n_auth=int(len(auth)),
               mesh_obj=os.path.basename(ctx["mesh_obj"]), mesh_tris=int(T1.shape[0]))

    # ---- the stretch, fixed by 294's own rule (not re-invented here) ----
    i, j, mean_gap, arc, thr = worst_stretch(ours, auth)
    rec["stretch"] = dict(i=int(i), j=int(j), n_dots=int(j - i + 1), arc_mm=round(arc, 2),
                          mean_gap_mm=round(mean_gap, 3), threshold_mm=thr)

    # ---- the chord: their dots from the one nearest our dot i to the one nearest our dot j ----
    ai = int(np.argmin(((auth - ours[i]) ** 2).sum(1)))
    aj = int(np.argmin(((auth - ours[j]) ** 2).sum(1)))
    lo, hi = min(ai, aj), max(ai, aj)
    chord = auth[lo:hi + 1]
    step = np.linalg.norm(np.diff(chord, axis=0), axis=1) if len(chord) > 1 else np.zeros(0)
    rec["chord"] = dict(lo=int(lo), hi=int(hi), n_dots=int(len(chord)),
                        polyline_mm=round(float(step.sum()), 2),
                        straight_mm=round(float(np.linalg.norm(chord[-1] - chord[0])), 2),
                        own_detour_arc_mm=round(arc, 2))

    # ---- (a) the authors' dots against the mesh, chord and rest separately ----
    da = pts_to_mesh(auth, T1, T2, T3)
    in_chord = np.zeros(len(auth), dtype=bool)
    in_chord[lo:hi + 1] = True
    rec["dist"] = dict(
        auth_all=dist_stats(da),
        auth_chord=dist_stats(da[in_chord]),
        auth_rest=dist_stats(da[~in_chord]),
    )
    seg = step if len(step) else np.zeros(0)
    if len(seg):
        f = da[lo:hi]
        g = da[lo + 1:hi + 1]
        fl = 0.5 * (f + g) > REFUTE_FLOAT_MM
        rec["dist"]["auth_chord"]["length_share_gt_1.0mm"] = round(100.0 * float(seg[fl].sum() / seg.sum()), 2)
        rec["dist"]["auth_chord"]["length_share_le_0.5mm"] = round(100.0 * float(seg[0.5 * (f + g) <= CONFIRM_CHORD_MM].sum() / seg.sum()), 2)

    # ---- (b) our dots against the mesh (instrument control) ----
    do = pts_to_mesh(ours, T1, T2, T3)
    in_det = np.zeros(len(ours), dtype=bool)
    in_det[i:j + 1] = True
    rec["dist"]["ours_all"] = dist_stats(do)
    rec["dist"]["ours_detour"] = dist_stats(do[in_det])
    rec["dist"]["ours_rest"] = dist_stats(do[~in_det])

    # ---- the interior-face plane: the authors' own labelled interior surface, local to the stretch
    mid = (chord[0] + chord[-1]) / 2.0
    body = ctx["corp_s0"].mean(0) if len(ctx["corp_s0"]) else auth.mean(0)
    # which corpus surface is the interior one: the one our own interior face agrees with
    s_ours = our_face(run, "rep1")
    ident = {}
    if s_ours is not None:
        for nm, P in (("corpus_Surface_0", ctx["corp_s0"]), ("corpus_Surface_1", ctx["corp_s1"])):
            ident[nm] = round(float(np.median(cKDTree(P).query(s_ours)[0])), 3)
        interior_key = min(ident, key=ident.get)
    else:
        interior_key = "corpus_Surface_0"
    interior_pts = ctx["corp_s0"] if interior_key == "corpus_Surface_0" else ctx["corp_s1"]
    pl = face_plane(interior_pts, mid, interior_pts.mean(0))
    if pl is None:
        rec["plane"] = dict(error="face plane fit failed")
        return rec
    c, n = pl["centre"], pl["normal"]
    u, v = plane_basis(n)
    cross = dict()
    if s_ours is not None:
        pl2 = face_plane(s_ours, mid, s_ours.mean(0))
        if pl2 is not None:
            cross["ours_S0_plane_angle_deg"] = round(float(np.degrees(np.arccos(
                np.clip(abs(np.dot(pl2["normal"], n)), 0, 1)))), 2)
    ma = mesh_alignment(ctx["cen"], ctx["nrm"], ctx["area"], mid, n)
    if ma is not None:
        cross["mesh_%gmm_parallel_area_pct" % R_FACE] = ma["parallel_area_share"]
        cross["mesh_%gmm_perpendicular_area_pct" % R_FACE] = ma["perpendicular_area_share"]
        cross["mesh_%gmm_steeper_than_45_pct" % R_FACE] = ma["steeper_than_45_area_share"]
        cross["mesh_tris_in_disc"] = ma["n_tris"]
    rec["plane"] = dict(source=interior_key + " (authors' labelled face, within %.1f mm of the stretch)"
                                     % pl["radius"],
                        centre=[round(float(q), 3) for q in c], normal=[round(float(q), 4) for q in n],
                        rms_mm=round(pl["rms"], 3), n_pts=pl["n_pts"], radius_mm=round(pl["radius"], 2),
                        surface_identity_median_mm=ident, cross_check=cross)

    # ---- (c)(d)(e) the patch enclosed between the chord and our detour ----
    det = ours[i:j + 1][::-1]
    poly = np.vstack([chord, det])
    from matplotlib.path import Path
    pq = np.column_stack([(poly - c) @ u, (poly - c) @ v])
    path = Path(pq)
    cq = np.column_stack([(ctx["cen"] - c) @ u, (ctx["cen"] - c) @ v])
    inside = path.contains_points(cq)
    rec["patch"] = dict(polygon_pts=int(len(poly)),
                        chord_plane_offset=[round(float(q), 3) for q in ((chord - c) @ n)],
                        detour_plane_offset=[round(float(q), 3) for q in ((det - c) @ n)])
    n_tri = int(inside.sum())
    rec["patch"]["n_tris"] = n_tri
    if n_tri == 0:
        rec["patch"]["empty"] = True
    else:
        pn = ctx["nrm"][inside]; pa = ctx["area"][inside]; pc = ctx["cen"][inside]
        A1, A2, A3 = T1[inside], T2[inside], T3[inside]
        q1 = np.column_stack([(A1 - c) @ u, (A1 - c) @ v])
        q2 = np.column_stack([(A2 - c) @ u, (A2 - c) @ v])
        q3 = np.column_stack([(A3 - c) @ u, (A3 - c) @ v])
        pa2 = 0.5 * np.abs((q2[:, 0] - q1[:, 0]) * (q3[:, 1] - q1[:, 1]) -
                           (q3[:, 0] - q1[:, 0]) * (q2[:, 1] - q1[:, 1]))
        tilt = tilted(pn, n)
        off = (pc - c) @ n
        area_tot = float(pa.sum())
        rec["patch"].update(area_mm2=round(area_tot, 2), area_projected_mm2=round(float(pa2.sum()), 2))
        hist = []
        for a0, a1 in BINS:
            m = (tilt >= a0) & (tilt < a1)
            hist.append(dict(bin="%02d-%02d" % (a0, a1), n=int(m.sum()),
                             area_mm2=round(float(pa[m].sum()), 2),
                             area_share=round(100.0 * float(pa[m].sum() / area_tot), 2)))
        rec["patch"]["tilt_histogram"] = hist
        ge45 = tilt >= CONFIRM_TILT_DEG
        le20 = tilt <= REFUTE_FACE_TILT_DEG
        rec["patch"]["tilt_share_ge45_area"] = round(100.0 * float(pa[ge45].sum() / area_tot), 2)
        rec["patch"]["tilt_share_ge45_count"] = round(100.0 * float(ge45.mean()), 2)
        rec["patch"]["tilt_share_le20_area"] = round(100.0 * float(pa[le20].sum() / area_tot), 2)
        rec["patch"]["tilt_share_le20_count"] = round(100.0 * float(le20.mean()), 2)
        rec["patch"]["offset_mm"] = dict(
            min=round(float(off.min()), 3), p5=round(float(np.percentile(off, 5)), 3),
            median=round(float(np.median(off)), 3), p95=round(float(np.percentile(off, 95)), 3),
            max=round(float(off.max()), 3), depth_mm=round(float(np.abs(off).max()), 3))
        near = np.abs(off) <= FACE_PLANE_MM
        rec["patch"]["share_within_1mm_area"] = round(100.0 * float(pa[near].sum() / area_tot), 2)
        rec["patch"]["share_within_1mm_count"] = round(100.0 * float(near.mean()), 2)
        facelike = le20 & near
        rec["patch"]["facelike_area_mm2"] = round(float(pa[facelike].sum()), 2)
        rec["patch"]["facelike_share_area"] = round(100.0 * float(pa[facelike].sum() / area_tot), 2)
    if keep_arrays:
        rec["_mask"] = inside
        rec["_poly"] = poly
        rec["_ours"] = ours
        rec["_plane"] = (c, n, u, v)
    return rec


def verdict_of(rec):
    c = rec.get("dist", {}).get("auth_chord", {})
    p = rec.get("patch", {})
    chord_share = c.get("share_le_0.5")
    len_gt1 = c.get("length_share_gt_1.0mm")
    tilt45 = p.get("tilt_share_ge45_area")
    tilt20 = p.get("tilt_share_le20_area")
    if chord_share is None or tilt45 is None:
        return dict(verdict="PARTIAL", why="a limb of the rule could not be measured")
    if chord_share >= CONFIRM_CHORD_SHARE and tilt45 >= CONFIRM_TILT_SHARE:
        v = "CONFIRM"
    elif (len_gt1 is not None and len_gt1 > REFUTE_FLOAT_LENGTH_SHARE) or tilt20 >= REFUTE_FACE_SHARE:
        v = "REFUTE"
    else:
        v = "PARTIAL"
    return dict(verdict=v,
                limb_chord_share_le_050mm=chord_share, need=CONFIRM_CHORD_SHARE,
                limb_chord_length_share_gt_10mm=len_gt1, refute_gt=REFUTE_FLOAT_LENGTH_SHARE,
                limb_patch_tilt_ge45_share=tilt45, need_ge45=CONFIRM_TILT_SHARE,
                limb_patch_tilt_le20_share=tilt20, refute_ge20=REFUTE_FACE_SHARE)


def gate_check(run, reps):
    """Ticket 294's D22 Bl0 row must sit inside the spread this piece shows across the repeats."""
    p = os.path.join(run, "out", "scores.tsv")
    rows = {}
    if os.path.exists(p):
        for line in open(p):
            t = line.split()
            if len(t) >= 12 and t[0].startswith("rep"):
                rows[t[0]] = dict(piece=t[2], lane=int(t[3]), n_ours=int(t[4]), n_auth=int(t[5]),
                                  median=float(t[6]), cov_ours=float(t[7]), cov_auth=float(t[8]),
                                  jumps=int(t[9]), max_step=float(t[10]), len_ours=float(t[11]))
    med = [r["median"] for r in rows.values()]
    cov = [r["cov_ours"] for r in rows.values()]
    out = dict(gate_row=GATE, fresh={k: v for k, v in rows.items()},
               spread_median_mm=round(max(med) - min(med), 3) if med else None,
               spread_cov_ours_pp=round(max(cov) - min(cov), 2) if cov else None)
    if med:
        out["gate_median_inside_range"] = bool(min(med) <= GATE["median"] <= max(med))
        out["gate_median_delta_mm"] = round(GATE["median"] - float(np.median(med)), 3)
        out["gate_cov_inside_range"] = bool(min(cov) <= GATE["cov_ours"] <= max(cov))
        out["gate_cov_delta_pp"] = round(GATE["cov_ours"] - float(np.median(cov)), 2)
        out["gate_pass"] = bool(out["gate_median_inside_range"] and out["gate_cov_inside_range"])
    return out


def report(res):
    L = []
    g = res["gate"]
    L.append("GATE (ticket 294 row vs this piece's own spread over %d repeats)" % len(g["fresh"]))
    for k, v in sorted(g["fresh"].items()):
        L.append("  %-5s n_ours %d  n_auth %d  median %.3f  cov_ours %.2f  cov_auth %.2f  len_ours %.3f  max_step %.3f"
                 % (k, v["n_ours"], v["n_auth"], v["median"], v["cov_ours"], v["cov_auth"], v["len_ours"], v["max_step"]))
    L.append("  294 row: n_ours %d median %.3f cov_ours %.2f cov_auth %.2f len_ours %.3f  theta %.5f"
             % (GATE["n_ours"], GATE["median"], GATE["cov_ours"], GATE["cov_auth"], GATE["len_ours"], GATE["theta"]))
    L.append("  spread over the repeats: median %.3f mm, cov_ours %.2f pp" % (g["spread_median_mm"], g["spread_cov_ours_pp"]))
    L.append("  294 median inside the repeats' range: %s (delta %+.3f mm); cov_ours inside: %s (delta %+.2f pp); GATE %s"
             % (g.get("gate_median_inside_range"), g.get("gate_median_delta_mm", 0.0),
                g.get("gate_cov_inside_range"), g.get("gate_cov_delta_pp", 0.0),
                "PASS" if g.get("gate_pass") else "FAIL"))
    for rep, r in res["reps"].items():
        L.append("")
        L.append("== %s  (%d of our dots, %d of theirs, %d mesh triangles)" % (rep, r["n_ours"], r["n_auth"], r["mesh_tris"]))
        s = r["stretch"]; ch = r["chord"]
        L.append("  stretch (294's rule): our dots %d-%d (%d), arc %.2f mm, mean gap %.3f mm, threshold %.2f mm"
                 % (s["i"], s["j"], s["n_dots"], s["arc_mm"], s["mean_gap_mm"], s["threshold_mm"]))
        L.append("  chord: their dots %d-%d (%d), polyline %.2f mm, straight %.2f mm, our detour %.2f mm"
                 % (ch["lo"], ch["hi"], ch["n_dots"], ch["polyline_mm"], ch["straight_mm"], ch["own_detour_arc_mm"]))
        d = r["dist"]
        for k in ("auth_chord", "auth_rest", "auth_all", "ours_detour", "ours_rest", "ours_all"):
            v = d.get(k, {})
            L.append("  %-12s n %3d  median %6.3f  p95 %6.3f  max %6.3f  <=0.50 %6.2f%%  >1.0 %5.2f%%  >2.0 %5.2f%%"
                     % (k, v.get("n", 0), v.get("median", 0.0), v.get("p95", 0.0), v.get("max", 0.0),
                        v.get("share_le_0.5", 0.0), v.get("share_gt_1.00", 0.0), v.get("share_gt_2.00", 0.0)))
        if "length_share_gt_1.0mm" in d.get("auth_chord", {}):
            L.append("  chord by length: %.2f%% of it >1.0 mm from the mesh, %.2f%% <=0.50 mm"
                     % (d["auth_chord"]["length_share_gt_1.0mm"], d["auth_chord"]["length_share_le_0.5mm"]))
        pl = r["plane"]
        if "normal" in pl:
            L.append("  face plane: %s  n_pts %d  R %.1f mm  rms %.3f mm  normal %s"
                     % (pl["source"], pl["n_pts"], pl["radius_mm"], pl["rms_mm"], pl["normal"]))
            L.append("  cross-checks: %s" % pl["cross_check"])
        p = r["patch"]
        if p.get("empty") or "area_mm2" not in p:
            L.append("  PATCH: no mesh triangle inside the enclosed polygon (%d inside) -- the enclosed region is not on the model" % p.get("n_tris", 0))
        else:
            L.append("  patch: %d triangles, %.2f mm2 on the mesh (%.2f mm2 projected)" % (p["n_tris"], p["area_mm2"], p["area_projected_mm2"]))
            L.append("  tilt histogram (area share): " + " ".join("%s:%.1f" % (h["bin"], h["area_share"]) for h in p["tilt_histogram"]))
            L.append("  tilt >=45 deg: %.2f%% of area (%.2f%% of triangles);  <=20 deg: %.2f%% of area (%.2f%% of triangles)"
                     % (p["tilt_share_ge45_area"], p["tilt_share_ge45_count"], p["tilt_share_le20_area"], p["tilt_share_le20_count"]))
            o = p["offset_mm"]
            L.append("  offset from the face plane along its normal: min %.2f p5 %.2f median %.2f p95 %.2f max %.2f mm (depth %.2f mm)"
                     % (o["min"], o["p5"], o["median"], o["p95"], o["max"], o["depth_mm"]))
            L.append("  within 1 mm of the face plane: %.2f%% of area (%.2f%% of triangles)" % (p["share_within_1mm_area"], p["share_within_1mm_count"]))
            L.append("  face-like and cut away by the chord (tilt<=20 deg and within 1 mm): %.2f mm2, %.2f%% of the patch"
                     % (p["facelike_area_mm2"], p["facelike_share_area"]))
        v = r["verdict"]
        L.append("  VERDICT %s -- chord dots <=0.50 mm: %.2f%% (need >=%.0f); patch tilt >=45 deg: %.2f%% (need >=%.0f);"
                 "  chord length >1.0 mm: %.2f%% (refute >%.0f); patch tilt <=20 deg: %.2f%% (refute >=%.0f)"
                 % (v["verdict"], v["limb_chord_share_le_050mm"], v["need"], v["limb_patch_tilt_ge45_share"], v["need_ge45"],
                    v["limb_chord_length_share_gt_10mm"] if v["limb_chord_length_share_gt_10mm"] is not None else -1,
                    v["refute_gt"], v["limb_patch_tilt_le20_share"], v["refute_ge20"]))
    L.append("")
    L.append("OVERALL: %s" % res["overall"])
    return "\n".join(L)


def run_all(run, reps, keep_arrays=False):
    ctx = load_context(run)
    res = dict(run=run, reps_dir=os.path.join(run, "out", "geom"), gate=gate_check(run, reps), reps={})
    for rep in reps:
        p = os.path.join(run, "out", "geom", rep, "ours.Bl0.pcd")
        if not os.path.exists(p):
            res["reps"][rep] = dict(error="missing " + p)
            continue
        r = analyse_rep(ctx, run, rep, keep_arrays=keep_arrays)
        r["verdict"] = verdict_of(r)
        res["reps"][rep] = r
    vs = [r["verdict"]["verdict"] for r in res["reps"].values() if "verdict" in r]
    if len(set(vs)) == 1 and vs:
        res["overall"] = vs[0]
    elif vs:
        res["overall"] = "PARTIAL (the repeats disagree: %s)" % ", ".join(vs)
    else:
        res["overall"] = "no measurement"
    res["_ctx"] = ctx
    return res


def strip(obj):
    if isinstance(obj, dict):
        return {k: strip(v) for k, v in obj.items() if not k.startswith("_")}
    if isinstance(obj, (list, tuple)):
        return [strip(v) for v in obj]
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    return obj


def selftest(run):
    """Two checks that need no pipeline output: the mesh instrument against ticket 294's own
    authors_to_mesh row, and the whole patch machinery on a synthetic detour."""
    if run is None:
        run = "."
        SC = None
    ctx = None
    T1 = T2 = T3 = None
    verts, faces = read_obj(os.path.join(CORPUS, "Mesh", PIECE + "_Mesh_DS.obj"))
    T1 = verts[faces[:, 0]]; T2 = verts[faces[:, 1]]; T3 = verts[faces[:, 2]]
    auth = read_pcd_here(os.path.join(CORPUS, "Breaklines", PIECE + "_Breakline_0.pcd"))
    d = pts_to_mesh(auth, T1, T2, T3)
    print("[selftest] authors' whole line to mesh: n %d tris %d median %.3f p95 %.3f max %.3f"
          % (len(auth), len(faces), np.median(d), np.percentile(d, 95), d.max()))
    print("[selftest] ticket 294 mesh_ref row for this lane:               n 133 tris 18116 median 0.012 p95 0.107 max 1.386")
    ok1 = abs(np.median(d) - 0.012) < 0.002 and abs(d.max() - 1.386) < 0.010 and len(faces) == 18116
    print("[selftest] instrument reproduces the 294 row: %s" % ok1)

    # synthetic: push a stretch of their own line 4 mm sideways off the surface
    n0 = np.array([0.0, 0.0, 1.0])
    mid = auth.mean(0)
    u = auth[-1] - auth[0]; u = u / np.linalg.norm(u)
    w = np.cross(u, n0); w = w / np.linalg.norm(w)
    fake = auth.copy()
    fake[42:53] += 4.0 * w
    i, j, mg, arc, thr = worst_stretch(fake, auth)
    print("[selftest] synthetic detour on dots 42-52 found as %d-%d (arc %.2f mm, mean gap %.3f mm)" % (i, j, arc, mg))
    ok2 = (i <= 43) and (j >= 51)
    print("[selftest] worst_stretch finds the planted stretch: %s" % ok2)
    print("[selftest] PASS" if (ok1 and ok2) else "[selftest] FAIL")
    return 0 if (ok1 and ok2) else 1


def read_pcd_here(path):
    """Fallback PCD reader for --selftest, where no score292.py is present."""
    import struct
    fields = None; size = None; typ = None; count = None; npts = 0; data = "ascii"; off = 0
    with open(path, "rb") as fh:
        while True:
            line = fh.readline()
            if not line:
                break
            off = fh.tell()
            k = line.decode("ascii", "replace").split()
            if not k:
                continue
            key = k[0].upper()
            if key == "FIELDS":
                fields = k[1:]
            elif key == "SIZE":
                size = [int(x) for x in k[1:]]
            elif key == "TYPE":
                typ = k[1:]
            elif key == "COUNT":
                count = [int(x) for x in k[1:]]
            elif key == "POINTS":
                npts = int(k[1])
            elif key == "DATA":
                data = k[1].lower()
                break
        fh.seek(off)
        ix, iy, iz = fields.index("x"), fields.index("y"), fields.index("z")
        if data == "ascii":
            out = []
            for line in fh:
                v = line.split()
                if len(v) < 3:
                    continue
                out.append((float(v[ix]), float(v[iy]), float(v[iz])))
            return np.asarray(out, dtype=float)
        if count is None:
            count = [1] * len(fields)
        fmts = {"F": "f", "U": "I", "I": "i"}
        tags = [(str(c) + fmts[t]) if c > 1 else fmts[t] for t, c in zip(typ, count)]
        st = struct.Struct("".join(tags))
        raw = fh.read(npts * st.size)
        out = []
        for r in st.iter_unpack(raw):
            out.append((float(r[ix]), float(r[iy]), float(r[iz])))
        return np.asarray(out, dtype=float)


def main(argv):
    if len(argv) > 1 and argv[1] == "--selftest":
        return selftest(argv[2] if len(argv) > 2 else None)
    run = argv[1]
    reps = argv[2:] or REPS
    res = run_all(run, reps)
    txt = report(res)
    print(txt)
    os.makedirs(os.path.join(run, "out"), exist_ok=True)
    with open(os.path.join(run, "out", "measure297.json"), "w") as fh:
        json.dump(strip(res), fh, indent=1)
    with open(os.path.join(run, "out", "measure297.txt"), "w") as fh:
        fh.write(txt + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
