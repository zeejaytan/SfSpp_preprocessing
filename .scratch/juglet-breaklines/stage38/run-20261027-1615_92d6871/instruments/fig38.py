#!/usr/bin/env python3
"""Ticket 38 figure: the largest pre-floor region at every density, against the original mesh,
one panel per (level, view), same camera and scale within a piece, 5 mm bar and measured mm/px
printed; below them the largest region against achieved spacing with the 50-point floor and the
level at which the floor is reached marked.

The camera is the ORIGINAL MESH's cube, so the four levels of one piece are comparable pixel for
pixel: the mesh does not move, only the cloud density does.

usage: fig38.py --cells <dir> --mesh M.obj --piece P --outdir O [--arm A] [--target-mm-px 0.05]
                [--levels 1,2,4,10]
"""
import argparse
import glob
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fig37 as F37            # read_ply_vertices: ascii and binary PLY, unchanged
import measure34 as M          # read_obj: the original mesh and its area-weighted normals


def load_cell(cells, piece, arm, level):
    js = os.path.join(cells, "%s_%s_x%d_cell.json" % (piece, arm, level))
    if not os.path.exists(js):
        return None
    with open(js) as f:
        meta = json.load(f)
    ply = os.path.join(cells, "%s_%s_x%d_prefloor_regions.ply" % (piece, arm, level))
    if not os.path.exists(ply):
        return None
    cols, n, fmt = F37.read_ply_vertices(ply)
    xyz = np.column_stack([cols["x"], cols["y"], cols["z"]]).astype(np.float64)
    cid = cols["cluster_id"].astype(np.int64) if "cluster_id" in cols else np.full(n, -1, np.int64)
    return meta, xyz, cid, fmt


def _panel(ax, mesh_xyz, xyz, cid, view, geometry, marker_mm, mm_px_target, dpi):
    _title, i, j, la, lb = view
    _lo, _hi, mid, half, span_p = geometry
    pt = max(0.6, (marker_mm / mm_px_target) * 72.0 / dpi)

    def pt_for(m):
        return max(0.6, (m / mm_px_target) * 72.0 / dpi)

    ax.set_facecolor("white")
    ax.scatter(mesh_xyz[:, i], mesh_xyz[:, j], c="#d9d9d9", s=pt_for(0.30) ** 2, marker="o",
               linewidths=0, zorder=1)
    m1 = cid == 1
    if m1.any():
        ax.scatter(xyz[m1, i], xyz[m1, j], c="red", s=pt ** 2, marker="o", edgecolors="black",
                   linewidths=0.10, alpha=0.85, zorder=2)
    m0 = cid == 0
    if m0.any():
        ax.scatter(xyz[m0, i], xyz[m0, j], c="blue", s=pt ** 2, marker="o", edgecolors="black",
                   linewidths=0.10, zorder=3)
    ax.set_xlim(mid[i] - half, mid[i] + half)
    ax.set_ylim(mid[j] - half, mid[j] + half)
    ax.set_aspect("equal", adjustable="box")
    ax.tick_params(labelsize=5, length=2)
    ax.set_xlabel("%s (mm)" % la, fontsize=6)
    ax.set_ylabel("%s (mm)" % lb, fontsize=6)
    bx = mid[i] - half + span_p * 0.04
    by = mid[j] - half + span_p * 0.10
    ax.plot([bx, bx + 5.0], [by, by], color="black", lw=2.0, solid_capstyle="butt", zorder=5)
    ax.text(bx + 2.5, by + span_p * 0.015, "5 mm", ha="center", va="bottom", fontsize=6, zorder=5)


