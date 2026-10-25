#!/usr/bin/env python3
"""Ticket 295, Q2-Q5 -- the conservator's reading measured lane by lane.

PRE-REGISTERED BEFORE ANY LANE WAS MEASURED.  Thresholds (T) and the vocabulary they produce were
fixed in this docstring before the first lane ran; the numbers the run then produced are in the
ticket, not here.

  T1 BAR       2.0 mm  the edgeline bar (tickets 292/294).
  T2 EDGE     100 deg  the material-edge statistic (tickets 280/286); 108 deg (ticket 293) alongside.
  T3 TILT      45 deg  a surface pitched further than this off its neighbour is a different facet.
  T4 BAND      2.0 mm  corridor radius around a reference dot for the welded-facet test.
  T5 WELDED   >=20% of the stretch's dots own a kept-material point inside T4 whose PCA(k=20) normal is
               more than T3 off the reference plane, AND the tilted band runs >=5 mm along the
               stretch, AND the control (the reference's non-stretch dots, same test) stays <5%.
  T6 MATERIAL  0.5 mm  plane offset separating a coplanar continuation from a step in the face.
  T7 PAIRING  measured, never taken from the k index: a lane's two sides are paired by the median
               distance from the reference's ridden surface to each of our kept clusters.

The extra-surface test reports one of
  coplanar   angle < 10 deg and |offset| <  T6 -- our surface continues the same face; their line is
                                                 inset; nothing was welded.
  step       angle < 10 deg and |offset| >= T6 and |offset| >= the control's -- a step inside the face.
  welded     T5 met                            -- our kept surface carries a distinct pitched facet.
  tilted_face angle >= 10 deg but T5 not met   -- a distinct face, too small/ragged to call a band.
  undefined  fewer than 30 kept points inside T4 of the stretch, so the test cannot be made.

THE INSTRUMENT (amended once, before any lane's verdict was read, and only because the pre-registered
version failed on the data): the first version of this test fitted a reference plane to the face 3-7 mm
from the reference's dots and compared our band's plane to it.  That annulus wraps around a >100 deg
edge wherever the reference line runs along one -- on Pot D 22 the control came back with an 81 deg
plane angle and a 13.6 mm offset, which is a corner, not a face -- so the reference plane is unusable
there and the test was replaced by the direct comparison below.  No threshold moved: T3, T5 and T6 are
as registered above.
  For every kept-material point inside T4 of the reference's dots, take the authors' own supplied
  surface normal at its nearest point on the ridden surface and our PCA(k=20) normal there, and record
  the angle between them (|dot|, sign-free) and the signed offset along their normal.  A welded facet
  shows as a share of band points pitched >= T3 off the face they say the edge belongs to; a step shows
  as a flat but displaced band; a coplanar continuation shows neither.
  The same test runs on the whole of their line (w_*), on the stretch only (p_*), and on their
  non-stretch dots as the control (pc_*) -- the lane's own curvature and noise are the baseline.

"""
import argparse
import json
import math
import os
import sys

import numpy as np
from scipy.spatial import ConvexHull, cKDTree

import p295_lib as L

R293 = "/data/gpfs/projects/punim2657/SfSpp/runs/20261025-0456_3ada802_p293-census"

LANES = [
    ("Pot_C_Piece_03", 1),   # Phase A: our dots survive
    ("Pot_I_Piece_25", 0),   # Phase A
    ("Pot_I_Piece_25", 1),   # Phase A
    ("Pot_D_Piece_22", 0),   # Phase B
    ("Pot_D_Piece_27", 0),
    ("Pot_D_Piece_27", 1),
    ("Pot_E_Piece_16", 0),
    ("Pot_H_Piece_02", 1),
    ("Pot_H_Piece_10", 1),
    ("Pot_I_Piece_06", 1),
    ("Pot_I_Piece_13", 1),
]

