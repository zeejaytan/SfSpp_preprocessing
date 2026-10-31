#!/usr/bin/env python3
"""Ticket 39 instrument: the three derived quantities the own-mode question turns on, plus the
distinct point count of each written surface.

Nothing here re-implements a reader or a statistic that already exists: the PLY reader, the
normal fallback and the folded-angle definition are measure34's (the file beside this one, copied
verbatim from stage38).  What is new is only the bookkeeping ticket 39 asks for:

  distinct   the number of distinct positions in a surface, coordinates rounded to 1e-4 mm --
             the same rounding the coordinator's check38.py used, which is why its 2 471 / 3 979
             can be read against these numbers.
  shared     the count of the smaller surface's distinct positions that also appear in the
             larger, and the same the other way round, with the fraction each way and of the
             smaller.  Two surfaces that are an inside and an outside of one wall share almost
             nothing; two surfaces that nest share most of one.
  meandot    the dot product of the two surfaces' mean normals, each normalised.  Positive means
             the two sheets face the same way, negative means they face opposite ways.
  ang        the median folded angle, per matching position, between the two surfaces' own
             normals.  Folded, so it cannot tell 0 from 180 -- meandot is the sign.

usage:
  nest39.py selftest
  nest39.py count --ply S0.ply --tag T --outdir DIR
  nest39.py pair --a S0.ply --b S1.ply --tag T --outdir DIR
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import measure34 as M          # noqa: E402

ROUND = 4                      # 1e-4 mm, check38.py's rounding


def load(path):
    """-> (xyz, normals, source).  A PLY without normals gets measure34's pca fallback, and the
    source is reported so a table never silently mixes the two."""
    d = M.read_ply(path)
    pts = M.ply_xyz(d)
    n = M.ply_normals(d)
    if n is None:
        n, _c = M.pca_normals(pts, M.NORM_PCA_K)
        return pts, n, "pca%d" % M.NORM_PCA_K
    return pts, n, "ply"


def distinct_index(pts):
    """rounded position -> the index of its first occurrence.  Rounding is what makes two files
    written by the same run comparable: the pipeline rewrites the same point into both surfaces
    from the same bytes, so the positions are equal before rounding too, and the rounding only
    absorbs the ASCII round-trip."""
    seen = {}
    for i, row in enumerate(np.round(pts, ROUND)):
        key = (float(row[0]), float(row[1]), float(row[2]))
        if key not in seen:
            seen[key] = i
    return seen


def mean_normal(n):
    m = np.asarray(n, dtype=np.float64).mean(axis=0)
    ln = float(np.linalg.norm(m))
    return m / ln if ln > 0.0 else m


def pair_row(pts0, nrm0, src0, pts1, nrm1, src1, tag=""):
    i0 = distinct_index(pts0)
    i1 = distinct_index(pts1)
    common = set(i0) & set(i1)
    shared = len(common)
    d0, d1 = len(i0), len(i1)
    smaller = min(d0, d1)
    row = {"tag": tag,
           "n0": int(len(pts0)), "n0_distinct": d0, "normal_src_a": src0,
           "n1": int(len(pts1)), "n1_distinct": d1, "normal_src_b": src1,
           "shared": shared,
           "shared_over_a": (shared / float(d0)) if d0 else 0.0,
           "shared_over_b": (shared / float(d1)) if d1 else 0.0,
           "shared_over_smaller": (shared / float(smaller)) if smaller else 0.0,
           "mean_normal_dot": float(mean_normal(nrm0) @ mean_normal(nrm1)),
           "matched": shared, "median_point_normal_angle_deg": None}
    if shared:
        a = np.array([i0[k] for k in common], dtype=np.int64)
        b = np.array([i1[k] for k in common], dtype=np.int64)
        row["median_point_normal_angle_deg"] = float(np.median(M.folded_angle_deg(nrm0[a], nrm1[b])))
    return row


def cmd_pair(a):
    p0, n0, s0 = load(a.a)
    p1, n1, s1 = load(a.b)
    row = pair_row(p0, n0, s0, p1, n1, s1, tag=a.tag)
    row.update({"surface_a": a.a, "surface_b": a.b, "round_mm": 10.0 ** -ROUND})
    os.makedirs(a.outdir, exist_ok=True)
    with open(os.path.join(a.outdir, "nest_%s.json" % a.tag), "w") as f:
        json.dump(row, f, indent=1, sort_keys=True)
    ang = row["median_point_normal_angle_deg"]
    print("[NEST] %s n0=%d (distinct %d) n1=%d (distinct %d) shared=%d "
          "of_a=%.4f of_b=%.4f of_smaller=%.4f meandot=%+.4f ang=%s deg (normals a:%s b:%s)"
          % (a.tag, row["n0"], row["n0_distinct"], row["n1"], row["n1_distinct"], row["shared"],
             row["shared_over_a"], row["shared_over_b"], row["shared_over_smaller"],
             row["mean_normal_dot"],
             "na" if ang is None else "%.3f" % ang, s0, s1))
    return 0


def cmd_count(a):
    """Point count and distinct point count of one written surface.  Distinct is what makes a
    nesting claim measurable: the pipeline rewrites the same point into both surfaces, so the
    written files repeat positions and a raw count overstates a surface."""
    pts, _n, src = load(a.ply)
    d = distinct_index(pts)
    row = {"ply": a.ply, "tag": a.tag, "points": int(len(pts)), "distinct": len(d),
           "normal_src": src, "round_mm": 10.0 ** -ROUND}
    os.makedirs(a.outdir, exist_ok=True)
    with open(os.path.join(a.outdir, "distinct_%s.json" % a.tag), "w") as f:
        json.dump(row, f, indent=1, sort_keys=True)
    print("[NEST-COUNT] %s points=%d distinct=%d (normals %s)"
          % (a.tag, row["points"], row["distinct"], src))
    return 0


def selftest():
    """The cases that would catch a wrong shared count or a sign-blind meandot."""
    bad = 0
    g = np.stack(np.meshgrid(np.arange(5.0), np.arange(5.0)), axis=-1).reshape(-1, 2)
    p = np.column_stack([g, np.zeros(len(g))])
    up = np.tile(np.array([0.0, 0.0, 1.0]), (len(p), 1))

    r = pair_row(p, up, "t", p + np.array([0.0, 0.0, 2.0]), up, "t")
    ok = r["shared"] == 0 and abs(r["mean_normal_dot"] - 1.0) < 1e-12 and r["n0_distinct"] == len(p)
    print("[NEST-SELFTEST] %s sheet 2 mm away: shared=%d meandot=%+.4f distinct=%d (want 0/+1.0000/%d)"
          % ("ok  " if ok else "FAIL", r["shared"], r["mean_normal_dot"], r["n0_distinct"], len(p)))
    bad += 0 if ok else 1

    # folded, so the angle reads 0.0 for opposed normals too -- that is the definition, and it is
    # exactly why meandot is reported beside it: the angle cannot carry the sign, meandot must.
    r = pair_row(p, up, "t", p, -up, "t")
    ok = (r["shared"] == len(p) and abs(r["mean_normal_dot"] + 1.0) < 1e-12
          and abs(r["median_point_normal_angle_deg"]) < 1e-9)
    print("[NEST-SELFTEST] %s same sheet, normals flipped: shared=%d meandot=%+.4f ang=%.1f deg "
          "(want %d/-1.0000/0.0 -- folded angle is sign-blind by definition, meandot carries it)"
          % ("ok  " if ok else "FAIL", r["shared"], r["mean_normal_dot"],
             r["median_point_normal_angle_deg"], len(p)))
    bad += 0 if ok else 1

    r = pair_row(p, up, "t", p + np.array([0.0, 0.0, 3e-5]), up, "t")
    ok = r["shared"] == len(p) and r["shared_over_smaller"] == 1.0
    print("[NEST-SELFTEST] %s same sheet 3e-5 mm away: shared=%d of_smaller=%.4f "
          "(want %d/1.0000 -- the 1e-4 mm rounding absorbs it)"
          % ("ok  " if ok else "FAIL", r["shared"], r["shared_over_smaller"], len(p)))
    bad += 0 if ok else 1

    print("[NEST-SELFTEST] %s (%d failures)" % ("PASS" if bad == 0 else "FAIL", bad))
    return 0 if bad == 0 else 5


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    s = sub.add_parser("selftest"); s.set_defaults(fn=lambda a: selftest())
    s = sub.add_parser("count")
    s.add_argument("--ply", required=True); s.add_argument("--tag", default="surface")
    s.add_argument("--outdir", required=True)
    s.set_defaults(fn=cmd_count)
    s = sub.add_parser("pair")
    s.add_argument("--a", required=True); s.add_argument("--b", required=True)
    s.add_argument("--tag", default="pair"); s.add_argument("--outdir", required=True)
    s.set_defaults(fn=cmd_pair)
    a = ap.parse_args(argv)
    if not getattr(a, "fn", None):
        ap.print_help()
        return 2
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
