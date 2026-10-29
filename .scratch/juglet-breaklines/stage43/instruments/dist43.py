#!/usr/bin/env python3
"""dist43.py -- ticket 43 Part A/B: the within-face vs across-fold neighbour-turn distributions
per sherd, and the two derived theta rules.

Nothing here is part of the pipeline.  The pipeline (mesh_processing_headless.cpp) is untouched.

Method, and the one deviation from the ticket text this instrument records openly:

  The ticket says "compute the turn angle between the two face normals" and, one line later,
  "label a pair WITHIN-FACE if the two source-triangle normals differ by less than 45 deg".
  Read literally on the same normals those are the SAME quantity and the label is degenerate:
  every within-face pair would measure <45 deg by construction and every across-fold pair >=45,
  so the "gap" would sit at exactly 45 deg on every sherd and carry no information.  What the
  growth gate actually tests (mesh_processing_headless.cpp:3184-3192) is the angle between the
  NORMALS THE PIPELINE ESTIMATES on the sampled cloud, not the raw face normals.  So this
  instrument measures the turn on TWO normal fields and reports both:

    est     PCA over k = max(5, min(20, n/1000)) neighbours of the sampled cloud, each flipped
            towards the PCD viewpoint (0,0,0) exactly as PCL's NormalEstimation does.  Kept
            unchanged, as its own column set, so the two orientation rules can be diffed.
    mst     the SAME PCA normals, oriented the way the PIPELINE orients them: a minimum
            spanning tree over the k-NN graph with edge weight 1 - |n_i . n_j| and the sign
            propagated along the tree (CGAL::mst_orient_normals, mesh_processing_headless.cpp:
            805-806).  The viewpoint flip is nearly one vector for a sherd ~530 mm from the
            origin and 8-35 mm across, so it forces the cloud into one hemisphere and turns
            roughly half a closed solid's normals onto their neighbours; the mst columns are
            the field the growth gate actually sees.  The root's own sign is arbitrary and
            changes no turn angle (a global flip leaves every dot product alone).
    face    the analytic face normals mesh38's sampler carries (voxel-merged, viewpoint-flipped).
            Reported as the literal reading, with its degenerate label visible in the numbers.

  The label in both cases uses the SOURCE-TRIANGLE face normals (the folded angle between the
  two source triangles' normals, <45 deg = WITHIN-FACE, >=45 = ACROSS-FOLD), which is what the
  ticket specifies and what the mesh, not the sampler, determines.

  Neighbourhood criterion = the pipeline's own: nearestKSearch(p, nb + 1) with nb = 10
  (mesh_processing_headless.cpp:3184, SFS_PAPER_NB default 10).  Each unordered pair is counted
  once.  The turn is pcl::getAngle3D's: acos of the dot of the two (oriented) unit normals.

  Spacing: each piece is sampled at the S its own pipeline run resolved
  ([SPACING-22] policy=piece ... S=..., run of record 33989453), read from a spec tsv.

usage:
  dist43.py selftest
  dist43.py pieces --spec spec.tsv --outdir DIR [--seed 4301]
  dist43.py rules   --partA-dir DIR --outdir DIR
  dist43.py figure  --partA-dir DIR --out fig.png

spec.tsv rows (tab-separated): pot <tab> piece <tab> mesh.obj <tab> spacing_mm <tab> ladder_theta_deg
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mesh38 as S          # noqa: E402

VIEWPOINT = np.zeros(3, dtype=np.float64)
FOLD_LABEL_DEG = 45.0
NB = 10                      # pipeline default (SFS_PAPER_NB)
RHO_CAP_MM = 60.0
MAX_PTS_RHO = 20000


def pipeline_k(n):
    """mesh_processing_headless.cpp:405-433: g_normalMinK=5, g_normalMaxK=20, n/1000."""
    return int(max(5, min(20, n // 1000)))


def orient(nrm, pts, vp=VIEWPOINT):
    v = vp[None, :] - pts
    d = np.einsum("ij,ij->i", nrm, v)
    out = nrm.copy()
    out[d < 0] *= -1.0
    return out


def pca_normals_raw(pts, k):
    """PCA normal over the k nearest neighbours, with NO orientation rule applied."""
    from scipy.spatial import cKDTree
    tree = cKDTree(pts)
    kq = min(k + 1, len(pts))
    _d, nb = tree.query(pts, k=kq, workers=-1)
    Q = pts[nb]                                   # (n,kq,3)
    C = Q - Q.mean(axis=1, keepdims=True)
    cov = np.einsum("mki,mkj->mij", C, C)
    _w, V = np.linalg.eigh(cov)
    return V[:, :, 0]


def pca_normals(pts, k):
    """PCA normal over the k nearest neighbours, then the viewpoint flip (grow38 arm B)."""
    return orient(pca_normals_raw(pts, k), pts)


def mst_orient(nrm, pts, k):
    """The pipeline's orientation rule, on the same normals: CGAL::mst_orient_normals.

    mesh_processing_headless.cpp:805-806 orients the estimated normals with a minimum spanning
    tree over the nb-neighbour graph and propagates the sign along it, so neighbours agree.
    Reproduced here with CGAL's normal-deviation weight 1 - |n_i . n_j| over the same k-NN
    graph, Kruskal's MST, and a breadth-first sign pass from a root.  Returns (oriented,
    reached): CGAL hands back the first point it could not orient and the pipeline erases it
    and everything after (:821), so the caller can exclude the same points.
    """
    from scipy.spatial import cKDTree
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import minimum_spanning_tree, breadth_first_order
    n = len(pts)
    tree = cKDTree(pts)
    kq = min(k + 1, n)
    _d, nb = tree.query(pts, k=kq, workers=-1)
    i = np.repeat(np.arange(n), kq - 1)
    j = nb[:, 1:].ravel()
    keep = j != i
    i, j = i[keep], j[keep]
    key = np.unique(np.minimum(i, j).astype(np.int64) * n + np.maximum(i, j))
    i = key // n
    j = key % n
    w = 1.0 - np.abs(np.einsum("ij,ij->i", nrm[i], nrm[j]))
    g = coo_matrix((np.maximum(w, 1e-9), (i, j)), shape=(n, n)).tocsr()
    mst = minimum_spanning_tree(g)                # scipy treats the graph as undirected
    order, pred = breadth_first_order(mst, 0, directed=False)
    out = nrm.copy()
    reached = np.zeros(n, dtype=bool)
    reached[0] = True
    for v in order[1:]:
        p = pred[v]
        reached[v] = True
        if np.dot(out[p], out[v]) < 0.0:
            out[v] = -out[v]
    return out, reached


def quadric_radii(pts, sub, tree, k):
    """radius = 1 / max(|k1|,|k2|) of an osculating paraboloid over the k nearest neighbours.
    Lifted from stage32/analyse30.py (the ticket-32 instrument) unchanged in method."""
    n = pts.shape[0]
    kq = int(min(k, n))
    _d, nb = tree.query(pts[sub], k=kq, workers=-1)
    Q = pts[nb]
    P = pts[sub]
    C = Q - Q.mean(axis=1, keepdims=True)
    cov = np.einsum("mki,mkj->mij", C, C)
    _w, V = np.linalg.eigh(cov)
    e = V[:, :, 0]
    a = np.tile(np.array([1.0, 0.0, 0.0]), (e.shape[0], 1))
    a[np.abs(e[:, 0]) > 0.9] = np.array([0.0, 1.0, 0.0])
    u = np.cross(e, a)
    u /= np.linalg.norm(u, axis=1, keepdims=True)
    v = np.cross(e, u)
    rel = Q - P[:, None, :]
    x = np.einsum("mki,mi->mk", rel, u)
    y = np.einsum("mki,mi->mk", rel, v)
    z = np.einsum("mki,mi->mk", rel, e)
    one = np.ones_like(x)
    A = np.stack([x, y, 0.5 * x * x, x * y, 0.5 * y * y, one], axis=2)
    M = np.einsum("mki,mkj->mij", A, A)
    b = np.einsum("mki,mk->mi", A, z)
    ridge = 1e-12 * np.trace(M, axis1=1, axis2=2)
    M[:, np.arange(6), np.arange(6)] += ridge[:, None]
    coef = np.linalg.solve(M, b[:, :, None])[:, :, 0]
    L, Mm, N = coef[:, 2], coef[:, 3], coef[:, 4]
    tr = L + N
    det = L * N - Mm * Mm
    disc = np.sqrt(np.maximum(0.25 * tr * tr - det, 0.0))
    k1 = 0.5 * tr + disc
    k2 = 0.5 * tr - disc
    kmax = np.maximum(np.abs(k1), np.abs(k2))
    ok = np.isfinite(kmax)
    rad = np.full(kmax.shape, np.inf)
    good = ok & (kmax > 1.0 / RHO_CAP_MM)
    rad[good] = 1.0 / kmax[good]
    rad[~np.isfinite(rad)] = RHO_CAP_MM
    return np.clip(rad, 0.0, RHO_CAP_MM)


def pair_angles(pts, nrm, tri_face):
    """Turn angles and labels of every unordered neighbour pair.

    Returns (turn_deg_est, turn_deg_face, fold_deg) aligned arrays over the same pairs: the
    neighbourhood is the pipeline's (nb nearest, each unordered pair once), the label source is
    the folded angle between the two samples' source-triangle normals.
    """
    from scipy.spatial import cKDTree
    tree = cKDTree(pts)
    kq = min(NB + 1, len(pts))
    _d, nb = tree.query(pts, k=kq, workers=-1)
    i = np.repeat(np.arange(len(pts)), kq - 1)
    j = nb[:, 1:].ravel()
    keep = j != i
    i, j = i[keep], j[keep]
    lo = np.minimum(i, j)
    hi = np.maximum(i, j)
    key = lo.astype(np.int64) * len(pts) + hi
    key = np.unique(key)
    i = key // len(pts)
    j = key % len(pts)
    dot_est = np.einsum("ij,ij->i", nrm[i], nrm[j])
    turn_est = np.degrees(np.arccos(np.clip(dot_est, -1.0, 1.0)))
    return turn_est, i, j


def folded_pairs(pts, nrm, tri_nrm):
    """All three quantities per unordered pair: turn on est normals, turn on face normals,
    folded source-triangle angle (the label)."""
    from scipy.spatial import cKDTree
    tree = cKDTree(pts)
    kq = min(NB + 1, len(pts))
    _d, nb = tree.query(pts, k=kq, workers=-1)
    i = np.repeat(np.arange(len(pts)), kq - 1)
    j = nb[:, 1:].ravel()
    keep = j != i
    i, j = i[keep], j[keep]
    lo = np.minimum(i, j)
    hi = np.maximum(i, j)
    key = np.unique(lo.astype(np.int64) * len(pts) + hi)
    i = key // len(pts)
    j = key % len(pts)
    dot_est = np.einsum("ij,ij->i", nrm[i], nrm[j])
    turn_est = np.degrees(np.arccos(np.clip(dot_est, -1.0, 1.0)))
    dot_face = np.einsum("ij,ij->i", tri_nrm[i], tri_nrm[j])
    turn_face = np.degrees(np.arccos(np.clip(dot_face, -1.0, 1.0)))
    fold = np.degrees(np.arccos(np.clip(np.abs(dot_face), -1.0, 1.0)))
    return i, j, turn_est, turn_face, fold


THETA_GRID = (0.85, 1.7, 2.55, 3.4, 5.1, 6.8, 10.2)


def separability(turn, lab, thetas=THETA_GRID):
    """Per theta: the two fractions that decide the outcome, not a gap between percentiles.

    miss  = fraction of ACROSS-FOLD pairs whose turn is BELOW theta -- at this theta the growth
            would weld the break surface onto the face.
    false = fraction of WITHIN-FACE pairs whose turn is ABOVE theta -- at this theta the growth
            would refuse its own face.
    A theta that separates needs both near zero at once.  Nothing is clipped: every pair is in
    exactly one of the two sets, and the counts are returned so the denominators are visible.
    """
    out = {"n_within": int(lab.sum()), "n_across": int((~lab).sum()), "thetas": list(thetas),
           "miss": [], "false": []}
    for t in thetas:
        out["miss"].append(float((turn[~lab] < t).mean()) if (~lab).any() else float("nan"))
        out["false"].append(float((turn[lab] > t).mean()) if lab.any() else float("nan"))
    return out


def dist_stats(turn):
    if len(turn) == 0:
        return {"n": 0}
    return {"n": int(len(turn)),
            "p50": float(np.percentile(turn, 50)),
            "p90": float(np.percentile(turn, 90)),
            "p99": float(np.percentile(turn, 99))}


def head_stats(turn):
    if len(turn) == 0:
        return {"n": 0}
    return {"n": int(len(turn)),
            "p10": float(np.percentile(turn, 10)),
            "p50": float(np.percentile(turn, 50))}


def measure_piece(spec_row, seed):
    pot, piece, mesh_path, spacing, ladder = spec_row
    spacing = float(spacing)
    ladder = float(ladder) if ladder not in ("", "na") else float("nan")
    v, fc = S.read_obj(mesh_path)
    samp = S.sample_at(v, fc, spacing, seed=seed)
    pts = samp["pts"]
    fnrm_raw = samp["nrm"]                       # merged analytic face normals (unit)
    k_pipe = pipeline_k(len(pts))
    n_raw = pca_normals_raw(pts, k_pipe)
    n_est = orient(n_raw, pts)                   # viewpoint flip (PCL's rule, as before)
    n_mst, reached = mst_orient(n_raw, pts, k_pipe)   # MST propagation (the pipeline's rule)
    fnrm = orient(fnrm_raw, pts)
    _i, _j, turn_est, turn_face, fold = folded_pairs(pts, n_est, fnrm)
    _i, _j, turn_mst, _tf, fold_mst = folded_pairs(pts, n_mst, fnrm)
    lab = fold < FOLD_LABEL_DEG                  # True = WITHIN-FACE
    if not np.array_equal(fold, fold_mst):
        raise SystemExit("label changed between fields -- the pairs are not the same pairs")
    from scipy.spatial import cKDTree
    tree = cKDTree(pts)
    rng = np.random.default_rng(seed)
    sub = np.arange(len(pts))
    if sub.size > MAX_PTS_RHO:
        sub = np.sort(rng.choice(sub, size=MAX_PTS_RHO, replace=False))
    rad = quadric_radii(pts, sub, tree, 30)
    row = {
        "pot": pot, "piece": piece, "mesh": mesh_path,
        "spacing_requested_mm": spacing,
        "spacing_achieved_mm": samp["sp"]["median"],
        "sampled_points": int(len(pts)),
        "ladder_theta_deg": ladder,
        "shipped_theta_deg": 3.4,
        "fold_radius_med_mm": float(np.median(rad)),
        "fold_radius_p25_mm": float(np.percentile(rad, 25)),
        "fold_radius_p75_mm": float(np.percentile(rad, 75)),
        "pairs_total": int(len(turn_est)),
        "est": {"within": dist_stats(turn_est[lab]), "across": head_stats(turn_est[~lab]),
                "margin_p10_across_minus_p99_within": None,
                "margin_p10_across_minus_p90_within": None},
        "mst": {"within": dist_stats(turn_mst[lab]), "across": head_stats(turn_mst[~lab]),
                "margin_p10_across_minus_p99_within": None,
                "margin_p10_across_minus_p90_within": None},
        "face": {"within": dist_stats(turn_face[lab]), "across": head_stats(turn_face[~lab]),
                 "margin_p10_across_minus_p99_within": None,
                 "margin_p10_across_minus_p90_within": None},
        "turn_est_hist": None, "fold_hist": None,
        "frac_turn_over_90deg": {"est": float((turn_est > 90.0).mean()),
                                 "mst": float((turn_mst > 90.0).mean()),
                                 "face": float((turn_face > 90.0).mean())},
        "mst_reached_frac": float(reached.mean()),
        "mst_unreached_points": int((~reached).sum()),
        "pairs_est": int(len(turn_est)),
    }
    for fld in ("est", "mst", "face"):
        w = row[fld]["within"]
        a = row[fld]["across"]
        if w.get("n") and a.get("n"):
            row[fld]["margin_p10_across_minus_p99_within"] = a["p10"] - w["p99"]
            row[fld]["margin_p10_across_minus_p90_within"] = a["p10"] - w["p90"]
    # the separability grids: what a theta actually does to each field
    row["sep"] = {"est": separability(turn_est, lab), "mst": separability(turn_mst, lab)}
    # histograms are binned over the WHOLE turn range (0,180).  The first run binned the est
    # field to (0,90) and silently dropped 1.6-6.7 % of the pairs; nothing is dropped now, and
    # the counts say so explicitly instead of being inferred from a bin sum.
    edges = np.linspace(0.0, 180.0, 201)
    h_e, _ = np.histogram(turn_est, bins=200, range=(0.0, 180.0))
    row["turn_est_hist"] = {"counts": h_e.tolist(), "edges": edges.tolist()}
    h_m, _ = np.histogram(turn_mst, bins=200, range=(0.0, 180.0))
    row["turn_mst_hist"] = {"counts": h_m.tolist(), "edges": edges.tolist()}
    h_f, _ = np.histogram(turn_face, bins=200, range=(0.0, 180.0))
    row["turn_face_hist"] = h_f.tolist()
    row["hist_coverage"] = {
        "pairs": int(len(turn_est)),
        "est_in_hist": int(h_e.sum()), "mst_in_hist": int(h_m.sum()),
        "est_dropped": int(len(turn_est) - h_e.sum()),
        "mst_dropped": int(len(turn_mst) - h_m.sum()),
        "face_dropped": int(len(turn_face) - h_f.sum()),
    }
    if len(turn_est) - h_e.sum() or len(turn_mst) - h_m.sum() or len(turn_face) - h_f.sum():
        raise SystemExit("histogram dropped pairs -- the bin range is wrong again")
    return row


def cmd_selftest(_a):
    bad = 0
    # a folded sheet: two planes meeting at 90 deg, sampled at 0.5 mm, placed so that no
    # face normal is perpendicular to the line back to the viewpoint at the origin
    # (otherwise the viewpoint flip is degenerate and the test measures the test).
    v = np.array([[0.0, 0, 10], [20, 0, 10], [20, 20, 10], [0, 20, 10],
                  [20, 20, 30], [0, 20, 30]])
    fc = np.array([[0, 1, 2], [0, 2, 3], [2, 4, 5], [2, 5, 3]], dtype=np.int64)
    samp = S.sample_at(v, fc, 0.5, seed=1)
    pts = samp["pts"]
    fnrm = orient(samp["nrm"], pts)
    n_est = pca_normals(pts, pipeline_k(len(pts)))
    _i, _j, turn_est, turn_face, fold = folded_pairs(pts, n_est, fnrm)
    lab = fold < FOLD_LABEL_DEG
    nwf = int((~lab).sum())
    print("[SELFTEST] folded sheet: %d points, %d pairs, %d across-fold (%.1f%%)"
          % (len(pts), len(turn_est), nwf, 100.0 * nwf / max(1, len(turn_est))))
    if nwf == 0:
        bad += 1
        print("[SELFTEST] FAIL no across-fold pairs on a folded sheet")
    if lab.all():
        bad += 1
        print("[SELFTEST] FAIL every pair labelled within-face")
    w90 = np.percentile(turn_est[lab], 90)
    a10 = np.percentile(turn_est[~lab], 10)
    print("[SELFTEST] est within p90=%.3f deg, across p10=%.3f deg (fold at 90 deg: across turns must be large)"
          % (w90, a10))
    if a10 < 10.0:
        bad += 1
        print("[SELFTEST] FAIL across-fold p10 too small on a 90-deg sheet")
    # the literal face-normal reading is label-degenerate away from the fold: within pairs on
    # truly coplanar triangles measure ~0 exactly because the label says so.  Near the fold the
    # voxel-merged normals straddle the crease, which is the second reason the face field is not
    # the headline.  Assert the coplanar degeneracy (within-face pairs at <2 deg dominate) and
    # that the fold band mixes into the within label.
    fw = turn_face[lab]
    frac_flat = float((fw < 2.0).mean())
    fw_far = np.percentile(fw, 90)
    print("[SELFTEST] face-field within: %.1f%% under 2 deg (coplanar degeneracy), p90=%.3f deg (fold band leaks in)"
          % (100.0 * frac_flat, fw_far))
    if frac_flat < 0.9:
        bad += 1
        print("[SELFTEST] FAIL face-field coplanar degeneracy does not hold")
    # the mst rule must leave a sheet's own face coherent: on the coplanar part every pair must
    # agree, which is what the viewpoint flip cannot promise and what the pipeline relies on.
    n_mst, reached = mst_orient(pca_normals_raw(pts, pipeline_k(len(pts))), pts,
                                pipeline_k(len(pts)))
    _i, _j, turn_mst, _tf, _fold = folded_pairs(pts, n_mst, fnrm)
    flat = _fold < 2.0
    frac_flat_mst = float((turn_mst[flat] < 2.0).mean()) if flat.any() else 0.0
    frac_flat_est = float((turn_est[flat] < 2.0).mean()) if flat.any() else 0.0
    print("[SELFTEST] coplanar pairs agreeing (<2 deg): mst %.1f%% vs viewpoint %.1f%%; "
          "mst reached %d/%d points" % (100.0 * frac_flat_mst, 100.0 * frac_flat_est,
                                        int(reached.sum()), len(reached)))
    if frac_flat_mst < 0.95:
        bad += 1
        print("[SELFTEST] FAIL mst orientation does not make a flat sheet's normals agree")
    if not reached.all():
        bad += 1
        print("[SELFTEST] FAIL mst orientation left %d points unreached" % int((~reached).sum()))
    # the separability grid must be well formed: fractions in [0,1] and the two sets disjoint
    sp = separability(turn_est, lab)
    if sp["n_within"] + sp["n_across"] != len(turn_est):
        bad += 1
        print("[SELFTEST] FAIL separability sets do not partition the pairs")
    if not all(0.0 <= x <= 1.0 for x in sp["miss"] + sp["false"]):
        bad += 1
        print("[SELFTEST] FAIL separability fraction outside [0,1]")
    print("[SELFTEST] separability on the sheet (theta: miss/false): %s"
          % "  ".join("%.2f:%.3f/%.3f" % (t, sp["miss"][k], sp["false"][k])
                      for k, t in enumerate(sp["thetas"])))
    print("[SELFTEST] %s (%d failures)" % ("PASS" if bad == 0 else "FAIL", bad))
    return 0 if bad == 0 else 1


def cmd_pieces(a):
    os.makedirs(a.outdir, exist_ok=True)
    rows = []
    with open(a.spec) as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            t = line.split("\t")
            if len(t) < 4:
                raise SystemExit("bad spec line: %r" % line)
            rows.append((t[0], t[1], t[2], float(t[3]), t[4] if len(t) > 4 else ""))
    tsv = os.path.join(a.outdir, "partA.tsv")
    sepp = os.path.join(a.outdir, "sep.tsv")
    # Columns 0-19 are unchanged from the first run so the two tables diff column for column;
    # the mst field and the p90 gap are APPENDED, never substituted.
    hdr = ("pot\tpiece\tspacing_req_mm\tspacing_ach_mm\tpoints\tfold_radius_med_mm"
           "\tn_pairs\test_within_p50\test_within_p90\test_within_p99"
           "\test_across_p10\test_across_p50\test_margin"
           "\tface_within_p50\tface_within_p90\tface_within_p99"
           "\tface_across_p10\tface_across_p50\tface_margin\tladder_theta"
           "\tmst_within_p50\tmst_within_p90\tmst_within_p99"
           "\tmst_across_p10\tmst_across_p50\tmst_margin_p99\tmst_margin_p90"
           "\test_margin_p90"
           "\tfrac_over90_est\tfrac_over90_mst\tfrac_over90_face"
           "\tmst_reached_frac\tmst_unreached_points\n")
    sephdr = ("pot\tpiece\tfield\ttheta\tn_within\tn_across\tmiss_across_below_theta"
              "\tfalse_within_above_theta\n")
    sepout = open(sepp, "w")
    sepout.write(sephdr)
    with open(tsv, "w") as out:
        out.write(hdr)
        for r in rows:
            row = measure_piece(r, a.seed)
            rows_json_path = os.path.join(a.outdir, "piece_%s.json" % r[1])
            with open(rows_json_path, "w") as jf:
                json.dump(row, jf, sort_keys=True)
            e, fa, m = row["est"], row["face"], row["mst"]
            out.write("\t".join(str(x) for x in [
                row["pot"], row["piece"], "%.6f" % row["spacing_requested_mm"],
                "%.6f" % row["spacing_achieved_mm"], row["sampled_points"],
                "%.4f" % row["fold_radius_med_mm"], row["pairs_total"],
                "%.4f" % e["within"]["p50"], "%.4f" % e["within"]["p90"],
                "%.4f" % e["within"]["p99"], "%.4f" % e["across"]["p10"],
                "%.4f" % e["across"]["p50"], "%.4f" % e["margin_p10_across_minus_p99_within"],
                "%.4f" % fa["within"]["p50"], "%.4f" % fa["within"]["p90"],
                "%.4f" % fa["within"]["p99"], "%.4f" % fa["across"]["p10"],
                "%.4f" % fa["across"]["p50"],
                "%.4f" % fa["margin_p10_across_minus_p99_within"],
                ("%.4f" % row["ladder_theta_deg"]) if row["ladder_theta_deg"] == row["ladder_theta_deg"] else "na",
                "%.4f" % m["within"]["p50"], "%.4f" % m["within"]["p90"],
                "%.4f" % m["within"]["p99"], "%.4f" % m["across"]["p10"],
                "%.4f" % m["across"]["p50"],
                "%.4f" % m["margin_p10_across_minus_p99_within"],
                "%.4f" % m["margin_p10_across_minus_p90_within"],
                "%.4f" % e["margin_p10_across_minus_p90_within"],
                "%.6f" % row["frac_turn_over_90deg"]["est"],
                "%.6f" % row["frac_turn_over_90deg"]["mst"],
                "%.6f" % row["frac_turn_over_90deg"]["face"],
                "%.6f" % row["mst_reached_frac"], row["mst_unreached_points"],
            ]) + "\n")
            print("[A43] %s %s: EST within p50/p90/p99 = %.3f/%.3f/%.3f across p10/p50 = %.3f/%.3f "
                  "| MST within p90/p99 = %.3f/%.3f across p10 = %.3f "
                  "| gap p90 = %+.3f gap p99 = %+.3f | >90deg est/mst = %.4f/%.4f | rho_med %.2f mm"
                  % (r[0], r[1], e["within"]["p50"], e["within"]["p90"], e["within"]["p99"],
                     e["across"]["p10"], e["across"]["p50"],
                     m["within"]["p90"], m["within"]["p99"], m["across"]["p10"],
                     m["margin_p10_across_minus_p90_within"],
                     m["margin_p10_across_minus_p99_within"],
                     row["frac_turn_over_90deg"]["est"], row["frac_turn_over_90deg"]["mst"],
                     row["fold_radius_med_mm"]))
            for fld in ("est", "mst"):
                sp = row["sep"][fld]
                for k, t in enumerate(sp["thetas"]):
                    sepout.write("%s\t%s\t%s\t%.2f\t%d\t%d\t%.6f\t%.6f\n"
                                 % (row["pot"], row["piece"], fld, t,
                                    sp["n_within"], sp["n_across"],
                                    sp["miss"][k], sp["false"][k]))
            hc = row["hist_coverage"]
            print("[A43] %s %s separability EST theta:miss/false  %s"
                  % (r[0], r[1], "  ".join("%.2f:%.4f/%.4f" % (t, row["sep"]["est"]["miss"][k],
                                                               row["sep"]["est"]["false"][k])
                                           for k, t in enumerate(row["sep"]["est"]["thetas"]))))
            print("[A43] %s %s separability MST theta:miss/false  %s"
                  % (r[0], r[1], "  ".join("%.2f:%.4f/%.4f" % (t, row["sep"]["mst"]["miss"][k],
                                                               row["sep"]["mst"]["false"][k])
                                           for k, t in enumerate(row["sep"]["mst"]["thetas"]))))
            print("[A43] %s %s hist coverage pairs=%d est_in=%d mst_in=%d dropped est/mst/face=%d/%d/%d"
                  % (r[0], r[1], hc["pairs"], hc["est_in_hist"], hc["mst_in_hist"],
                     hc["est_dropped"], hc["mst_dropped"], hc["face_dropped"]))
    sepout.close()
    print("[A43] wrote %s and %s" % (tsv, sepp))


def cmd_rules(a):
    """R1: theta = k x within p90, k fixed so Pot A's median lands at 3.4.
    R2: theta = sqrt(within p90 x across p10) (geometric mid-gap).

    Two gap tests are reported, not one, because the FIRST run's choice of p99 was wrong: a p99
    of the turn sits in the near-180-degree sign-flip tail, so the p99 gap is a statement about
    orientation noise and not about the fold.  Both are written side by side.
      gap_p99 = across p10 - within p99   (the ticket's original test)
      gap_p90 = across p10 - within p90   (the same test one percentile down)

    The R1/R2 columns in thetas.tsv are the VIEWPOINT field's, unchanged from the first run, so
    Part C's cells still carry the thetas they were run with.  The mst field's thetas are extra
    columns (R1_mst/R2_mst) for comparison; they are not what Part C used.
    """
    with open(os.path.join(a.partA_dir, "partA.tsv")) as f:
        rd = [ln.rstrip("\n").split("\t") for ln in f]
    hdr = rd[0]
    rd = rd[1:]
    ci = {name: i for i, name in enumerate(hdr)}
    for need in ("est_within_p90", "est_within_p99", "est_across_p10",
                 "mst_within_p90", "mst_within_p99", "mst_across_p10"):
        if need not in ci:
            raise SystemExit("partA.tsv has no column %r -- rerun 'pieces' first" % need)
    pa = [r for r in rd if r[0] == "Pot_A"]
    k_r1 = 3.4 / float(np.median([float(r[ci["est_within_p90"]]) for r in pa]))
    k_mst = 3.4 / float(np.median([float(r[ci["mst_within_p90"]]) for r in pa]))
    out_rows = []
    for r in rd:
        e90 = float(r[ci["est_within_p90"]]); e99 = float(r[ci["est_within_p99"]])
        ea10 = float(r[ci["est_across_p10"]])
        m90 = float(r[ci["mst_within_p90"]]); m99 = float(r[ci["mst_within_p99"]])
        ma10 = float(r[ci["mst_across_p10"]])
        r1 = k_r1 * e90
        r2 = math.sqrt(e90 * ea10) if ea10 > 0 else float("nan")
        r1m = k_mst * m90
        r2m = math.sqrt(m90 * ma10) if ma10 > 0 else float("nan")
        out_rows.append((
            r[0], r[1],
            "%.4f" % e90, "%.4f" % e99, "%.4f" % ea10,
            "%.4f" % (ea10 - e90), "%.4f" % (ea10 - e99),
            "%.5f" % k_r1, "%.4f" % r1, "yes" if (e99 < r1 <= ea10) else "NO",
            "%.4f" % r2, "yes" if (e99 < r2 <= ea10) else "NO",
            "%.4f" % m90, "%.4f" % m99, "%.4f" % ma10,
            "%.4f" % (ma10 - m90), "%.4f" % (ma10 - m99),
            "%.5f" % k_mst, "%.4f" % r1m, "yes" if (m99 < r1m <= ma10) else "NO",
            "%.4f" % r2m, "yes" if (m99 < r2m <= ma10) else "NO",
            "yes" if (m90 < r1 <= ma10) else "NO",
            "yes" if (m90 < r2 <= ma10) else "NO"))
    pb = os.path.join(a.outdir, "partB.tsv")
    with open(pb, "w") as f:
        f.write("pot\tpiece\test_within_p90\test_within_p99\test_across_p10"
                "\test_gap_p90\test_gap_p99\tk_R1\tR1_theta\tR1_inside_gap_p99"
                "\tR2_theta\tR2_inside_gap_p99"
                "\tmst_within_p90\tmst_within_p99\tmst_across_p10"
                "\tmst_gap_p90\tmst_gap_p99\tk_R1_mst\tR1_mst_theta\tR1_mst_inside_gap_p99"
                "\tR2_mst_theta\tR2_mst_inside_gap_p99"
                "\tR1_inside_gap_p90\tR2_inside_gap_p90\n")
        for r in out_rows:
            f.write("\t".join(r) + "\n")
    th = os.path.join(a.outdir, "thetas.tsv")
    with open(th, "w") as f:
        f.write("pot\tpiece\tR1\tR2\n")
        for r in out_rows:
            f.write("%s\t%s\t%s\t%s\n" % (r[0], r[1], r[8], r[10]))
    print("[B43] k_R1 = %.5f (est: Pot A median within-p90 %.4f -> 3.4)"
          % (k_r1, float(np.median([float(r[ci["est_within_p90"]]) for r in pa]))))
    print("[B43] k_R1_mst = %.5f (mst: Pot A median within-p90 %.4f -> 3.4)"
          % (k_mst, float(np.median([float(r[ci["mst_within_p90"]]) for r in pa]))))
    for r in out_rows:
        print("[B43] %s %s: EST gap_p90 %+.3f gap_p99 %+.3f | MST gap_p90 %+.3f gap_p99 %+.3f"
              " | R1 %.3f R2 %.3f (mst R1 %.3f R2 %.3f)"
              % (r[0], r[1], float(r[5]), float(r[6]), float(r[15]), float(r[16]),
                 float(r[8]), float(r[10]), float(r[18]), float(r[20])))
    print("[B43] wrote %s and %s" % (pb, th))


def cmd_figure(a):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import glob
    js = sorted(glob.glob(os.path.join(a.partA_dir, "piece_*.json")))
    n = len(js)
    ncol = 3
    nrow = n
    fig, axes = plt.subplots(nrow, ncol, figsize=(4.0 * ncol, 2.1 * nrow), squeeze=False)
    for k, jp in enumerate(js):
        row = json.load(open(jp))
        lt = row["ladder_theta_deg"]
        # column 0 and 1: the two orientation rules' turn distributions over the WHOLE range,
        # nothing truncated at 90 deg (the first run's histogram stopped there and dropped the
        # near-180-degree tail; the coverage line in the title proves nothing is lost now)
        for col, fld in ((0, "est"), (1, "mst")):
            ax = axes[k][col]
            h = row["turn_%s_hist" % fld]
            edges = np.asarray(h["edges"]); cnt = np.asarray(h["counts"])
            tot = max(1, cnt.sum())
            ax.bar(edges[:-1], cnt / float(tot), width=np.diff(edges), align="edge",
                   color="#88a" if fld == "est" else "#8a8", alpha=0.6, linewidth=0)
            st = row[fld]
            for q, c in (("p50", "#444"), ("p90", "#44f"), ("p99", "#22a")):
                if st["within"].get(q) is not None:
                    ax.axvline(st["within"][q], color=c, lw=0.8)
            if st["across"].get("n"):
                ax.axvline(st["across"]["p10"], color="#f22", lw=0.8)
                ax.axvline(st["across"]["p50"], color="#922", lw=0.8)
            ax.axvline(3.4, color="k", lw=1.4, ls="--")
            if lt == lt:
                ax.axvline(lt, color="g", lw=1.4, ls=":")
            ax.set_xlim(0, 180)
            ax.set_yscale("log")
            hc = row["hist_coverage"]
            ax.set_title("%s  %s field  S=%.3f  dropped=%d"
                         % (row["piece"], fld, row["spacing_requested_mm"],
                            hc["est_dropped"] + hc["mst_dropped"]), fontsize=7)
            ax.tick_params(labelsize=6)
        # column 2: the separability curve -- miss (across below theta) and false (within above
        # theta).  A usable theta is one where BOTH are near zero at the same abscissa.
        ax = axes[k][2]
        th = row["sep"]["est"]["thetas"]
        for fld, ls, c in (("est", "-", "#1a1"), ("mst", "--", "#17c")):
            sp = row["sep"][fld]
            ax.plot(th, sp["miss"], ls, color=c, lw=1.1, marker="o", ms=2)
            ax.plot(th, sp["false"], ls, color="#c33", lw=1.1, marker="s", ms=2)
        ax.axvline(3.4, color="k", lw=1.2, ls="--")
        if lt == lt:
            ax.axvline(lt, color="g", lw=1.2, ls=":")
        ax.set_xscale("log")
        ax.set_ylim(-0.02, 1.02)
        ax.set_title("separability: green=miss red=false  solid=est dashed=mst", fontsize=7)
        ax.tick_params(labelsize=6)
    fig.suptitle("ticket 43 Part A: neighbour-turn distributions per sherd, est (viewpoint) vs mst "
                 "(pipeline rule), black=3.4, green=ladder theta; separability vs theta at right")
    fig.tight_layout()
    fig.savefig(a.out, dpi=110)
    print("[FIG43] wrote %s" % a.out)


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("selftest")
    sp = sub.add_parser("pieces"); sp.add_argument("--spec", required=True); sp.add_argument("--outdir", required=True); sp.add_argument("--seed", type=int, default=4301)
    sp = sub.add_parser("rules"); sp.add_argument("--partA-dir", required=True); sp.add_argument("--outdir", required=True)
    sp = sub.add_parser("figure"); sp.add_argument("--partA-dir", required=True); sp.add_argument("--out", required=True)
    a = p.parse_args()
    if a.cmd == "selftest":
        sys.exit(cmd_selftest(a))
    if a.cmd == "pieces":
        sys.exit(cmd_pieces(a))
    if a.cmd == "rules":
        sys.exit(cmd_rules(a))
    if a.cmd == "figure":
        sys.exit(cmd_figure(a))
    p.error("unknown command")


if __name__ == "__main__":
    main()
