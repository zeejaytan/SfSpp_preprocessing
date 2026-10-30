#!/usr/bin/env python3
"""Ticket 46's two eye pictures.

A  j2_covering.png   what the pipeline reads for Juglet Piece 2 beside an even
                     covering of the same piece at the same spacing.  This is
                     the input half of the question: a vertex dump of the mesh
                     is not a covering of the surface.
B  juglet_surfaces.png  the surfaces each Juglet cell grew, on the piece's own
                     silhouette, one panel per piece, counts in the title.

Both are drawn inside the job (matplotlib Agg is present in the TORA env) and
written under $OUT/figures/ so the geometry sweep never touches them.
"""
import argparse
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mesh38      # noqa: E402
import measure34   # noqa: E402

BLUE = "#1f5fbf"
ORANGE = "#d2691e"
GREY = "#9a9a9a"


def log(m):
    sys.stdout.write("[FIG46] %s\n" % m)
    sys.stdout.flush()


def basis_2d(pts):
    c = pts.mean(axis=0)
    u, s, vt = np.linalg.svd(pts - c, full_matrices=False)
    return c, vt[:2], vt[2]


def project(pts, c, W):
    return (pts - c) @ W.T


def read_cell_tsv(path):
    d = {}
    with open(path, "r") as fh:
        for line in fh:
            line = line.rstrip("\n").rstrip("\r")
            if "\t" in line:
                k, v = line.split("\t", 1)
                d[k] = v
    return d


def fig_a(out, ds, cover, piece, max_edges=60000):
    mpath = os.path.join(ds, "Mesh", "Juglet", "%s_Mesh.obj" % piece)
    cpath = os.path.join(ds, "Point", "Juglet", "%s_Point.pcd" % piece)
    gpath = os.path.join(cover, "%s_covering.pcd" % piece)
    if not (os.path.exists(mpath) and os.path.exists(cpath) and os.path.exists(gpath)):
        log("A: inputs missing (mesh=%s cloud=%s covering=%s) -- skipped"
            % (os.path.exists(mpath), os.path.exists(cpath), os.path.exists(gpath)))
        return None
    v, fc = mesh38.read_obj(mpath)
    shipped = measure34.read_pcd(cpath)["xyz"]
    cov = measure34.read_pcd(gpath)["xyz"]
    c, W, _ = basis_2d(cov)
    sv = project(v, c, W)
    s2 = project(shipped, c, W)
    g2 = project(cov, c, W)

    edges = np.concatenate([sv[fc[:, [0, 1]]], sv[fc[:, [1, 2]]], sv[fc[:, [2, 0]]]], axis=0)
    if len(edges) > max_edges:
        step = int(np.ceil(len(edges) / float(max_edges)))
        edges = edges[::step]

    fig, ax = plt.subplots(figsize=(11, 11), dpi=150)
    ax.add_collection(LineCollection(edges, colors=GREY, linewidths=0.18, alpha=0.30))
    ax.scatter(s2[:, 0], s2[:, 1], s=16, c=BLUE, alpha=0.95, linewidths=0,
               label="shipped cloud: %s pts (%.2f per mm2)" % (format(len(shipped), ","),
                                                              len(shipped) / mesh_area(v, fc)))
    ax.scatter(g2[:, 0], g2[:, 1], s=4, c=ORANGE, alpha=0.85, linewidths=0,
               label="even covering: %s pts (%.2f per mm2)" % (format(len(cov), ","),
                                                              len(cov) / mesh_area(v, fc)))
    ax.set_aspect("equal")
    ax.set_xlabel("mm, principal direction 1")
    ax.set_ylabel("mm, principal direction 2")
    ax.set_title("Juglet Piece 2 -- the input the growth reads, and an even covering of the same piece\n"
                 "mesh %.0f mm2;  covering / shipped = %.1fx"
                 % (mesh_area(v, fc), len(cov) / float(len(shipped))), fontsize=11)
    ax.legend(loc="upper right", fontsize=9, framealpha=0.9)
    ax.grid(alpha=0.15)
    p = os.path.join(out, "j2_covering.png")
    os.makedirs(out, exist_ok=True)
    fig.tight_layout()
    fig.savefig(p)
    plt.close(fig)
    log("A: %s (shipped %d, covering %d, mesh %d v / %d f)"
        % (p, len(shipped), len(cov), len(v), len(fc)))
    return p


