#!/usr/bin/env python3
"""analyse310a.py -- ticket 310 A2/A3/A4 from the Stage A TSVs.

Reads <root>/p<P>/s<S>/{written.tsv,basins.tsv,pool.tsv}.

The good/wrong LABEL exists on Piece 08 only: ang_good is the angle to the axis that
seated in ticket 308 (piece 08 seeds 1/4/5). On A_01/A_04 the same number is just the
angle to an unrelated axis, so those pieces are used for the control question (does the
worst-wall ranker agree with the line the writer puts first, and how many lines are
written at all), never for a separation table.

Sections:
  A3  prevalence: seeds whose FILE carries a line within 5 deg of the seating axis
  A2  separation: good vs wrong on piece 08, per statistic, threshold or no threshold
  A4  cheap nulls: good draw in the first 10/30 draws; its rank by full-cloud cost
  C   controls: A_01 / A_04 shape of the output, ranker vs writer

usage: analyse310a.py <root> [--gooddeg 5]
"""
import argparse
import os
import sys
from collections import defaultdict

import numpy as np

NUM = ("ang_good hub0 hub1 huball worst_pt maxovermin gm0 gm1 gmall gminl0 gminl1"
       " gminlall hinl0 hinl1 pott0 pott1 a_c0 a_c1 a_c0_c1 ld_c0 ld_c1 ld_c0_c1"
       " c1_of_opt0 c0_of_opt1 opt0_c0_pt opt1_c1_pt rough0 rough1 thick_std"
       " thick_range d_centroid d_bbox frac_in_r90 n10 n25 basin_size basin_rank_hub"
       " rank_written_hub").split()
INT = ("piece seed written basin_rank_hub rank_written_hub cluster basin_size"
       " rank_in_file rank is_rep").split()


def read_tsv(path):
    with open(path) as fh:
        head = fh.readline().rstrip("\n").split("\t")
        rows = []
        for line in fh:
            v = line.rstrip("\n").split("\t")
            if len(v) != len(head):
                continue
            r = dict(zip(head, v))
            for k in NUM:
                if k in r:
                    try:
                        r[k] = float(r[k])
                    except ValueError:
                        r[k] = float("nan")
            for k in INT:
                if k in r:
                    try:
                        r[k] = int(r[k])
                    except ValueError:
                        r[k] = -1
            for k in list(r):
                if k in ("piece", "seed", "cand", "kind") or k in INT:
                    continue
                try:
                    r[k] = float(r[k])
                except ValueError:
                    pass
            rows.append(r)
    return rows


def seeds_of(root, pieces):
    out = []
    for p in pieces:
        d = os.path.join(root, "p%d" % p)
        if not os.path.isdir(d):
            continue
        for s in sorted(os.listdir(d), key=lambda x: int(x[1:]) if x[1:].isdigit() else 0):
            if s.startswith("s") and os.path.isdir(os.path.join(d, s)):
                out.append((p, int(s[1:]), os.path.join(d, s)))
    return out


