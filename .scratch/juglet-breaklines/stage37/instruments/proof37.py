#!/usr/bin/env python3
"""ticket 37: compose the evidence tables from one run directory.

Reads only files the job wrote (out/cells37.tsv, out/surfaces34.tsv, out/proof1.md5.tsv) and,
optionally, ticket 36's out/cells36.tsv as the reference for proof 2.  It computes nothing about
geometry: every number here is copied from a file, and the join key is (tag, pot, piece).

usage: proof37.py --run <run dir> [--t36 <cells36.tsv>] [--out <dir>]
"""
import argparse
import os
import sys

T36_ARM_B = {  # ticket 37 proof 2, quoted from the ticket itself
    "Juglet_Piece_1": (10800, 15780),
    "Juglet_Piece_5": (229, 2317),
    "Juglet_Piece_7": (1753, 1997),
}
TABLE_COLS = [
    "tag", "pot", "piece", "spacing_s_mm", "npts", "retries", "clusters_pre_merge",
    "clusters_post_merge", "sizes_post_merge", "floor", "floor_from", "capped", "outcome",
    "surf0", "surf1", "surf0_points", "surf1_points",
    "s0_points", "s0_diag_mm", "s0_cov2mm", "s0_fold_deg", "s1_points", "s1_diag_mm",
    "s1_cov2mm", "s1_fold_deg",
]


def read_tsv(path):
    if not os.path.exists(path):
        return [], []
    with open(path, "r", errors="replace") as f:
        hdr = f.readline().rstrip("\n").split("\t")
        rows = []
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) < 2:
                continue
            rows.append(dict(zip(hdr, p)))
    return hdr, rows


def num(v, default=""):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--t36", default="")
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    out = a.out or os.path.join(a.run, "out")
    out_hdr, cells = read_tsv(os.path.join(a.run, "out", "cells37.tsv"))
    _sh, surf = read_tsv(os.path.join(a.run, "out", "surfaces34.tsv"))
    surf_by = {}
    for r in surf:
        surf_by[(r.get("tag"), r.get("pot"), r.get("piece"), r.get("surface"))] = r

    rows = []
    for c in cells:
        k = (c.get("tag"), c.get("pot"), c.get("piece"))
        row = {col: c.get(col, "") for col in TABLE_COLS}
        for slot in (0, 1):
            s = surf_by.get((k[0], k[1], k[2], str(slot)), {})
            row["s%d_points" % slot] = s.get("points", "")
            row["s%d_diag_mm" % slot] = s.get("diag", "")
            row["s%d_cov2mm" % slot] = s.get("cov_2mm", "")
            row["s%d_fold_deg" % slot] = s.get("fold_deg", "")
        rows.append(row)
    rows.sort(key=lambda r: (r["tag"], r["pot"], r["piece"]))
    p = os.path.join(out, "cells37_table.tsv")
    with open(p, "w") as f:
        f.write("\t".join(TABLE_COLS) + "\n")
        for r in rows:
            f.write("\t".join(str(r[c]) for c in TABLE_COLS) + "\n")
    print("[P37] %s rows=%d" % (p, len(rows)))

    # ---- proof 2 ----------------------------------------------------------
    lines = ["# proof 2: arm A (no environment at all: the new default) against ticket 36 arm B",
             "# piece\trun surf0/surf1\tt36 expected\tcomparison"]
    pot_a_two = 0
    pot_a_n = 0
    for r in rows:
        if r["tag"] != "A":
            continue
        if r["pot"] == "Pot_A":
            pot_a_n += 1
            if r["outcome"] == "two":
                pot_a_two += 1
            continue
        exp = T36_ARM_B.get(r["piece"])
        if not exp:
            continue
        got = (r["surf0_points"], r["surf1_points"])
        same = (num(got[0]) == exp[0]) and (num(got[1]) == exp[1])
        lines.append("%s\t%s/%s\t%d/%d\t%s" % (r["piece"], got[0], got[1], exp[0], exp[1],
                                               "IDENTICAL" if same else "DIFFERENT"))
    lines.append("Pot_A\t%d of %d two-surface\t8 of 8\tthe ticket asks for 8 of 8" % (pot_a_two, pot_a_n))
    p2 = os.path.join(out, "proof2.tsv")
    with open(p2, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print("[P37] %s" % p2)

    # ---- proof 1 ----------------------------------------------------------
    p1_path = os.path.join(a.run, "out", "proof1.md5.tsv")
    rows1 = []
    if os.path.exists(p1_path):
        with open(p1_path, "r", errors="replace") as f:
            for line in f:
                if line.startswith("#") or not line.strip():
                    continue
                v = line.rstrip("\n").split("\t")
                if len(v) >= 7 and v[0] != "pot":
                    rows1.append(v[:7])
    if rows1:
        same = sum(1 for v in rows1 if v[6] == "IDENTICAL")
        print("[P37] proof 1: %d of %d pieces IDENTICAL under SFS_SPACING_POLICY=fixed"
              % (same, len(rows1)))
        for v in rows1:
            print("      %-18s %-9s md5 %s  %s" % (v[1], v[6], v[2], v[3]))
    else:
        print("[P37] proof 1: no out/proof1.md5.tsv")

    # ---- the ticket-36 reference, side by side ----------------------------
    if a.t36:
        _h, c36 = read_tsv(a.t36)
        b = {}
        for r in c36:
            b[(r.get("tag"), r.get("pot"), r.get("piece"))] = r
        p3 = os.path.join(out, "cells37_vs_t36.tsv")
        hdr3 = ["commit", "arm", "pot", "piece", "npts", "spacing_s_mm", "clusters_pre", "floor",
                "outcome", "surf0_points", "surf1_points"]
        with open(p3, "w") as f:
            f.write("\t".join(hdr3) + "\n")
            for r in rows:
                if r["tag"] not in ("A", "D"):
                    continue
                src = b.get(("A" if r["tag"] == "D" else "B", r["pot"], r["piece"]))
                if not src:
                    continue
                f.write("\t".join(["t37 " + r["tag"], r["tag"], r["pot"], r["piece"], r["npts"],
                                   r["spacing_s_mm"], r["clusters_pre_merge"], r["floor"],
                                   r["outcome"], r["surf0_points"], r["surf1_points"]]) + "\n")
                f.write("\t".join(["t36 " + ("A" if r["tag"] == "D" else "B"),
                                   "A" if r["tag"] == "D" else "B", r["pot"], r["piece"],
                                   src.get("npts", ""), src.get("spacing_s_mm", ""),
                                   src.get("clusters_pre_merge", ""), src.get("floor", ""),
                                   src.get("outcome", ""), src.get("surf0_points", ""),
                                   src.get("surf1_points", "")]) + "\n")
        print("[P37] %s" % p3)
    return 0


if __name__ == "__main__":
    sys.exit(main())