T_BAR, T_EDGE, T_EDGE2, T_TILT, T_BAND, T_MAT = 2.0, 100.0, 108.0, 45.0, 2.0, 0.5
T_WELD_SHARE, T_WELD_LEN, T_CTRL = 20.0, 5.0, 5.0
BAND2 = 4.0   # T4b: corridor widened to this only when fewer than 30 kept points fall inside T4, and
              # every row that used it says so in band_r
FLAT_ANGLE = 10.0

# 293's own numbers for the three Phase-A lanes, to be reproduced (crosspair.tsv).
CP293 = {
    ("Pot_C_Piece_03", 1, 0): dict(median=6.190, cov_ours=0.00, cov_auth=0.00, max=26.715),
    ("Pot_C_Piece_03", 1, 1): dict(median=11.287, cov_ours=17.99, cov_auth=50.00, max=57.172),
    ("Pot_I_Piece_25", 0, 0): dict(median=6.910, cov_ours=0.00, cov_auth=0.00, max=7.549),
    ("Pot_I_Piece_25", 0, 1): dict(median=0.680, cov_ours=100.00, cov_auth=100.00, max=1.420),
    ("Pot_I_Piece_25", 1, 0): dict(median=0.568, cov_ours=100.00, cov_auth=100.00, max=1.752),
    ("Pot_I_Piece_25", 1, 1): dict(median=6.951, cov_ours=0.00, cov_auth=0.00, max=7.722),
}
# 293's lanes_fresh lengths for our own line, to be reproduced from the assign tables.
ARC293 = {("Pot_C_Piece_03", 1): (339, 611.262),
          ("Pot_I_Piece_25", 0): (58, 104.794),
          ("Pot_I_Piece_25", 1): (67, 120.573)}


def pct(x, p):
    return L.q(x, p)


def ang(n1, n2):
    d = abs(float(np.dot(n1, n2)) / (np.linalg.norm(n1) * np.linalg.norm(n2) + 1e-12))
    return float(np.degrees(np.arccos(min(1.0, d))))


def sub(Q, n, seed=29595):
    if len(Q) <= n:
        return Q
    rng = np.random.default_rng(seed)
    return Q[np.sort(rng.choice(len(Q), n, replace=False))]


def patch_stats(Q, p0, w, u, v):
    """Extent and area of a surface patch in the axis frame.  Area is the convex hull in the (a, r*dth)
    chart; it overestimates a concave patch and is used only to compare two sides the same way."""
    a, r, an = L.axial(Q, p0, w, u, v)
    th = np.radians(an)
    th0 = math.atan2(float(np.sin(th).mean()), float(np.cos(th).mean()))
    dth = (th - th0 + math.pi) % (2.0 * math.pi) - math.pi
    X = np.column_stack([a - a.mean(), r * dth])
    area = float("nan")
    if len(X) >= 4:
        try:
            area = float(ConvexHull(X).volume)
        except Exception:
            area = float("nan")
    return dict(n=len(Q), r5=pct(r, 5), r50=pct(r, 50), r95=pct(r, 95),
                a5=pct(a, 5), a50=pct(a, 50), a95=pct(a, 95), area=area,
                a_span=float(a.max() - a.min()), s_span=float(X[:, 1].max() - X[:, 1].min()))


