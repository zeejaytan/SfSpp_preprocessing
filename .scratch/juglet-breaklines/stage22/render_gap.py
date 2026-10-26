#!/usr/bin/env python3
"""ticket 22: one before/after render of the same piece, at a scale that resolves the wall gap.

usage: render_gap.py --before <cell dir> --after <cell dir> --piece <name> --out <png>
                     [--dpi 200] [--title "..."] [--zoom-mm 12]

Each argument names a cell directory that holds surfaces/<piece>_Surface_{0,1}.ply
(e.g. .../out/cells/A/Juglet/Juglet_Piece_1). The two panels share one projection so
that a reader can compare them point for point:

  d  = unit(centroid(Surface_1) - centroid(Surface_0)) of the AFTER pair, the direction
       across the wall. A merged pair has no such direction; the AFTER pair is the one
       that is asked to supply it, and the BEFORE pair is projected the same way.
  e2 = first principal direction of the pooled points orthogonal to d
  u  = (x - centroid(Surface_0)) . d      across the wall, in mm
  v  = (x - centroid(Surface_0)) . e2     along the surface, in mm

Pixels per millimetre are measured from the drawn axes and written on the panel, with a
2 mm scale bar, so the figure says its own scale. --zoom-mm crops u to +-zoom_mm/2.
"""
import argparse
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from measure_arm import load_ply


def load_pair(cell, piece):
    d = os.path.join(cell, "surfaces")
    p0, n0 = load_ply(os.path.join(d, piece + "_Surface_0.ply"))
    p1, n1 = load_ply(os.path.join(d, piece + "_Surface_1.ply"))
    return p0, n0, p1, n1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", required=True)
    ap.add_argument("--after", required=True)
    ap.add_argument("--piece", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dpi", type=int, default=200)
    ap.add_argument("--title", default="")
    ap.add_argument("--zoom-mm", type=float, default=0.0)
    a = ap.parse_args()

    b0, bn0, b1, bn1 = load_pair(a.before, a.piece)
    a0, an0, a1, an1 = load_pair(a.after, a.piece)

    c0 = a0.mean(axis=0)
    d = a1.mean(axis=0) - c0
    d /= np.linalg.norm(d)
    pooled = np.vstack([a0, a1]) - c0
    resid = pooled - np.outer(pooled.dot(d), d)
    _, _, vt = np.linalg.svd(resid, full_matrices=False)
    e2 = vt[0]
    e2 -= e2.dot(d) * d
    e2 /= np.linalg.norm(e2)

    def project(p):
        q = p - c0
        return q.dot(d), q.dot(e2)

    panels = [
        (a.before, b0, b1, "BEFORE  %s" % os.path.basename(a.before)),
        (a.after, a0, a1, "AFTER  %s" % os.path.basename(a.after)),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 5.2), dpi=a.dpi)
    uall, vall = [], []
    for _, p0, p1, _ in panels:
        u0, v0 = project(p0)
        u1, v1 = project(p1)
        uall += [u0, u1]
        vall += [v0, v1]
    uu = np.concatenate(uall)
    vv = np.concatenate(vall)
    if a.zoom_mm > 0:
        half = a.zoom_mm / 2.0
        keep = np.abs(uu) <= half
        uu = uu[keep]
        vv = vv[keep]
        ulim = (-half, half)
    else:
        ulim = (uu.min() - 0.5, uu.max() + 0.5)

    for ax, (cell, p0, p1, label) in zip(axes, panels):
        u0, v0 = project(p0)
        u1, v1 = project(p1)
        ax.scatter(u0, v0, s=3, c="#1f5fa8", label="Surface_0 (interior) n=%d" % len(p0), linewidths=0)
        ax.scatter(u1, v1, s=3, c="#d1622b", label="Surface_1 (exterior) n=%d" % len(p1), linewidths=0)
        ax.set_xlim(*ulim)
        ax.set_ylim(vv.min() - 0.5, vv.max() + 0.5)
        ax.set_aspect("equal")
        ax.set_xlabel("across the wall (mm)")
        ax.set_ylabel("along the surface (mm)")
        ax.set_title(label, fontsize=10)
        ax.legend(loc="upper right", fontsize=7, markerscale=3)
        ax.grid(alpha=0.25, linewidth=0.4)
        fig.canvas.draw()
        bb = ax.get_window_extent()
        width_mm = ulim[1] - ulim[0]
        px_per_mm = bb.width / width_mm
        y0 = ax.get_ylim()[0]
        bar_y = y0 + 0.06 * (ax.get_ylim()[1] - y0)
        bar_x = ulim[0] + 0.06 * width_mm
        ax.plot([bar_x, bar_x + 2.0], [bar_y, bar_y], color="black", linewidth=3, solid_capstyle="butt")
        ax.annotate("2 mm", (bar_x + 1.0, bar_y), textcoords="offset points", xytext=(0, 4),
                    ha="center", fontsize=7)
        ax.annotate("1 mm = %.1f px (dpi %d, %.2f mm across the panel)"
                    % (px_per_mm, a.dpi, width_mm),
                    (0.01, 0.99), xycoords="axes fraction", va="top", fontsize=7)
        ax.annotate("%s\n%d + %d points" % (os.path.basename(os.path.dirname(os.path.dirname(cell))),
                                             len(p0), len(p1)),
                    (0.01, 0.03), xycoords="axes fraction", fontsize=7, family="monospace")

    if a.title:
        fig.suptitle(a.title, fontsize=11)
    fig.tight_layout()
    fig.savefig(a.out, dpi=a.dpi)
    print("[RENDER] %s" % a.out)
    for ax in axes:
        bb = ax.get_window_extent()
        print("[RENDER] panel %.1f x %.1f px, %.1f px/mm" % (bb.width, bb.height,
              bb.width / (ax.get_xlim()[1] - ax.get_xlim()[0])))


if __name__ == "__main__":
    main()
