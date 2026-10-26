#!/usr/bin/env python3
"""ticket 23: what a written surface looks like against its own piece.

Each panel draws that piece's cloud (grey) and every surface the arm wrote (Surface_0 red,
Surface_1 blue) in one common projection, so a surface that is one wall of a sherd reads as a
patch over a slice of the cloud rather than as another wall. A 10 mm scale bar is drawn in the
panel and the mm-per-pixel of the panel is printed beside the bar and in the log, measured from
the drawn axes -- not assumed.

usage: render23.py <cellroot> <out_png> [arm:pot:piece ...]
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from measure_arm23 import load_ply, read_cells  # noqa: E402
from coverage23 import cloud_path, read_pcd_xyz  # noqa: E402

DEFAULT_PANELS = [
    # the two pieces that keep one cluster at today's defaults, and what B does with each
    "A:Juglet:Juglet_Piece_3",
    "B:Juglet:Juglet_Piece_3",
    "A:Juglet:Juglet_Piece_5",
    "B:Juglet:Juglet_Piece_5",
    # the two pieces that reach zero clusters at today's defaults, and what C does with each
    "A:Juglet:Juglet_Piece_2",
    "C:Juglet:Juglet_Piece_2",
    "C:Juglet:Juglet_Piece_5",
    # references: a Juglet piece that already writes two surfaces, and a healthy Pot A wall pair
    "A:Juglet:Juglet_Piece_1",
    "A:Pot_A:Pot_A_Piece_07",
]


def surf(cellroot, tag, pot, piece, k):
    return os.path.join(cellroot, tag, pot, piece, "surfaces", "%s_Surface_%d.ply" % (piece, k))


def main():
    cellroot, outpng = sys.argv[1], sys.argv[2]
    panels = sys.argv[3:] or DEFAULT_PANELS
    rows = read_cells(os.path.join(cellroot, "cells23.tsv"))
    idx = {(r["tag"], r["pot"], r["piece"]): r for r in rows}
    clouds = {}
    ncol = 4
    nrow = (len(panels) + ncol - 1) // ncol
    fig, axes = plt.subplots(nrow, ncol, figsize=(4.5 * ncol, 4.3 * nrow), dpi=110)
    axes = np.atleast_1d(axes).ravel()
    for ax in axes:
        ax.set_visible(False)
    for ax, spec in zip(axes, panels):
        ax.set_visible(True)
        arm, pot, piece = spec.split(":")
        key = (pot, piece)
        if key not in clouds:
            clouds[key] = read_pcd_xyz(cloud_path(pot, piece), maxpts=40000)[0]
        cloud = clouds[key]
        c = cloud - cloud.mean(axis=0)
        _, _, vt = np.linalg.svd(c, full_matrices=False)
        basis = vt[:2].T
        cxy = c.dot(basis)
        ax.scatter(cxy[:, 0], cxy[:, 1], s=0.25, c="0.62", linewidths=0, label="cloud")
        n0 = n1 = 0
        for k, col in ((0, "#d62728"), (1, "#1f77b4")):
            f = surf(cellroot, arm, pot, piece, k)
            if not os.path.exists(f):
                continue
            p = load_ply(f)[0]
            if len(p) == 0:
                continue
            xy = (p - cloud.mean(axis=0)).dot(basis)
            ax.scatter(xy[:, 0], xy[:, 1], s=1.5, c=col, linewidths=0, label="Surface_%d" % k)
            if k == 0:
                n0 = len(p)
            else:
                n1 = len(p)
        r = idx.get((arm, pot, piece), {})
        ax.set_title("%s  arm=%s  outcome=%s\nn0=%d n1=%d floor=%s capped=%s"
                     % (piece, arm, r.get("outcome", "NA"), n0, n1,
                        r.get("floor", "NA"), r.get("capped", "NA")), fontsize=8)
        ax.set_aspect("equal")
        ax.set_xticks([]); ax.set_yticks([])
        ax.legend(loc="upper right", fontsize=6, markerscale=4)
    fig.tight_layout()
    fig.canvas.draw()
    print("[RENDER] panel scale, measured from the drawn axes:")
    for ax, spec in zip(axes, panels):
        x0, x1 = ax.get_xlim()
        bb = ax.get_window_extent()
        mmpx = (x1 - x0) / bb.width
        y0, y1 = ax.get_ylim()
        ax.plot([x0 + 0.06 * (x1 - x0), x0 + 0.06 * (x1 - x0) + 10.0],
                [y0 + 0.06 * (y1 - y0)] * 2, color="k", lw=2.5)
        ax.text(x0 + 0.06 * (x1 - x0) + 5.0, y0 + 0.10 * (y1 - y0), "10 mm",
                fontsize=6, ha="center")
        ax.text(x0 + 0.06 * (x1 - x0), y0 + 0.13 * (y1 - y0),
                "%.3f mm/px" % mmpx, fontsize=6)
        print("  %-34s x span %8.2f mm over %4d px -> %.4f mm/px"
              % (spec, x1 - x0, int(bb.width), mmpx))
    # no bbox_inches="tight": cropping the saved canvas would change the pixels-per-mm
    # after the mm/px above was measured, and the stated scale has to describe the file.
    fig.savefig(outpng, dpi=110)
    print("[RENDER] wrote %s" % outpng)


if __name__ == "__main__":
    main()
