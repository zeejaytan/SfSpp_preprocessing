#!/usr/bin/env python3
"""ticket 48 PART 1 -- the one eye picture: what every Juglet cell grew on the new corpus clouds.

  juglet_panel48.png  3x3, one panel per Juglet piece: the piece's own silhouette (grey) with
                      the surfaces the formula arm grew on it (blue = Surface_0, orange =
                      Surface_1), counts + outcome + the [GROWTH-45] theta in the title.
                      This is the panel the ticket asks to read BESIDE ticket 46's juglet
                      figure: same nine pieces, now fed the ticket-47 corpus clouds.

Drawn inside the job (matplotlib Agg is present in the TORA env), written under
$OUT/figures/ so the geometry sweep never touches it.
"""
import argparse
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mesh38      # noqa: E402
import measure34   # noqa: E402

BLUE = "#1f5fbf"
ORANGE = "#d2691e"
GREY = "#9a9a9a"


def log(m):
    sys.stdout.write("[FIG48] %s\n" % m)
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


def fig_panel(out, cells, ds, pieces, arm="V"):
    n = len(pieces)
    if n == 0:
        log("no Juglet pieces found under %s -- nothing to draw" % ds)
        return None
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
        ctsv = os.path.join(cells, "%s_arm%s" % (piece, arm), "cell.tsv")
        info = read_cell_tsv(ctsv) if os.path.exists(ctsv) else None
        outcome = info.get("status_outcome", "?") if info else "missing"
        theta = (info.get("growth45_theta", "") or "").strip() if info else ""
        nmade = 0
        counts = []
        for k, col in ((0, BLUE), (1, ORANGE)):
            sp = os.path.join(cells, "%s_arm%s" % (piece, arm), "surfaces",
                              "%s_Surface_%d.ply" % (piece, k))
            if not os.path.exists(sp):
                continue
            d = measure34.read_ply(sp)
            pts = measure34.ply_xyz(d)
            p2 = project(pts, c, W)
            ax.scatter(p2[:, 0], p2[:, 1], s=2.5, c=col, alpha=0.9, linewidths=0,
                       label="surface %d: %s pts" % (k, format(len(pts), ",")))
            counts.append(len(pts))
            nmade += 1
        ax.set_aspect("equal")
        ax.set_title("%s  %s  (%s)%s" % (
            piece.replace("Juglet_Piece_", "J"), outcome,
            " / ".join(format(x, ",") for x in counts) or "no surface",
            ("  theta=%s" % theta) if theta else ""), fontsize=10)
        ax.grid(alpha=0.15)
        if nmade:
            ax.legend(fontsize=7, loc="best")
        if i % ncol == 0:
            ax.set_ylabel("mm, PC2")
        if i >= n - ncol:
            ax.set_xlabel("mm, PC1")
        rows.append((piece, outcome, theta or "-",
                     counts[0] if len(counts) > 0 else 0,
                     counts[1] if len(counts) > 1 else 0))
    for j in range(n, len(axes)):
        axes[j].axis("off")
    fig.suptitle("Juglet: what the formula arm grew on the ticket-47 corpus clouds", fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    p = os.path.join(out, "juglet_panel48.png")
    os.makedirs(out, exist_ok=True)
    fig.savefig(p)
    plt.close(fig)
    log("panel: %s" % p)
    with open(os.path.join(out, "figures_summary.tsv"), "w") as fh:
        fh.write("piece\toutcome\ttheta_computed_deg\tsurf0_points\tsurf1_points\n")
        for r in rows:
            fh.write("%s\t%s\t%s\t%d\t%d\n" % r)
    return p


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--cells", required=True)
    ap.add_argument("--ds", required=True)
    a = ap.parse_args(argv)
    figdir = os.path.join(a.out, "figures")
    os.makedirs(figdir, exist_ok=True)
    pieces = ["Juglet_Piece_%d" % i for i in range(1, 10)]
    pieces = [p for p in pieces if os.path.exists(os.path.join(a.ds, "Mesh", "Juglet", "%s_Mesh.obj" % p))]
    p = fig_panel(figdir, a.cells, a.ds, pieces)
    log("%s of 1 figures written under %s" % (1 if p else 0, figdir))
    return 0 if p else 1


if __name__ == "__main__":
    sys.exit(main())
