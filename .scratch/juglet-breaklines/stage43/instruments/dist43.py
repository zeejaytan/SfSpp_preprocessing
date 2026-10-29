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

    est     the pipeline's own re-estimation (grow38 arm B): PCA over k = max(5, min(20, n/1000))
            neighbours of the sampled cloud, each flipped towards the PCD viewpoint (0,0,0)
            exactly as PCL's NormalEstimation does.  This is the headline field: it is what
            theta actually gates, and it is NOT degenerate against the triangle-based label.
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


def pca_normals(pts, k):
    """PCA normal over the k nearest neighbours, then the viewpoint flip (grow38 arm B)."""
    from scipy.spatial import cKDTree
    tree = cKDTree(pts)
    kq = min(k + 1, len(pts))
    _d, nb = tree.query(pts, k=kq, workers=-1)
    Q = pts[nb]                                   # (n,kq,3)
    C = Q - Q.mean(axis=1, keepdims=True)
    cov = np.einsum("mki,mkj->mij", C, C)
    _w, V = np.linalg.eigh(cov)
    nrm = V[:, :, 0]
    return orient(nrm, pts)


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
    n_est = pca_normals(pts, pipeline_k(len(pts)))
    fnrm = orient(fnrm_raw, pts)
    _i, _j, turn_est, turn_face, fold = folded_pairs(pts, n_est, fnrm)
    lab = fold < FOLD_LABEL_DEG                  # True = WITHIN-FACE
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
                "margin_p10_across_minus_p99_within": None},
        "face": {"within": dist_stats(turn_face[lab]), "across": head_stats(turn_face[~lab]),
                 "margin_p10_across_minus_p99_within": None},
        "turn_est_hist": None, "fold_hist": None,
    }
    for fld in ("est", "face"):
        w = row[fld]["within"]
        a = row[fld]["across"]
        if w.get("n") and a.get("n"):
            row[fld]["margin_p10_across_minus_p99_within"] = a["p10"] - w["p99"]
    # keep a coarse histogram for the figure without dumping every angle
    h_e, edges = np.histogram(turn_est, bins=200, range=(0.0, 90.0))
    row["turn_est_hist"] = {"counts": h_e.tolist(), "edges": edges.tolist()}
    h_f, _ = np.histogram(turn_face, bins=200, range=(0.0, 180.0))
    row["turn_face_hist"] = h_f.tolist()
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
    hdr = ("pot\tpiece\tspacing_req_mm\tspacing_ach_mm\tpoints\tfold_radius_med_mm"
           "\tn_pairs\test_within_p50\test_within_p90\test_within_p99"
           "\test_across_p10\test_across_p50\test_margin"
           "\tface_within_p50\tface_within_p90\tface_within_p99"
           "\tface_across_p10\tface_across_p50\tface_margin\tladder_theta\n")
    with open(tsv, "w") as out:
        out.write(hdr)
        for r in rows:
            row = measure_piece(r, a.seed)
            rows_json_path = os.path.join(a.outdir, "piece_%s.json" % r[1])
            with open(rows_json_path, "w") as jf:
                json.dump(row, jf, sort_keys=True)
            e, fa = row["est"], row["face"]
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
            ]) + "\n")
            print("[A43] %s %s: within p50/p90/p99 = %.3f/%.3f/%.3f  across p10/p50 = %.3f/%.3f  margin %.3f  rho_med %.2f mm"
                  % (r[0], r[1], e["within"]["p50"], e["within"]["p90"], e["within"]["p99"],
                     e["across"]["p10"], e["across"]["p50"],
                     e["margin_p10_across_minus_p99_within"], row["fold_radius_med_mm"]))
    print("[A43] wrote %s" % tsv)


