#!/usr/bin/env python3
"""Ticket 17 deliverable 3: the three eye-check renders.

Fig 1  renders/Juglet_Piece_1_handle_and_walls.png -- the juglet handle below,
       and far from, the S0 body; orthogonal panels (XY/XZ/YZ) plus one oblique
       3D panel, 20 mm scale bars, equal aspect.
Fig 2  renders/Pot_J_Piece_03_clusters_3d.png -- the 11,511-point third cluster
       that t09 dropped, shown as the mesh far from both released walls.
Fig 3  renders/Flagged_appendage_sherds_gallery.png -- 12 panels: the three
       pieces the ticket names plus the nine highest-scoring remaining flagged
       sherds (score = s1_off_author/5 + c3_frac/0.05 + (82-cov)/18, i.e. each
       term reaches 1.0 at its flag threshold).

Grey mesh, blue S0, teal S1 near, orange-red S1 far, purple uncovered mesh.
Juglet geometry is divided by JUG_ROWS = 3.0 to put it in the 1x mm frame.
Panels are read-only projections of the t09 surfaces; no geometry is written.
"""
import argparse
import csv
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from scipy.spatial import cKDTree  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import t17_common as tc  # noqa: E402

C_MESH = "#cccccc"
C_S0 = "#4c72b0"
C_NEAR = "#1b9e77"
C_FAR = "#d95f02"
C_UNCOV = "#7570b3"
C_AX09 = "#2ca02c"
C_GT = "#000000"
DPI = 190
NEAR_MM = 4.0
COVER_MM = 2.0
AUTHOR_MM = 5.0
SCALE_MM = 20.0
FORCED = ["Pot_J_Piece_01", "Pot_J_Piece_03", "Juglet_Piece_1"]
RENDERS = ["renders/Juglet_Piece_1_handle_and_walls.png",
           "renders/Pot_J_Piece_03_clusters_3d.png",
           "renders/Flagged_appendage_sherds_gallery.png"]


def read_census(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def gallery_score(r):
    au = max(0.0, float(r["s1_off_author_5mm_pct"]))
    c3 = max(0.0, float(r["c3_frac"]))
    cov = float(r["mesh_covered_2mm_pct"])
    return au / 5.0 + c3 / 0.05 + max(0.0, 82.0 - cov) / 18.0


def project(P, B):
    return P @ B.T


def limits(ax, Q, pad=0.06, square=True):
    x = Q[:, 0]
    y = Q[:, 1]
    dx = max(float(x.max() - x.min()), 1e-6)
    dy = max(float(y.max() - y.min()), 1e-6)
    lo_x, hi_x = float(x.min()), float(x.max())
    lo_y, hi_y = float(y.min()), float(y.max())
    if square:
        span = max(dx, dy) * (1.0 + 2 * pad)
        cx, cy = 0.5 * (lo_x + hi_x), 0.5 * (lo_y + hi_y)
        lo_x, hi_x = cx - span / 2, cx + span / 2
        lo_y, hi_y = cy - span / 2, cy + span / 2
    else:
        lo_x -= dx * pad
        hi_x += dx * pad
        lo_y -= dy * pad
        hi_y += dy * pad
    ax.set_xlim(lo_x, hi_x)
    ax.set_ylim(lo_y, hi_y)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)


def scale_bar(ax, label="20 mm"):
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    sx = x0 + 0.05 * (x1 - x0)
    sy = y0 + 0.05 * (y1 - y0)
    ax.plot([sx, sx + SCALE_MM], [sy, sy], color="k", lw=2.6,
            solid_capstyle="butt", zorder=20)
    ax.text(sx + SCALE_MM / 2.0, sy + 0.02 * (y1 - y0), label, ha="center",
            va="bottom", fontsize=7, zorder=20,
            bbox=dict(fc="white", ec="none", alpha=0.8, pad=0.6))


def panels(fig, groups, basis, titles, bar=True, tsize=8):
    axes = []
    for dims, title in zip([(0, 1), (0, 2), (1, 2)], titles):
        ax = fig.add_subplot(2, 2, len(axes) + 1)
        allq = []
        for g in groups:
            Q = project(g["pts"], basis)
            ax.scatter(Q[:, dims[0]], Q[:, dims[1]], s=g["s"], c=g["c"],
                       alpha=g["a"], linewidths=0, label=g.get("label"),
                       rasterized=True, zorder=g["z"])
            allq.append(Q[:, dims])
        lim = np.vstack(allq)
        limits(ax, lim)
        if bar:
            scale_bar(ax)
        ax.set_title(title, fontsize=tsize)
        axes.append(ax)
    return axes


