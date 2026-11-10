#!/usr/bin/env python3
"""Ticket 328 bar 6 renders: the three claims drawn from the measured data.

fig1_bar3_pairs.png   the correspondence bar, per touching pair, before vs after (dot_med_d3, +0.7 line)
fig2_bl0_normals.png  per piece, Breakline_0 points coloured by agreement with the wall they ride (S0),
                      shipped bundle (top) vs cured (bottom)
fig3_hard_pairs.png   the two pairs that still read low (1-9, 6-7): both pieces' Bl0 points in the shared
                      GT pose, arrow = the line normal, before vs after

Usage: render328.py BEFORE_GEOM AFTER_GEOM PAIRS_TSV OUTDIR
"""
import sys, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from scipy.spatial import cKDTree

BEFORE, AFTER, PTSV, OUT = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
GT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "artifacts", "pota328", "in", "gt")
GT = os.path.abspath(GT)
os.makedirs(OUT, exist_ok=True)


def read_ply(path, cols=6):
    pts = []
    with open(path) as f:
        n = None
        for line in f:
            if line.startswith("element vertex"):
                n = int(line.split()[-1])
            if line.strip() == "end_header":
                break
        for i, line in enumerate(f):
            if i >= (n or 10 ** 9):
                break
            v = [float(x) for x in line.split()[:cols]]
            pts.append(v)
    return np.asarray(pts)


def read_pcd(path):
    rows = []
    with open(path) as f:
        n = 0
        data = False
        for line in f:
            if data:
                if line.startswith("#"):
                    continue
                v = line.split()
                if len(v) >= 6:
                    rows.append([float(x) for x in v[:6]])
            elif line.startswith("POINTS"):
                n = int(line.split()[1])
            elif line.strip() == "DATA ascii":
                data = True
    return np.asarray(rows)


def load(geom, k, kind):
    if kind == "S":
        return read_ply(os.path.join(geom, "Juglet_Piece_%d.S%d" % (k, 0))), read_ply(os.path.join(geom, "Juglet_Piece_%d.S%d" % (k, 1)))
    return read_pcd(os.path.join(geom, "Juglet_Piece_%d.Bl0" % k)), read_pcd(os.path.join(geom, "Juglet_Piece_%d.Bl1" % k))


def wall_dot(geom, k):
    """dot(line normal, wall normal at the nearest S0 point) for every Bl0 point."""
    s0, _ = load(geom, k, "S")
    bl0, _ = load(geom, k, "B")
    t = cKDTree(s0[:, :3])
    d, i = t.query(bl0[:, :3], k=1)
    dot = np.einsum("ij,ij->i", bl0[:, 3:6], s0[i, 3:6])
    return bl0, dot, d


# ---------------- fig 1: the pair table
rows = []
with open(PTSV) as f:
    hdr = f.readline().rstrip("\n").split("\t")
    for line in f:
        if line.strip():
            rows.append(dict(zip(hdr, line.rstrip("\n").split("\t"))))
pairs = [r["pair"] for r in rows]
before = [float(r["dot_med_d3_before"]) for r in rows]
after = [float(r["dot_med_d3_after"]) for r in rows]
y = np.arange(len(pairs))
fig, ax = plt.subplots(figsize=(7.5, 4.2))
ax.barh(y - 0.2, before, 0.4, color="#b03030", label="before (shipped bundle)")
ax.barh(y + 0.2, after, 0.4, color="#207040", label="after (cure)")
ax.axvline(0.7, color="k", ls="--", lw=1)
ax.text(0.68, -0.75, "+0.7 bar", fontsize=8, ha="right", va="bottom")
ax.axvline(0.0, color="k", lw=0.8)
ax.set_yticks(y)
ax.set_yticklabels(pairs)
ax.set_xlabel(r"dot_med_d3 (median $n_A\cdot n_B$ over correspondences within 3 mm)")
ax.set_title("Ticket 328 bar 3 — touching pairs at ground truth")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=2, fontsize=8, frameon=False)
ax.set_xlim(-1.05, 1.05)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig1_bar3_pairs.png"), dpi=170)
plt.close(fig)

# ---------------- fig 2: Bl0 agreement per piece, before/after
fig = plt.figure(figsize=(12, 7))
for j, geom in enumerate((BEFORE, AFTER)):
    for k in range(1, 10):
        ax = fig.add_subplot(2, 9, j * 9 + k, projection="3d")
        s0, _ = load(geom, k, "S")
        bl0, dot, _ = wall_dot(geom, k)
        ax.scatter(s0[:, 0], s0[:, 1], s0[:, 2], s=0.8, c="#c8c8c8", alpha=0.5, linewidths=0)
        sc = ax.scatter(bl0[:, 0], bl0[:, 1], bl0[:, 2], s=22, c=dot, cmap="RdYlGn", vmin=-1, vmax=1, linewidths=0.2, edgecolors="k")
        ax.set_title("P%d  %.2f" % (k, np.mean(dot > 0)), fontsize=8)
        ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])
        ax.view_init(elev=22, azim=-60)
        try:
            ax.set_box_aspect([1, 1, 1])
        except Exception:
            pass
fig.suptitle("Breakline_0 points coloured by $n_{line}\\cdot n_{wall}$ at the nearest S0 point — shipped (top) / cured (bottom); titles = fraction positive", fontsize=10)
cb = fig.colorbar(sc, ax=fig.axes, fraction=0.015, pad=0.01)
cb.set_label("agreement with the ridden wall")
plt.savefig(os.path.join(OUT, "fig2_bl0_normals.png"), dpi=150)
plt.close(fig)

# ---------------- fig 3: the two hard pairs in the shared GT pose
def T(k):
    return np.loadtxt(os.path.join(GT, "Juglet_Piece_%d_T.txt" % k))


fig = plt.figure(figsize=(12, 7))
for j, geom in enumerate((BEFORE, AFTER)):
    for col, (a, b) in enumerate(((1, 9), (6, 7))):
        ax = fig.add_subplot(2, 2, j * 2 + col + 1, projection="3d")
        blA, _ = load(geom, a, "B")
        blB, _ = load(geom, b, "B")
        MA, MB = T(a), T(b)
        pA = blA[:, :3] @ MA[:3, :3].T + MA[:3, 3]
        nA = blA[:, 3:6] @ MA[:3, :3].T
        pB = blB[:, :3] @ MB[:3, :3].T + MB[:3, 3]
        nB = blB[:, 3:6] @ MB[:3, :3].T
        # zoom on the meeting: keep only points within 8 mm of the other piece
        dAB, _ = cKDTree(pB).query(pA)
        dBA, _ = cKDTree(pA).query(pB)
        kA, kB = dAB < 8.0, dBA < 8.0
        for p, n, c, k in ((pA, nA, "#1f4e9c", kA), (pB, nB, "#b06000", kB)):
            ax.scatter(p[k, 0], p[k, 1], p[k, 2], s=34, c=c, linewidths=0)
            ax.quiver(p[k, 0], p[k, 1], p[k, 2], n[k, 0], n[k, 1], n[k, 2], length=4.0, color=c, linewidth=1.1)
        ax.set_title("%s  %d-%d  (%.1f mm of line each side)" % ("before" if j == 0 else "after", a, b, 8.0), fontsize=9)
        ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])
        ax.view_init(elev=18, azim=-70)
fig.suptitle("The two hard pairs at the seam, shared GT pose — Bl0 points and their exported normals (arrows, 4 mm), zoomed to the meeting", fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(OUT, "fig3_hard_pairs.png"), dpi=160)
plt.close(fig)
print("wrote", OUT)
