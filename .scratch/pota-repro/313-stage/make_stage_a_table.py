#!/usr/bin/env python3
"""make_stage_a_table.py -- Generate Stage A verification table on 10 failing Pot E pieces."""

import os
import sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "sfs_axes"))

from sfs_axes.io_axes import read_axes, direction_angle_deg
from sfs_axes.normalized import centroid_distance, worst_wall_normalized_cost

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
RUNS = "/data/gpfs/projects/punim2657/SfSpp/runs"
AX_310 = os.path.join(RUNS, "20261105-1215_1a6f16e_t310b3-timing/out/axes310")
AX_313 = os.path.join(RUNS, "20261106-1316_fe906ab_t313a-axes/out/axes313")


def load_surface(path):
    a = np.loadtxt(path, usecols=(0, 1, 2, 3, 4, 5), ndmin=2)
    return np.asarray(a, dtype=float).T


def canonicalize(vt):
    vt = np.asarray(vt, dtype=float).copy()
    if vt[2] < 0:
        vt[0:3] = -vt[0:3]
    return vt


def main():
    failing_10 = [3, 9, 23, 24, 25, 26, 27, 28, 29, 31]
    print("| Piece | 310 Rank-1 (deg) | 310 d(C,L) (mm) | 313 Rank-1 (deg) | 313 Best (deg) [K] | 313 d(C,L) (mm) | GT d(C,L) (mm) | Mechanism Eliminated |")
    print("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |")

    for p in failing_10:
        stem = f"Pot_E_Piece_{p:02d}"
        s0 = load_surface(os.path.join(CORPUS, "Surfaces", f"{stem}_Surface_0.xyz"))
        s1 = load_surface(os.path.join(CORPUS, "Surfaces", f"{stem}_Surface_1.xyz"))
        C = np.concatenate([s0, s1], axis=1)

        gt_path = os.path.join(CORPUS, "Ground Truth Axes", f"{stem}_Axis.xyz")
        rel_path = os.path.join(CORPUS, "Axes", f"{stem}_Axis.xyz")
        gt_ax = read_axes(gt_path) if os.path.isfile(gt_path) else read_axes(rel_path)
        rel_ax = read_axes(rel_path)

        vt_gt = canonicalize(gt_ax[:, 0])
        vt_rel = canonicalize(rel_ax[:, 0])
        d_gt = centroid_distance(vt_gt, C)

        # 310 unnormalized
        ax310_path = os.path.join(AX_310, f"{stem}_Axis.xyz")
        ax310 = read_axes(ax310_path)
        v310_0 = canonicalize(ax310[:, 0])
        ang310_0 = min(direction_angle_deg(v310_0[:3], vt_gt[:3]), direction_angle_deg(v310_0[:3], vt_rel[:3]))
        d310_0 = centroid_distance(v310_0, C)

        # 313 normalized
        ax313_path = os.path.join(AX_313, f"{stem}_Axis.xyz")
        ax313 = read_axes(ax313_path)
        K313 = ax313.shape[1]
        v313_0 = canonicalize(ax313[:, 0])
        ang313_0 = min(direction_angle_deg(v313_0[:3], vt_gt[:3]), direction_angle_deg(v313_0[:3], vt_rel[:3]))
        d313_0 = centroid_distance(v313_0, C)

        angs_all = [min(direction_angle_deg(canonicalize(ax313[:, k])[:3], vt_gt[:3]),
                        direction_angle_deg(canonicalize(ax313[:, k])[:3], vt_rel[:3]))
                    for k in range(K313)]
        best_ang = min(angs_all)

        mech = "Centroid Lever-Arm Bias"
        if d310_0 < 30.0:
            mech = f"Centroid Collapse ({d310_0:.1f}mm -> {d313_0:.1f}mm)"
        elif ang310_0 > 40.0:
            mech = f"Perpendicular Decoy ({ang310_0:.1f}° -> {best_ang:.1f}°)"

        print(f"| Pot E Piece {p:02d} | {ang310_0:.2f}° | {d310_0:.1f} mm | {ang313_0:.2f}° | **{best_ang:.2f}°** [K={K313}] | {d313_0:.1f} mm | {d_gt:.1f} mm | {mech} |")


if __name__ == "__main__":
    main()
