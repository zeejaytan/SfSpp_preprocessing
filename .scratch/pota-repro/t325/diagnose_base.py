#!/usr/bin/env python3
"""Ticket 325 bar 3: instrument the SHIPPED scale-free base test and cylindrical gate.

The measure run's is_base_new column is not the shipped verdict: it used the
near-set axial extent with a 0.08*D cut, while sfs_axes/normalized.py:220-223
uses the ALL-points extent with 0.05*D. This script calls the shipped functions
themselves and prints every intermediate, so the verdict can be audited.

Axis file convention: "x y z dx dy dz" = [position(3), direction(3)].
In-code convention (normalized.py): vt = [direction(3), position(3)].
The swap is done once, in read_vt(), and asserted (|direction| == 1).
"""
import os
import sys
import glob
import numpy as np

IMPL = sys.argv[1]
sys.path.insert(0, IMPL)
from sfs_axes.normalized import (is_base_fragment, line_radial_gates,
                                 CLEARANCE_FLOOR_FRAC, RADIUS_CEILING_FRAC)

A323 = "/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0740_d628fc0_t323-axes/out/axes323"
A325 = "/data/gpfs/projects/punim2657/SfSpp/runs/20261110-1450_22151d0_t325-axes/out/axes325"
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
JUG = "/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom"
GTDIR = "/data/gpfs/projects/punim2657/Dataset/Juglet_GT"


def load_wall(path):
    with open(path) as fh:
        first = fh.readline()
    if first.startswith("ply"):
        n = None
        with open(path) as fh:
            for line in fh:
                if line.startswith("element vertex"):
                    n = int(line.split()[-1])
                if line.strip() == "end_header":
                    break
            rows = [[float(v) for v in fh.readline().split()[:6]] for _ in range(n)]
        return np.asarray(rows, dtype=float).T
    return np.loadtxt(path, usecols=(0, 1, 2, 3, 4, 5), ndmin=2).T


def read_vt(path, which=0):
    rows = np.atleast_2d(np.loadtxt(path, ndmin=2))
    row = np.asarray(rows[which], dtype=float)[:6]
    pos, d = row[0:3], row[3:6]
    nd = np.linalg.norm(d)
    if abs(nd - 1.0) > 1e-3:
        raise SystemExit(f"NOT-A-DIRECTION {path} |d|={nd}")
    return np.concatenate([d, pos]), row


def instrument(C, vt):
    """Repeat is_base_fragment's arithmetic and report every test value."""
    a = vt[0:3] / np.linalg.norm(vt[0:3])
    p0 = vt[3:6] - (vt[3:6] @ a) * a
    P, N = C[0:3, :], C[3:6, :]
    dp = P - p0[:, None]
    z = a @ dp
    r = np.linalg.norm(dp - a[:, None] * z[None, :], axis=0)
    r_mean = float(r.mean())
    near = r < 0.75 * r_mean
    n_near = int(near.sum())
    mean_ax_near = float(np.mean(np.abs(a @ N[:, near]))) if n_near else 0.0
    ref = np.array([1.0, 0.0, 0.0])
    if abs(np.dot(ref, a)) > 0.9:
        ref = np.array([0.0, 1.0, 0.0])
    u = ref - np.dot(ref, a) * a
    u /= np.linalg.norm(u)
    v = np.cross(a, u)
    if n_near:
        ang = np.sort(np.arctan2(v @ (dp - a[:, None] * z[None, :])[:, near],
                                 u @ (dp - a[:, None] * z[None, :])[:, near]))
        gaps = np.diff(ang)
        max_gap = np.max(np.append(gaps, 2 * np.pi - (ang[-1] - ang[0])))
        span = 360.0 - np.degrees(max_gap)
    else:
        span = 0.0
    D = float(np.linalg.norm(P.max(axis=1) - P.min(axis=1)))
    z_all = float(z.max() - z.min())
    z_near = float(z[near].max() - z[near].min()) if n_near else 0.0
    return dict(near=n_near, mean_ax_near=mean_ax_near, span=span,
                z_all_frac=z_all / D, z_near_frac=z_near / D, D=D, r_mean=r_mean)


