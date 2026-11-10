#!/usr/bin/env python3
"""render328b.py - ticket 328 bar 6, figure 2: the per-correspondence evidence behind bar 3.

For each of the nine touching pairs, every mutual-nearest correspondence is a dot product of the two
pieces' exported Breakline_0 normals against its separation (the harness's own correspondence rule, the
local replica reproduces the harness to 3 decimals). The shaded rectangle is the assembler's strict
inlier condition: separation < 1.5 mm AND |dot| > cos(15 deg) = 0.9659 (class/reconstruction.h:24-26,
class/feature_matching.cpp:1000). Points inside it are the strict-gate inliers.

Usage: render328b.py BEFORE_GEOM AFTER_GEOM OUTDIR
"""
import sys, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree

BEFORE, AFTER, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
HERE = os.path.dirname(os.path.abspath(__file__))
GT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "artifacts", "pota328", "in", "gt"))
os.makedirs(OUT, exist_ok=True)
PAIRS = [(1, 2), (1, 4), (1, 8), (1, 9), (2, 5), (2, 9), (3, 5), (6, 7), (7, 9)]


def load_pcd(p):
    L = open(p, errors="ignore").read().splitlines()
    i = [n for n, l in enumerate(L) if l.startswith("DATA")][0]
    rows = [l.split() for l in L[i + 1:] if l.strip() and len(l.split()) >= 6]
    return np.array([[float(x) for x in r[:6]] for r in rows])


T = {k: np.loadtxt(os.path.join(GT, "Juglet_Piece_%d_T.txt" % k)) for k in range(1, 10)}


def move(Bx, M):
    xyz = (M[:3, :3] @ Bx[:, :3].T).T + M[:3, 3]
    n = (M[:3, :3] @ Bx[:, 3:6].T).T
    return np.hstack([xyz, n])


def cor(dots_geom, y, x):
    A = load_pcd(os.path.join(dots_geom, "Juglet_Piece_%d.Bl0" % y))
    B = move(load_pcd(os.path.join(dots_geom, "Juglet_Piece_%d.Bl0" % x)), np.linalg.inv(T[y]) @ T[x])
    tA, tB = cKDTree(A[:, :3]), cKDTree(B[:, :3])
    _, ia = tA.query(B[:, :3])
    _, ib = tB.query(A[ia, :3])
    keep = ib == np.arange(len(B))
    bi = np.where(keep)[0]
    ai = ia[keep]
    d = np.linalg.norm(A[ai, :3] - B[bi, :3], axis=1)
    dots = np.sum(A[ai, 3:6] * B[bi, 3:6], axis=1)
    return d, dots


fig = plt.figure(figsize=(17, 6.0))
axes = [[fig.add_subplot(2, 9, j * 9 + i + 1) for i in range(9)] for j in range(2)]
for j, geom in enumerate((BEFORE, AFTER)):
    for i, (y, x) in enumerate(PAIRS):
        ax = axes[j][i]
        if i:
            ax.sharey(axes[j][0])
        if j:
            ax.sharex(axes[0][i])
        d, dots = cor(geom, y, x)
        ax.axons = None
        ax.add_patch(plt.Rectangle((0.0, -1.02), 1.5, 1.98, color="#dfe8f5", zorder=0))
        ax.axhline(0.0, color="k", lw=0.8)
        ax.axhline(0.9659, color="#1f4e9c", lw=0.8, ls=":")
        ax.axvline(1.5, color="#1f4e9c", lw=0.8, ls=":")
        ax.scatter(d, dots, s=18, c="#207040" if j else "#b03030", linewidths=0)
        nin = int(np.sum((d < 1.5) & (np.abs(dots) > 0.9659)))
        ax.set_title("%d-%d  n=%d  inl=%d" % (y, x, len(d), nin), fontsize=9)
        ax.set_xlim(-0.1, 3.0)
        ax.set_ylim(-1.05, 1.05)
        if i == 0:
            ax.set_ylabel(("before (shipped)" if j == 0 else "after (cure)") + "\n$n_A\\cdot n_B$", fontsize=9)
        if j == 1:
            ax.set_xlabel("separation (mm)", fontsize=9)
fig.suptitle("Bar 3, correspondences at ground truth: blue box = the assembler's strict inlier test "
             "(separation < 1.5 mm, |dot| > 0.9659); dotted lines are that box's edges", fontsize=10)
plt.tight_layout(rect=(0, 0, 1, 0.95))
plt.savefig(os.path.join(OUT, "fig2_pair_correspondences.png"), dpi=150)
plt.close(fig)
print("wrote", os.path.join(OUT, "fig2_pair_correspondences.png"))
