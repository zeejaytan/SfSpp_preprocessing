#!/usr/bin/env python3
"""ticket 37 part D: render pre-floor regions as three orthographic views.

The colour map is fixed by the ticket and never varies with the data: 0 blue, 1 red, 2 green,
3 violet, 4 orange, 5 brown, 6 pink, 7 cyan, -1 grey.  Region ids beyond 7 share grey with -1
(no-region) and the figure says so, so nothing is silently recoloured.

One piece is drawn at one scale in all three views (a cube around the bounding box).  mm/px is
MEASURED from the rendered axes box, not estimated: the figure is laid out, measured, and
re-laid-out at a corrected dpi until the measured value is within 5% of --target-mm-px.  The
measured mm/px and a 5 mm bar are printed on every figure.

usage: fig37.py --dumpdir <dir> --outdir <dir> [--target-mm-px 0.2] [--pieces a,b,c]
"""
import argparse
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

FIXED = {-1: ("grey", "no region / id >= 8"), 0: ("blue", "region 0"),
         1: ("red", "region 1"), 2: ("green", "region 2"), 3: ("violet", "region 3"),
         4: ("orange", "region 4"), 5: ("brown", "region 5"), 6: ("pink", "region 6"),
         7: ("cyan", "region 7")}
PLY_TYPES = {"char": "i1", "uchar": "u1", "int8": "i1", "uint8": "u1", "short": "i2",
             "ushort": "u2", "int16": "i2", "uint16": "u2", "int": "i4", "uint": "u4",
             "int32": "i4", "uint32": "u4", "float": "f4", "float32": "f4",
             "double": "f8", "float64": "f8"}
VIEWS = [("XY  (looking down -Z)", 0, 1, "x", "y"), ("XZ  (looking down -Y)", 0, 2, "x", "z"),
         ("YZ  (looking down -X)", 1, 2, "y", "z")]


def read_ply_vertices(path):
    """Return (named columns dict, n, fmt) for the vertex element of an ascii or binary PLY."""
    with open(path, "rb") as f:
        raw = f.read()
    end = raw.find(b"end_header")
    if end < 0:
        raise ValueError("PLY %s: no end_header" % path)
    nl = raw.find(b"\n", end)
    head = raw[:nl].decode("ascii", "replace").splitlines()
    body_at = nl + 1
    fmt = "ascii"
    elements = []
    for line in head:
        p = line.split()
        if not p:
            continue
        if p[0] == "format":
            fmt = p[1]
        elif p[0] == "element":
            elements.append([p[1], int(p[2]), []])
        elif p[0] == "property" and elements:
            elements[-1][2].append((p[2], p[1]))
    for name, cnt, props in elements:
        if name == "vertex" and fmt == "ascii":
            rows = []
            at = body_at
            for _ in range(cnt):
                nl2 = raw.find(b"\n", at)
                if nl2 < 0:
                    nl2 = len(raw)
                rows.append(raw[at:nl2].split())
                at = nl2 + 1
            cols = {}
            for i, (pn, _pt) in enumerate(props):
                cols[pn] = np.array([r[i] for r in rows])
            return cols, cnt, fmt
        if fmt == "ascii":
            at = body_at
            for _ in range(cnt):
                at = raw.find(b"\n", at) + 1
            body_at = at
        else:
            dtype = np.dtype([(pn, "<" + PLY_TYPES[pt]) for pn, pt in props])
            arr = np.frombuffer(raw, dtype=dtype, count=cnt, offset=body_at)
            body_at += dtype.itemsize * cnt
            if name == "vertex":
                return {pn: arr[pn] for pn, _pt in props}, cnt, fmt
    raise ValueError("PLY %s: no vertex element" % path)


def load_piece(path):
    cols, n, fmt = read_ply_vertices(path)
    for k in ("x", "y", "z"):
        if k not in cols:
            raise ValueError("PLY %s: no property %s" % (path, k))
    xyz = np.column_stack([cols["x"], cols["y"], cols["z"]]).astype(np.float64)
    cid = cols["cluster_id"].astype(np.int64) if "cluster_id" in cols else np.full(n, -1, np.int64)
    return xyz, cid, fmt


def colour_of(cid):
    if 0 <= cid <= 7:
        return FIXED[cid][0]
    return "grey"


