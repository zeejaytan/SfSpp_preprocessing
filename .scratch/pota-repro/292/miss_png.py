#!/usr/bin/env python3
"""miss_png.py -- one lane: always a 200x200 thumbnail (montage input), and a two-panel X-Y / X-Z
picture only when the lane is below bar (ticket 292, job B step 5)."""
import importlib.util
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("score292", os.path.join(HERE, "score292.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)

OURS_C = "#00a000"
AUTH_C = "#000000"


def limits(ours, auth, i, j):
    pts = np.vstack([ours, auth])
    x0, x1 = float(pts[:, i].min()), float(pts[:, i].max())
    y0, y1 = float(pts[:, j].min()), float(pts[:, j].max())
    span = max(x1 - x0, y1 - y0) * 1.12 + 1e-6
    cx, cy = 0.5 * (x0 + x1), 0.5 * (y0 + y1)
    return (cx - span / 2.0, cx + span / 2.0), (cy - span / 2.0, cy + span / 2.0), span


def draw(ax, ours, auth, i, j, tiny):
    ax.plot(auth[:, i], auth[:, j], "-", color=AUTH_C, lw=1.0 if tiny else 1.8,
            label="authors" if not tiny else None, zorder=2)
    ax.plot(ours[:, i], ours[:, j], "-", color=OURS_C, lw=1.1 if tiny else 2.0,
            label="ours" if not tiny else None, zorder=3)
    ax.plot(ours[:, i], ours[:, j], ".", color=OURS_C, ms=1.0 if tiny else 2.4, zorder=4)
    xl, yl, _ = limits(ours, auth, i, j)
    ax.set_xlim(*xl)
    ax.set_ylim(*yl)
    ax.set_aspect("equal", adjustable="box")


def main(argv):
    if len(argv) != 8:
        print("usage: miss_png.py <piece> <lane> <ours.pcd> <author.pcd> <pngdir> <tiledir> <at_bar>", file=sys.stderr)
        return 2
    piece, lane, ours_path, auth_path, pngdir, tiledir, atbar = argv[1:8]
    ours = S.read_pcd(ours_path)
    auth = S.read_pcd(auth_path)
    if len(ours) == 0 or len(auth) == 0:
        print("[PNG] skip " + piece + " Bl" + lane + ": empty input")
        return 0

    os.makedirs(tiledir, exist_ok=True)
    os.makedirs(pngdir, exist_ok=True)
    label = piece.replace("_Piece_", " ") + " Bl" + lane

    fig = plt.figure(figsize=(2.0, 2.0), dpi=100)
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.88])
    draw(ax, ours, auth, 0, 1, True)
    ax.set_axis_off()
    ax.set_title(label, fontsize=6.5, pad=1.0)
    tile = os.path.join(tiledir, piece + "_Bl" + lane + ".png")
    fig.savefig(tile, dpi=100)
    plt.close(fig)
    print("[PNG] tile " + tile + " " + str(os.path.getsize(tile)) + " B")

    if atbar != "no":
        return 0

    fig = plt.figure(figsize=(10.0, 4.2), dpi=90)
    for k, (i, j) in enumerate([(0, 1), (0, 2)]):
        ax = fig.add_subplot(1, 2, k + 1)
        draw(ax, ours, auth, i, j, False)
        ax.set_xlabel(["x", "y", "z"][i] + " (mm)", fontsize=8)
        ax.set_ylabel(["x", "y", "z"][j] + " (mm)", fontsize=8)
        ax.tick_params(labelsize=7)
        ax.set_title("X-Y" if (i, j) == (0, 1) else "X-Z", fontsize=9)
    ax.legend(loc="lower center", fontsize=8, frameon=False, ncol=2)
    fig.suptitle(label + "  BELOW BAR: ours " + str(len(ours)) + " pts, authors " + str(len(auth)) + " pts",
                 fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    out = os.path.join(pngdir, piece + "_Bl" + lane + ".png")
    fig.savefig(out, dpi=90)
    plt.close(fig)
    print("[PNG] miss " + out + " " + str(os.path.getsize(out)) + " B")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))