def _draw(piece, mesh_xyz, rows, geometry, outpath, target_mm_px, dpi, arm):
    _lo, _hi, mid, half, span_p = geometry
    inch = (span_p / target_mm_px) / dpi
    nrow = len(rows)
    fig = plt.figure(figsize=(inch * 3.0 + 1.5, inch * nrow + 1.9 + 0.9 * nrow), dpi=dpi)
    gs = fig.add_gridspec(nrow + 1, 4, height_ratios=[1.0] * nrow + [1.25],
                          width_ratios=[0.17, 1.0, 1.0, 1.0],
                          hspace=0.55, wspace=0.22,
                          left=0.012, right=0.995, top=1.0 - 0.30 / (nrow + 1.4), bottom=0.035)
    axes = []
    for r, (level, meta, xyz, cid, fmt) in enumerate(rows):
        for c, view in enumerate(F37.VIEWS):
            ax = fig.add_subplot(gs[r, c + 1])
            _panel(ax, mesh_xyz, xyz, cid, view, geometry, 0.55, target_mm_px, dpi)
            if r == 0:
                ax.set_title(view[0], fontsize=7)
            if c == 0:
                tag = "x%d\nn=%s" % (level, (meta["points"] if meta else "?"))
                if meta:
                    tag += ("\nreq %.4f\nach %.4f" %
                            (meta["requested_spacing_mm"], meta["achieved_spacing_mm"]))
                lab = fig.add_subplot(gs[r, 0])
                lab.axis("off")
                lab.text(0.98, 0.5, tag, ha="right", va="center", transform=lab.transAxes,
                         fontsize=6.5, linespacing=1.15)
            axes.append(ax)
    fig.canvas.draw()
    box = axes[0].get_window_extent()
    mm_px = ((axes[0].get_xlim()[1] - axes[0].get_xlim()[0]) / float(box.width),
             (axes[0].get_ylim()[1] - axes[0].get_ylim()[0]) / float(box.height))
    # bottom: largest region against achieved spacing
    axp = fig.add_subplot(gs[nrow, 1:])
    styles = {"A": ("blue", "arm A  analytic face normals"),
              "F": ("#1a9850", "arm F  face normals, viewpoint flip"),
              "B": ("#d95f02", "arm B  pipeline PCA re-estimation")}
    floor = 50
    axp.axhline(floor, color="black", ls="--", lw=1.0)
    axp.text(0.995, floor * 1.06, "50-point floor", ha="right", va="bottom", fontsize=7,
             transform=axp.get_yaxis_transform())
    handles = []
    reached = None
    for arm_key in ("A", "F", "B"):
        pts = []
        for level, meta, _xyz, _cid, _fmt in rows:
            if meta and meta["arm"] == arm_key:
                pts.append((meta["achieved_spacing_mm"], meta["largest"], level))
        if not pts:
            continue
        pts.sort(key=lambda t: -t[0])
        col, lab = styles[arm_key]
        xs = [p[0] for p in pts]
        ys = [max(1, p[1]) for p in pts]
        axp.plot(xs, ys, "-o", color=col, ms=4, lw=0.9, label=lab)
        for x, y, lv in pts:
            axp.annotate("x%d" % lv, (x, max(1, y)), textcoords="offset points", xytext=(3, 4),
                         fontsize=6, color=col)
        if arm_key == arm:
            for x, y, lv in pts:
                if y >= floor and (reached is None or y > reached[1]):
                    reached = (lv, y, x)
        handles.append(Line2D([], [], color=col, marker="o", ms=4, lw=0.9, label=lab))
    axp.set_xlabel("achieved spacing (mm, halved and tenth-ed by the level)", fontsize=7)
    axp.set_ylabel("largest pre-floor region (points, log)", fontsize=7)
    axp.set_yscale("log")
    axp.tick_params(labelsize=6)
    axp.grid(True, which="both", lw=0.3, alpha=0.4)
    handles.append(Line2D([], [], color="black", ls="--", lw=1.0, label="50-point floor"))
    axp.legend(handles=handles, fontsize=6.5, loc="upper right", frameon=False)
    note = ("largest region reaches the floor at x%d (%d points, %.5f mm)"
            % (reached[0], reached[1], reached[2])) if reached else \
           ("no level tested reaches the 50-point floor for arm %s" % arm)
    axp.set_title(note, fontsize=7.5)
    fig.suptitle("%s: largest pre-floor region at 3.4 deg by sampling density, drawn against the "
                 "original mesh   mm/px %.4f x %.4f   5 mm bar   arm %s"
                 % (piece, mm_px[0], mm_px[1], arm), fontsize=8.5, y=0.995)
    if outpath:
        fig.savefig(outpath, facecolor="white", bbox_inches="tight", pad_inches=0.06)
        from PIL import Image
        with Image.open(outpath) as im:
            w, h = im.size
    else:
        w = int(round(fig.get_size_inches()[0] * dpi))
        h = int(round(fig.get_size_inches()[1] * dpi))
    plt.close(fig)
    return mm_px, w, h, reached


