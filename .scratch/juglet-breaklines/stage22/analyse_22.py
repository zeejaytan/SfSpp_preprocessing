#!/usr/bin/env python3
"""Ticket 22: assemble the arm table and choose the piece for the before/after figure.

usage: analyse_22.py <juglet cellroot> <pota cellroot> <outdir>

Writes
  <outdir>/arm_table.tsv    every measured cell of both pots, one row per (pot, arm, piece)
  <outdir>/arm_summary.tsv  per (pot, arm): cells, pairs written, pairs at the wall-pair bar,
                            median dot / cross distance / share over the pieces that wrote a pair,
                            and the pieces that reach the bar
  <outdir>/render_choice.txt  the piece the figure uses, and the rule that picked it

The render choice is a presentation rule, not a verdict: of the pieces where BOTH arm A and
arm D200 wrote a pair, take the one with the largest drop in the 1-micron coincidence share
(share_A - share_D200); ties go to the lower piece number. If no piece has both, take the
largest |dot_D200 - dot_A|; if there is none, piece 1.
"""
import os
import sys

ARMS = ["A", "A_old", "A_new2", "B", "C100", "C200", "C400", "C2_100", "C2_200", "C2_400",
        "D100", "D200", "D400"]


def read_measure(root):
    path = os.path.join(root, "measure.tsv")
    rows = []
    with open(path) as fh:
        head = fh.readline().rstrip("\n").split("\t")
        for line in fh:
            f = line.rstrip("\n").split("\t")
            if len(f) < len(head):
                f += ["NA"] * (len(head) - len(f))
            rows.append(dict(zip(head, f)))
    return rows


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def median(xs):
    xs = sorted(xs)
    if not xs:
        return None
    n = len(xs)
    return xs[n // 2] if n % 2 else 0.5 * (xs[n // 2 - 1] + xs[n // 2])


def fmt(v, nd=4):
    return "NA" if v is None else ("%." + str(nd) + "f") % v


def main():
    jug, pota, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
    rows = read_measure(jug) + read_measure(pota)
    os.makedirs(outdir, exist_ok=True)

    cols = ["pot", "tag", "piece", "mesh_exit", "n0", "n1", "share", "mean_dot", "med_nn_mm",
            "med_abs_dot", "frac_neg", "med_off_mm", "bar"]
    with open(os.path.join(outdir, "arm_table.tsv"), "w") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in sorted(rows, key=lambda r: (r["pot"], ARMS.index(r["tag"]) if r["tag"] in ARMS else 99, r["piece"])):
            fh.write("\t".join(r.get(c, "NA") for c in cols) + "\n")

    with open(os.path.join(outdir, "arm_summary.tsv"), "w") as fh:
        fh.write("pot\ttag\tcells\tpairs\tbar_yes\tmed_dot\tmed_nn_mm\tmed_share\tbar_pieces\n")
        for pot in sorted(set(r["pot"] for r in rows)):
            for arm in ARMS:
                sub = [r for r in rows if r["pot"] == pot and r["tag"] == arm]
                if not sub:
                    continue
                pairs = [r for r in sub if r["n0"] != "NA"]
                at_bar = [r for r in pairs if r["bar"] == "yes"]
                md = median([num(r["mean_dot"]) for r in pairs if num(r["mean_dot"]) is not None])
                mn = median([num(r["med_nn_mm"]) for r in pairs if num(r["med_nn_mm"]) is not None])
                ms = median([num(r["share"]) for r in pairs if num(r["share"]) is not None])
                pieces = ",".join(sorted(r["piece"].split("_")[-1] for r in at_bar)) or "-"
                fh.write("%s\t%s\t%d\t%d\t%d\t%s\t%s\t%s\t%s\n"
                         % (pot, arm, len(sub), len(pairs), len(at_bar), fmt(md), fmt(mn, 3), fmt(ms), pieces))

    # render choice, Juglet only
    jug_rows = [r for r in rows if r["pot"] == "Juglet"]
    by = {}
    for r in jug_rows:
        by.setdefault((r["piece"], r["tag"]), r)
    cand = []
    for piece in sorted(set(r["piece"] for r in jug_rows)):
        a = by.get((piece, "A"))
        d = by.get((piece, "D200"))
        if a and d and a["n0"] != "NA" and d["n0"] != "NA":
            sa, sd = num(a["share"]), num(d["share"])
            if sa is not None and sd is not None:
                cand.append((sa - sd, piece))
    rule = "largest drop in 1-micron coincidence share, A -> D200, among pieces where both wrote a pair"
    if cand:
        cand.sort(key=lambda t: (-t[0], t[1]))
        piece, detail = cand[0][1], "share drop %.4f" % cand[0][0]
    else:
        cand2 = []
        for piece in sorted(set(r["piece"] for r in jug_rows)):
            a = by.get((piece, "A"))
            d = by.get((piece, "D200"))
            if a and d and a["n0"] != "NA" and d["n0"] != "NA":
                da, dd = num(a["mean_dot"]), num(d["mean_dot"])
                if da is not None and dd is not None:
                    cand2.append((abs(dd - da), piece))
        rule = "no piece had a pair in both arms; largest |dot change| A -> D200"
        if cand2:
            cand2.sort(key=lambda t: (-t[0], t[1]))
            piece, detail = cand2[0][1], "|dot change| %.4f" % cand2[0][0]
        else:
            piece, detail = "Juglet_Piece_1", "no piece had a pair in both arms; fell back to piece 1"
    with open(os.path.join(outdir, "render_choice.txt"), "w") as fh:
        fh.write("%s\t%s\t%s\n" % (piece, rule, detail))
    print("[ANALYSE] arm_table.tsv %d rows" % len(rows))
    print("[ANALYSE] render piece=%s (%s; %s)" % (piece, rule, detail))


if __name__ == "__main__":
    main()