def fmt(v, w=7):
    if not np.isfinite(v):
        return " " * w + "-"
    return ("%*.*g" % (w, 4, v)) if abs(v) < 1e4 else ("%*.*e" % (w, 3, v))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--pieces", default="8,1,4")
    ap.add_argument("--goodpiece", type=int, default=8)
    ap.add_argument("--gooddeg", type=float, default=5.0)
    a = ap.parse_args()
    pieces = [int(x) for x in a.pieces.split(",") if x.strip()]
    cases = seeds_of(a.root, pieces)
    if not cases:
        print("no seed directories under", a.root)
        return 2

    rows_by_seed, pool_by_seed, basins_by_seed = {}, {}, {}
    for p, s, d in cases:
        for name, store in (("written.tsv", rows_by_seed), ("pool.tsv", pool_by_seed),
                            ("basins.tsv", basins_by_seed)):
            f = os.path.join(d, name)
            if os.path.isfile(f):
                store[(p, s)] = read_tsv(f)

    G = a.gooddeg
    gp = a.goodpiece
    ss8 = [s for (p, s) in rows_by_seed if p == gp]

    print("=" * 90)
    print("A3  PREVALENCE on Piece A_%02d -- seeds whose axis FILE carries a line within %.0f deg"
          % (gp, G))
    print("    of the seating axis, and whether that line is first in the file")
    print("=" * 90)
    wr = [s for s in ss8
          if any(r["written"] == 1 and r["ang_good"] < G for r in rows_by_seed[(gp, s)])]
    l0 = [s for s in ss8
          if any(r["written"] == 1 and r["rank_in_file"] == 0 and r["ang_good"] < G
                 for r in rows_by_seed[(gp, s)])]
    nl = [len([r for r in rows_by_seed[(gp, s)] if r["written"] == 1]) for s in ss8]
    print("seeds                      : %d" % len(ss8))
    print("write it (any position)    : %d of %d  (%.0f%%)  seeds %s"
          % (len(wr), len(ss8), 100.0 * len(wr) / max(len(ss8), 1),
             ",".join(str(x) for x in wr)))
    print("write it as LINE 0         : %d of %d  (%.0f%%)  seeds %s"
          % (len(l0), len(ss8), 100.0 * len(l0) / max(len(ss8), 1),
             ",".join(str(x) for x in l0)))
    print("lines written per file     : min %d, median %.1f, max %d"
          % (min(nl), float(np.median(nl)), max(nl)))
    print()
    print("per seed: (line no: angle to good axis / its rank by worst-wall cost / pool draws within %.0f deg)" % G)
    for s in ss8:
        rr = sorted([r for r in rows_by_seed[(gp, s)] if r["written"] == 1],
                    key=lambda r: r["rank_in_file"])
        npool = len([r for r in pool_by_seed.get((gp, s), []) if r["ang_good"] < G])
        print("  s%-2d  %s   pool=%d" %
              (s, "  ".join("%d:%.2f/%d" % (r["rank_in_file"], r["ang_good"],
                                            r["rank_written_hub"]) for r in rr), npool))

    print()
    print("=" * 90)
    print("A2  SEPARATION on Piece A_%02d -- good (angle < %.0f deg) vs wrong, every written line"
          % (gp, G))
    print("    and every 10-deg basin representative pooled over all seeds")
    print("=" * 90)
    good, wrong = defaultdict(list), defaultdict(list)
    nG = nW = 0
    for key, rows in rows_by_seed.items():
        if key[0] != gp:
            continue
        for r in rows:
            if not np.isfinite(r["ang_good"]):
                continue
            isg = r["ang_good"] < G
            tgt = good if isg else wrong
            for k in NUM:
                v = r.get(k, float("nan"))
                if k == "ang_good" or not np.isfinite(v):
                    continue
                tgt[k].append(v)
            nG += isg
            nW += (not isg)
    print("%-14s %4s %24s %24s  %s" %
          ("statistic", "n", "good min/med/max", "wrong min/med/max", "gap?"))
    sep = []
    for k in NUM:
        g = np.array([x for x in good.get(k, []) if np.isfinite(x)])
        w = np.array([x for x in wrong.get(k, []) if np.isfinite(x)])
        if g.size < 3 or w.size < 3:
            continue
        verdict = ""
        if g.max() < w.min():
            verdict = "LOW  thr %.3g" % ((g.max() + w.min()) / 2)
        elif g.min() > w.max():
            verdict = "HIGH thr %.3g" % ((g.max() + w.min()) / 2)
        if verdict:
            sep.append((k, verdict, g, w))
        print("%-14s %4d %24s %24s  %s" %
              (k, min(g.size, w.size),
               "%.4g/%.4g/%.4g" % (g.min(), np.median(g), g.max()),
               "%.4g/%.4g/%.4g" % (w.min(), np.median(w), w.max()), verdict))
    print()
    print("rows: good=%d wrong=%d" % (nG, nW))
    if sep:
        print("CLEAN GAPS: %s" % ", ".join("%s (%s)" % (k, v) for k, v, _g, _w in sep))
        print("margin ratio (worst good vs best wrong) for the two most used:")
        for k, v, g, w in sep[:4]:
            print("   %-12s good max %.4g   wrong min %.4g   ratio %.3f"
                  % (k, g.max(), w.min(), w.min() / max(g.max(), 1e-30)))
    else:
        print("NO STATISTIC SEPARATES good from wrong with a gap -- report this as the result")

    print()
    print("=" * 90)
    print("A4  CHEAP NULLS on Piece A_%02d" % gp)
    print("=" * 90)
    print("  %-4s %9s %11s %11s %9s %9s" %
          ("seed", "gooddraw", "best_rank", "rank_hub", "top10", "top30"))
    t10 = t30 = n = 0
    for s in ss8:
        q = pool_by_seed.get((gp, s), [])
        if not q:
            continue
        gd = [r for r in q if r["ang_good"] < G]
        best_rank = min([r["rank"] for r in gd], default=-1)
        hs = sorted([r for r in q if np.isfinite(r["hub_pt_all"])],
                    key=lambda r: r["hub_pt_all"])
        hub_rank = next((i for i, r in enumerate(hs) if r["ang_good"] < G), -1)
        i10 = int(0 <= best_rank < 10)
        i30 = int(0 <= best_rank < 30)
        t10 += i10
        t30 += i30
        n += 1
        print("  s%-3d %9d %11d %11d %9d %9d" %
              (s, len(gd), best_rank, hub_rank, i10, i30))
    print("  seeds with a good draw in the first 10 draws (the shipped shortlist): %d of %d"
          % (t10, n))
    print("  seeds with a good draw in the first 30 draws                          : %d of %d"
          % (t30, n))

    print()
    print("=" * 90)
    print("C   CONTROLS -- shape of the output and ranker vs writer (no good/wrong label,")
    print("    the seating axis of Piece 08 has no meaning on another piece)")
    print("=" * 90)
    for p in pieces:
        if p == gp:
            continue
        ss = [s for (pp, s) in rows_by_seed if pp == p]
        if not ss:
            continue
        nl = [len([r for r in rows_by_seed[(p, s)] if r["written"] == 1]) for s in ss]
        nb = [r["basins"] if "basins" in r else len(basins_by_seed.get((p, s), []))
              for r in [dict(basins=len(basins_by_seed.get((p, s), []))) for s in ss]]
        agree = 0
        ranks = []
        for s in ss:
            rr = sorted([r for r in rows_by_seed[(p, s)] if r["written"] == 1],
                        key=lambda r: r["rank_in_file"])
            if not rr:
                continue
            ranks.append(rr[0]["rank_written_hub"])
            if rr[0]["rank_written_hub"] == 0:
                agree += 1
        print("p%-3d seeds %2d  lines/file min/med/max %d/%.1f/%d  basins/file med %.1f"
              % (p, len(ss), min(nl), float(np.median(nl)), max(nl),
                 float(np.median(nb))))
        print("      line 0 IS the worst-wall-cost-best basin in %d of %d seeds;"
              " rank of line 0: %s"
              % (agree, len(ranks), ",".join(str(x) for x in ranks)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
