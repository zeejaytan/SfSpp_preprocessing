#!/usr/bin/env python3
"""analyse306a2.py -- rank the 10-deg basins of each pool case under every selection
rule we could ship, and report where the basin the ticket needs (Piece 07's second
axis, Piece 08's released second axis) lands.

Reads out/x/<tag>/s<seed>/reps3.tsv.  Nothing here informs the shipped rule; the
released axes enter only through the ang_rel_* columns, as a score.
"""
import argparse
import glob
import os
import sys

TARGET = {("A", 7): 1, ("A", 8): 1, ("A", 1): 0}   # piece -> released line to track


def load(path):
    with open(path) as fh:
        hdr = fh.readline().rstrip("\n").split("\t")
        rows = []
        for line in fh:
            v = line.rstrip("\n").split("\t")
            rows.append(dict(zip(hdr, v)))
    return rows


def fnum(r, k):
    try:
        return float(r[k])
    except (KeyError, ValueError):
        return float("nan")


def rank_of(rows, key, target_cluster, reverse=False):
    order = sorted(rows, key=lambda r: -fnum(r, key) if reverse else fnum(r, key))
    for i, r in enumerate(order):
        if int(r["cluster"]) == target_cluster:
            return i + 1, order
    return -1, order


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    lines = []
    for d in sorted(glob.glob(os.path.join(a.root, "P*_t*", "s*"))):
        tag = os.path.basename(os.path.dirname(d))
        seed = os.path.basename(d)
        piece = int(tag[2:4])
        rows = load(os.path.join(d, "reps3.tsv"))
        if not rows:
            continue
        # the basin nearest the tracked released line, among clusters with a rep
        tgt_line = TARGET[("A", piece)]
        cand = [r for r in rows if str(r["ang_rel_all"]).strip()]
        def ang(r):
            parts = str(r["ang_rel_all"]).split()
            return float(parts[tgt_line]) if len(parts) > tgt_line else float("nan")
        tgt = min(cand, key=ang)
        tcl = int(tgt["cluster"])
        n = len(rows)
        rank_cd, _ = rank_of(rows, "huber_cd_rep", tcl)
        rank_max, _ = rank_of(rows, "max_pt", tcl)
        rank_sum, _ = rank_of(rows, "sum_pt", tcl)
        rank_cross, _ = rank_of(rows, "max_cross_pt", tcl)
        rank_size, _ = rank_of(rows, "size", tcl, reverse=True)
        best_cross = min(rows, key=lambda r: fnum(r, "max_cross_pt"))
        lines.append("%s %s n=%d target=c%d ang_L%d=%.2f size=%d "
                     "rank{cd=%d maxpt=%d sumpt=%d cross=%d size=%d} "
                     "target{cd=%.4e max=%.4e cross=%.4e} best_cross=c%d@%.4e"
                     % (tag, seed, n, tcl, tgt_line, ang(tgt), int(tgt["size"]),
                        rank_cd, rank_max, rank_sum, rank_cross, rank_size,
                        fnum(tgt, "huber_cd_rep"), fnum(tgt, "max_pt"),
                        fnum(tgt, "max_cross_pt"), int(best_cross["cluster"]),
                        fnum(best_cross, "max_cross_pt")))
    txt = "\n".join(lines)
    print(txt)
    if a.out:
        open(a.out, "w").write(txt + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
