#!/usr/bin/env python3
"""ticket 24: the pictures the conservator reads -- cloud coloured by normal-angle error, and the
written surfaces over that same cloud, one row per arm, one figure per piece.

Left column: every cloud point coloured by the angle between the estimated normal at that point
and the MESH normal at the nearest surface point (green 0 deg -> red 45 deg, clipped). That is the
only honest view of whether the normals became coherent rather than merely different.
Right column: the same cloud in grey with Surface_0 red and Surface_1 blue drawn over it.

Every panel carries a drawn 5 mm bar; the measured mm/px of every panel is printed and written to
the output directory, because a picture at an unstated scale is not evidence.

usage: render24.py <cells_root> <out_dir> <combining tags> <piece,piece,...>   e.g.
       render24.py out/cells out/renders A,A_old,A2,B,C,D,dE Juglet/Juglet_Piece_1,Juglet/Juglet_Piece_4
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coverage23 import cloud_path, read_pcd_xyz  # noqa: E402
from measure_arm23 import load_ply  # noqa: E402

VMAX = 45.0
MAXPLOT = 25000


def project(pts, centre, basis):
    d = pts - centre
    return d.dot(basis[:, 0]), d.dot(basis[:, 1])


def load_angles(path, call):
    if not os.path.exists(path):
        return None
    import csv
    out = {}
    with open(path) as fh:
        rd = csv.DictReader(fh, delimiter="\t")
        for r in rd:
            if int(r["call"]) != call:
                continue
            out.setdefault("x", []).append(float(r["x"]))
            out.setdefault("y", []).append(float(r["y"]))
            out.setdefault("z", []).append(float(r["z"]))
            out.setdefault("ang", []).append(float(r["ang_deg"]))
    if not out:
        return None
    return (np.column_stack([out["x"], out["y"], out["z"]]), np.array(out["ang"]))


def last_call(path):
    """the call id of the table's last row: the call whose normals the segmentation actually used."""
    call = None
    with open(path) as fh:
        for line in fh:
            if line.startswith("tag\t"):
                continue
            call = int(line.split("\t")[3])
    return call


def scale_bar(ax, lim, dpi, inches):
    dx = lim[1] - lim[0]
    x0 = lim[0] + 0.06 * dx
    y0 = lim[2] + 0.07 * (lim[3] - lim[2])
    ax.plot([x0, x0 + 5.0], [y0, y0], color="k", lw=2.0, solid_capstyle="butt")
    ax.annotate("5 mm", (x0 + 2.5, y0), textcoords="offset points", xytext=(0, 5),
                ha="center", fontsize=7)
    px = inches * dpi
    return (lim[1] - lim[0]) / px


def main():
    root, outdir, tags_csv, pieces_csv = sys.argv[1:5]
    tags = tags_csv.split(",")
    pieces = [p.split("/") for p in pieces_csv.split(",")]
    os.makedirs(outdir, exist_ok=True)
    dpi = 100
    print("[RENDER] dpi=%d vmax=%.0fdeg colours: green=0 red=%.0f" % (dpi, VMAX, VMAX))
    for pot, piece in pieces:
        try:
            draw_piece(pot, piece, root, outdir, tags, dpi)
        except Exception as exc:  # one bad panel must not cost the other four
            print("[RENDER] FAILED %s/%s %s: %s" % (pot, piece, type(exc).__name__, exc))


def draw_piece(pot, piece, root, outdir, tags, dpi):
    for _once in (0,):
        cpath = cloud_path(pot, piece)
        cloud, _nall, _stride = read_pcd_xyz(cpath)  # (xyz strided down to MAXPTS, n, stride)
        centre = cloud.mean(axis=0)
        u, s, vt = np.linalg.svd(cloud - centre, full_matrices=False)
        basis = vt.T
        cx, cy = project(cloud, centre, basis)
        lim = [cx.min(), cx.max(), cy.min(), cy.max()]
        padx = 0.05 * (lim[1] - lim[0])
        pady = 0.05 * (lim[3] - lim[2])
        lim = [lim[0] - padx, lim[1] + padx, lim[2] - pady, lim[3] + pady]
        idx = np.arange(len(cloud))
        if len(idx) > MAXPLOT:
            idx = np.random.default_rng(24).choice(len(idx), MAXPLOT, replace=False)
        fig, axes = plt.subplots(len(tags), 2, figsize=(7.0, 3.4 * len(tags)), squeeze=False)
        for r, tag in enumerate(tags):
            cell = os.path.join(root, tag, pot, piece)
            axL, axR = axes[r][0], axes[r][1]
            apath = os.path.join(cell, "angle_points.tsv")
            sc = None
            # probing with load_angles(path, None) can never match a row, so the first version of this
            # panel drew nothing at all; probe the file and read its last call instead.
            ang = load_angles(apath, last_call(apath)) if os.path.exists(apath) else None
            if ang is not None:
                px, py = project(ang[0], centre, basis)
                sc = axL.scatter(px, py, c=np.clip(ang[1], 0, VMAX), cmap="RdYlGn_r",
                                 vmin=0, vmax=VMAX, s=2.0, linewidths=0)
                axL.set_title("%s  normal vs mesh  med=%.1f deg" % (tag, float(np.median(ang[1]))),
                              fontsize=7)
            else:
                axL.set_title("%s  no per-point table" % tag, fontsize=7)
            axL.set_xlim(lim[0], lim[1]); axL.set_ylim(lim[2], lim[3])
            axR.scatter(cx[idx], cy[idx], c="0.6", s=1.0, linewidths=0, label="cloud")
            n0 = n1 = 0
            for k, col, lab in ((0, "tab:red", "S0"), (1, "tab:blue", "S1")):
                f = os.path.join(cell, "surfaces", "%s_Surface_%d.ply" % (piece, k))
                if not os.path.exists(f):
                    continue
                p, _ = load_ply(f)
                if len(p) == 0:
                    continue
                qx, qy = project(p, centre, basis)
                axR.scatter(qx, qy, c=col, s=3.0, linewidths=0, label=lab)
                if k == 0:
                    n0 = len(p)
                else:
                    n1 = len(p)
            axR.set_xlim(lim[0], lim[1]); axR.set_ylim(lim[2], lim[3])
            axR.set_title("%s  S0=%d S1=%d" % (tag, n0, n1), fontsize=7)
            for ax in (axL, axR):
                ax.set_aspect("equal", "box")
                ax.tick_params(labelsize=5)
            mmpx = scale_bar(axL, lim, dpi, 3.5)
            print("[RENDER] %s %s/%s row=%s mm_per_px=%.4f" % (pot, pot, piece, tag, mmpx))
        if sc is not None:
            cb = fig.colorbar(sc, ax=axes[:, 0].tolist(), fraction=0.02, pad=0.01)
            cb.set_label("normal vs mesh normal (deg)", fontsize=7)
            cb.ax.tick_params(labelsize=5)
        fig.suptitle("%s / %s  (%0.3f mm/px, drawn 5 mm bar)" % (pot, piece, mmpx), fontsize=8)
        out = os.path.join(outdir, "render24_%s_%s.png" % (pot, piece))
        fig.savefig(out, dpi=dpi)
        plt.close(fig)
        print("[RENDER] wrote %s" % out, flush=True)


if __name__ == "__main__":
    main()