def faces_test(anchor, K, Ktree, Sref, Stree, Nref):
    """Are we on the authors' face, a step off it, or a different facet?  Measured in a corridor.

    For every kept-material point inside T4 (T4b if T4 holds fewer than 30) of the reference's dots,
    compare our PCA(k=20) normal with the authors' own supplied normal at the nearest point of the
    ridden surface, and take the signed offset along that normal.  No plane is fitted, so a >100 deg
    edge in the corridor cannot turn the reference into a corner."""
    out = dict(n=0, band_r=float("nan"), ang_med=float("nan"), ang_p90=float("nan"),
               ang_share_gt45=float("nan"), s_med=float("nan"), s_sign=float("nan"),
               dot_share_gt45=float("nan"))
    if len(anchor) < 1:
        return out
    idx = []
    r = T_BAND
    for r in (T_BAND, BAND2):
        idx = [np.asarray(i, dtype=int) for i in Ktree.query_ball_point(anchor, r) if len(i)]
        if sum(len(i) for i in idx) >= 30:
            break
    if not idx:
        return out
    band = np.unique(np.concatenate(idx))
    out["n"] = int(len(band))
    out["band_r"] = float(r)
    if len(band) < 30:
        return out
    Q = K[band]
    j = Stree.query(Q)[1]
    nref = np.asarray(Nref[j], dtype=float)
    nref = nref / (np.linalg.norm(nref, axis=1, keepdims=True) + 1e-12)
    Nb = L.local_normals(Q, Ktree, k=20)
    a = np.degrees(np.arccos(np.clip(np.abs((Nb * nref).sum(1)), 0.0, 1.0)))
    sgn = ((Q - Sref[j]) * nref).sum(1)
    out["ang_med"] = float(np.median(a))
    out["ang_p90"] = float(np.percentile(a, 90))
    out["ang_share_gt45"] = float(100.0 * (a > T_TILT).mean())
    out["s_med"] = float(np.median(np.abs(sgn)))
    out["s_sign"] = float(np.median(sgn))
    jj = cKDTree(Q).query(anchor)[1]
    out["dot_share_gt45"] = float(100.0 * (a[jj] > T_TILT).mean())
    return out


EMPTY = dict(n=0, band_r=float("nan"), ang_med=float("nan"), ang_p90=float("nan"),
             ang_share_gt45=float("nan"), s_med=float("nan"), s_sign=float("nan"),
             dot_share_gt45=float("nan"))


def classify_tilt(p, pc, band_len):
    if p["n"] < 30:
        return "undefined"
    ctrl = pc["ang_share_gt45"] if pc["ang_share_gt45"] == pc["ang_share_gt45"] else 0.0
    if p["dot_share_gt45"] >= T_WELD_SHARE and band_len >= T_WELD_LEN and ctrl < T_CTRL:
        return "welded"
    cs = pc["s_med"] if pc["s_med"] == pc["s_med"] else 0.0
    if p["ang_med"] < FLAT_ANGLE and p["s_med"] >= T_MAT and p["s_med"] >= cs:
        return "step"
    if p["ang_med"] < FLAT_ANGLE:
        return "coplanar"
    return "tilted_face"


def read_assign(path):
    rows = []
    with open(path) as fh:
        fh.readline()
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 9:
                rows.append(p)
    ours = np.array([[float(r[2]), float(r[3]), float(r[4])] for r in rows if r[0] == "ours"], dtype=float)
    auth = np.array([[float(r[2]), float(r[3]), float(r[4])] for r in rows if r[0] != "ours"], dtype=float)
    return ours, auth, rows


def read_tsv(path):
    with open(path) as fh:
        hdr = fh.readline().rstrip("\n").split("\t")
        return [dict(zip(hdr, line.rstrip("\n").split("\t"))) for line in fh if line.strip()]


