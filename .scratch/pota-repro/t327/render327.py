"""Ticket 327 bar 5: before/after renders for the three mis-filed Juglet pieces.

Left column  = the t66 export as shipped (Surface_0 = OUTER wall, Breakline_0 on it).
Right column = the same piece after the wall-side swap on a copy (Surface_0 = INNER wall,
               Breakline_0 = the walk that rides the inner wall).
Row 1: 3D view about the GT vessel axis. Row 2: unrolled radial view (x = height along the
GT axis, y = distance from the axis), which is where a wall-side error is unambiguous.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

BASE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(BASE, "..", "..", ".."))
GEOM = os.path.join(WT, "artifacts", "pota327", "geom")
GTD = os.path.join(WT, "artifacts", "pota327", "gt")
OUT = os.path.join(WT, "artifacts", "pota327", "renders")
os.makedirs(OUT, exist_ok=True)

PIECES = (2, 6, 9)


def load_ply(p):
    L = open(p).read().splitlines()
    i = [n for n, l in enumerate(L) if l == "end_header"][0]
    n = [int(l.split()[2]) for l in L[:i] if l.startswith("element vertex")][0]
    rows = [l.split() for l in L[i + 1:i + 1 + n] if l.strip()]
    return np.array([[float(x) for x in r[:6]] for r in rows])


def load_pcd(p):
    L = open(p).read().splitlines()
    i = [n for n, l in enumerate(L) if l.startswith("DATA")][0]
    rows = [l.split() for l in L[i + 1:] if l.strip() and len(l.split()) >= 6]
    return np.array([[float(x) for x in r[:6]] for r in rows])


def load_ax(k):
    v = [float(x) for x in open(os.path.join(GTD, "Juglet_Piece_%d_Axis.xyz" % k)).read().split()]
    o = np.array(v[-6:-3]); d = np.array(v[-3:]); d = d / np.linalg.norm(d)
    return o, d


def cyl(P, o, d):
    w = P[:, :3] - o
    z = w @ d
    r = np.linalg.norm(w - np.outer(z, d), axis=1)
    return z, r


def sub(P, n=3500):
    if len(P) <= n:
        return P
    idx = np.random.default_rng(0).choice(len(P), n, replace=False)
    return P[np.sort(idx)]


def panel3d(ax, S0, S1, B, o, d, title):
    pts = []
    for P, col, lab, sz in ((S1, "#4a90c8", "Surface_1", 7), (S0, "#7f7f7f", "Surface_0", 7)):
        w = P[:, :3] - o
        zc = w @ d
        perp = w - np.outer(zc, d)
        ax.scatter(perp[:, 0], perp[:, 1], zc, c=col, s=sz, alpha=0.7, linewidths=0, label=lab)
        pts.append(perp)
    w = B[:, :3] - o
    zb = w @ d
    pb = w - np.outer(zb, d)
    ax.scatter(pb[:, 0], pb[:, 1], zb, c="#d62728", s=22, depthshade=False, label="Breakline_0")
    allp = np.vstack([p for p in pts] + [pb])
    lo, hi = allp.min(0), allp.max(0)
    ctr = (lo + hi) / 2.0
    half = float(np.max(hi - lo)) / 2.0
    ax.set_xlim(ctr[0] - half, ctr[0] + half)
    ax.set_ylim(ctr[1] - half, ctr[1] + half)
    ax.set_box_aspect((1, 1, 1))
    ax.set_xlabel("x (mm)", fontsize=8); ax.set_ylabel("y (mm)", fontsize=8)
    ax.set_zlabel("h along GT axis (mm)", fontsize=8)
    ax.tick_params(labelsize=7)
    ax.set_title(title, fontsize=10)
    ax.legend(loc="upper left", fontsize=7, markerscale=1.6)
    ax.view_init(elev=8, azim=-62)


def panel_radial(ax, S0, S1, B, o, d, title):
    for P, col, lab in ((S0, "#bdbdbd", "Surface_0"), (S1, "#4a90c8", "Surface_1")):
        z, r = cyl(P, o, d)
        ax.scatter(z, r, c=col, s=2, alpha=0.5, linewidths=0, label=lab)
    zb, rb = cyl(B, o, d)
    ax.scatter(zb, rb, c="#d62728", s=14, zorder=5, label="Breakline_0")
    ax.set_xlabel("height along GT axis (mm)"); ax.set_ylabel("radius from GT axis (mm)")
    ax.set_title(title, fontsize=10); ax.grid(alpha=0.3)
    ax.legend(loc="upper right", fontsize=7, markerscale=2)


made = []
for k in PIECES:
    S0 = load_ply(os.path.join(GEOM, "Juglet_Piece_%d.S0" % k))
    S1 = load_ply(os.path.join(GEOM, "Juglet_Piece_%d.S1" % k))
    B0 = load_pcd(os.path.join(GEOM, "Juglet_Piece_%d.Bl0" % k))
    B1 = load_pcd(os.path.join(GEOM, "Juglet_Piece_%d.Bl1" % k))
    o, d = load_ax(k)
    fig = plt.figure(figsize=(13.5, 9.5))
    ax1 = fig.add_subplot(2, 2, 1, projection="3d")
    panel3d(ax1, sub(S0), sub(S1), B0, o, d,
            "BEFORE (t66 as shipped): Surface_0 = OUTER wall,\nBreakline_0 rides it  (piece %d)" % k)
    ax2 = fig.add_subplot(2, 2, 2, projection="3d")
    panel3d(ax2, sub(S1), sub(S0), B1, o, d,
            "AFTER swap on a copy: Surface_0 = INNER wall,\nBreakline_0 rides it  (piece %d)" % k)
    ax3 = fig.add_subplot(2, 2, 3)
    panel_radial(ax3, S0, S1, B0, o, d, "radial view, before")
    ax4 = fig.add_subplot(2, 2, 4)
    panel_radial(ax4, S1, S0, B1, o, d, "radial view, after")
    fig.suptitle("Juglet piece %d - wall-side cause, ticket 327 bar 5" % k, fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    p = os.path.join(OUT, "juglet_piece_%d_wall_side.png" % k)
    fig.savefig(p, dpi=130)
    plt.close(fig)
    made.append(p)
print("\n".join(made))