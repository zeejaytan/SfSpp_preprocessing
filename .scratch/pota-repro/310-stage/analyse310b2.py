#!/usr/bin/env python3
"""analyse310b2.py -- read out stage310b2's b2.tsv as the B2 table.

Counts are seeds, never bests.  "seating" = a written line within 5 deg of the
Pot A Piece 08 seating axis; "line0" = that line is the file's first line.
"""
import argparse
import collections
import sys


def rows(path):
    with open(path) as fh:
        hdr = fh.readline().rstrip("\n").split("\t")
        for line in fh:
            f = line.rstrip("\n").split("\t")
            d = dict(zip(hdr, f))
            for k in ("piece", "seed", "K", "within5"):
                d[k] = int(d[k])
            for k in ("secs", "best_ang", "line0_ang", "margin"):
                d[k] = float(d[k])
            yield d


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("tsv")
    ap.add_argument("--label", default="Pot A Piece 08")
    a = ap.parse_args(argv)
    rs = list(rows(a.tsv))
    print("%s: %d cases" % (a.label, len(rs)))
    arms = collections.OrderedDict()
    for r in rs:
        arms.setdefault(r["arm"], []).append(r)
    print()
    print("%-8s %5s %9s %9s %7s %8s %7s %7s" %
          ("arm", "seeds", "any<5deg", "line0<5", "med K", "med secs",
           "min ang", "margin"))
    for arm, sel in arms.items():
        n = len(sel)
        any5 = sum(1 for r in sel if r["within5"] == 1)
        l05 = sum(1 for r in sel if 0 <= r["line0_ang"] < 5.0)
        ks = sorted(r["K"] for r in sel)
        ss = sorted(r["secs"] for r in sel)
        ang = min(r["best_ang"] for r in sel)
        mg = [r["margin"] for r in sel if r["margin"] > 0]
        mgs = ("%.4f-%.4f" % (min(mg), max(mg))) if mg else "-"
        print("%-8s %5d %6d/%-2d %6d/%-2d %7.1f %8.1f %7.2f %s" %
              (arm, n, any5, n, l05, n, ks[len(ks) // 2], ss[len(ss) // 2],
               ang, mgs))
    print()
    missing = [(r["arm"], r["seed"]) for r in rs if r["within5"] == 0]
    print("no line within 5 deg: %s" %
          (", ".join("%s s%d" % m for m in missing) if missing else "none"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