def lane(piece, k):
    p0, w, u, v = L.frame(os.path.join(L.CORP, "Axes", piece + "_Axis.xyz"))
    hdr, cl, labels, P = L.read_dump(os.path.join(R293, "out", "diag", piece + ".diag276.txt"))
    kept = L.kept_clusters(labels)
    keptmask = np.isin(labels, kept)
    K = P[keptmask]
    D = P[~keptmask & (labels != -1)]
    U = P[labels == -1]
    Ktree = cKDTree(K)
    gK, bK = L.boundary_mask(K, T_EDGE)
    Fedge = K[bK]
    Rtree = cKDTree(Fedge)

    S = {}
    SN = {}
    for s in (0, 1):
        S[s], SN[s] = L.read_xyz6(os.path.join(L.CORP, "Surfaces", "%s_Surface_%d.xyz" % (piece, s)))
    BL = L.read_pcd_xyz(os.path.join(L.CORP, "Breaklines", "%s_Breakline_%d.pcd" % (piece, k)))
    if len(BL) < 8:
        raise SystemExit("lane %s Bl%d: %d reference dots" % (piece, k, len(BL)))

    dS = {s: cKDTree(S[s]).query(BL)[0] for s in (0, 1)}
    rides = 0 if pct(dS[0], 50) <= pct(dS[1], 50) else 1
    other = 1 - rides
    margin = pct(dS[other], 50) - pct(dS[rides], 50)
    Sride = S[rides]
    Stree = cKDTree(Sride)
    gS, bS = L.boundary_mask(Sride, T_EDGE)
    FedS = Sride[bS]
    own_edge = gS[Stree.query(BL)[1]]
    own_d_rim = cKDTree(FedS).query(BL)[0] if len(FedS) else np.full(len(BL), np.nan)

    d_rim = Rtree.query(BL)[0]
    d_kept = Ktree.query(BL)[0]

    mask = d_rim > T_BAR
    rr = L.runs(mask)
    arc_all = L.polyline_length(BL)
    stretch = dict(n=0, i0=-1, i1=-1, arc=0.0, share=0.0)
    if rr:
        arcs = sorted([(L.polyline_length(BL[a:b + 1]), a, b) for a, b in rr], reverse=True)
        arc, a, b = arcs[0]
        stretch = dict(n=int(b - a + 1), i0=int(a), i1=int(b), arc=float(arc),
                       share=float(100.0 * arc / arc_all) if arc_all > 0 else float("nan"))
    if stretch["n"] > 0:
        Sd = BL[stretch["i0"]:stretch["i1"] + 1]
    else:
        Sd = np.zeros((0, 3), dtype=float)
    rest = np.ones(len(BL), dtype=bool)
    if stretch["n"] > 0:
        rest[stretch["i0"]:stretch["i1"] + 1] = False
    Rest = BL[rest]

    # ---- which of OUR dump labels is nearest each reference dot (Q2/Q5: does their line lie on
    # material the pipeline dropped?).  Dump ids are survivors re-issued in DESCENDING SIZE order
    # (ticket 283), so an id here names a size rank on this piece, never 293's PAIR or classify face.
    Pt = cKDTree(P)
    _, nidx = Pt.query(BL)
    nlab = labels[nidx]
    near = {}
    isk = np.isin(nlab, kept)
    near["near_neg1"] = round(float(100.0 * (nlab == -1).mean()), 2)
    near["near_kept"] = round(float(100.0 * isk.mean()), 2)
    near["near_dropped"] = round(float(100.0 * ((nlab != -1) & ~isk).mean()), 2)
    vals, cnts = np.unique(nlab, return_counts=True)
    top = int(vals[int(np.argmax(cnts))])
    near["near_top_lab"] = ("c%d" % top) if top >= 0 else "-1"
    near["near_top_share"] = round(float(100.0 * cnts.max() / cnts.sum()), 2)
    near["near_top_n"] = int((labels == top).sum())
    if stretch["n"] > 0:
        _, sidx = Pt.query(Sd)
        slab = labels[sidx]
        sk = np.isin(slab, kept)
        near["s_near_neg1"] = round(float(100.0 * (slab == -1).mean()), 2)
        near["s_near_kept"] = round(float(100.0 * sk.mean()), 2)
        near["s_near_dropped"] = round(float(100.0 * ((slab != -1) & ~sk).mean()), 2)
        sv, sc = np.unique(slab, return_counts=True)
        stop = int(sv[int(np.argmax(sc))])
        near["s_near_top_lab"] = ("c%d" % stop) if stop >= 0 else "-1"
        near["s_near_top_share"] = round(float(100.0 * sc.max() / sc.sum()), 2)
        near["s_near_top_n"] = int((labels == stop).sum())

    Nr = SN[rides]
    wt = faces_test(BL, K, Ktree, Sride, Stree, Nr)
    if stretch["n"] >= 3:
        pt = faces_test(Sd, K, Ktree, Sride, Stree, Nr)
        ct = faces_test(Rest, K, Ktree, Sride, Stree, Nr) if int(rest.sum()) >= 3 else dict(EMPTY)
        cls = classify_tilt(pt, ct, stretch["arc"])
    else:
        pt = dict(EMPTY)
        ct = dict(EMPTY)
        cls = "no_stretch"

    # ---- pairing: which of our kept clusters is the face their line rides?  (T7)
    ourpts = {c: P[labels == c] for c in kept}
    ourtree = {c: cKDTree(ourpts[c]) for c in kept}
    theirtree = {s: cKDTree(S[s]) for s in (0, 1)}
    pair_rows = []
    best = None
    for c in kept:
        for s in (0, 1):
            pair_rows.append(dict(piece=piece, lane="Bl%d" % k, left="our_c%d" % c, right="authS%d" % s,
                                  n_left=len(ourpts[c]),
                                  d_left_to_right=round(float(np.median(theirtree[s].query(sub(ourpts[c], 3000))[0])), 4),
                                  d_right_to_left=round(float(np.median(ourtree[c].query(sub(S[s], 3000))[0])), 4)))
        rev = float(np.median(ourtree[c].query(sub(Sride, 3000))[0]))
        if best is None or rev < best[1]:
            best = (c, rev)
    for nm, Q in (("our_dropped", D), ("our_unclustered", U)):
        if len(Q) < 5:
            continue
        for s in (0, 1):
            pair_rows.append(dict(piece=piece, lane="Bl%d" % k, left=nm, right="authS%d" % s, n_left=len(Q),
                                  d_left_to_right=round(float(np.median(theirtree[s].query(sub(Q, 3000))[0])), 4),
                                  d_right_to_left=""))
    ours_face = best[0]
    alts = [float(np.median(ourtree[c].query(sub(Sride, 3000))[0])) for c in kept if c != ours_face]
    pair_margin = (min(alts) - best[1]) if alts else float("nan")

    oa = patch_stats(ourpts[ours_face], p0, w, u, v)
    aa = patch_stats(Sride, p0, w, u, v)

    ours_n = ours_arc = float("nan")
    ours_ride = ""
    ours_arc293 = float("nan")
    ap = os.path.join(R293, "out", "census", "%s_Bl%d.assign.tsv" % (piece, k))
    if os.path.exists(ap):
        O, A, rows = read_assign(ap)
        ours_n = len(O)
        ours_arc = L.polyline_length(O)
        lab = np.array([int(r[7]) for r in rows if r[0] == "ours"], dtype=int)
        lab = lab[lab >= 0]
        ours_ride = "c%d" % np.bincount(lab).argmax() if len(lab) else ""
        if (piece, k) in ARC293:
            ours_arc293 = ARC293[(piece, k)][1]

    # who sits further out: our edge, or their line?  and how far their stretch is from our material
    if stretch["n"] >= 3:
        cen = Sd.mean(0)
        near_rim = Fedge[np.linalg.norm(Fedge - cen, axis=1) <= 20.0]
        rim_med = (float(np.median(cKDTree(BL).query(near_rim)[0])) if len(near_rim) else float("nan"))
        stretch_kept = float(np.median(d_kept[stretch["i0"]:stretch["i1"] + 1]))
    else:
        rim_med = float("nan")
        stretch_kept = float("nan")

    row = dict(
        piece=piece, lane="Bl%d" % k,
        n_theirs=len(BL), arc_theirs=round(arc_all, 3),
        rides="authS%d" % rides, ride_margin=round(margin, 4),
        d_authS0_med=round(pct(dS[0], 50), 4), d_authS1_med=round(pct(dS[1], 50), 4),
        own_edge_med=round(pct(own_edge, 50), 4),
        own_d_rim_med=round(pct(own_d_rim, 50), 4),
        own_share_gt100=round(float(100.0 * (own_edge > T_EDGE).mean()), 2),
        own_share_gt108=round(float(100.0 * (own_edge > T_EDGE2).mean()), 2),
        chord_ratio=round(L.chord_ratio(BL), 4),
        endgap=round(float(np.linalg.norm(BL[-1] - BL[0])), 4),
        d_rim_med=round(pct(d_rim, 50), 4), d_rim_p95=round(pct(d_rim, 95), 4),
        d_rim_max=round(float(d_rim.max()), 4),
        share_drim_gt2=round(float(100.0 * (d_rim > T_BAR).mean()), 2),
        d_kept_med=round(pct(d_kept, 50), 4), d_kept_max=round(float(d_kept.max()), 4),
        stretch_n=stretch["n"], stretch_i0=stretch["i0"], stretch_i1=stretch["i1"],
        stretch_arc=round(stretch["arc"], 3), stretch_share=round(stretch["share"], 2),
        stretch_drim_med=round(pct(d_rim[mask], 50), 4) if mask.any() else float("nan"),
        stretch_drim_max=round(float(d_rim[mask].max()), 4) if mask.any() else float("nan"),
        stretch_dkept_med=round(stretch_kept, 4),
        rim_d_ref_med=round(rim_med, 4),
        band_area_mm2=round(stretch["arc"] * pct(d_rim[mask], 50), 1) if mask.any() else float("nan"),
        w_n=wt["n"], w_band_r=wt["band_r"], w_ang_med=round(wt["ang_med"], 3),
        w_ang_p90=round(wt["ang_p90"], 3), w_ang_share_gt45=round(wt["ang_share_gt45"], 2),
        w_s_abs=round(wt["s_med"], 4),
        p_n=pt["n"], p_band_r=pt["band_r"], p_ang_med=round(pt["ang_med"], 3),
        p_ang_p90=round(pt["ang_p90"], 3), p_ang_share_gt45=round(pt["ang_share_gt45"], 2),
        p_s_abs=round(pt["s_med"], 4), p_s_sign=round(pt["s_sign"], 4),
        p_dot_share_gt45=round(pt["dot_share_gt45"], 2),
        pc_n=ct["n"], pc_ang_med=round(ct["ang_med"], 3), pc_s_abs=round(ct["s_med"], 4),
        pc_ang_share_gt45=round(ct["ang_share_gt45"], 2),
        stat_class=("different_surface" if (cls == "welded" and best[1] > T_MAT) else cls),
        ours_face="c%d" % ours_face, pair_med=round(best[1], 4), pair_margin=round(pair_margin, 4),
        pair_verdict=("matched" if best[1] <= T_MAT else "not_matched"),
        our_n=oa["n"], their_n=aa["n"],
        our_r50=round(oa["r50"], 4), their_r50=round(aa["r50"], 4),
        our_a50=round(oa["a50"], 4), their_a50=round(aa["a50"], 4),
        our_area=round(oa["area"], 1), their_area=round(aa["area"], 1),
        our_a_span=round(oa["a_span"], 3), their_a_span=round(aa["a_span"], 3),
        our_s_span=round(oa["s_span"], 3), their_s_span=round(aa["s_span"], 3),
        **near,
        ours_n=ours_n, ours_arc=round(ours_arc, 3) if ours_arc == ours_arc else float("nan"),
        ours_arc293=ours_arc293, ours_ride=ours_ride,
    )
    detail = dict(row=row, stretch=stretch, whole=wt, stretch_test=pt, control=ct, arc_all=arc_all)
    return row, pair_rows, detail


