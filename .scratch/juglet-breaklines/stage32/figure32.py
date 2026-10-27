#!/usr/bin/env python3
"""Ticket 32 -- the figure. Two panels, 300 dpi, Agg only.

Panel 1: neighbour-normal angle (median) against the sherd/vessel extent ratio, one
marker per (piece, arm) per window; colour = window, marker shape = arm.
Panel 2: fitted curvature radius (median) against the window width, one line per
(piece, arm); the two vessel radii are drawn as labelled reference lines.
"""
import argparse
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ARM_STYLE = {"J": ("o", "Juglet (native, mesh-derived)"),
             "PA_native": ("s", "Pot A (released cloud)"),
             "PA_025": ("^", "Pot A (0.25 mm subsample)")}
WIN_COL = {"1.0": "#440154", "2.0": "#31688e", "3.0": "#35b779", "5.0": "#fde725"}


def read_tsv(path):
    with open(path) as f:
        head = f.readline().rstrip("\n").split("\t")
        rows = []
        for line in f:
            p = line.rstrip("\n").split("\t")
            rows.append(dict(zip(head, p)))
    return rows


def fnum(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True)
    a = ap.parse_args(argv)
    out = a.outdir
    sizes = read_tsv(os.path.join(out, "sizes32.tsv"))
    wins = read_tsv(os.path.join(out, "windows32.tsv"))
    vess = read_tsv(os.path.join(out, "vessel32.tsv"))
    ratio = {(r["piece"], r["arm"]): fnum(r["ratio"]) for r in sizes}
    vessel_mm = {}
    for r in vess:
        if r.get("chosen") == "yes":
            vessel_mm[r["pot"]] = fnum(r["vessel_mm"])
        elif r["mode"] == "Rp+t" and r["pot"] not in vessel_mm and fnum(r["diag_mm"]):
            vessel_mm[r["pot"]] = fnum(r["diag_mm"])
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.0, 5.4))
    seen = set()
    for r in wins:
        arm = r["arm"]
        x = ratio.get((r["piece"], arm))
        y = fnum(r["angle_p50_deg"])
        if x is None or y is None:
            continue
        mk, lab = ARM_STYLE[arm]
        ax1.scatter(x, y, c=WIN_COL[r["window_mm"]], marker=mk, s=46,
                    edgecolors="black", linewidths=0.4,
                    label=None if r["window_mm"] in seen and arm in seen else None)
        seen.add(r["window_mm"])
        seen.add(arm)
    for wm, col in WIN_COL.items():
        ax1.scatter([], [], c=col, marker="o", s=40, edgecolors="black",
                    linewidths=0.4, label="window %s mm (colour)" % wm)
    for arm, (mk, lab) in ARM_STYLE.items():
        ax1.scatter([], [], c="0.6", marker=mk, s=40, edgecolors="black",
                    linewidths=0.4, label=lab)
    ax1.set_xlabel("sherd extent / vessel extent (bbox diagonals)")
    ax1.set_ylabel("neighbour-normal angle, median (deg)")
    ax1.set_title("A. angle against size, by fixed physical window")
    ax1.grid(alpha=0.3)
    ax1.legend(fontsize=6, loc="best", ncol=2)
    styles = ["-", "--", ":"]
    arms = ["J", "PA_native", "PA_025"]
    pieces = []
    for r in wins:
        if r["piece"] not in pieces:
            pieces.append(r["piece"])
    cmap = plt.get_cmap("tab20")
    colof = {p: cmap(i % 20) for i, p in enumerate(pieces)}
    for p in pieces:
        for ai, arm in enumerate(arms):
            xs, ys = [], []
            for wm in ("1.0", "2.0", "3.0", "5.0"):
                hit = [r for r in wins if r["piece"] == p and r["arm"] == arm
                       and r["window_mm"] == wm]
                if not hit:
                    continue
                y = fnum(hit[0]["rho_median_mm"])
                if y is None:
                    continue
                xs.append(float(wm))
                ys.append(y)
            if len(xs) >= 1:
                ax2.plot(xs, ys, styles[ai], color=colof[p], marker="o", ms=3,
                         lw=1.0, alpha=0.9,
                         label=None)
    for p in pieces:
        ax2.plot([], [], "-", color=colof[p], label=p)
    for arm, ls in zip(arms, styles):
        ax2.plot([], [], ls, color="0.35", label="arm %s" % arm)
    jr = vessel_mm.get("Juglet")
    pr = vessel_mm.get("PotA")
    if jr:
        ax2.axhline(jr / 2.0, color="tab:red", lw=1.2, ls="-.")
        ax2.text(0.02, jr / 2.0, " Juglet vessel radius %.2f mm" % (jr / 2.0),
                 color="tab:red", fontsize=7, va="bottom")
    if pr:
        ax2.axhline(pr / 2.0, color="tab:blue", lw=1.2, ls="-.")
        ax2.text(0.02, pr / 2.0, " Pot A vessel radius %.2f mm" % (pr / 2.0),
                 color="tab:blue", fontsize=7, va="bottom")
    ax2.set_yscale("log")
    ax2.set_xlabel("window width (mm)")
    ax2.set_ylabel("curvature radius, median (mm, log scale)")
    ax2.set_title("B. fitted radius against window width")
    ax2.grid(alpha=0.3, which="both")
    ax2.legend(fontsize=5, loc="center left", bbox_to_anchor=(1.01, 0.5), ncol=1)
    fig.tight_layout()
    p = os.path.join(out, "figure32.png")
    fig.savefig(p, dpi=300)
    print("[F32] wrote %s" % p)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