def add_3d(fig, groups, axis_lines=(), elev=18, azim=-62):
    ax = fig.add_subplot(2, 2, 4, projection="3d")
    for g in groups:
        ax.scatter(g["pts"][:, 0], g["pts"][:, 1], g["pts"][:, 2], s=g["s3"],
                   c=g["c"], alpha=g["a"], linewidths=0, depthshade=False)
    for P, color, style, lw in axis_lines:
        ax.plot(P[:, 0], P[:, 1], P[:, 2], color=color, ls=style, lw=lw)
    ax.view_init(elev=elev, azim=azim)
    ax.set_box_aspect((1, 1, 1))
    ax.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    ax.set_title("oblique 3D", fontsize=8)
    return ax


def axis_segment(axis, P, frac=1.0):
    """Segment of a line through the point cloud, long enough to be visible."""
    d = np.asarray(axis[0:3], dtype=float)
    d = d / np.linalg.norm(d)
    rel = P - np.asarray(axis[3:6], dtype=float)[None, :]
    t = rel @ d
    lo, hi = float(t.min()) - 0.1 * frac * (t.max() - t.min()), float(t.max()) + 0.1 * frac * (t.max() - t.min())
    p0 = axis[3:6] + lo * d
    p1 = axis[3:6] + hi * d
    return np.vstack([p0, p1])


def legend(fig, extra=None):
    h = [Line2D([], [], marker="o", ls="", color=C_MESH, ms=7, label="mesh"),
         Line2D([], [], marker="o", ls="", color=C_S0, ms=7, label="S0 (body)"),
         Line2D([], [], marker="o", ls="", color=C_NEAR, ms=7, label="S1 near S0 (<=%.0f mm)" % NEAR_MM),
         Line2D([], [], marker="o", ls="", color=C_FAR, ms=7, label="S1 far / uncovered (orange)"),
         Line2D([], [], marker="o", ls="", color=C_UNCOV, ms=7, label="mesh >%.0f mm from walls" % COVER_MM)]
    if extra:
        h += extra
    fig.legend(handles=h, loc="lower center", ncol=len(h), fontsize=8, frameon=False,
               bbox_to_anchor=(0.5, 0.005))