def mesh_area(v, fc):
    tri = v[fc]
    cr = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    return float(0.5 * np.sum(np.linalg.norm(cr, axis=1)))


def fig_b(out, cells, ds, pieces, which_arm=("E", "A")):
    n = len(pieces)
    ncol = 3
    nrow = int(np.ceil(n / float(ncol)))
    fig, axes = plt.subplots(nrow, ncol, figsize=(15, 5.0 * nrow), dpi=130)
    axes = np.atleast_1d(axes).ravel()
    rows = []
    for i, piece in enumerate(pieces):
        ax = axes[i]
        mpath = os.path.join(ds, "Mesh", "Juglet", "%s_Mesh.obj" % piece)
        v, fc = mesh38.read_obj(mpath)
        c, W, _ = basis_2d(v)
        sv = project(v, c, W)
        ax.scatter(sv[:, 0], sv[:, 1], s=0.7, c=GREY, alpha=0.35, linewidths=0, label="mesh")
        info = None
        for arm in which_arm:
            cdir = os.path.join(cells, "%s_arm%s" % (piece, arm))
            ctsv = os.path.join(cdir, "cell.tsv")
            if not os.path.exists(ctsv):
                continue
            info = read_cell_tsv(ctsv)
            break
        outcome = info.get("status_outcome", "?") if info else "missing"
        nmade = 0
        counts = []
        for k, col in ((0, BLUE), (1, ORANGE)):
            sp = None
            for arm in which_arm:
                p = os.path.join(cells, "%s_arm%s" % (piece, arm), "surfaces",
                                 "%s_Surface_%d.ply" % (piece, k))
                if os.path.exists(p):
                    sp = p
                    break
            if sp is None:
                continue
            d = measure34.read_ply(sp)
            pts = measure34.ply_xyz(d)
            p2 = project(pts, c, W)
            ax.scatter(p2[:, 0], p2[:, 1], s=2.5, c=col, alpha=0.9, linewidths=0,
                       label="surface %d: %s pts" % (k, format(len(pts), ",")))
            counts.append(len(pts))
            nmade += 1
        ax.set_aspect("equal")
        ax.set_title("%s  %s  (%s)" % (piece.replace("Juglet_Piece_", "J"), outcome,
                                       " / ".join(format(x, ",") for x in counts) or "no surface"),
                     fontsize=10)
        ax.grid(alpha=0.15)
        if nmade:
            ax.legend(fontsize=7, loc="best")
        if i % ncol == 0:
            ax.set_ylabel("mm, PC2")
        if i >= n - ncol:
            ax.set_xlabel("mm, PC1")
        rows.append((piece, outcome, counts[0] if len(counts) > 0 else 0,
                     counts[1] if len(counts) > 1 else 0))
    for j in range(n, len(axes)):
        axes[j].axis("off")
    fig.suptitle("Juglet: what each cell grew, on the piece's own silhouette", fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    p = os.path.join(out, "juglet_surfaces.png")
    os.makedirs(out, exist_ok=True)
    fig.savefig(p)
    plt.close(fig)
    log("B: %s" % p)
    with open(os.path.join(out, "figures_summary.tsv"), "w") as fh:
        fh.write("piece\toutcome\tsurf0_points\tsurf1_points\n")
        for r in rows:
            fh.write("%s\t%s\t%d\t%d\n" % r)
    return p


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--cells", required=True)
    ap.add_argument("--cover", required=True)
    ap.add_argument("--ds", required=True)
    ap.add_argument("--j2", default="Juglet_Piece_2")
    a = ap.parse_args(argv)
    figdir = os.path.join(a.out, "figures")
    os.makedirs(figdir, exist_ok=True)
    ok = 0
    if fig_a(figdir, a.ds, a.cover, a.j2):
        ok += 1
    pieces = ["Juglet_Piece_%d" % i for i in range(1, 10)]
    pieces = [p for p in pieces if os.path.exists(os.path.join(a.ds, "Mesh", "Juglet", "%s_Mesh.obj" % p))]
    if fig_b(figdir, a.cells, a.ds, pieces):
        ok += 1
    log("%d of 2 figures written under %s" % (ok, figdir))
    return 0 if ok == 2 else 1


if __name__ == "__main__":
    sys.exit(main())
