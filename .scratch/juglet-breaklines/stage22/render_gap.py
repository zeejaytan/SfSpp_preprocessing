#!/usr/bin/env python3
"""ticket 22: one before/after render of the same piece, at a scale that resolves the wall gap.

usage: render_gap.py --before <cell dir> --after <cell dir> --piece <name> --out <png>
                     [--dpi 200] [--title "..."] [--zoom-mm 8] [--v-window-mm 12]

Each argument names a cell directory that holds surfaces/<piece>_Surface_{0,1}.ply
(e.g. .../out/cells/A/Juglet/Juglet_Piece_1).

The piece is a curved wall, so one flat projection smears a 2 mm gap over several
millimetres of curvature. The panels therefore unroll the pair point by point instead:

  for every Surface_1 point: its nearest Surface_0 point, and that point's normal n0
  u = (x1 - x0) . n0        signed offset across the wall, in mm, along the local normal
  v = (x1 - centroid) . e2  along the surface, in mm, e2 = first principal direction

Surface_0 is the reference line at u = 0. The two faces of a wall then appear as two bands
2 mm apart, and a fused pair appears as one band at 0. Both panels share one axis, each
panel states its own pixels per millimetre measured from the drawn axes, and the pair
statistics are the same ones measure_arm.py reports.
"""
import argparse
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from measure_arm import load_ply, pair_stats


def load_pair(cell, piece):
    d = os.path.join(cell, "surfaces")
    p0, n0 = load_ply(os.path.join(d, piece + "_Surface_0.ply"))
    p1, n1 = load_ply(os.path.join(d, piece + "_Surface_1.ply"))
    return p0, n0, p1, n1


def unroll(p0, n0, p1):
    """signed offset of every Surface_1 point along the local Surface_0 normal, plus v."""
    from scipy.spatial import cKDTree
    n0u = n0 / np.maximum(np.linalg.norm(n0, axis=1, keepdims=True), 1e-12)
    _, idx = cKDTree(p0).query(p1, k=1, workers=-1)
    off = np.einsum("ij,ij->i", p1 - p0[idx], n0u[idx])
    c = p1.mean(axis=0)
    q = np.vstack([p0, p1]) - c
    _, _, vt = np.linalg.svd(q, full_matrices=False)
    e2 = vt[0]
    v0 = (p0 - c).dot(e2)
    v1 = (p1 - c).dot(e2)
    return off, v0, v1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", required=True)
    ap.add_argument("--after", required=True)
    ap.add_argument("--piece", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dpi", type=int, default=200)
    ap.add_argument("--title", default="")
    ap.add_argument("--zoom-mm", type=float, default=8.0, help="width of the across-wall axis")
    ap.add_argument("--v-window-mm", type=float, default=12.0, help="height of the along-surface axis")
    a = ap.parse_args()

    panels = []
    for cell, label in ((a.before, "BEFORE"), (a.after, "AFTER")):
        p0, n0, p1, n1 = load_pair(cell, a.piece)
        off, v0, v1 = unroll(p0, n0, p1)
        if float(np.median(off)) < 0.0:
            off = -off
            v0 = -v0
        st = pair_stats(p0, n0, p1, n1)
        arm = os.path.basename(os.path.dirname(os.path.dirname(cell)))
        panels.append((label, arm, p0, v0, off, v1, st))

    half = a.zoom_mm / 2.0
    ulim = (-half, half)
    vlim = (-a.v_window_mm / 2.0, a.v_window_mm / 2.0)

    fig, axes = plt.subplots(1, 2, figsize=(11.0, 5.6), dpi=a.dpi)
    for ax, (label, arm, p0, v0, off, v1, st) in zip(axes, panels):
        ax.scatter(np.zeros(len(p0)), v0, s=3, c="#1f5fa8", linewidths=0,
                   label="Surface_0 (interior) n=%d, reference at 0" % len(p0))
        ax.scatter(off, v1, s=3, c="#d1622b", linewidths=0,
                   label="Surface_1 (exterior) n=%d" % len(off))
        ax.axvline(0.0, color="#1f5fa8", linewidth=0.6, alpha=0.5)
        ax.set_xlim(*ulim)
        ax.set_ylim(*vlim)
        ax.set_aspect("equal")
        ax.set_xlabel("across the wall (mm), offset along the local Surface_0 normal")
        ax.set_ylabel("along the surface (mm)")
        ax.legend(loc="upper right", fontsize=7, markerscale=3, framealpha=0.9)
        ax.grid(alpha=0.25, linewidth=0.4)
        fig.canvas.draw()
        bb = ax.get_window_extent()
        width_mm = ulim[1] - ulim[0]
        px_per_mm = bb.width / width_mm
        ax.set_title("%s  %s\n1 mm = %.1f px (dpi %d, %.2f mm across the panel)"
                     % (label, arm, px_per_mm, a.dpi, width_mm), fontsize=9)
        y0 = ax.get_ylim()[0]
        bar_y = y0 + 0.13 * (ax.get_ylim()[1] - y0)
        bar_x = ulim[1] - 0.06 * width_mm - 2.0
        ax.plot([bar_x, bar_x + 2.0], [bar_y, bar_y], color="black", linewidth=3,
                solid_capstyle="butt")
        ax.annotate("2 mm", (bar_x + 1.0, bar_y), textcoords="offset points", xytext=(0, 4),
                    ha="center", fontsize=7)
        bar = ("yes" if (st["mean_dot"] <= -0.9 and st["med_nn_mm"] >= 1.5
                         and st["share"] <= 0.05) else "no")
        ax.annotate("share<=1um %.3f   med nn %.2f mm   dot %+.3f   bar %s"
                    % (st["share"], st["med_nn_mm"], st["mean_dot"], bar),
                    (0.01, 0.01), xycoords="axes fraction", va="bottom", fontsize=6.5,
                    family="monospace")
    if a.title:
        fig.suptitle(a.title, fontsize=9.5)
    fig.tight_layout()
    fig.savefig(a.out, dpi=a.dpi)
    print("[RENDER] %s" % a.out)
    for ax in axes:
        bb = ax.get_window_extent()
        print("[RENDER] panel %.1f x %.1f px, %.1f px/mm"
              % (bb.width, bb.height, bb.width / (ax.get_xlim()[1] - ax.get_xlim()[0])))


if __name__ == "__main__":
    main()
