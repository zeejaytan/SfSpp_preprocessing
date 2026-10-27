#!/usr/bin/env python3
"""Ticket 38 part E: redraw piece 9 and Pot A 07 with (a) the tail at full opacity and a marker
one step larger and (b) a continuous rank palette, then MEASURE ink / grey / colour from the PNGs
that come out, and calibrate that measurement by re-rendering the ticket-37 style first.

The measurement is defined here rather than quoted, because ticket 37's 10.6/13.9/16.0 % and
82-83 % pale grey were recorded without an instrument.  Definition used for every PNG below:
  * a pixel is INK when any channel is below 245 (the figures have a white facecolor)
  * an ink pixel is GREY when max(rgb) - min(rgb) <= 12, else COLOUR
  * panels are found by splitting the image at fully-white columns wider than 8 px
  * fractions are of the panel's own bounding box

usage: parte38.py --t37 <dir with ticket-37 pre-floor PLYs> --outdir O [--pieces P9,PotA07]
"""
import argparse
import glob
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import cm, colors as mcolors
from matplotlib.lines import Line2D
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fig37 as F37

INK_THRESH = 245
GREY_CHROMA = 12


# ------------------------------------------------------------------ measurement
def ink_stats(arr):
    sub = arr[:, :, :3].astype(np.int16)
    ink = sub.min(axis=2) < INK_THRESH
    n = int(ink.sum())
    if n == 0:
        return {"ink": 0, "ink_frac": 0.0, "grey_frac": 0.0, "colour_frac": 0.0,
                "grey_share_of_ink": 0.0, "area": int(arr.shape[0] * arr.shape[1])}
    chroma = sub.max(axis=2) - sub.min(axis=2)
    grey = ink & (chroma <= GREY_CHROMA)
    area = int(arr.shape[0] * arr.shape[1])
    ng = int(grey.sum())
    return {"ink": n, "ink_frac": n / float(area), "grey_frac": ng / float(area),
            "colour_frac": (n - ng) / float(area), "grey_share_of_ink": ng / float(n),
            "area": area}


def panels(arr):
    sub = arr[:, :, :3].astype(np.int16)
    anyink = (sub.min(axis=2) < INK_THRESH)
    col = anyink.any(axis=0)
    runs = []
    x = 0
    W = len(col)
    while x < W:
        if col[x]:
            x0 = x
            while x < W and col[x]:
                x += 1
            runs.append((x0, x))
        else:
            x += 1
    merged = []
    for r in runs:
        if merged and r[0] - merged[-1][1] <= 8:
            merged[-1] = (merged[-1][0], r[1])
        else:
            merged.append(list(r) if False else (r[0], r[1]))
    out = []
    for x0, x1 in merged:
        seg = anyink[:, x0:x1]
        rows = np.where(seg.any(axis=1))[0]
        if len(rows) == 0:
            continue
        out.append((x0, x1, int(rows[0]), int(rows[-1]) + 1))
    return out


def measure_png(path, label, npoints=None, boxes=None):
    """boxes = explicit (x0,x1,y0,y1) panel rectangles in saved-PNG pixels; when given, the
    panels are those rectangles and no content-based split is used (a sparse cloud can carry a
    fully white column inside a panel, which would split it)."""
    with Image.open(path) as im:
        arr = np.asarray(im.convert("RGB"))
    ps = list(boxes) if boxes else panels(arr)
    rows = []
    for i, (x0, x1, y0, y1) in enumerate(ps):
        st = ink_stats(arr[y0:y1, x0:x1])
        st.update({"panel": i, "x0": x0, "x1": x1, "y0": y0, "y1": y1})
        if npoints:
            st["ink_per_point"] = st["ink"] / float(npoints)
        rows.append(st)
    whole = ink_stats(arr)
    rec = {"png": os.path.basename(path), "label": label, "file": path,
           "pixel_width": int(arr.shape[1]), "pixel_height": int(arr.shape[0]),
           "panel_source": "axes boxes" if boxes else "white-column split",
           "panels_found": len(ps), "panels": rows, "whole": whole,
           "ink_frac_mean": (float(np.mean([r["ink_frac"] for r in rows])) if rows else 0.0),
           "grey_share_of_ink_mean": (float(np.mean([r["grey_share_of_ink"] for r in rows]))
                                      if rows else 0.0),
           "points": npoints, "bytes": os.path.getsize(path)}
    print("[PARTE-MEAS] %-34s panels=%d ink %s  grey_share %s  colour_frac %s"
          % (label, len(ps), ["%.4f" % r["ink_frac"] for r in rows],
             ["%.3f" % r["grey_share_of_ink"] for r in rows],
             ["%.4f" % r["colour_frac"] for r in rows]))
    return rec


