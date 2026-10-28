#!/usr/bin/env python3
"""Ticket 39 instrument: the picture of what each arm wrote.

The tables in this ticket say the two surfaces separate in own mode; this instrument is the look at
them the ticket also asks for.  It draws, from the SAME arrays it measures:

  views   per arm, the two written surfaces in two colours over the sherd's cloud: three
          orthographic projections on the combined surfaces' own principal axes, plus ONE edge-on
          view whose PLANE CONTAINS the mean normal of Surface_0 -- the page's horizontal axis of
          that panel IS that normal, and the view direction is perpendicular to it, which is what
          puts the normal in the plane of the view rather than along the line of sight.  All four
          panels share one mm/px; each carries a 5 mm bar and prints its own mm/px.
  hist    the signed through-distance of every Surface_1 point to its nearest Surface_0 point,
          measured along Surface_0's own normal (measure34.pair_pointwise's t): one panel per arm,
          on ONE common x axis and ONE common set of bins, so a nested pair and a separated pair
          are read off the same scale.

Nothing here re-implements a reader or a statistic: the PLY/PCD readers, the normal fallback, the
folded angle and the pair statistic are measure34's, and the shared-position and mean-normal
quantities are nest39's.  Their results are written into this instrument's own JSON beside the
figure paths, byte counts and input md5s, so a figure can never be a picture of a different surface
than the table row it is set beside.

usage:
  fig39.py selftest
  fig39.py render --piece P --level L --cloud C.pcd --a-s0 A0.ply --a-s1 A1.ply \
                  --b-s0 B0.ply --b-s1 B1.ply --outdir D --tag T
"""
import argparse
import hashlib
import json
import os
import sys
import tempfile

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import measure34 as M          # noqa: E402
import nest39 as N             # noqa: E402

C_S0 = "#1f4fd8"
C_S1 = "#e8620c"
C_CLOUD = "#b8b8b8"
BAR_MM = 5.0
BIN_MM = 0.1
DPI = 150
PAD = 1.06


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def pca_frame(pts):
    """Centroid and principal axes of the combined surfaces, largest variance first.  The sign of
    each axis is fixed by making its largest-magnitude component positive, so the same points give
    the same picture every time -- an axis whose sign floated would mirror a panel at random."""
    c = pts.mean(axis=0)
    X = pts - c
    w, V = np.linalg.eigh(X.T @ X / float(max(1, len(X))))
    V = V[:, np.argsort(w)[::-1]]
    for k in range(3):
        j = int(np.argmax(np.abs(V[:, k])))
        if V[j, k] < 0.0:
            V[:, k] = -V[:, k]
    return c, V


def edge_on_frame(n0m, pts, V):
    """(page_x, page_y, view_direction) for the view whose plane contains n0m.

    page_x is n0m itself, so the panel's horizontal axis is the direction the two sheets are
    separated along; page_y is the in-plane direction in which the points are widest, so the panel
    shows the most of the sherd; the view direction is their cross product, perpendicular to n0m by
    construction.  A view direction perpendicular to n0m is exactly what makes n0m lie in the plane
    of the view instead of pointing along the line of sight."""
    n = np.asarray(n0m, dtype=np.float64)
    n = n / np.linalg.norm(n)
    cand = []
    for k in range(3):
        e = V[:, k] - float(V[:, k] @ n) * n
        ln = float(np.linalg.norm(e))
        if ln > 1e-9:
            cand.append(e / ln)
    if not cand:
        raise ValueError("no in-plane direction: n0m is orthogonal to all three principal axes")
    c = pts.mean(axis=0)
    v = max(cand, key=lambda u: float(np.ptp((pts - c) @ u)))
    w = np.cross(n, v)
    w = w / float(np.linalg.norm(w))
    return n, v, w


def _centroid(arm, u, v):
    m = np.vstack([arm["s0"]["pts"], arm["s1"]["pts"]]).mean(axis=0)
    return float(m @ u), float(m @ v)


def _proj(pts, u, v, cx, cy):
    return pts @ u - cx, pts @ v - cy