def render_piece(cells, mesh, piece, outdir, arm="A", target_mm_px=0.05, levels=(1, 2, 4, 10)):
    verts, _vn = M.read_obj(mesh)
    have = []
    for lv in levels:
        got = load_cell(cells, piece, arm, lv)
        if got is None:
            print("[FIG38] %s x%d arm %s: no cell, skipped" % (piece, lv, arm))
            continue
        have.append((lv,) + got)
    if not have:
        print("[FIG38] %s arm %s: nothing to draw" % (piece, arm))
        return None
    lo, hi = verts.min(axis=0), verts.max(axis=0)
    span = float((hi - lo).max())
    half = span / 2.0 + span * 0.05
    geometry = (lo, hi, (lo + hi) / 2.0, half, 2.0 * half)
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, "%s_resolution_by_density.png" % piece)
    dpi = 110.0
    mm_px, w, h, reached = _draw(piece, verts, have, geometry, None, target_mm_px, dpi, arm)
    for _ in range(6):
        if abs(mm_px[0] - target_mm_px) <= 0.05 * target_mm_px:
            break
        dpi = max(50.0, min(1200.0, dpi * mm_px[0] / target_mm_px))
        mm_px, w, h, reached = _draw(piece, verts, have, geometry, None, target_mm_px, dpi, arm)
    conv = ("converged within 5 pct of the %.6f mm/px target" % target_mm_px
            if abs(mm_px[0] - target_mm_px) <= 0.05 * target_mm_px else
            "did NOT converge to the %.6f mm/px target inside 6 iterations" % target_mm_px)
    print("[FIG38] dpi solve: %.1f dpi, %s" % (dpi, conv))
    mm_px, w, h, reached = _draw(piece, verts, have, geometry, out, target_mm_px, dpi, arm)
    meta = {"piece": piece, "png": os.path.basename(out), "arm": arm,
            "levels_drawn": [r[0] for r in have], "mesh": os.path.basename(mesh),
            "mesh_vertices": int(len(verts)),
            "camera_half_mm": half, "mm_per_px": [round(mm_px[0], 6), round(mm_px[1], 6)],
            "scale_bar_mm": 5.0, "pixel_width": w, "pixel_height": h,
            "bytes": os.path.getsize(out), "dpi": round(dpi, 1),
            "target_mm_px": target_mm_px,
            "floor_reached_at": (None if not reached else
                                 {"level": reached[0], "largest": reached[1],
                                  "achieved_mm": reached[2]}),
            "rows": [{"level": r[0], "points": (r[1] or {}).get("points"),
                      "regions": (r[1] or {}).get("regions"),
                      "largest": (r[1] or {}).get("largest"),
                      "requested_mm": (r[1] or {}).get("requested_spacing_mm"),
                      "achieved_mm": (r[1] or {}).get("achieved_spacing_mm")} for r in have]}
    with open(os.path.join(outdir, "figure_%s.json" % piece), "w") as f:
        json.dump(meta, f, indent=1, sort_keys=True)
    print("[FIG38] %s arm %s -> %s  levels=%s mm/px=%.4f x %.4f px=%dx%d bytes=%d floor_at=%s"
          % (piece, arm, out, meta["levels_drawn"], mm_px[0], mm_px[1], w, h,
             meta["bytes"], meta["floor_reached_at"]))
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", required=True)
    ap.add_argument("--mesh", required=True)
    ap.add_argument("--piece", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--arm", default="A")
    ap.add_argument("--target-mm-px", type=float, default=0.05)
    ap.add_argument("--levels", default="1,2,4,10")
    a = ap.parse_args()
    levels = tuple(int(v) for v in a.levels.split(",") if v)
    m = render_piece(a.cells, a.mesh, a.piece, a.outdir, a.arm, a.target_mm_px, levels)
    return 0 if m else 1


if __name__ == "__main__":
    sys.exit(main())