def fig1(outdir, rows):
    stem = "Juglet_Piece_1"
    s0 = tc.read_wall(os.path.join(tc.geom_dir(stem), stem + ".S0"), with_normals=False)[0:3] / tc.JUG_ROWS
    s1 = tc.read_wall(os.path.join(tc.geom_dir(stem), stem + ".S1"), with_normals=False)[0:3] / tc.JUG_ROWS
    # the Juglet mesh is already 1x mm; only its 3x walls are divided
    mesh = tc.read_obj_vertices(tc.mesh_obj(stem))
    d = cKDTree(s0.T).query(s1.T, k=1)[0]
    near = d <= NEAR_MM
    dmesh = cKDTree(np.hstack([s0, s1]).T).query(mesh, k=1)[0]
    unc = mesh[dmesh > COVER_MM]
    gt = tc.gt_axis(stem)
    ax09 = tc.read_axis_lines(tc.axis09_path(stem))
    ax09_1x = ax09.copy()
    ax09_1x[3:6] = ax09_1x[3:6] / tc.JUG_ROWS
    wrap = tc.wrap_deg(s0.T, gt)
    gt_deg = tc.line_angle_deg(ax09_1x[0:3, 0], gt[0:3]) if ax09.shape[1] else float("nan")

    allp = np.vstack([mesh, s0.T, s1.T])
    B = np.eye(3)  # world axes: the panel labels say XY/XZ/YZ
    groups = [
        {"pts": mesh, "c": C_MESH, "s": 0.6, "s3": 0.5, "a": 0.55, "z": 1},
        {"pts": unc, "c": C_UNCOV, "s": 1.2, "s3": 0.9, "a": 0.9, "z": 2},
        {"pts": s0.T, "c": C_S0, "s": 0.7, "s3": 0.6, "a": 0.65, "z": 3},
        {"pts": s1.T[near], "c": C_NEAR, "s": 0.7, "s3": 0.6, "a": 0.55, "z": 4},
        {"pts": s1.T[~near], "c": C_FAR, "s": 1.0, "s3": 0.9, "a": 0.85, "z": 5},
    ]
    fig = plt.figure(figsize=(13.0, 12.2))
    panels(fig, groups, B, ["XY (mm)", "XZ (mm)", "YZ (mm)"])
    axis_lines = []
    if ax09.shape[1]:
        axis_lines.append((axis_segment(ax09_1x[:, 0], allp), C_AX09, "--", 1.6))
    axis_lines.append((axis_segment(gt, allp), C_GT, "-", 2.0))
    add_3d(fig, groups, axis_lines=axis_lines)
    fig.suptitle("Juglet_Piece_1: S0=%d pts, S1=%d pts, %d S1 pts >%.0f mm from S0 (handle), "
                 "S0 wrap %.1f deg, t09-vs-GT %.2f deg\norange-red = handle/far S1;  purple = mesh >%.0f mm from S0|S1;  "
                 "green dashed = t09 axis, black = GT axis;  all panels 1x mm, equal aspect, 20 mm bar"
                 % (s0.shape[1], s1.shape[1], int((~near).sum()), NEAR_MM, wrap, gt_deg, COVER_MM),
                 fontsize=10)
    legend(fig)
    p = os.path.join(outdir, RENDERS[0])
    fig.savefig(p, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    return p


def fig2(outdir):
    stem = "Pot_J_Piece_03"
    s0 = tc.read_wall(os.path.join(tc.geom_dir(stem), stem + ".S0"), with_normals=False)[0:3]
    s1 = tc.read_wall(os.path.join(tc.geom_dir(stem), stem + ".S1"), with_normals=False)[0:3]
    mesh = tc.read_obj_vertices(tc.mesh_obj(stem))
    dmesh = cKDTree(np.hstack([s0, s1]).T).query(mesh, k=1)[0]
    unc = mesh[dmesh > COVER_MM]
    B = np.eye(3)  # world axes: the panel labels say XY/XZ/YZ
    groups = [
        {"pts": mesh, "c": C_MESH, "s": 0.7, "s3": 0.6, "a": 0.5, "z": 1},
        {"pts": unc, "c": C_FAR, "s": 1.4, "s3": 1.0, "a": 0.9, "z": 2},
        {"pts": s0.T, "c": C_S0, "s": 0.9, "s3": 0.8, "a": 0.65, "z": 3},
        {"pts": s1.T, "c": C_NEAR, "s": 0.9, "s3": 0.8, "a": 0.6, "z": 4},
    ]
    fig = plt.figure(figsize=(13.0, 12.2))
    panels(fig, groups, B, ["XY (mm)", "XZ (mm)", "YZ (mm)"])
    add_3d(fig, groups)
    fig.suptitle("Pot_J_Piece_03: S0=%d, S1=%d, mesh %d verts, %d uncovered (>%.0f mm) -- the dropped "
                 "11,511-pt third cluster\norange-red = mesh far from both released walls; grey = mesh; "
                 "blue = S0; teal = S1; 1x mm, equal aspect, 20 mm bar"
                 % (s0.shape[1], s1.shape[1], mesh.shape[0], unc.shape[0], COVER_MM), fontsize=10)
    fig.legend(handles=[
        Line2D([], [], marker="o", ls="", color=C_MESH, ms=7, label="mesh"),
        Line2D([], [], marker="o", ls="", color=C_FAR, ms=7, label="mesh >%.0f mm from S0|S1" % COVER_MM),
        Line2D([], [], marker="o", ls="", color=C_S0, ms=7, label="S0 (body)"),
        Line2D([], [], marker="o", ls="", color=C_NEAR, ms=7, label="S1")],
        loc="lower center", ncol=4, fontsize=8, frameon=False, bbox_to_anchor=(0.5, 0.005))
    p = os.path.join(outdir, RENDERS[1])
    fig.savefig(p, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    return p


def gallery_choice(rows):
    by = {r["stem"]: r for r in rows}
    flagged = sorted([r for r in rows if r["flag_reason"] != "ok" and r["stem"] not in FORCED],
                     key=gallery_score, reverse=True)
    pick = FORCED + [r["stem"] for r in flagged[:9]]
    if len(pick) < 12:
        rest = [r for r in rows if r["stem"] not in pick]
        rest.sort(key=gallery_score, reverse=True)
        pick += [r["stem"] for r in rest[:12 - len(pick)]]
    return by, pick[:12]


def fig3(outdir, rows):
    by, pick = gallery_choice(rows)
    fig = plt.figure(figsize=(13.4, 10.4))
    for i, stem in enumerate(pick):
        ax = fig.add_subplot(3, 4, i + 1)
        r = by[stem]
        s0 = tc.read_wall(os.path.join(tc.geom_dir(stem), stem + ".S0"), with_normals=False)[0:3]
        s1 = tc.read_wall(os.path.join(tc.geom_dir(stem), stem + ".S1"), with_normals=False)[0:3]
        mesh = tc.read_obj_vertices(tc.mesh_obj(stem))
        if tc.is_jug(stem):
            s0 = s0 / tc.JUG_ROWS
            s1 = s1 / tc.JUG_ROWS
            d = cKDTree(s0.T).query(s1.T, k=1)[0]
            far = d > NEAR_MM
            note = "S1 far >%.0f mm from S0" % NEAR_MM
        else:
            aw = tc.read_wall(tc.author_wall(stem), with_normals=False)[0:3]
            d = cKDTree(aw.T).query(s1.T, k=1)[0]
            far = d > AUTHOR_MM
            note = "S1 far >%.0f mm from author" % AUTHOR_MM
        dmesh = cKDTree(np.hstack([s0, s1]).T).query(mesh, k=1)[0]
        unc = mesh[dmesh > COVER_MM]
        B = np.eye(3)  # world axes: the panel labels say XY/XZ/YZ
        groups = [
            {"pts": mesh, "c": C_MESH, "s": 0.5, "s3": 0.4, "a": 0.45, "z": 1},
            {"pts": unc, "c": C_UNCOV, "s": 0.7, "s3": 0.5, "a": 0.8, "z": 2},
            {"pts": s0.T, "c": C_S0, "s": 0.7, "s3": 0.6, "a": 0.65, "z": 3},
            {"pts": s1.T[~far], "c": C_NEAR, "s": 0.7, "s3": 0.6, "a": 0.55, "z": 4},
            {"pts": s1.T[far], "c": C_FAR, "s": 0.9, "s3": 0.7, "a": 0.85, "z": 5},
        ]
        Q = np.vstack([project(g["pts"], B) for g in groups])
        for g, Qg in zip(groups, [project(g["pts"], B) for g in groups]):
            ax.scatter(Qg[:, 0], Qg[:, 1], s=g["s"], c=g["c"], alpha=g["a"],
                       linewidths=0, rasterized=True, zorder=g["z"])
        limits(ax, Q)
        scale_bar(ax)
        ax.set_title("%s  (score %.2f)" % (stem, gallery_score(r)), fontsize=8)
        ax.text(0.02, 0.98,
                "%s\nS0 %d  S1 %d  far %d (%.1f%%)\nc3 %.3f  cov %.1f%%  gt0 %.2f"
                % (r["flag_reason"], int(r["s0_pts"]), int(r["s1_pts"]), int(far.sum()),
                   100.0 * far.mean() if far.size else 0.0, float(r["c3_frac"]),
                   float(r["mesh_covered_2mm_pct"]), float(r["gt_rank0_deg"])),
                transform=ax.transAxes, fontsize=6.2, va="top", ha="left", zorder=30,
                bbox=dict(fc="white", ec="none", alpha=0.75, pad=1.0))
    fig.suptitle("Flagged appendage sherds: %s + top 9 remaining by score\nblue S0, teal S1 near, "
                 "orange S1 far (%s), purple mesh >%.0f mm from S0|S1; 1x mm, equal aspect, 20 mm bar"
                 % (", ".join(FORCED), "author wall or S0", COVER_MM), fontsize=10)
    fig.legend(handles=[
        Line2D([], [], marker="o", ls="", color=C_MESH, ms=6, label="mesh"),
        Line2D([], [], marker="o", ls="", color=C_S0, ms=6, label="S0"),
        Line2D([], [], marker="o", ls="", color=C_NEAR, ms=6, label="S1 near"),
        Line2D([], [], marker="o", ls="", color=C_FAR, ms=6, label="S1 far"),
        Line2D([], [], marker="o", ls="", color=C_UNCOV, ms=6, label="uncovered mesh")],
        loc="lower center", ncol=5, fontsize=8, frameon=False, bbox_to_anchor=(0.5, 0.005))
    p = os.path.join(outdir, RENDERS[2])
    fig.savefig(p, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--census", required=True)
    a = ap.parse_args()
    rows = read_census(a.census)
    print("census rows: %d" % len(rows), flush=True)
    p1 = fig1(a.outdir, rows)
    print("wrote %s" % p1, flush=True)
    p2 = fig2(a.outdir)
    print("wrote %s" % p2, flush=True)
    p3 = fig3(a.outdir, rows)
    print("wrote %s" % p3, flush=True)
    with open(os.path.join(a.outdir, "evidence", "renders.tsv"), "w") as fh:
        for r in RENDERS:
            fh.write(r + "\n")


if __name__ == "__main__":
    main()
