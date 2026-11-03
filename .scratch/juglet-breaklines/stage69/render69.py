#!/usr/bin/env python3
"""render69.py -- draw one assembler Result directory: the seated pieces and their assembled edges.

A ticket-69 Part C arm writes, in Result/: Top_1_OBJ_<i>.obj per placed piece (the piece mesh in the
assembled frame), T_<i>to<i>.txt its pose, and Top_1_Edgeline_<k>.xyz the assembled breaklines. There
is no assembly-level renderer in the repo (t66_render.py draws ONE piece over its own mesh), so this
draws the whole result in the assembled frame: every piece in its own colour, filled triangles
painted far-to-near, plus the assembled edges as thick dark lines.

Two panels, same scale: plan view (looking down -Z) and elevation (looking along -Y). Equal aspect,
5 mm grid, axis ticks in mm, so a compact assembly reads as compact and a scattered one as scattered.

Usage: render69.py <result_dir> <out.png> [title]
"""
import os, sys, glob
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

PALETTE = ["#4c78a8", "#f58518", "#54a24b", "#e45756", "#72b7b2", "#eeca3b",
           "#b279a2", "#ff9da6", "#9d755d", "#bab0ac", "#1f77b4", "#ff7f0e"]


def read_obj(path):
    """(V, F) from a simple OBJ: v lines, f lines with 1-based indices (f may carry /slashes)."""
    V, F = [], []
    with open(path, "r", errors="replace") as fh:
        for line in fh:
            if line.startswith("v "):
                p = line.split()
                V.append([float(p[1]), float(p[2]), float(p[3])])
            elif line.startswith("f "):
                p = line.split()[1:]
                idx = []
                for tok in p:
                    idx.append(int(tok.split("/")[0]))
                for k in range(1, len(idx) - 1):
                    F.append([idx[0] - 1, idx[k] - 1, idx[k + 1] - 1])
    return np.asarray(V, float), np.asarray(F, int)


def read_xyz(path):
    A = np.loadtxt(path, ndmin=2, usecols=(0, 1, 2))
    return A.reshape(-1, 3)


def project(X, view):
    """world -> 2d: plan (x,y) or elevation (x,z)."""
    if view == "plan":
        return X[:, [0, 1]]
    return X[:, [0, 2]]


def main():
    res, out = sys.argv[1], sys.argv[2]
    title = sys.argv[3] if len(sys.argv) > 3 else os.path.basename(res)
    objs = sorted(glob.glob(os.path.join(res, "*_Top_1_OBJ_*.obj")),
                  key=lambda p: int(p.rsplit("_", 1)[1].split(".")[0]))
    if not objs:
        sys.exit("no Top_1_OBJ_*.obj under " + res)
    edges = sorted(glob.glob(os.path.join(res, "*_Top_1_Edgeline_*.xyz")))
    pieces = []
    for i, p in enumerate(objs):
        V, F = read_obj(p)
        pieces.append((i + 1, V, F))
        print("piece %d: %d verts %d tris" % (i + 1, len(V), len(F)))
    E = [read_xyz(e) for e in edges]
    allpts = np.vstack([V for _, V, _ in pieces] + (E if E else []))
    lo, hi = allpts.min(0), allpts.max(0)
    span = float(max(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]))
    print("assembled bbox mm: %.1f x %.1f x %.1f (span %.1f)" % (hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2], span))
    pad = 0.06 * span + 3.0
    fig, axes = plt.subplots(1, 2, figsize=(17, 8.6))
    for ax, view, (a, b, xl, yl) in zip(
            axes, ("plan", "elev"),
            ((0, 1, "X (mm)", "Y (mm)"), (0, 2, "X (mm)", "Z (mm)"))):
        for (n, V, F) in pieces:
            if len(F) == 0:
                P = project(V, view)
                ax.scatter(P[:, 0], P[:, 1], s=0.3, c=PALETTE[(n - 1) % len(PALETTE)])
                continue
            tri = V[F]
            P2 = project(tri.reshape(-1, 3), view).reshape(-1, 3, 2)
            depth = tri.mean(1)[:, 2 if view == "plan" else 1]
            order = np.argsort(depth)
            ax.add_collection(PolyCollection(P2[order],
                                             facecolors=PALETTE[(n - 1) % len(PALETTE)],
                                             edgecolors="none", alpha=0.55, zorder=1))
            Pv = project(V, view)
            ax.scatter(Pv[::max(1, len(Pv) // 4000), 0], Pv[::max(1, len(Pv) // 4000), 1],
                       s=0.2, c=PALETTE[(n - 1) % len(PALETTE)], zorder=2)
        for k, A in enumerate(E):
            P2 = project(A, view)
            ax.plot(P2[:, 0], P2[:, 1], "-", lw=2.2, c="#111111", zorder=5,
                    label="assembled edge %d (%d dots)" % (k + 1, len(A)) if k < 6 else None)
        ax.set_xlim(lo[a] - pad, hi[a] + pad)
        ax.set_ylim(lo[b] - pad, hi[b] + pad)
        ax.set_aspect("equal")
        ax.grid(lw=0.3, alpha=0.5)
        ax.set_xlabel(xl); ax.set_ylabel(yl)
        ax.set_title("%s view" % ("plan" if view == "plan" else "elevation"))
    handles = [plt.Line2D([], [], marker="s", ls="none", ms=9,
                          markerfacecolor=PALETTE[(n - 1) % len(PALETTE)], markeredgecolor="none",
                          label="piece %d" % n) for n, _, _ in pieces]
    handles += [plt.Line2D([], [], color="#111111", lw=2.2, label="assembled edge")]
    fig.legend(handles=handles, loc="lower center", ncol=min(12, len(handles)), fontsize=8, frameon=False)
    fig.suptitle("%s\n%d pieces placed, %d assembled edges, bbox %.1f x %.1f x %.1f mm"
                 % (title, len(pieces), len(E), hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]), fontsize=11)
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    plt.savefig(out, dpi=115)
    print("wrote", out)


if __name__ == "__main__":
    main()
