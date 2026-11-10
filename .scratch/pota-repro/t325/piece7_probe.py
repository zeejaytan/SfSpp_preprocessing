#!/usr/bin/env python3
"""Ticket 325 bar 3: is Juglet piece 7 the vessel's BASE, or is the base test firing on a wall?

The question the bar asks: "no piece may be classified as a base fragment by a wall axis".
A base verdict is correct if the piece physically contains the vessel bottom (a disc
perpendicular to the axis, spanning all azimuths, whose normals are axial). It is wrong
if the piece is a curved wall sheet and the test fires anyway.

For each of the nine pieces, about the Juglet_GT axis, report:
  r_min   the piece's closest approach to the axis (a wall sheet cannot come closer
          than the vessel radius; a base disc reaches r ~ 0)
  n(z)    the axial spread of the near set (r < 0.75 r_mean): a disc sits in one thin
          z band at the vessel bottom; a wall arc spreads over the piece's whole height
  r(z)    near-set radial reach: a disc runs from 0 out to the vessel radius at one z
"""
import os
import sys
import numpy as np

sys.path.insert(0, sys.argv[1])
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


def main():
    print("piece  pts    r_min  r_mean   near  near_z_span  near_z_frac_of_span  near_r_max  near_r_min")
    for idx in range(1, 10):
        S0 = load_wall(os.path.join(JUG, f"Juglet_Piece_{idx}.S0"))
        S1 = load_wall(os.path.join(JUG, f"Juglet_Piece_{idx}.S1"))
        rows = np.atleast_2d(np.loadtxt(os.path.join(GTDIR, f"Juglet_Piece_{idx}_Axis.xyz"), ndmin=2))
        pos, d = rows[0][0:3], rows[0][3:6]
        a = d / np.linalg.norm(d)
        p0 = pos - (pos @ a) * a
        out = []
        for S in (S0, S1):
            dp = S[0:3] - p0[:, None]
            z = a @ dp
            r = np.linalg.norm(dp - a[:, None] * z[None, :], axis=0)
            out.append((z, r))
        z = np.concatenate([o[0] for o in out])
        r = np.concatenate([o[1] for o in out])
        r_mean = r.mean()
        near = r < 0.75 * r_mean
        zspan = z.max() - z.min()
        if near.sum():
            zn = z[near]
            nz_span = zn.max() - zn.min()
            print(f"{idx:5d} {len(r):6d} {r.min():6.2f} {r_mean:7.2f} {int(near.sum()):6d} "
                  f"{nz_span:12.2f} {nz_span/zspan:19.3f} {r[near].max():11.2f} {r[near].min():11.2f}")
        else:
            print(f"{idx:5d} {len(r):6d} {r.min():6.2f} {r_mean:7.2f} {0:6d} {'-':>12s} {'-':>19s} {'-':>11s} {'-':>11s}")
        del S0, S1


if __name__ == "__main__":
    main()
