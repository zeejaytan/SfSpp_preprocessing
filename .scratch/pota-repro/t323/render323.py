#!/usr/bin/env python3
"""Ticket 323: GT assembly beside two assembled arms, one PNG per pot.

Same drawing as 314-stage/render_assemblies.py (corpus Surface_0/1 points, every 8th, posed by the
4x4 a' = R a + t, top view and perspective), plus a ground-truth panel. Pieces are the 'on' rows of
the run's staged arm_pieces table, so T_<k>to_<k> is matched to the k-th staged piece (J09 is off).
Each arm is moved into the GT frame through its first piece (GT_1 inv(T_1)), so the three panels
share one frame and a stray piece shows as a displaced colour.
usage: render323.py POT RUN_DIR ARM_A LABEL_A ARM_B LABEL_B OUT_PNG [TITLE]
"""

import glob
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
PALETTE = ["#4e79a7", "#f28e2b", "#e15759", "#76b7b2", "#59a14f", "#edc948", "#b07aa1", "#ff9da7",
           "#9c755f", "#bab0ac", "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]


def staged(run_dir, pot):
    f = glob.glob(os.path.join(run_dir, "trees", "*", "arm_pieces_%s.tsv" % pot))[0]
    out = []
    for ln in open(f):
        c = ln.rstrip("\n").split("\t")
        if len(c) >= 5 and c[4] == "on":
            out.append(int(c[2]))
    return out


def cloud(pot, n, step=8):
    pts = []
    for s in (0, 1):
        p = os.path.join(CORPUS, "Surfaces", "Pot_%s_Piece_%02d_Surface_%d.xyz" % (pot, n, s))
        if os.path.isfile(p):
            a = np.loadtxt(p)
            pts.append(a[::step, :3])
    return np.vstack(pts)


def T4(path):
    a = np.loadtxt(path, ndmin=2)
    T = np.eye(4)
    T[:3, :4] = a[:3, :4]
    return T


def main():
    pot, run, arm_a, lab_a, arm_b, lab_b, out = sys.argv[1:8]
    title = sys.argv[8] if len(sys.argv) > 8 else ""
    pieces = staged(run, pot)
    C = [cloud(pot, n) for n in pieces]
    GT = [T4(os.path.join(CORPUS, "Ground Truth", "Pot_%s_Piece_%d_T.txt" % (pot, n))) for n in pieces]
    panels = [("Ground truth", GT)]
    for arm, lab in ((arm_a, lab_a), (arm_b, lab_b)):
        d = os.path.join(run, "out", arm)
        Ts = []
        for k in range(len(pieces)):
            p = os.path.join(d, "T_%dto_%d.txt" % (k, k))
            Ts.append(T4(p) if os.path.isfile(p) else None)
        k0 = next(k for k, T in enumerate(Ts) if T is not None)
        A = GT[k0] @ np.linalg.inv(Ts[k0])
        panels.append((lab, [A @ T if T is not None else None for T in Ts]))
    gt_pts = np.vstack([c @ T[:3, :3].T + T[:3, 3] for c, T in zip(C, GT)])
    mid = 0.5 * (gt_pts.max(0) + gt_pts.min(0))
    span = 0.75 * (gt_pts.max(0) - gt_pts.min(0)).max()
    views = [(90, 0, "top"), (20, 45, "perspective")]
    fig = plt.figure(figsize=(18, 12), dpi=130)
    for ci, (lab, Ts) in enumerate(panels):
        for ri, (el, az, vn) in enumerate(views):
            ax = fig.add_subplot(2, 3, ri * 3 + ci + 1, projection="3d")
            for k, (c, T) in enumerate(zip(C, Ts)):
                if T is None:
                    continue
                q = c @ T[:3, :3].T + T[:3, 3]
                ax.scatter(q[:, 0], q[:, 1], q[:, 2], s=1.5, c=PALETTE[k % len(PALETTE)], alpha=0.7,
                           label=("P%02d" % pieces[k]) if (ci == 0 and ri == 0) else None)
            ax.set_xlim(mid[0] - span, mid[0] + span)
            ax.set_ylim(mid[1] - span, mid[1] + span)
            ax.set_zlim(mid[2] - span, mid[2] + span)
            ax.view_init(elev=el, azim=az)
            ax.set_title("%s\n%s" % (lab, vn), fontsize=11, fontweight="bold")
            if ci == 0 and ri == 0:
                ax.legend(loc="upper right", markerscale=3, fontsize=7, ncol=2)
    if title:
        fig.suptitle(title, fontsize=13, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(out)
    print("saved", out)


if __name__ == "__main__":
    main()
