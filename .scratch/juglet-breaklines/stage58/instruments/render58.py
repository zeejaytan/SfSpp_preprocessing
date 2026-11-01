#!/usr/bin/env python3
"""Ticket 58 renderer: pose the GT meshes with the assembler's T files and with the
GT T files, and draw both, so every arm's result is looked at before it is reported.

Poses: for a piece i (0-based index used by the T files, piece = i+1), the estimate
mesh = T_result[i] applied to the ORIGINAL mesh vertices (Dataset frame) and the
reference mesh = GT[i] applied to the same vertices. Both live in the same assembled
frame, so overlaying them answers 'did this piece land where the answer key puts it'.

The same global gauge (a Kabsch on the active pieces' translation triplets) that
score58.py reported is applied to the estimate, so the picture and the printed
chamfer are the same measurement.

Usage: render58.py --arm NAME --result DIR --gt DIR --mesh DIR --score JSON --out DIR
"""
import argparse, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa

EST_C = "#d81b60"
REF_C = "#9e9e9e"
PIECE_COLORS = ["#d81b60", "#1e88e5", "#43a047", "#f4511e", "#8e24aa",
                "#00897b", "#c0ca33", "#6d4c41", "#3949ab"]


def read_obj_verts(path, cap=4000):
    pts = []
    with open(path, "r", errors="ignore") as fh:
        for line in fh:
            if line.startswith("v "):
                f = line.split()
                pts.append((float(f[1]), float(f[2]), float(f[3])))
    P = np.asarray(pts, dtype=float)
    if len(P) > cap:
        k = int(np.ceil(len(P) / cap))
        P = P[::k]
    return P


def read_T(path):
    return np.loadtxt(path)


def read_gt(gt, n, fmt="Juglet_Piece_%d_T.txt"):
    return read_T(os.path.join(gt, fmt % (n + 1)))


def pose(T, P):
    return (T[:3, :3] @ P.T).T + T[:3, 3]


def set_axes_equal(ax, pts):
    if len(pts) == 0:
        return
    c = pts.mean(axis=0)
    span = float(np.max(pts.max(axis=0) - pts.min(axis=0)))
    if span <= 0:
        span = 1.0
    h = span / 2.0
    ax.set_xlim(c[0] - h, c[0] + h)
    ax.set_ylim(c[1] - h, c[1] + h)
    ax.set_zlim(c[2] - h, c[2] + h)


def mesh_of(meshdir, n, fmt="Juglet_Piece_%d_Mesh.obj"):
    p = os.path.join(meshdir, fmt % (n + 1))
    if not os.path.exists(p):
        p = os.path.join(meshdir, fmt % (n + 1))
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True)
    ap.add_argument("--result", required=True)
    ap.add_argument("--gt", required=True)
    ap.add_argument("--mesh", required=True)
    ap.add_argument("--score", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--mesh-fmt", default="Juglet_Piece_%d_Mesh.obj")
    ap.add_argument("--gt-fmt", default="Juglet_Piece_%d_T.txt")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    with open(a.score) as fh:
        sc = json.load(fh)
    G = np.eye(4)
    g = sc.get("gauge", {})
    if g.get("pieces_used"):
        G[:3, :3] = np.asarray(g["R"], dtype=float)
        G[:3, 3] = np.asarray(g["t"], dtype=float)
    seat_bar = sc.get("seat_bar_mm", 4.596)
    seating = {int(r["piece"]): r for r in sc.get("tables", {}).get("seating", [])}

    pieces = []
    for f in sorted(os.listdir(a.result)):
        if f.startswith("T_") and f.endswith(".txt"):
            i = int(f.split("_")[1][:-2])
            T = read_T(os.path.join(a.result, f))
            pieces.append((i, T))
    if not pieces:
        print("%s: no T files, nothing to render" % a.arm)
        return

    verts = {}
    for i, _ in pieces:
        verts[i] = read_obj_verts(mesh_of(a.mesh, i, a.mesh_fmt))
    gt = {i: read_gt(a.gt, i, a.gt_fmt) for i, _ in pieces}

    # ---- Figure 1: the assembly, estimate vs reference ------------------------
    fig = plt.figure(figsize=(14.0, 6.6), dpi=110)
    axs = [fig.add_subplot(1, 2, 1, projection="3d"),
           fig.add_subplot(1, 2, 2, projection="3d")]
    all_est, all_ref = [], []
    for k, (i, T) in enumerate(pieces):
        E = pose(G @ T, verts[i])
        R = pose(gt[i], verts[i])
        all_est.append(E)
        all_ref.append(R)
        axs[0].scatter(E[:, 0], E[:, 1], E[:, 2], s=1.2,
                       color=PIECE_COLORS[k % len(PIECE_COLORS)], alpha=.55,
                       label="piece %d" % (i + 1))
        axs[1].scatter(R[:, 0], R[:, 1], R[:, 2], s=1.2,
                       color=PIECE_COLORS[k % len(PIECE_COLORS)], alpha=.55,
                       label="piece %d" % (i + 1))
    both = np.vstack(all_est + all_ref)
    for ax, ttl in zip(axs, ["assembler result (poses from T files)",
                             "GT reference (poses from answer-key T files)"]):
        set_axes_equal(ax, both)
        ax.set_title(ttl, fontsize=10)
        ax.set_xlabel("x mm"); ax.set_ylabel("y mm"); ax.set_zlabel("z mm")
        ax.tick_params(labelsize=7)
        ax.legend(fontsize=7, loc="upper right")
        for ang in (30,):
            ax.view_init(elev=18, azim=ang)
    fig.suptitle("%s: %d piece(s) posed by the saved T files, active set %s"
                 % (a.arm, len(pieces), [i + 1 for i, _ in pieces]), fontsize=11)
    f1 = os.path.join(a.out, "%s_assembly.png" % a.arm)
    fig.tight_layout()
    fig.savefig(f1)
    plt.close(fig)
    print("wrote", f1)

    # ---- Figure 2: per piece, estimate overlaid on reference -----------------
    n = len(pieces)
    ncol = min(3, n)
    nrow = int(np.ceil(n / float(ncol)))
    fig = plt.figure(figsize=(5.0 * ncol, 4.6 * nrow), dpi=110)
    for k, (i, T) in enumerate(pieces):
        ax = fig.add_subplot(nrow, ncol, k + 1, projection="3d")
        E = pose(G @ T, verts[i])
        R = pose(gt[i], verts[i])
        ax.scatter(R[:, 0], R[:, 1], R[:, 2], s=1.0, color=REF_C, alpha=.5,
                   label="reference (GT)")
        ax.scatter(E[:, 0], E[:, 1], E[:, 2], s=1.0, color=EST_C, alpha=.5,
                   label="estimate")
        set_axes_equal(ax, np.vstack([E, R]))
        row = seating.get(i + 1, {})
        ch = row.get("chamfer_mm", float("nan"))
        ax.set_title("piece %d  chamfer %.2f mm (bar %.2f)" % (i + 1, ch, seat_bar),
                     fontsize=9)
        ax.tick_params(labelsize=6)
        ax.view_init(elev=18, azim=30)
        if k == 0:
            ax.legend(fontsize=7, loc="upper right")
    fig.suptitle("%s: estimate vs reference, one panel per active piece" % a.arm,
                 fontsize=11)
    f2 = os.path.join(a.out, "%s_perpiece.png" % a.arm)
    fig.tight_layout()
    fig.savefig(f2)
    plt.close(fig)
    print("wrote", f2)


if __name__ == "__main__":
    main()