def verdict(C, vt):
    g = line_radial_gates(vt, C)
    base = bool(is_base_fragment(C, vt))
    i = instrument(C, vt)
    cyl = (g["u_clr"] >= CLEARANCE_FLOOR_FRAC) and (g["v"] <= RADIUS_CEILING_FRAC)
    return g, base, i, cyl


def failing_test(i):
    if i["near"] < 80:
        return f"near_count {i['near']} < 80"
    if i["mean_ax_near"] < 0.70:
        return f"mean_ax_near {i['mean_ax_near']:.3f} < 0.70"
    if i["span"] < 160.0:
        return f"span {i['span']:.1f} < 160"
    if i["z_all_frac"] < 0.05:
        return f"z_all_frac {i['z_all_frac']:.4f} < 0.05"
    return "none (base)"


def main():
    print("== Juglet, nine pieces, three axis sources (shipped functions) ==")
    print("piece source   u_clr   v     u1    z_frac  cyl  base  near  ax_near  span   z_all   fails")
    for idx in range(1, 10):
        C = np.concatenate([load_wall(os.path.join(JUG, f"Juglet_Piece_{idx}.S0")),
                            load_wall(os.path.join(JUG, f"Juglet_Piece_{idx}.S1"))], axis=1)
        srcs = [("gt", os.path.join(GTDIR, f"Juglet_Piece_{idx}_Axis.xyz")),
                ("a323", os.path.join(A323, f"Juglet_Piece_{idx}_Axis.xyz")),
                ("a325", os.path.join(A325, f"Juglet_Piece_{idx}_Axis.xyz"))]
        for name, path in srcs:
            if not os.path.isfile(path):
                print(f"{idx:2d} {name:5s} MISSING {path}")
                continue
            vt, _raw = read_vt(path)
            g, base, i, cyl = verdict(C, vt)
            print(f"{idx:2d} {name:5s} {g['u_clr']:6.3f} {g['v']:5.2f} {g['u1']:5.2f} "
                  f"{g['z_frac']:6.3f}  {'Y' if cyl else 'n'}   {'Y' if base else 'n'}   "
                  f"{i['near']:5d} {i['mean_ax_near']:7.3f} {i['span']:6.1f} {i['z_all_frac']:7.4f}  "
                  f"{failing_test(i) if base else ''}")
        del C

    print()
    print("== corpus, released (authors') axes: the shipped base verdict, all 143 pieces ==")
    nb = 0
    n = 0
    fails = {}
    for axf in sorted(glob.glob(os.path.join(CORPUS, "Axes", "*_Axis.xyz"))):
        stem = os.path.basename(axf)[:-len("_Axis.xyz")]
        c0 = os.path.join(CORPUS, "Surfaces", f"{stem}_Surface_0.xyz")
        c1 = os.path.join(CORPUS, "Surfaces", f"{stem}_Surface_1.xyz")
        if not (os.path.isfile(c0) and os.path.isfile(c1)):
            continue
        C = np.concatenate([load_wall(c0), load_wall(c1)], axis=1)
        vt, _raw = read_vt(axf)
        base = bool(is_base_fragment(C, vt))
        i = instrument(C, vt)
        n += 1
        nb += base
        if base:
            fails[stem] = (i["near"], i["mean_ax_near"], i["span"], i["z_all_frac"])
        del C
    print(f"pieces {n}  base verdicts {nb}  ({100.0*nb/max(n,1):.0f}%)")
    for stem, v in fails.items():
        print(f"  {stem} near {v[0]} ax {v[1]:.3f} span {v[2]:.1f} z_all {v[3]:.4f}")


if __name__ == "__main__":
    main()
