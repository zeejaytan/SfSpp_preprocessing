#!/usr/bin/env python3
"""Ticket 59 Task 4 renders.

Per Juglet piece: before (outU = gate-closed patched) vs after (outG = SFS_BREAK_STOP=1)
side by side: mesh light gray, stage-0 fracture-labelled faces orange, S0 surface claim
points blue, Bl0 breakline points red. J1 additionally gets a zoom on the blind stretch
(window around the Bl0 centroid). --skip-after renders the before panel only (gate fail).
PNGs land in the run dir; they are measurement aids, not verdicts.
"""
import argparse
import os

import numpy as np


def read_ply_vertices(path):
    """Header-aware ASCII PLY reader: returns xyz of the *vertex* element only
    (PCL appends a bogus trailing camera element -- one extra row)."""
    nvert = None
    props = []
    with open(path, "r", errors="replace") as f:
        line = f.readline()
        while line:
            t = line.split()
            if t and t[0] == "element":
                if t[1] == "vertex":
                    nvert = int(t[2])
                else:
                    nvert = nvert  # camera etc: stop collecting
            elif t and t[0] == "property" and nvert is not None and not props:
                props.append(t[2])
            elif t and t[0] == "end_header":
                break
            line = f.readline()
        rows = []
        for _ in range(nvert):
            rows.append(f.readline().split())
    a = np.array(rows, dtype=np.float64)
    return a[:, :3]


def read_pcd_xyz(path):
    n = None
    data_ascii = False
    fields = []
    with open(path, "r", errors="replace") as f:
        for line in f:
            t = line.split()
            if not t:
                continue
            if t[0] == "POINTS":
                n = int(t[1])
            elif t[0] == "FIELDS":
                fields = t[1:]
            elif t[0] == "DATA":
                data_ascii = t[1] == "ascii"
                break
        if not data_ascii:
            raise ValueError("binary PCD not handled: " + path)
        rows = []
        for line in f:
            t = line.split()
            if t:
                rows.append(t)
    a = np.array(rows[:n], dtype=np.float64)
    ix = [fields.index(k) for k in ("x", "y", "z")]
    return a[:, ix]


def load_obj(path):
    vs = []
    fs = []
    with open(path, "r", errors="replace") as f:
        for line in f:
            if line.startswith("v "):
                vs.append([float(x) for x in line.split()[1:4]])
            elif line.startswith("f "):
                idx = [int(p.split("/")[0]) - 1 for p in line.split()[1:]]
                if len(idx) == 3:
                    fs.append(idx)
    return np.array(vs), np.array(fs, dtype=np.int64)


def lambert(v, f, light=np.array([0.4, 0.3, 0.86])):
    tri = v[f]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    ln = np.linalg.norm(n, axis=1, keepdims=True)
    ln[ln == 0] = 1.0
    n = n / ln
    d = np.clip(n @ (light / np.linalg.norm(light)), 0.15, 1.0)
    base = np.array([0.82, 0.82, 0.84])
    return np.clip(d[:, None] * base[None, :], 0, 1)


