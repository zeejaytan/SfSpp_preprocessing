#!/usr/bin/env python3
"""fig40.py -- ticket 40's cross-piece figure, F2.

Reads the nest and cell tables the grid job's cells wrote and draws, for every
piece that produced a pair row in both arms: (top) the shared fraction of the
smaller surface -- shared_over_smaller -- arm A (radius, control) against arm B
(own); (bottom) the mean normal dot between the two surfaces, same arms.  Pot A
pieces are drawn flagged: a Pot A pair whose shared fraction rises above 0 or
whose dot climbs above -0.9 is the regression line the ticket watches, so the
figure marks the pieces, and the JSON records the numbers.

A categorical axis has no mm/px; the JSON records the pixel size instead.
"""
import argparse, hashlib, json, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_tsv(path):
    with open(path) as f:
        rows = [l.rstrip("\n").split("\t") for l in f if l.strip()]
    hdr = rows[0]
    return [dict(zip(hdr, r)) for r in rows[1:]]


def cmd_f2(a):
    nest = read_tsv(a.nest)
    by = {}
    for r in nest:
        by[(r["group"], r["piece"], r["arm"])] = r
    pieces = []
    for r in nest:
        k = (r["group"], r["piece"])
        if k in pieces:
            continue
        if ("A" in [x[2] for x in by if x[:2] == k]) and \
           (k + ("B",)) in by and (k + ("A",)) in by:
            pieces.append(k)
    pieces.sort()
    if not pieces:
        print("[F2] no piece has a pair row in both arms; nothing to draw")
        return 0

    labels, shA, shB, dotA, dotB, pota = [], [], [], [], [], []
    def fnum(r, k):
        try:
            return float(r[k])
        except (KeyError, ValueError):
            return None
    good = []
    for g, p in pieces:
        vals = [fnum(r, k) for r in (by[(g, p, "A")], by[(g, p, "B")])
                for k in ("shared_over_smaller", "mean_normal_dot")]
        if any(v is None for v in vals):
            print("[F2] WARN %s/%s has a non-numeric nest cell (%r); piece skipped" % (g, p, vals))
            continue
        good.append((g, p))
    pieces = sorted(good)
    for g, p in pieces:
        ra, rb = by[(g, p, "A")], by[(g, p, "B")]
        labels.append("%s %s" % (g, p.replace("Juglet_Piece_", "J").replace("Pot_A_Piece_", "PA")))
        shA.append(float(ra["shared_over_smaller"]))
        shB.append(float(rb["shared_over_smaller"]))
        dotA.append(float(ra["mean_normal_dot"]))
        dotB.append(float(rb["mean_normal_dot"]))
        pota.append(g == "g3")

    x = np.arange(len(labels))
    w = 0.38
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 8.5), sharex=True)
    for ax, va, vb, title, ylim in (
        (ax1, shA, shB, "shared fraction of the smaller surface (nest: shared / min(n0,n1))", (0, 1.05)),
        (ax2, dotA, dotB, "mean normal dot between Surface_0 and Surface_1", (-1.05, 1.05)),
    ):
        b1 = ax.bar(x - w / 2, va, w, label="A radius (control)", color="#4477aa", edgecolor="black", linewidth=0.4)
        b2 = ax.bar(x + w / 2, vb, w, label="B own", color="#ee6677", edgecolor="black", linewidth=0.4)
        for bars, vals in ((b1, va), (b2, vb)):
            for bar, v in zip(bars, vals):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + (0.02 if v >= 0 else -0.05),
                        "%.2f" % v, ha="center", fontsize=6, rotation=90)
        ax.set_title(title, fontsize=10)
        ax.set_ylim(*ylim)
        ax.axhline(0, color="black", linewidth=0.6)
        ax.legend(fontsize=8, loc="upper right")
        ax.grid(axis="y", alpha=0.3)
    # the regression line: dot above -0.9 on a Pot A pair
    for i in range(len(labels)):
        if pota[i] and (shB[i] > 0 or dotB[i] > -0.9 or shA[i] > 0 or dotA[i] > -0.9):
            ax1.get_xaxis().set_ticks(x)
            for ax in (ax1, ax2):
                ax.axvspan(x[i] - 0.5, x[i] + 0.5, color="red", alpha=0.15)
                ax.text(x[i], ax.get_ylim()[1] * 0.97, "REGRESSION?", color="red",
                        fontsize=7, rotation=90, ha="right", va="top")
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, rotation=60, ha="right", fontsize=7)
    fig.suptitle("ticket 40 F2 -- arm A (radius) vs arm B (own), every piece, both quantities", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    png = os.path.join(a.outdir, "fig40_%s.png" % a.tag)
    fig.savefig(png, dpi=130)
    H = plt.imread(png)
    plt.close(fig)

    flagged = [labels[i] for i in range(len(labels)) if pota[i] and (shB[i] > 0 or dotB[i] > -0.9)]
    rec = dict(
        figure=png, bytes=os.path.getsize(png), md5=md5_of(png),
        pixels="%dx%d" % (H.shape[1], H.shape[0]),
        nest=a.nest, cells=a.cells,
        n_pieces=len(labels),
        pieces=[dict(label=labels[i], group=pieces[i][0], piece=pieces[i][1], pot_a=pota[i],
                     shared_over_smaller_A=shA[i], shared_over_smaller_B=shB[i],
                     mean_normal_dot_A=dotA[i], mean_normal_dot_B=dotB[i]) for i in range(len(labels))],
        pot_a_flagged_regression=flagged,
    )
    out = os.path.join(a.outdir, "fig40_%s.json" % a.tag)
    with open(out, "w") as f:
        json.dump(rec, f, indent=1, sort_keys=True)
        f.write("\n")
    print("[F2] %s %d bytes %s px, %d pieces, flagged %r" % (png, rec["bytes"], rec["pixels"], len(labels), flagged))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    s = sub.add_parser("f2")
    s.add_argument("--nest", required=True)
    s.add_argument("--cells", required=True)
    s.add_argument("--outdir", required=True)
    s.add_argument("--tag", required=True)
    s.set_defaults(fn=cmd_f2)
    a = ap.parse_args(argv)
    if not getattr(a, "fn", None):
        ap.print_help()
        return 2
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