def _draw_panel(ax, u, v, cx, cy, L, cloud, arm, first):
    xc, yc = _proj(cloud, u, v, cx, cy)
    ax.plot(xc, yc, ".", ms=1.1, color=C_CLOUD, alpha=0.55, zorder=1,
            label="sherd cloud" if first else None)
    for key, col, lab in (("s0", C_S0, "Surface_0"), ("s1", C_S1, "Surface_1")):
        x, y = _proj(arm[key]["pts"], u, v, cx, cy)
        ax.plot(x, y, ".", ms=1.5, color=col, alpha=0.9, zorder=2,
                label=lab if first else None)
    ax.set_xlim(-L / 2.0, L / 2.0)
    ax.set_ylim(-L / 2.0, L / 2.0)
    ax.set_aspect("equal", adjustable="box")
    ax.tick_params(labelsize=7)
    ax.set_xlabel("mm", fontsize=8)
    ax.set_ylabel("mm", fontsize=8)


def _scale_bar(ax, L):
    bx = -L / 2.0 + 0.06 * L
    by = -L / 2.0 + 0.075 * L
    ax.plot([bx, bx + BAR_MM], [by, by], "-", color="k", lw=3.2,
            solid_capstyle="butt", zorder=20)
    ax.text(bx + BAR_MM / 2.0, by + 0.028 * L, "%.0f mm" % BAR_MM,
            ha="center", va="bottom", fontsize=8.5, zorder=20)


def render_all(piece, tag, level, cloud, arms, outdir, dpi=DPI):
    os.makedirs(outdir, exist_ok=True)
    keys = sorted(arms)
    allpts = np.vstack([cloud] + [arms[k][s]["pts"] for k in keys for s in ("s0", "s1")])
    _c, V = pca_frame(allpts)
    ortho = [("e0-e1", V[:, 0], V[:, 1]),
             ("e0-e2", V[:, 0], V[:, 2]),
             ("e1-e2", V[:, 1], V[:, 2])]
    panels, edge_rec = {}, {}
    for k in keys:
        n, v, w = edge_on_frame(N.mean_normal(arms[k]["s0"]["nrm"]), allpts, V)
        edge_rec[k] = {"page_x": n.tolist(), "page_y": v.tolist(), "view_dir": w.tolist(),
                       "page_x_is": "the mean normal of Surface_0",
                       "plane_contains": "the mean normal of Surface_0"}
        panels[k] = list(ortho) + [("edge-on, plane contains Surface_0's mean normal", n, v)]

    L = 0.0
    for k in keys:
        P = np.vstack([cloud, arms[k]["s0"]["pts"], arms[k]["s1"]["pts"]])
        for _n, u, v in panels[k]:
            L = max(L, float(np.ptp(P @ u)), float(np.ptp(P @ v)))
    L = max(L * PAD, 1e-6)

    rec = {"piece": piece, "tag": tag, "level": level, "cloud_kind": "SYNTHETIC",
           "panel_span_mm": L, "bar_mm": BAR_MM, "dpi": dpi, "pad": PAD,
           "colours": {"surface_0": C_S0, "surface_1": C_S1, "cloud": C_CLOUD},
           "pca_axes": V.tolist(), "edge_on": edge_rec, "views": {}}

    for k in keys:
        fig, axes = plt.subplots(2, 2, figsize=(12.6, 13.0), dpi=dpi)
        fig.subplots_adjust(left=0.055, right=0.985, top=0.900, bottom=0.078,
                            wspace=0.14, hspace=0.20)
        flat = axes.ravel()
        drawn = []
        for ax, (name, u, v) in zip(flat, panels[k]):
            cx, cy = _centroid(arms[k], u, v)
            _draw_panel(ax, u, v, cx, cy, L, cloud, arms[k], first=(ax is flat[0]))
            drawn.append((ax, name))
        fig.canvas.draw()
        vals = []
        for ax, _name in drawn:
            bb = ax.get_window_extent()
            vals.append(L / float(bb.width))
            vals.append(L / float(bb.height))
        mmp = float(np.mean(vals))
        spread = float(np.max(vals) - np.min(vals))
        for ax, name in drawn:
            ax.set_title("%s   ·   %.5f mm/px" % (name, mmp), fontsize=9.5)
            _scale_bar(ax, L)
        flat[0].legend(loc="upper right", fontsize=7.5, markerscale=4, framealpha=0.85)
        fig.suptitle("%s  x%s  —  SYNTHETIC cloud  —  arm %s (%s)"
                     % (piece, level, k, arms[k]["label"]), fontsize=13)
        fig.text(0.5, 0.020,
                 "all four panels at ONE scale: %.5f mm/px (spread over the 8 panel sides %.2e)   ·   "
                 "scale bar %.0f mm   ·   Surface_0 blue, Surface_1 orange, sherd cloud grey"
                 % (mmp, spread, BAR_MM), ha="center", fontsize=9)
        path = os.path.join(outdir, "fig39_%s_arm%s_views_SYNTHETIC.png" % (tag, k))
        fig.savefig(path, dpi=dpi)
        plt.close(fig)
        rec["views"][k] = {"png": path, "bytes": os.path.getsize(path), "md5": md5(path),
                           "mm_per_px": mmp, "mm_per_px_spread": spread,
                           "panels": [n for _a, n in drawn]}
    return rec