def _draw(piece, xyz, cid, fmt, outpath, target_mm_px, dpi, geometry):
    lo, hi, mid, half, span_p = geometry
    inch = (span_p / target_mm_px) / dpi
    fig, axes = plt.subplots(1, 3, figsize=(inch * 3 + 0.9, inch + 1.15), dpi=dpi)
    order = np.argsort(cid)  # tail first, so the eight named colours stay on top
    colours = [colour_of(int(c)) for c in cid[order]]
    marker_pt = max(0.4, 2.2 * target_mm_px)
    mm_px = None
    for ax, (title, i, j, la, lb) in zip(axes, VIEWS):
        ax.set_facecolor("white")
        ax.scatter(xyz[order, i], xyz[order, j], c=colours, s=marker_pt ** 2, marker=".",
                   linewidths=0, edgecolors="none")
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
    sizes = {}
    for c in cid.tolist():
        sizes[int(c)] = sizes.get(int(c), 0) + 1
    top = sorted([c for c in sizes if 0 <= c <= 7])
    handles = [Line2D([], [], marker="o", ls="", markersize=4, color=colour_of(c),
                      label="%d %s n=%d" % (c, FIXED[c][0], sizes.get(c, 0))) for c in top]
    tail = sum(v for k, v in sizes.items() if k > 7 or k < 0)
    handles.append(Line2D([], [], marker="o", ls="", markersize=4, color="grey",
                          label="id>=8 / none n=%d" % tail))
    fig.legend(handles=handles, loc="lower center", ncol=min(6, len(handles)), fontsize=7,
               frameon=False, bbox_to_anchor=(0.5, 0.0))
    fig.suptitle("%s pre-floor regions: npts=%d regions=%d largest=%d   mm/px %.4f x %.4f   "
                 "5 mm bar   (%s PLY)" % (piece, len(xyz), len(sizes), max(sizes), mm_px[0],
                                          mm_px[1], fmt), fontsize=8)
    fig.tight_layout(rect=(0, 0.10, 1, 0.93))
    # bbox_inches="tight" crops/expands the whitespace only: the axes box keeps its pixel size, so
    # the mm/px measured above still describes the saved file. Read the true size back.
    w = h = None
    if outpath:
        fig.savefig(outpath, facecolor="white", bbox_inches="tight", pad_inches=0.06)
        from PIL import Image
        with Image.open(outpath) as im:
            w, h = im.size
    if w is None:
        w = int(round(fig.get_size_inches()[0] * dpi))
        h = int(round(fig.get_size_inches()[1] * dpi))
    plt.close(fig)
    return mm_px, sizes, w, h


def render(piece, ply, sidecar, outpath, target_mm_px):
    xyz, cid, fmt = load_piece(ply)
    lo = xyz.min(axis=0)
    hi = xyz.max(axis=0)
    span = float((hi - lo).max())
    half = span / 2.0 + span * 0.05
    geometry = (lo, hi, (lo + hi) / 2.0, half, 2.0 * half)
    dpi = 110.0
    mm_px, sizes, w, h = _draw(piece, xyz, cid, fmt, None, target_mm_px, dpi, geometry)
    for _ in range(3):
        if abs(mm_px[0] - target_mm_px) <= 0.05 * target_mm_px:
            break
        dpi = max(50.0, min(400.0, dpi * mm_px[0] / target_mm_px))
        mm_px, sizes, w, h = _draw(piece, xyz, cid, fmt, None, target_mm_px, dpi, geometry)
    mm_px, sizes, w, h = _draw(piece, xyz, cid, fmt, outpath, target_mm_px, dpi, geometry)
    meta = {"piece": piece, "ply": os.path.basename(ply), "png": os.path.basename(outpath),
            "points": int(len(xyz)), "regions": len(sizes), "largest_region": int(max(sizes)),
            "region_sizes_top8": {int(k): int(v) for k, v in
                                  sorted(sizes.items(), key=lambda kv: -kv[1])[:8]},
            "mm_per_px": [round(mm_px[0], 6), round(mm_px[1], 6)], "scale_bar_mm": 5.0,
            "pixel_width": w, "pixel_height": h, "bytes": os.path.getsize(outpath),
            "dpi": round(dpi, 1), "target_mm_px": target_mm_px,
            "sidecar": os.path.basename(sidecar) if sidecar else None}
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dumpdir", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--target-mm-px", type=float, default=0.2)
    ap.add_argument("--pieces", default="")
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    pieces = [p for p in a.pieces.split(",") if p] or sorted(
        f[:-4] for f in os.listdir(a.dumpdir) if f.endswith(".ply"))
    metas = []
    for piece in pieces:
        ply = os.path.join(a.dumpdir, piece + ".ply")
        side = os.path.join(a.dumpdir, piece + ".json")
        if not os.path.exists(ply):
            print("[F37] MISSING %s" % ply, file=sys.stderr)
            continue
        out = os.path.join(a.outdir, piece + "_regions_3views.png")
        m = render(piece, ply, side if os.path.exists(side) else None, out, a.target_mm_px)
        metas.append(m)
        print("[F37] %s px=%dx%d mm/px=%.4f bar=5mm bytes=%d regions=%d largest=%d" %
              (piece, m["pixel_width"], m["pixel_height"], m["mm_per_px"][0], m["bytes"],
               m["regions"], m["largest_region"]))
    with open(os.path.join(a.outdir, "figures37.json"), "w") as f:
        json.dump(metas, f, indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