def panel(ax, V, F, facecol, fracture_mask, s0, bl0, title, lims=None):
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    tri = V[F]
    pc = Poly3DCollection(tri, linewidths=0.0, antialiased=False)
    pc.set_facecolor(np.hstack([facecol, np.full((len(facecol), 1), 0.35)]))
    ax.add_collection3d(pc)
    if fracture_mask is not None and fracture_mask.any():
        pcf = Poly3DCollection(tri[fracture_mask], linewidths=0.0, antialiased=False)
        pcf.set_facecolor(np.hstack([np.tile([1.0, 0.45, 0.05], (fracture_mask.sum(), 1)),
                                     np.full((fracture_mask.sum(), 1), 0.9)]))
        ax.add_collection3d(pcf)
    if s0 is not None and len(s0):
        ax.scatter(s0[:, 0], s0[:, 1], s0[:, 2], s=0.6, c=[0.1, 0.25, 0.95], depthshade=False)
    if bl0 is not None and len(bl0):
        ax.scatter(bl0[:, 0], bl0[:, 1], bl0[:, 2], s=22, c=[0.9, 0.05, 0.05], depthshade=False)
    ax.set_title(title, fontsize=8)
    ax.set_axis_off()
    ax.view_init(elev=22, azim=135)
    if lims is not None:
        for setter, lo, hi in ((ax.set_xlim, lims[0], lims[1]),
                               (ax.set_ylim, lims[2], lims[3]),
                               (ax.set_zlim, lims[4], lims[5])):
            setter(lo, hi)
    else:
        allp = V
        if s0 is not None and len(s0):
            allp = np.vstack([allp, s0])
        lo, hi = allp.min(0) - 1.0, allp.max(0) + 1.0
        c = (lo + hi) / 2
        r = (hi - lo).max() / 2 + 1.0
        for setter, cc in ((ax.set_xlim, c[0]), (ax.set_ylim, c[1]), (ax.set_zlim, c[2])):
            setter(cc - r, cc + r)


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ap = argparse.ArgumentParser()
    ap.add_argument("--mesh-dir", required=True)
    ap.add_argument("--labels", required=True, help="stage0 out/labels dir with <P>.npz")
    ap.add_argument("--outU", required=True, help="geom dir of gate-closed arm")
    ap.add_argument("--outG", default=None, help="geom dir of armed arm (omit/--skip-after for before-only)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--skip-after", action="store_true")
    ap.add_argument("--zoom-piece", default="Juglet_Piece_1")
    ap.add_argument("--zoom-half", type=float, default=14.0)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    have_after = bool(args.outG) and not args.skip_after

    pieces = [f"Juglet_Piece_{k}" for k in range(1, 10)]
    for p in pieces:
        V, F = load_obj(os.path.join(args.mesh_dir, p + "_Mesh.obj"))
        npz = np.load(os.path.join(args.labels, p + ".npz"))
        labels = npz["labels"]  # 0 wall 1 roll 2 fracture 3 anomaly (primary params)
        fm = labels == 2
        fc = lambert(V, F)
        s0u = read_ply_vertices(os.path.join(args.outU, p + ".S0"))
        bl0u = read_pcd_xyz(os.path.join(args.outU, p + ".Bl0"))
        s0g = read_ply_vertices(os.path.join(args.outG, p + ".S0")) if have_after else None
        bl0g = read_pcd_xyz(os.path.join(args.outG, p + ".Bl0")) if have_after else None
        ncols = 2 if have_after else 1
        fig = plt.figure(figsize=(4.2 * ncols, 4.6))
        panel(fig.add_subplot(1, ncols, 1, projection="3d"), V, F, fc, fm, s0u, bl0u,
              p + " before (gate closed, patched build)")
        if have_after:
            panel(fig.add_subplot(1, ncols, 2, projection="3d"), V, F, fc, fm, s0g, bl0g,
                  p + " after (SFS_BREAK_STOP=1)")
        fig.suptitle("gray=surface orange=stage-0 fracture label blue=S0 claim red=Bl0", fontsize=7)
        fig.tight_layout()
        fig.savefig(os.path.join(args.out, p + "_before_after.png"), dpi=110)
        plt.close(fig)
        print("rendered", p, "fracture_faces", int(fm.sum()), "nS0", len(s0u),
              "nS0after", -1 if s0g is None else len(s0g))
        if p == args.zoom_piece:
            for tag, s0, bl0 in ([("before", s0u, bl0u)] + ([("after", s0g, bl0g)] if have_after else [])):
                c = bl0.mean(0)
                lims = [c[0] - args.zoom_half, c[0] + args.zoom_half,
                        c[1] - args.zoom_half, c[1] + args.zoom_half,
                        c[2] - args.zoom_half, c[2] + args.zoom_half]
                fig = plt.figure(figsize=(4.6, 4.6))
                panel(fig.add_subplot(1, 1, 1, projection="3d"), V, F, fc, fm, s0, bl0,
                      p + " blind-stretch zoom (" + tag + ") around Bl0 centroid", lims=lims)
                fig.tight_layout()
                fig.savefig(os.path.join(args.out, p + "_zoom_" + tag + ".png"), dpi=110)
                plt.close(fig)
    print("done ->", args.out)


if __name__ == "__main__":
    main()