def render_hist(piece, tag, level, arms, outdir, dpi=DPI):
    os.makedirs(outdir, exist_ok=True)
    keys = sorted(arms)
    ts = {}
    for k in keys:
        a = arms[k]
        ts[k] = M.pair_pointwise(a["s0"]["pts"], a["s0"]["nrm"],
                                 a["s1"]["pts"], a["s1"]["nrm"])["t"]
    allt = np.concatenate([ts[k] for k in keys])
    lo = np.floor(float(allt.min()) / BIN_MM) * BIN_MM
    hi = np.ceil(float(allt.max()) / BIN_MM) * BIN_MM
    edges = np.arange(lo, hi + BIN_MM, BIN_MM)

    fig, axes = plt.subplots(len(keys), 1, figsize=(12.6, 3.3 * len(keys) + 1.3),
                             dpi=dpi, sharex=True, squeeze=False)
    axes = axes[:, 0]
    rec = {"piece": piece, "tag": tag, "level": level, "cloud_kind": "SYNTHETIC",
           "quantity": "signed through-distance Surface_1 -> nearest Surface_0, along "
                       "Surface_0's own normal (measure34.pair_pointwise t)",
           "bin_mm": BIN_MM, "edges_mm": edges.tolist(), "arms": {}}
    for ax, k in zip(axes, keys):
        c, _e = np.histogram(ts[k], bins=edges)
        ax.bar(edges[:-1], c, width=BIN_MM, align="edge",
               color=(C_S0 if k == "A" else C_S1), alpha=0.85, edgecolor="none")
        med = float(np.median(ts[k]))
        p05, p95 = (float(np.percentile(ts[k], 5)), float(np.percentile(ts[k], 95)))
        ax.axvline(med, color="k", ls="--", lw=1.1)
        ax.axvline(0.0, color="0.45", ls=":", lw=1.0)
        ax.set_ylabel("points", fontsize=9)
        ax.set_title("arm %s (%s)   n=%d   median %.3f mm   p05 %.3f   p95 %.3f"
                     % (k, arms[k]["label"], len(ts[k]), med, p05, p95), fontsize=10)
        ax.tick_params(labelsize=8)
        rec["arms"][k] = {"label": arms[k]["label"], "n": int(len(ts[k])),
                          "median_mm": med, "p05_mm": p05, "p95_mm": p95,
                          "min_mm": float(ts[k].min()), "max_mm": float(ts[k].max()),
                          "counts": [int(x) for x in c],
                          "counts_sum": int(c.sum())}
    axes[-1].set_xlabel("signed through-distance of Surface_1 to Surface_0 along Surface_0's "
                        "normal (mm)   —   negative = Surface_1 lies against that normal",
                        fontsize=9.5)
    axes[-1].set_xlim(lo, hi)
    fig.suptitle("%s  x%s  —  SYNTHETIC cloud  —  Surface_1 against Surface_0, one common axis, "
                 "%.2f mm bins" % (piece, level, BIN_MM), fontsize=12.5)
    fig.subplots_adjust(left=0.075, right=0.985, top=0.885, bottom=0.115, hspace=0.42)
    path = os.path.join(outdir, "fig39_%s_hist_SYNTHETIC.png" % tag)
    fig.savefig(path, dpi=dpi)
    plt.close(fig)
    rec["png"] = path
    rec["bytes"] = os.path.getsize(path)
    rec["md5"] = md5(path)
    return rec


def _load(path):
    pts, nrm, src = N.load(path)
    return {"pts": pts, "nrm": nrm, "src": src, "path": path, "md5": md5(path)}