def cmd_rules(a):
    """R1: theta = k x within p90, k fixed so Pot A's median lands at 3.4.
    R2: theta = sqrt(within p90 x across p10) (geometric mid-gap).
    Inside-gap test: within_p99 < theta <= across_p10 on the est field."""
    with open(os.path.join(a.partA_dir, "partA.tsv")) as f:
        rd = [ln.rstrip("\n").split("\t") for ln in f][1:]
    pa = [r for r in rd if r[0] == "Pot_A"]
    pa_p90 = [float(r[8]) for r in pa]
    k_r1 = 3.4 / float(np.median(pa_p90))
    out_rows = []
    for r in rd:
        w90 = float(r[8]); w99 = float(r[9]); a10 = float(r[10])
        r1 = k_r1 * w90
        r2 = math.sqrt(w90 * a10) if a10 > 0 else float("nan")
        in1 = (w99 < r1 <= a10)
        in2 = (w99 < r2 <= a10)
        out_rows.append((r[0], r[1], "%.4f" % w90, "%.4f" % w99, "%.4f" % a10,
                         "%.5f" % k_r1, "%.4f" % r1, "yes" if in1 else "NO",
                         "%.4f" % r2, "yes" if in2 else "NO"))
    pb = os.path.join(a.outdir, "partB.tsv")
    with open(pb, "w") as f:
        f.write("pot\tpiece\twithin_p90\twithin_p99\tacross_p10\tk_R1\tR1_theta\tR1_inside_gap"
                "\tR2_theta\tR2_inside_gap\n")
        for r in out_rows:
            f.write("\t".join(r) + "\n")
    th = os.path.join(a.outdir, "thetas.tsv")
    with open(th, "w") as f:
        f.write("pot\tpiece\tR1\tR2\n")
        for r in out_rows:
            f.write("%s\t%s\t%s\t%s\n" % (r[0], r[1], r[6], r[8]))
    print("[B43] k_R1 = %.5f (Pot A median within-p90 %.4f -> 3.4)" % (k_r1, float(np.median(pa_p90))))
    for r in out_rows:
        print("[B43] %s %s: R1 %.3f (%s)  R2 %.3f (%s)" % (r[0], r[1], float(r[6]), r[7], float(r[8]), r[9]))
    print("[B43] wrote %s and %s" % (pb, th))


def cmd_figure(a):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import glob
    js = sorted(glob.glob(os.path.join(a.partA_dir, "piece_*.json")))
    n = len(js)
    ncol = 3
    nrow = int(math.ceil(n / float(ncol)))
    fig, axes = plt.subplots(nrow, ncol, figsize=(4.2 * ncol, 2.6 * nrow), squeeze=False)
    for ax in axes.ravel():
        ax.set_visible(False)
    for k, jp in enumerate(js):
        row = json.load(open(jp))
        ax = axes[k // ncol][k % ncol]
        ax.set_visible(True)
        h = row["turn_est_hist"]
        edges = np.asarray(h["edges"]); cnt = np.asarray(h["counts"])
        tot = cnt.sum()
        lab = np.asarray(row["turn_face_hist"])
        # split the est histogram into within/across by refolding is not possible from the
        # histogram alone, so draw the est-field total and mark the percentiles instead
        ax.bar(edges[:-1], cnt / max(1, tot), width=np.diff(edges), align="edge",
               color="#88a", alpha=0.6, linewidth=0)
        e = row["est"]
        for q, c in (("p50", "#444"), ("p90", "#44f"), ("p99", "#22a")):
            ax.axvline(e["within"][q], color=c, lw=0.8)
        if e["across"].get("n"):
            ax.axvline(e["across"]["p10"], color="#f22", lw=0.8)
            ax.axvline(e["across"]["p50"], color="#922", lw=0.8)
        ax.axvline(3.4, color="k", lw=1.4, ls="--")
        lt = row["ladder_theta_deg"]
        if lt == lt:
            ax.axvline(lt, color="g", lw=1.4, ls=":")
        ax.set_xlim(0, 40)
        ax.set_yscale("log")
        ax.set_title("%s\nS=%.3f rho=%.2f n=%d" % (row["piece"], row["spacing_requested_mm"],
                     row["fold_radius_med_mm"], row["sampled_points"]), fontsize=8)
        ax.tick_params(labelsize=7)
    fig.suptitle("ticket 43 Part A: neighbour-turn distributions (est normals), black=3.4, green=ladder theta")
    fig.tight_layout()
    fig.savefig(a.out, dpi=140)
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