# ------------------------------------------------------------------ the redraw
def draw_e(piece, ply, outpath, target_mm_px, dpi=110.0):
    """Three views, every region coloured from a continuous rank palette at full opacity,
    marker one step larger than the ticket-37 tail (0.45 mm against 0.35)."""
    cols, n, fmt = F37.read_ply_vertices(ply)
    xyz = np.column_stack([cols["x"], cols["y"], cols["z"]]).astype(np.float64)
    cid = cols["cluster_id"].astype(np.int64) if "cluster_id" in cols else np.full(n, -1, np.int64)
    lo, hi = xyz.min(axis=0), xyz.max(axis=0)
    span = float((hi - lo).max())
    half = span / 2.0 + span * 0.05
    mid = (lo + hi) / 2.0
    span_p = 2.0 * half
    ranks = np.maximum(cid, 0).astype(np.float64)
    rmax = max(1.0, float(ranks.max()))
    cmap = (matplotlib.colormaps["turbo"] if hasattr(matplotlib, "colormaps")
            else cm.get_cmap("turbo"))
    norm = mcolors.LogNorm(vmin=1.0, vmax=rmax)
    rgba = cmap(norm(np.maximum(ranks, 1.0)))
    order = np.argsort(-cid, kind="stable")          # largest region last -> drawn on top
    inch = (span_p / target_mm_px) / dpi
    fig, axes = plt.subplots(1, 3, figsize=(inch * 3.2 + 0.9, inch + 1.35), dpi=dpi)

    def pt_for(marker_mm):
        return max(0.6, (marker_mm / target_mm_px) * 72.0 / dpi)

    pt = pt_for(0.45)
    mm_px = None
    for ax, (title, i, j, la, lb) in zip(axes, F37.VIEWS):
        ax.set_facecolor("white")
        ax.scatter(xyz[order, i], xyz[order, j], c=rgba[order], s=pt ** 2, marker="o",
                   linewidths=0, alpha=1.0, zorder=2)
        m0 = cid == 0
        if m0.any():
            ax.scatter(xyz[m0, i], xyz[m0, j], c=rgba[m0], s=pt ** 2, marker="o",
                       edgecolors="black", linewidths=0.15, zorder=3)
        ax.set_xlim(mid[i] - half, mid[i] + half)
        ax.set_ylim(mid[j] - half, mid[j] + half)
        ax.set_aspect("equal", adjustable="box")
        ax.set_title(title, fontsize=8)
        ax.set_xlabel("%s (mm)" % la, fontsize=7)
        ax.set_ylabel("%s (mm)" % lb, fontsize=7)
        ax.tick_params(labelsize=6, length=2)
        bx = mid[i] - half + span_p * 0.04
        by = mid[j] - half + span_p * 0.10
        ax.plot([bx, bx + 5.0], [by, by], color="black", lw=2.0, solid_capstyle="butt", zorder=5)
        ax.text(bx + 2.5, by + span_p * 0.015, "5 mm", ha="center", va="bottom", fontsize=6.5,
                zorder=5)
    fig.canvas.draw()
    box = axes[0].get_window_extent()
    mm_px = ((axes[0].get_xlim()[1] - axes[0].get_xlim()[0]) / float(box.width),
             (axes[0].get_ylim()[1] - axes[0].get_ylim()[0]) / float(box.height))
    sm = cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    cb = fig.colorbar(sm, ax=axes, fraction=0.022, pad=0.012)
    cb.set_label("region rank (0 = largest, log scale)", fontsize=7)
    cb.ax.tick_params(labelsize=6)
    handles = [Line2D([], [], marker="o", ls="", markersize=4, color=cmap(norm(1.0)),
                      label="rank 0 (largest, black edge)"),
               Line2D([], [], marker="o", ls="", markersize=4, color=cmap(norm(min(8.0, rmax))),
                      label="rank 8"),
               Line2D([], [], marker="o", ls="", markersize=4, color=cmap(norm(rmax)),
                      label="rank %d (smallest)" % int(rmax))]
    fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=7, frameon=False,
               bbox_to_anchor=(0.5, 0.005))
    fig.suptitle("%s pre-floor regions, every region coloured (no grey pool), full opacity, "
                 "0.45 mm marker: npts=%d regions=%d largest=%d   mm/px %.4f x %.4f   5 mm bar   "
                 "(%s PLY)" % (piece, len(xyz), len(np.unique(cid)), int(np.bincount(cid + 1)[1:].max())
                               if len(np.unique(cid)) else 0, mm_px[0], mm_px[1], fmt), fontsize=8)
    fig.tight_layout(rect=(0, 0.07, 1, 0.93))
    pad = 0.06
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    tb = fig.get_tightbbox(rend)                     # inches, before the pad
    fig.savefig(outpath, facecolor="white", bbox_inches="tight", pad_inches=pad)
    with Image.open(outpath) as im:
        w, h = im.size
    # panel rectangles in saved-PNG pixels (origin top-left): the saved image holds the tight
    # bbox plus the pad, so subtract that origin and flip y
    px0_in = tb.x0 - pad
    py0_in = tb.y0 - pad
    def to_png(x_disp, y_disp):
        return (int(round(x_disp - px0_in * dpi)), int(round(h - (y_disp - py0_in * dpi))))

    boxes, plot_boxes = [], []
    for ax in axes:
        b = ax.get_window_extent(rend)
        bx0, by1 = to_png(b.x0, b.y0)
        bx1, by0 = to_png(b.x1, b.y1)
        boxes.append((max(0, bx0), min(w, bx1), max(0, by0), min(h, by1)))
        # the data rectangle in the same pixels: everything inside is drawing, not furniture.
        # Inset 3 px so the spines and the tick marks just outside them fall out.
        x0d, y0d = to_png(*ax.transData.transform((ax.get_xlim()[0], ax.get_ylim()[0])))
        x1d, y1d = to_png(*ax.transData.transform((ax.get_xlim()[1], ax.get_ylim()[1])))
        plot_boxes.append((max(0, min(x0d, x1d) + 3), min(w, max(x0d, x1d) - 3),
                           max(0, min(y0d, y1d) + 3), min(h, max(y0d, y1d) - 3)))
    plt.close(fig)
    sizes = {}
    for c in cid.tolist():
        sizes[int(c)] = sizes.get(int(c), 0) + 1
    return {"piece": piece, "ply": os.path.basename(ply), "png": os.path.basename(outpath),
            "points": int(len(xyz)), "regions": len(sizes),
            "largest_region": int(max(sizes.values())),
            "mm_per_px": [round(mm_px[0], 6), round(mm_px[1], 6)],
            "pixel_width": w, "pixel_height": h, "dpi": round(dpi, 1),
            "marker_mm": 0.45, "alpha": 1.0, "palette": "turbo, log over rank",
            "scale_bar_mm": 5.0, "bytes": os.path.getsize(outpath),
            "panel_boxes": boxes, "plot_boxes": plot_boxes}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--t37", required=True, help="directory holding ticket 37's pre-floor PLYs")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--p9", default="Juglet_Piece_9")
    ap.add_argument("--pota", default="Pot_A_Piece_07")
    ap.add_argument("--t37-target-p9", type=float, default=0.05)
    ap.add_argument("--t37-target-pota", type=float, default=0.085)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    rec = {"t37_dir": a.t37, "definition": {"ink_thresh": INK_THRESH,
                                           "grey_chroma": GREY_CHROMA,
                                           "panel_split_white_px": 8},
           "replay": [], "redraw": [], "measure_replay": [], "measure_redraw": []}
    for piece, tgt in ((a.p9, a.t37_target_p9), (a.pota, a.t37_target_pota)):
        cand = sorted(glob.glob(os.path.join(a.t37, piece + "*.ply")))
        if not cand:
            print("[PARTE] %s: no pre-floor PLY under %s" % (piece, a.t37))
            continue
        ply = cand[0]
        # (1) replay the ticket-37 style so the measurement can be calibrated against its record
        rep = os.path.join(a.outdir, "%s_t37style_replay.png" % piece)
        meta = F37.render(piece + " (ticket-37 style replay)", ply, "", rep, tgt)
        rec["replay"].append(meta)
        rec["measure_replay"].append(measure_png(rep, "%s t37-style replay" % piece,
                                                 meta["points"]))
        # (2) the redraw the ticket asks for
        out = os.path.join(a.outdir, "%s_partE_ranked_fullopacity.png" % piece)
        m2 = draw_e(piece, ply, out, tgt)
        rec["redraw"].append(m2)
        m_ax = measure_png(out, "%s partE redraw axes box" % piece, m2["points"],
                           boxes=m2["panel_boxes"])
        m_pl = measure_png(out, "%s partE redraw plot interior" % piece, m2["points"],
                           boxes=m2["plot_boxes"])
        rec["measure_redraw"].append({"axes_box": m_ax, "plot_interior": m_pl})
    with open(os.path.join(a.outdir, "parte38.json"), "w") as f:
        json.dump(rec, f, indent=1, sort_keys=True)
    print("[PARTE] wrote %s" % os.path.join(a.outdir, "parte38.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