def repro(outdir):
    rows = []
    for (piece, k, ak), exp in CP293.items():
        ap = os.path.join(R293, "out", "census", "%s_Bl%d.assign.tsv" % (piece, k))
        bp = os.path.join(R293, "out", "census", "%s_Bl%d.assign.tsv" % (piece, ak))
        if not (os.path.exists(ap) and os.path.exists(bp)):
            continue
        O, A, _ = read_assign(ap)
        _, T, _ = read_assign(bp)
        d = cKDTree(T).query(O)[0]
        got = dict(median=float(np.median(d)),
                   cov_ours=float(100.0 * (d <= T_BAR).mean()),
                   cov_auth=float(100.0 * (cKDTree(O).query(T)[0] <= T_BAR).mean()),
                   max=float(d.max()))
        for q in ("median", "cov_ours", "cov_auth", "max"):
            tol = 1.0 if q.startswith("cov") else 0.05
            ok = abs(got[q] - exp[q]) <= tol
            rows.append(dict(piece=piece, lane="Bl%d" % k, quantity="crosspair_vs_authBl%d.%s" % (ak, q),
                             recomputed=round(got[q], 4), quoted293=exp[q],
                             delta=round(got[q] - exp[q], 4), tol=tol, ok=int(ok)))
    for (piece, k), (n293, arc293) in ARC293.items():
        ap = os.path.join(R293, "out", "census", "%s_Bl%d.assign.tsv" % (piece, k))
        O, A, _ = read_assign(ap)
        got = dict(n=float(len(O)), arc=L.polyline_length(O))
        for q, exp in (("n", n293), ("arc", arc293)):
            tol = 0.0 if q == "n" else 0.05
            ok = abs(got[q] - exp) <= tol
            rows.append(dict(piece=piece, lane="Bl%d" % k, quantity="ours.%s" % q,
                             recomputed=round(got[q], 4), quoted293=exp,
                             delta=round(got[q] - exp, 4), tol=tol, ok=int(ok)))
    L.write_tsv(os.path.join(outdir, "repro295.tsv"), rows,
                ["piece", "lane", "quantity", "recomputed", "quoted293", "delta", "tol", "ok"])
    bad = [r for r in rows if not r["ok"]]
    print("repro: %d/%d within tolerance" % (len(rows) - len(bad), len(rows)))
    for r in bad:
        print("  MISMATCH", r)
    return len(bad)


