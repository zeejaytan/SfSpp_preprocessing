#!/usr/bin/env python3
"""Ticket 302 renders: old vs corrected axis on the actual clouds.

Two objects, two views each (down-axis 'top', perpendicular 'side'), three
panels per view: cloud+old axis (released/Dataset), cloud+corrected axis,
both overlaid. PNGs under out/renders/.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "sfs_axes")))

from sfs_axes.io_axes import read_axes  # noqa: E402

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"


def load_surface(path):
    a = np.loadtxt(path, usecols=(0, 1, 2), ndmin=2)
    return np.asarray(a, dtype=float)


def seg(vt, X, f=1.15):
    d = vt[0:3] / np.linalg.norm(vt[0:3])
    p = vt[3:6]
    t = (X - p[:, None]).T @ d
    lo, hi = t.min() * f, t.max() * f
    return p[:, None] + np.outer(d, np.array([lo, hi]))


def draw(ax, X, s_old, s_new, title):
    ax.scatter(X[0], X[1], X[2], s=0.5, c="0.6", lw=0)
    if s_old is not None:
        ax.plot(s_old[0], s_old[1], s_old[2], "r-", lw=2, label="old/released")
    if s_new is not None:
        ax.plot(s_new[0], s_new[1], s_new[2], "b-", lw=2, label="corrected")
    ax.set_title(title, fontsize=8)
    ax.set_box_aspect((1, 1, 1))
    try:
        ax.set_axis_off()
    except Exception:
        pass


def views(d):
    a = np.deg2rad(np.arange(0, 360, 30))
    return [("side", a), ("top", None)]


def main(outdir, axes302, axes302_jug):
    os.makedirs(os.path.join(outdir, "renders"), exist_ok=True)
    jobs = []
    for piece in (1, 2):
        stem = "Pot_A_Piece_%02d" % piece
        X = np.concatenate([
            load_surface(os.path.join(CORPUS, "Surfaces", stem + "_Surface_0.xyz")),
            load_surface(os.path.join(CORPUS, "Surfaces", stem + "_Surface_1.xyz"))]).T
        old = read_axes(os.path.join(CORPUS, "Axes", stem + "_Axis.xyz"))[:, 0]
        new = read_axes(os.path.join(axes302, stem + "_Axis.xyz"))[:, 0]
        jobs.append((stem, X, old, new))
    for k in (8, 9):
        stem = "Juglet_Piece_%d" % k
        lanes = ("/data/gpfs/projects/punim2657/SfSpp/runs/"
                 "20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom")


        def read_ply(path):
            with open(path) as fh:
                lines = fh.read().splitlines()
            nv = None
            for i, ln in enumerate(lines):
                if ln.startswith("element vertex"):
                    nv = int(ln.split()[2])
                if ln.strip() == "end_header":
                    body = lines[i + 1:i + 1 + nv]
                    break
            return np.array([[float(x) for x in r.split()[:3]] for r in body]).T


        X = np.concatenate([read_ply(os.path.join(lanes, "Juglet_Piece_%d.S0" % k)),
                            read_ply(os.path.join(lanes, "Juglet_Piece_%d.S1" % k))], axis=1)
        ds = "/data/gpfs/projects/punim2657/sfs_preprocessing/Dataset"
        old = read_axes(os.path.join(ds, "Axes", "Juglet", stem + "_Axis.xyz"))[:, 0]
        new = read_axes(os.path.join(axes302_jug, stem + "_Axis.xyz"))[:, 0]
        jobs.append((stem, X, old, new))
    for stem, X, old, new in jobs:
        Xs = X[:, ::max(1, X.shape[1] // 4000)]
        s_old, s_new = seg(old, X), seg(new, X)
        d_new = new[0:3] / np.linalg.norm(new[0:3])
        for view, el in (("top", 90), ("side", 8)):
            fig = plt.figure(figsize=(11, 3.4))
            for i, (t, so, sn) in enumerate([
                    ("old (released)", s_old, None),
                    ("corrected (302)", None, s_new),
                    ("overlay", s_old, s_new)]):
                ax = fig.add_subplot(1, 3, i + 1, projection="3d")
                draw(ax, Xs, so, sn, "%s %s" % (stem, t))
                ax.view_init(elev=el, azim=35 if i else 35)
                if view == "top":
                    # look down the corrected axis: set eye along d_new
                    ax.view_init(elev=89.9, azim=0)
                    ax.set_proj_type("ortho")
            ax.legend(fontsize=6)
            out = os.path.join(outdir, "renders", "%s_%s.png" % (stem, view))
            fig.tight_layout()
            fig.savefig(out, dpi=140)
            plt.close(fig)
            print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
