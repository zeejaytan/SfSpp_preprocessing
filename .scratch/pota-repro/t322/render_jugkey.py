#!/usr/bin/env python3
"""Ticket 322 render: the Juglet key against the released file and a candidate set.

Panel 0: assembled juglet (true pose), side view along the vessel axis, pieces coloured,
the axis drawn, robust slice centres marked. Panels 1-9: each piece in its own scan frame,
viewed square-on to the key; green = key (vessel axis), red = released Axes/Juglet line 0,
blue = candidate rank 0. Titles give the angles.
"""

import argparse
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from juglet_key import DS  # noqa: E402
from juglet_key2 import LANES, frame, load_wall  # noqa: E402
from sfs_axes.io_axes import direction_angle_deg, read_axes  # noqa: E402


def draw_line(ax, vt, c, e1, e2, d, lim, **kw):
    u = vt[0:3] / np.linalg.norm(vt[0:3])
    foot = vt[3:6] + ((c - vt[3:6]) @ u) * u
    s = np.linspace(-lim, lim, 2)
    pts = foot[None, :] + s[:, None] * u[None, :] - c
    ax.plot(pts @ e1, pts @ d, **kw)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jugkey", required=True)
    ap.add_argument("--cands", required=True)
    ap.add_argument("--cand-label", default="axes320 rank 0")
    ap.add_argument("--png", required=True)
    a = ap.parse_args()
    S = np.load(os.path.join(a.jugkey, "assembled_samples.npz"))
    P, owner, axis = S["P"], S["owner"], S["axis"]
    rep2 = json.load(open(os.path.join(a.jugkey, "key2_report.json")))
    fig, axs = plt.subplots(2, 5, figsize=(25, 11))
    axs = axs.ravel()
    d, e1, e2 = frame(axis[0:3])
    rel = P - axis[3:6]
    cm = plt.get_cmap("tab10")
    ax = axs[0]
    for i in range(1, 10):
        m = owner == i
        ax.scatter(rel[m] @ e1, rel[m] @ d, s=0.3, color=cm(i - 1), label="p%d" % i)
    z = rel @ d
    ax.plot([0, 0], [z.min() - 5, z.max() + 5], "g-", lw=2, label="vessel axis")
    for r in rep2["slices"]:
        ax.plot(r["cx"], r["z"], "k+", ms=8)
    ax.set_aspect("equal")
    ax.set_title("Assembled juglet (true pose from juglet_gt.hdf5)\n"
                 "green = one fitted axis; + = slice-circle centres (mm)", fontsize=10)
    ax.legend(markerscale=10, fontsize=7, loc="lower right")
    for i in range(1, 10):
        ax = axs[i]
        C = np.concatenate([load_wall(os.path.join(LANES, "Juglet_Piece_%d.S0" % i)),
                            load_wall(os.path.join(LANES, "Juglet_Piece_%d.S1" % i))], axis=1)
        X = C[0:3].T
        c = X.mean(0)
        key = read_axes(os.path.join(a.jugkey, "key", "Juglet_Piece_%d_Axis.xyz" % i))[:, 0]
        relv = read_axes(os.path.join(DS, "Axes/Juglet/Juglet_Piece_%d_Axis.xyz" % i))[:, 0]
        cand = read_axes(os.path.join(a.cands, "Juglet_Piece_%d_Axis.xyz" % i))[:, 0]
        kd, ke1, ke2 = frame(key[0:3])
        # view: look along ke2, so the key lies in the drawing plane (vertical)
        Y = X - c
        ax.scatter(Y @ ke1, Y @ kd, s=0.2, color="0.6")
        lim = 40
        draw_line(ax, key, c, ke1, ke2, kd, lim, color="g", lw=2.5)
        draw_line(ax, relv, c, ke1, ke2, kd, lim, color="r", lw=1.5, ls="--")
        draw_line(ax, cand, c, ke1, ke2, kd, lim, color="b", lw=1.5)
        loc = rep2["pieces"][str(i)]["local_opt_vs_key_deg"]
        ax.set_title("p%d  released %.1f deg | %s %.1f deg\n piece's own nearest optimum %.1f deg from key"
                     % (i, direction_angle_deg(relv[0:3], key[0:3]), a.cand_label,
                        direction_angle_deg(cand[0:3], key[0:3]), loc), fontsize=9)
        ax.set_xlim(-35, 35)
        ax.set_ylim(-35, 35)
        ax.set_aspect("equal")
    fig.suptitle("Juglet answer key (green) vs released Dataset/Axes/Juglet (red dashed) vs %s (blue). "
                 "Pieces drawn in their own scan frame, viewed square-on to the key; mm." % a.cand_label,
                 fontsize=12)
    fig.tight_layout()
    fig.savefig(a.png, dpi=110)
    print("wrote", a.png)


if __name__ == "__main__":
    main()