def cmd_render(a):
    cloud_d = M.read_pcd(a.cloud)
    cloud = cloud_d["xyz"]
    arms = {"A": {"label": a.a_label, "s0": _load(a.a_s0), "s1": _load(a.a_s1)},
            "B": {"label": a.b_label, "s0": _load(a.b_s0), "s1": _load(a.b_s1)}}
    rec = {"piece": a.piece, "tag": a.tag, "level": a.level, "cloud_kind": "SYNTHETIC",
           "cloud": {"path": a.cloud, "points": int(len(cloud)), "md5": md5(a.cloud)},
           "arms": {}}
    for k in sorted(arms):
        a0, a1 = arms[k]["s0"], arms[k]["s1"]
        nest = N.pair_row(a0["pts"], a0["nrm"], a0["src"], a1["pts"], a1["nrm"], a1["src"],
                          tag="%s_arm%s" % (a.tag, k))
        pair = M.pair_stats(a0["pts"], a0["nrm"], a1["pts"], a1["nrm"])
        # pair_stats keeps |t| only; the signed median and its percentiles are what say WHICH SIDE
        # Surface_1 lies on, and they come from the same pointwise pass the histogram is drawn from.
        pw = M.pair_pointwise(a0["pts"], a0["nrm"], a1["pts"], a1["nrm"])
        pair["med_t_signed"] = float(np.median(pw["t"]))
        pair["p05_t_signed"] = float(np.percentile(pw["t"], 5))
        pair["p95_t_signed"] = float(np.percentile(pw["t"], 95))
        rec["arms"][k] = {"label": arms[k]["label"],
                          "surface_0": {"path": a0["path"], "md5": a0["md5"],
                                        "points": int(len(a0["pts"])), "normal_src": a0["src"]},
                          "surface_1": {"path": a1["path"], "md5": a1["md5"],
                                        "points": int(len(a1["pts"])), "normal_src": a1["src"]},
                          "nest": nest, "pair": pair}
    rec["views_figure"] = render_all(a.piece, a.tag, a.level, cloud, arms, a.outdir)
    rec["hist_figure"] = render_hist(a.piece, a.tag, a.level, arms, a.outdir)

    out = os.path.join(a.outdir, "fig39_%s_figures.json" % a.tag)
    with open(out, "w") as f:
        json.dump(rec, f, indent=1, sort_keys=True)
    rec["json"] = out
    for k in sorted(arms):
        v = rec["views_figure"]["views"][k]
        print("[FIG] arm %s views %s %d bytes %.5f mm/px"
              % (k, v["png"], v["bytes"], v["mm_per_px"]))
        n, p = rec["arms"][k]["nest"], rec["arms"][k]["pair"]
        print("[FIG] arm %s shared=%d of_smaller=%.4f meandot=%+.4f med_along=%.4f "
              "med_across=%.4f med_t=%+.4f"
              % (k, n["shared"], n["shared_over_smaller"], n["mean_normal_dot"],
                 p["med_along"], p["med_across"], p["med_t_signed"]))
    h = rec["hist_figure"]
    print("[FIG] hist %s %d bytes bins=%d %.2f mm"
          % (h["png"], h["bytes"], len(h["edges_mm"]) - 1, h["bin_mm"]))
    print("[FIG] record %s" % out)
    return 0


