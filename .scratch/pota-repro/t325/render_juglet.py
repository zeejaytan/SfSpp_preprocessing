
"""Ticket 325 bar 8: the Juglet at its true scale (33 mm across, 60 mm tall).

Pieces are stored in per-piece mesh frames; the GT matrices T (X_world = R*X + t,
Dataset/Juglet_GT/README-axes.md) put them into the assembled vessel. Verified: the nine
GT axis files, carried through their own T, collapse onto one world line (0.002 deg,
0.000 mm), so the axis files are the vessel axis expressed per piece.

A  the nine pieces carried through T = the juglet as it was before it broke
B  the eight pieces the assembler placed with the TRUE axes (job 34659057 arm GT_r1)
C  A viewed down the vessel axis
D  piece 7 (the one that reaches the axis, r_min 0.14 mm) with GT axis and found axis
"""
import glob
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ART = r"C:/PR/worktrees/sfs/325/artifacts/pota325"
OUT = os.path.join(ART, "renders")
os.makedirs(OUT, exist_ok=True)
COLS = plt.get_cmap("tab10").colors


def read_ply(path, want=4000):
    with open(path, errors="replace") as fh:
        n = None
        for line in fh:
            s = line.split()
            if len(s) >= 3 and s[0] == "element" and s[1] == "vertex":
                n = int(s[2])
            if line.strip() == "end_header":
                break
        rows = [fh.readline().split() for _ in range(n)]
    P = np.array([[float(v) for v in r[:3]] for r in rows])
    return P[:: max(1, len(P) // want)] if want and len(P) > want else P


def read_obj_vertices(path):
    V = []
    for line in open(path, errors="replace"):
        if line.startswith("v "):
            p = line.split()
            V.append((float(p[1]), float(p[2]), float(p[3])))
    return np.array(V)


def T(i):
    M = np.loadtxt(os.path.join(ART, "gtT", "Juglet_Piece_%d_T.txt" % i))
    return M[:3, :3], M[:3, 3]


def main():
    raw = {i: np.vstack([read_ply(os.path.join(ART, "juggeom", "Juglet_Piece_%d.S0" % i)),
                         read_ply(os.path.join(ART, "juggeom", "Juglet_Piece_%d.S1" % i))])
           for i in range(1, 10)}
    pieces = {}
    for i, P in raw.items():
        R, t = T(i)
        pieces[i] = P @ R.T + t
    allp = np.vstack(list(pieces.values()))
    c = allp.mean(axis=0)
    lo, hi = allp.min(axis=0), allp.max(axis=0)
    print("assembled bbox mm:", np.round(hi - lo, 2), "centre", np.round(c, 2))
    R = float(np.max(hi - lo)) * 0.55

    placed = {}
    for f in sorted(glob.glob(os.path.join(ART, "outgt", "*_OBJ_*.obj"))):
        V = read_obj_vertices(f)
        k = int(f.rsplit("_OBJ_", 1)[1].split(".")[0])
        placed[k] = V

    def setup(ax, title, elev, azim):
        ax.set_title(title, fontsize=11)
        ax.set_xlim(c[0] - R, c[0] + R)
        ax.set_ylim(c[1] - R, c[1] + R)
        ax.set_zlim(c[2] - R, c[2] + R)
        ax.set_box_aspect((1, 1, 1))
        ax.view_init(elev=elev, azim=azim)
        ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])
        ax.grid(False)

    fig = plt.figure(figsize=(13, 12), dpi=170)

    ax = fig.add_subplot(2, 2, 1, projection="3d")
    for i, P in sorted(pieces.items()):
        ax.scatter(P[:, 0], P[:, 1], P[:, 2], s=0.6, c=[COLS[i - 1]], linewidths=0, label="piece %d" % i)
    setup(ax, "A  ground truth: the nine pieces at their true pose (41 x 37 x 65 mm)", 12, -60)
    ax.legend(markerscale=12, fontsize=7, loc="upper left")

    ax = fig.add_subplot(2, 2, 2, projection="3d")
    for k, V in sorted(placed.items()):
        ax.scatter(V[:, 0], V[:, 1], V[:, 2], s=0.6, c=[COLS[(k * 3) % 10]], linewidths=0)
    ap = np.vstack(list(placed.values()))
    cb = (ap.min(axis=0) + ap.max(axis=0)) / 2.0
    Rb = float(np.max(ap.max(axis=0) - ap.min(axis=0))) * 0.55
    ax.set_xlim(cb[0] - Rb, cb[0] + Rb); ax.set_ylim(cb[1] - Rb, cb[1] + Rb); ax.set_zlim(cb[2] - Rb, cb[2] + Rb)
    ax.set_box_aspect((1, 1, 1)); ax.view_init(elev=12, azim=-60)
    ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([]); ax.grid(False)
    print("B bbox mm", np.round(ap.max(axis=0) - ap.min(axis=0), 2), "centre", np.round(cb, 1))
    ax.set_title("B  assembler given the TRUE axes: 8 pieces placed, 2/9 sherds, 0/18 edges", fontsize=11)

    ax = fig.add_subplot(2, 2, 3, projection="3d")
    for i, P in sorted(pieces.items()):
        ax.scatter(P[:, 0], P[:, 1], P[:, 2], s=0.6, c=[COLS[i - 1]], linewidths=0)
    setup(ax, "C  ground truth down the vessel axis: a ring of break edges", 78, -90)

    ax = fig.add_subplot(2, 2, 4, projection="3d")
    P = raw[7]
    ax.scatter(P[:, 0], P[:, 1], P[:, 2], s=0.6, c="0.45", linewidths=0)
    gt = np.loadtxt(os.path.join(ART, "axes", "gt", "Juglet_Piece_7_Axis.xyz"), ndmin=2)[0]
    fd = np.loadtxt(os.path.join(ART, "axes", "a325", "Juglet_Piece_7_Axis.xyz"), ndmin=2)[0]
    for row, col, lbl in ((gt, "#1a7f37", "true axis"), (fd, "#c62828", "finder's axis (48 deg off)")):
        p, d = row[:3], row[3:6]
        d = d / np.linalg.norm(d)
        q = P.mean(axis=0)
        q = q + ((p - q) - ((p - q) @ d) * d)   # closest point on the line to the piece
        seg = np.array([q + d * -30, q + d * 30])
        ax.plot(seg[:, 0], seg[:, 1], seg[:, 2], color=col, lw=2.0, label=lbl)
    c7 = P.mean(axis=0)
    R7 = 26.0
    ax.set_xlim(c7[0] - R7, c7[0] + R7); ax.set_ylim(c7[1] - R7, c7[1] + R7); ax.set_zlim(c7[2] - R7, c7[2] + R7)
    ax.set_box_aspect((1, 1, 1)); ax.view_init(elev=18, azim=-60)
    ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([]); ax.grid(False)
    ax.set_title("D  piece 7 (the only piece that reaches the axis)", fontsize=11)
    ax.legend(fontsize=8, loc="upper left")

    fig.suptitle("Ticket 325 - Juglet: correct axes still seat nothing; the gap is the assembler's scale",
                 fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    p = os.path.join(OUT, "juglet-axes-and-assembly.png")
    fig.savefig(p)
    print("wrote", p)


if __name__ == "__main__":
    main()
