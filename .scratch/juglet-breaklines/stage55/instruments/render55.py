#!/usr/bin/env python3
"""ticket 55 -- one PNG per Juglet piece: the edgelines ON the mesh, for the eye.

The conservator asked for these pictures by name (2026-11-01): what the SHIPPED edge stage
does at the recommended dial SFS_WORNESS=0.7, shown as it IS.  Mesh vertices as a light-grey
3D scatter; Breakline_0 dots in one bright colour (Bl0 is the lane the SfS assembly consumes
-- Breakline_1 appears nowhere in the assembler), Breakline_1 in another; TWO panels with
different azimuth/elevation so the traced rim is visible edge-on in at least one; title
carrying piece name, capped theta and Bl0/Bl1 point counts; equal-aspect axes labelled in
mm (the meshes are in mm).  The two views are FIXED (plan down the axis + a low side view),
not chosen per piece -- a picture whose view hides the rim fails the ticket even if every
number is green.
"""
import argparse
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

MESH_C = "#c7c7c7"
BL0_C = "#ff1f1f"   # bright red
BL1_C = "#00b3ff"   # bright cyan


def read_pcd(p):
    """ascii or binary-framed PCD -> (n,3) float array of xyz (the a289 reader)"""
    with open(p, "r", errors="replace") as f:
        txt = f.read().splitlines()
    k = None
    for i, l in enumerate(txt):
        if l.strip().upper().startswith("DATA"):
            k = i + 1
            break
    if k is None:
        raise SystemExit("no DATA header in " + p)
    rows = []
    for l in txt[k:]:
        s = l.split()
        if len(s) >= 3:
            try:
                rows.append((float(s[0]), float(s[1]), float(s[2])))
            except ValueError:
                pass
    return np.array(rows, dtype=float).reshape(-1, 3)


def read_obj_verts(p):
    rows = []
    with open(p, "r", errors="replace") as f:
        for l in f:
            if not l.startswith("v "):
                continue
            s = l.split()
            if len(s) >= 4:
                try:
                    rows.append((float(s[1]), float(s[2]), float(s[3])))
                except ValueError:
                    pass
    return np.array(rows, dtype=float).reshape(-1, 3)


def eq_axes(ax, pts):
    """equal-aspect cube around pts -- mm in, mm labelled, no per-axis stretching"""
    lo = pts.min(0)
    hi = pts.max(0)
    span = float((hi - lo).max())
    mid = (lo + hi) / 2.0
    ax.set_xlim(mid[0] - span / 2, mid[0] + span / 2)
    ax.set_ylim(mid[1] - span / 2, mid[1] + span / 2)
    ax.set_zlim(mid[2] - span / 2, mid[2] + span / 2)
    ax.set_box_aspect((1, 1, 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--piece", required=True)
    ap.add_argument("--mesh", required=True)
    ap.add_argument("--bl0", required=True)
    ap.add_argument("--bl1", required=True)
    ap.add_argument("--theta", default="na")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    V = read_obj_verts(a.mesh)
    B0 = read_pcd(a.bl0) if os.path.exists(a.bl0) else np.zeros((0, 3))
    B1 = read_pcd(a.bl1) if os.path.exists(a.bl1) else np.zeros((0, 3))
    print("[R55] %s mesh=%d verts bl0=%d bl1=%d theta=%s"
          % (a.piece, len(V), len(B0), len(B1), a.theta), flush=True)

    views = [(90, -60, "plan: looking down the piece axis"),
             (12, 115, "side: rim traced edge-on")]
    fig = plt.figure(figsize=(13.5, 6.4))
    allpts = np.vstack([V, B0, B1])
    for k, (elev, azim, lbl) in enumerate(views):
        ax = fig.add_subplot(1, 2, k + 1, projection="3d")
        ax.scatter(V[:, 0], V[:, 1], V[:, 2], s=0.8, c=MESH_C, alpha=0.35, lw=0)
        if len(B0):
            ax.scatter(B0[:, 0], B0[:, 1], B0[:, 2], s=9, c=BL0_C, lw=0)
        if len(B1):
            ax.scatter(B1[:, 0], B1[:, 1], B1[:, 2], s=9, c=BL1_C, lw=0)
        ax.view_init(elev=elev, azim=azim)
        eq_axes(ax, allpts)
        ax.set_xlabel("x (mm)")
        ax.set_ylabel("y (mm)")
        ax.set_zlabel("z (mm)")
        ax.set_title("%s  (elev=%d azim=%d)  %s" % (a.piece, elev, azim, lbl), fontsize=10)
    fig.suptitle("%s   SFS_WORNESS=0.7   capped theta=%s   Bl0=%d dots   Bl1=%d dots"
                 % (a.piece, a.theta, len(B0), len(B1)), fontsize=12)
    handles = [
        Line2D([], [], color=MESH_C, lw=6,
               label="mesh vertices (%d)" % len(V)),
        Line2D([], [], color=BL0_C, lw=6, marker="o",
               label="Breakline_0 = %d dots -- the assembly lane (SfS assembly consumes Breakline_0)" % len(B0)),
        Line2D([], [], color=BL1_C, lw=6, marker="o",
               label="Breakline_1 = %d dots" % len(B1)),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, fontsize=9)
    fig.tight_layout(rect=(0, 0.06, 1, 0.93))
    fig.savefig(a.out, dpi=110)
    plt.close(fig)
    print("[R55] wrote %s (%d bytes)" % (a.out, os.path.getsize(a.out)), flush=True)


if __name__ == "__main__":
    main()