def quote293(outdir):
    want = set((p, k) for p, k in LANES)
    pb = read_tsv(os.path.join(R293, "out", "phaseB.tsv"))
    keep = [r for r in pb if (r["piece"], int(r["lane"])) in want]
    if keep:
        L.write_tsv(os.path.join(outdir, "quoted293_phaseB.tsv"), keep, list(keep[0].keys()))
    print("quoted phaseB rows: %d" % len(keep))
    rows = []
    with open(os.path.join(R293, "out", "lanes_fresh.tsv")) as fh:
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 13 and (p[1], int(p[2])) in want:
                rows.append(dict(pot=p[0], piece=p[1], lane="Bl" + p[2], n_ours=p[3], n_auth=p[4],
                                 median=p[5], cov_ours=p[6], cov_auth=p[7], jumps=p[8], max_step=p[9],
                                 len_ours=p[10], len_auth=p[11], at_bar=p[12]))
    L.write_tsv(os.path.join(outdir, "quoted293_lanes_fresh.tsv"), rows,
                ["pot", "piece", "lane", "n_ours", "n_auth", "median", "cov_ours", "cov_auth",
                 "jumps", "max_step", "len_ours", "len_auth", "at_bar"])
    print("quoted lanes_fresh rows: %d" % len(rows))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--only")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    lanes = LANES
    if a.only:
        lanes = [x for x in LANES if ("%s_Bl%d" % x) == a.only or x[0] == a.only]
    if a.limit:
        lanes = lanes[:a.limit]
    rows = []
    pairs = []
    for piece, k in lanes:
        row, pr, det = lane(piece, k)
        rows.append(row)
        pairs.extend(pr)
        with open(os.path.join(a.outdir, "detail_%s_Bl%d.json" % (piece, k)), "w") as fh:
            json.dump(det, fh, indent=1, default=float)
        print(json.dumps(row, default=str))
    if rows:
        L.write_tsv(os.path.join(a.outdir, "lanes.tsv"), rows, list(rows[0].keys()))
    if pairs:
        L.write_tsv(os.path.join(a.outdir, "pairing.tsv"), pairs,
                    ["piece", "lane", "left", "right", "n_left", "d_left_to_right", "d_right_to_left"])
    repro(a.outdir)
    quote293(a.outdir)


if __name__ == "__main__":
    main()
