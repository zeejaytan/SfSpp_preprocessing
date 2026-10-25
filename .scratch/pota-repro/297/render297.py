#!/usr/bin/env python3
"""render297.py -- one picture for ticket 297: the Pot D 22 mesh, both Breakline_0 lines, and the
patch enclosed between the authors' chord and our detour.

The geometry of the patch is not re-derived here: it is measure297's, so the picture and the
numbers cannot drift apart.

Usage:  render297.py <run dir> [rep]
Writes: <run>/out/png/p297_D_22_Bl0_chord.png
"""
import importlib.util
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.colors import LightSource
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

C_OURS = "#12b012"
C_AUTH = "#000000"
C_PATCH = "#e0661a"
C_MESH = "#9a9a9a"
LIFT = 0.45
MAXF = 25000


def load_measure(run):
    spec = importlib.util.spec_from_file_location("measure297", os.path.join(run, "scripts", "measure297.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def subsample(arr, cap):
    if len(arr) <= cap:
        return arr, len(arr)
    idx = np.linspace(0, len(arr) - 1, cap).astype(int)
    return arr[idx], len(arr)


def lift(pts, verts, faces, dist=LIFT):
    from scipy.spatial import cKDTree
    tri = verts[faces]
    cen = tri.mean(1)
    nrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    nrm /= (np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-12)
    _, idx = cKDTree(cen).query(pts)
    return pts + dist * nrm[idx]


def shaded(tri, cap):
    idx, total = subsample(np.arange(len(tri)), cap)
    t = tri[idx]
    nrm = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
    shade = LightSource(azdeg=315, altdeg=45).shade_normals(nrm, fraction=1.0)
    base = np.array([0.88, 0.85, 0.78])
    cols = np.clip(shade[:, None] * base[None, :] * 1.22, 0.0, 1.0)
    return Poly3DCollection(t, facecolors=cols, edgecolors="none", linewidths=0), total, len(idx)


def view3d(ax, pts, elev, azim):
    ax.view_init(elev=elev, azim=azim)
    lo, hi = pts.min(0), pts.max(0)
    ctr = (lo + hi) / 2.0
    half = float(max(np.ptp(pts[:, 0]), np.ptp(pts[:, 1]), np.ptp(pts[:, 2]))) * 0.62
    ax.set_xlim(ctr[0] - half, ctr[0] + half)
    ax.set_ylim(ctr[1] - half, ctr[1] + half)
    ax.set_zlim(ctr[2] - half, ctr[2] + half)
    ax.set_box_aspect((1, 1, 1))
    ax.tick_params(labelsize=7)
    for lab, setlab in (("x", ax.set_xlabel), ("y", ax.set_ylabel), ("z", ax.set_zlabel)):
        setlab(lab + " mm", fontsize=8)


def main(argv):
    run = argv[1]
    rep = argv[2] if len(argv) > 2 else "rep1"
    M = load_measure(run)
    res = M.run_all(run, [rep], keep_arrays=True)
    r = res["reps"][rep]
    if "error" in r or "_mask" not in r:
        print("cannot render %s: %s" % (rep, r.get("error", "no patch")))
        return 2
    ctx = res["_ctx"]
    verts, faces = ctx["verts"], ctx["faces"]
    tri = verts[faces]
    auth = ctx["auth"]
    ours = r["_ours"]
    mask = r["_mask"]
    poly = r["_poly"]
    c, n, u, v = r["_plane"]
    i, j = r["stretch"]["i"], r["stretch"]["j"]
    lo, hi = r["chord"]["lo"], r["chord"]["hi"]

    ours_l = lift(ours, verts, faces)
    auth_l = lift(auth, verts, faces)
    fig = plt.figure(figsize=(23, 13.4), dpi=100)
    gs = fig.add_gridspec(2, 3, left=0.035, right=0.985, top=0.895, bottom=0.085, wspace=0.14, hspace=0.18)
    ax3 = fig.add_subplot(gs[0, 0], projection="3d")
    axw = fig.add_subplot(gs[0, 1:])
    axz = fig.add_subplot(gs[1, 0:2])
    axh = fig.add_subplot(gs[1, 2])

    coll, nf_total, nf_drawn = shaded(tri, MAXF)
    ax3.add_collection3d(coll)
    if mask.any():
        ax3.add_collection3d(Poly3DCollection(tri[mask], facecolors=C_PATCH, edgecolors="#5a2400",
                                             linewidths=0.2, alpha=0.95))
    ax3.plot(ours_l[:, 0], ours_l[:, 1], ours_l[:, 2], color=C_OURS, lw=3.0)
    ax3.plot(auth_l[:, 0], auth_l[:, 1], auth_l[:, 2], color=C_AUTH, lw=2.0, ls=(0, (6, 3)))
    view3d(ax3, verts, 24, -60)
    ax3.set_title("MESH, 3D  (dots lifted %.2f mm along the nearest face normal)" % LIFT, fontsize=11)
    ax3.legend(handles=[Line2D([], [], color=C_OURS, lw=3.0, label="ours (Bl0, edge stage)"),
                        Line2D([], [], color=C_AUTH, lw=2.0, ls=(0, (6, 3)), label="authors (Bl0, reference)"),
                        Line2D([], [], color=C_PATCH, lw=8, alpha=0.8,
                               label="patch enclosed between the chord and our detour")],
               loc="upper left", fontsize=9, framealpha=0.9)

    tc = ctx["cen"]
    t2 = np.column_stack([(tc - c) @ u, (tc - c) @ v])
    p2 = np.column_stack([(poly - c) @ u, (poly - c) @ v])
    o2 = np.column_stack([(ours - c) @ u, (ours - c) @ v])
    a2 = np.column_stack([(auth - c) @ u, (auth - c) @ v])
    mid = p2.mean(0)
    for ax, pad, ttl in ((axw, 26.0, "MESH, section cut along the face plane (u-v), whole stretch"),
                         (axz, 9.0, "zoom: the enclosed patch, both lines, the mesh it sits on")):
        keep = (np.abs(t2[:, 0] - mid[0]) < pad) & (np.abs(t2[:, 1] - mid[1]) < pad)
        ax.scatter(t2[keep, 0], t2[keep, 1], s=3.0, c=C_MESH, alpha=0.55, linewidths=0, rasterized=True)
        if mask.any():
            q1 = np.column_stack([(tri[mask][:, 0] - c) @ u, (tri[mask][:, 0] - c) @ v])
            q2 = np.column_stack([(tri[mask][:, 1] - c) @ u, (tri[mask][:, 1] - c) @ v])
            q3 = np.column_stack([(tri[mask][:, 2] - c) @ u, (tri[mask][:, 2] - c) @ v])
            ax.add_collection(PolyCollection(np.stack([q1, q2, q3], axis=1), facecolors=C_PATCH,
                                             edgecolors="#5a2400", linewidths=0.3, alpha=0.75))
        ax.plot(o2[i:j + 1, 0], o2[i:j + 1, 1], color=C_OURS, lw=3.4, solid_capstyle="round")
        ax.plot(o2[:, 0], o2[:, 1], color=C_OURS, lw=2.0, alpha=0.75)
        ax.plot(a2[lo:hi + 1, 0], a2[lo:hi + 1, 1], color=C_AUTH, lw=2.6, ls=(0, (6, 3)))
        ax.plot(a2[:, 0], a2[:, 1], color=C_AUTH, lw=1.5, ls=(0, (6, 3)), alpha=0.75)
        ax.plot(p2[:, 0], p2[:, 1], color="#5a2400", lw=0.6, alpha=0.5)
        ax.set_xlim(mid[0] - pad, mid[0] + pad)
        ax.set_ylim(mid[1] - pad, mid[1] + pad)
        ax.set_aspect("equal", adjustable="box")
        ax.tick_params(labelsize=8)
        ax.set_xlabel("u mm (face plane)", fontsize=9)
        ax.set_ylabel("v mm (face plane)", fontsize=9)
        ax.set_title(ttl, fontsize=11)
    axw.annotate("", xy=a2[hi], xytext=a2[lo], arrowprops=dict(arrowstyle="<->", color="#000000", lw=1.2))
    p = r["patch"]
    box = ("our detour: dots %d-%d (%d of %d), arc %.1f mm\n"
           "their chord: dots %d-%d (%d), polyline %.1f mm straight %.1f mm\n"
           "chord dots within 0.50 mm of the mesh: %.1f%%  (>1.0 mm: %.1f%% of its length)\n"
           "patch: %d triangles, %.1f mm2;  tilt >=45 deg %.1f%% of area,  <=20 deg %.1f%%\n"
           "patch offset from the face plane: p5 %+.2f  median %+.2f  p95 %+.2f mm;  within 1 mm %.1f%%\n"
           "face-like and cut away by the chord: %.1f mm2 (%.1f%% of the patch)"
           ) % (i, j, j - i + 1, len(ours), r["stretch"]["arc_mm"],
                lo, hi, r["chord"]["n_dots"], r["chord"]["polyline_mm"], r["chord"]["straight_mm"],
                r["dist"]["auth_chord"]["share_le_0.5"], r["dist"]["auth_chord"].get("length_share_gt_1.0mm", float("nan")),
                p.get("n_tris", 0), p.get("area_mm2", 0.0), p.get("tilt_share_ge45_area", 0.0),
                p.get("tilt_share_le20_area", 0.0),
                p.get("offset_mm", {}).get("p5", 0.0), p.get("offset_mm", {}).get("median", 0.0),
                p.get("offset_mm", {}).get("p95", 0.0), p.get("share_within_1mm_area", 0.0),
                p.get("facelike_area_mm2", 0.0), p.get("facelike_share_area", 0.0))
    axz.text(0.015, 0.985, box, transform=axz.transAxes, va="top", ha="left", fontsize=9,
             family="monospace", bbox=dict(fc="white", ec="#888888", alpha=0.93))

    hist = p.get("tilt_histogram", [])
    if hist:
        xs = np.arange(len(hist))
        axh.bar(xs, [h["area_share"] for h in hist], color="#4a7ebb", width=0.9)
        axh.axvline(9.5, color="#c02020", lw=1.4, ls="--")
        axh.text(9.6, max(h["area_share"] for h in hist) * 0.92, "45 deg", color="#c02020", fontsize=9)
        axh.set_xticks(xs[::2])
        axh.set_xticklabels([h["bin"].split("-")[0] for h in hist][::2], fontsize=8)
        axh.set_xlabel("triangle normal tilt off the interior-face normal (deg, 5 deg bins)", fontsize=9)
        axh.set_ylabel("% of the patch's area", fontsize=9)
        axh.set_title("how the enclosed patch is pitched\n(area-weighted, mesh triangles)", fontsize=11)
        axh.tick_params(labelsize=8)
        for k, h in enumerate(hist):
            if h["area_share"] > 0.5:
                axh.text(k, h["area_share"] + 0.3, "%.0f" % h["area_share"], ha="center", fontsize=7)
    else:
        axh.axis("off")
        axh.text(0.5, 0.5, "no mesh triangle inside the enclosed polygon\n(the chord spans a void)",
                 ha="center", va="center", fontsize=12, color="#b00000")

    fig.suptitle("%s %s  Bl0  --  is the authors' chord the better break edge?" % (M.POT, M.PIECE), fontsize=16, y=0.972)
    g = res["gate"]
    fig.text(0.5, 0.933,
             "VERDICT %s   |   gate 294 row: median %.3f / cov_ours %.2f (fresh %.3f / %.2f, spread %.3f mm / %.2f pp) -> %s"
             % (r["verdict"]["verdict"], M.GATE["median"], M.GATE["cov_ours"],
                np.median([q["median"] for q in g["fresh"].values()]) if g["fresh"] else float("nan"),
                np.median([q["cov_ours"] for q in g["fresh"].values()]) if g["fresh"] else float("nan"),
                g.get("spread_median_mm") or 0.0, g.get("spread_cov_ours_pp") or 0.0,
                "PASS" if g.get("gate_pass") else "FAIL/UNKNOWN"), ha="center", fontsize=12)
    fig.text(0.5, 0.012,
             "repeat %s  |  commit %s  |  our %d dots, theirs %d  |  mesh %s, %d triangles  |  face plane: %d points, rms %.3f mm  |  faces drawn %d of %d, decimation for display only"
             % (rep, (os.environ.get("SOURCE_COMMIT") or "?")[:12], len(ours), len(auth), r["mesh_obj"],
                r["mesh_tris"], r["plane"]["n_pts"], r["plane"]["rms_mm"], nf_drawn, nf_total),
             ha="center", fontsize=8.2, color="#333333")
    out = os.path.join(run, "out", "png")
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "p297_D_22_Bl0_chord.png")
    fig.savefig(path, dpi=100)
    plt.close(fig)
    print("[PNG] %s %d bytes verdict=%s patch_tris=%d" % (path, os.path.getsize(path),
                                                          r["verdict"]["verdict"], int(mask.sum())))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