def selftest():
    bad = 0

    # 1. the edge-on frame is orthonormal, its view direction is perpendicular to n0m, and the
    #    page's x axis IS n0m -- that is the whole claim the panel makes.
    n0 = np.array([0.3, -0.5, 0.81])
    n0 = n0 / np.linalg.norm(n0)
    g = np.stack(np.meshgrid(np.arange(6.0), np.arange(6.0)), axis=-1).reshape(-1, 2)
    P = np.column_stack([g, np.zeros(len(g))])
    _c, V = pca_frame(P + np.array([0.0, 0.0, 2.0]))
    px, py, wd = edge_on_frame(n0, P, V)
    orth = (abs(px @ py) < 1e-12 and abs(px @ wd) < 1e-12 and abs(py @ wd) < 1e-12
            and abs(np.linalg.norm(px) - 1) < 1e-12 and abs(np.linalg.norm(wd) - 1) < 1e-12)
    ok = orth and abs(px @ n0 - 1.0) < 1e-12 and abs(wd @ n0) < 1e-12
    print("[FIG-SELFTEST] %s edge-on frame: page_x IS n0m (dot %.6f), view_dir perpendicular "
          "(dot %.2e), orthonormal %s" % ("ok  " if ok else "FAIL", px @ n0, wd @ n0, orth))
    bad += 0 if ok else 1

    # 2. two sheets 2 mm apart along the normal land 2.0 mm apart on that panel's x axis
    up = np.tile(np.array([0.0, 0.0, 1.0]), (len(P), 1))
    px2, _py2, _w2 = edge_on_frame(np.array([0.0, 0.0, 1.0]), P, V)
    sep = float(np.max(np.abs((P + np.array([0.0, 0.0, 2.0])) @ px2 - P @ px2)))
    ok = abs(sep - 2.0) < 1e-12
    print("[FIG-SELFTEST] %s two sheets 2 mm apart project %.12f mm apart on the edge-on x axis"
          % ("ok  " if ok else "FAIL", sep))
    bad += 0 if ok else 1

    # 3. the histogram puts every point in exactly one bin, and both arms share the bins
    ta = np.concatenate([np.zeros(50), np.full(10, -1.0)])
    tb = np.full(40, -2.0)
    allt = np.concatenate([ta, tb])
    lo = np.floor(allt.min() / BIN_MM) * BIN_MM
    hi = np.ceil(allt.max() / BIN_MM) * BIN_MM
    edges = np.arange(lo, hi + BIN_MM, BIN_MM)
    ca, _ = np.histogram(ta, bins=edges)
    cb, _ = np.histogram(tb, bins=edges)
    ok = (int(ca.sum()) == len(ta) and int(cb.sum()) == len(tb) and len(ca) == len(cb))
    print("[FIG-SELFTEST] %s histogram: %d/%d and %d/%d points binned, %d shared bins"
          % ("ok  " if ok else "FAIL", ca.sum(), len(ta), cb.sum(), len(tb), len(ca)))
    bad += 0 if ok else 1

    # 4. end to end on synthetic surfaces: every panel side gives the same mm/px, the PNG lands,
    #    and the 5 mm bar is 5 mm of data
    with tempfile.TemporaryDirectory() as td:
        mk = lambda z: {"pts": P + np.array([0.0, 0.0, z]), "nrm": up, "src": "t",
                        "path": "synthetic", "md5": "0" * 32}
        arms = {"A": {"label": "synthetic nested", "s0": mk(0.0), "s1": mk(0.02)},
                "B": {"label": "synthetic separated", "s0": mk(0.0), "s1": mk(-2.1)}}
        rec = render_all("SYNTH_Piece_00", "selftest", "1", P, arms, td)
        sp = [rec["views"][k]["mm_per_px_spread"] for k in rec["views"]]
        by = [rec["views"][k]["bytes"] for k in rec["views"]]
        ok = (max(sp) < 1e-9 and min(by) > 0 and rec["bar_mm"] == BAR_MM
              and rec["panel_span_mm"] >= BAR_MM)
        print("[FIG-SELFTEST] %s render: mm/px spread %.2e, png bytes %s, bar %.1f mm, span "
              "%.3f mm" % ("ok  " if ok else "FAIL", max(sp), by, rec["bar_mm"],
                           rec["panel_span_mm"]))
        bad += 0 if ok else 1

        h = render_hist("SYNTH_Piece_00", "selftest", "1", arms, td)
        ok = (h["bytes"] > 0 and h["arms"]["A"]["counts_sum"] == len(P)
              and h["arms"]["B"]["counts_sum"] == len(P)
              and abs(h["arms"]["B"]["median_mm"] + 2.1) < 1e-9)
        print("[FIG-SELFTEST] %s hist: %d bytes, counts %d/%d, arm B median %.3f mm (want -2.100)"
              % ("ok  " if ok else "FAIL", h["bytes"], h["arms"]["A"]["counts_sum"],
                 h["arms"]["B"]["counts_sum"], h["arms"]["B"]["median_mm"]))
        bad += 0 if ok else 1

    print("[FIG-SELFTEST] %s (%d failures)" % ("PASS" if bad == 0 else "FAIL", bad))
    return 0 if bad == 0 else 5


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    s = sub.add_parser("selftest")
    s.set_defaults(fn=lambda a: selftest())
    r = sub.add_parser("render")
    for f in ("--piece", "--level", "--cloud", "--a-s0", "--a-s1", "--b-s0", "--b-s1",
              "--outdir", "--tag"):
        r.add_argument(f, required=True)
    r.add_argument("--a-label", default="A (radius)")
    r.add_argument("--b-label", default="B (own)")
    r.set_defaults(fn=cmd_render)
    a = ap.parse_args(argv)
    if not getattr(a, "fn", None):
        ap.print_help()
        return 2
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
