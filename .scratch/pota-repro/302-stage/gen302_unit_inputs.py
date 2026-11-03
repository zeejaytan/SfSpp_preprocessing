#!/usr/bin/env python3
"""Ticket 302 stage 1: build unit-proof inputs for the MATLAB comparison.

Three Pot A pieces from the released corpus (read only), each probed at three
axes: released line 1, +2 deg/+1 mm perturbed, +5 deg/+3 mm perturbed.
Clouds are subsampled with the ticket-71 stride (step=10) so MATLAB stays
fast; the stride is deterministic and recorded in run.json.

Writes CELLS/<cell>/{X.tsv (n x 6), vt.tsv (6)} and cells.tsv.
"""
import os
import sys

import numpy as np

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
PIECES = [("A", 1), ("A", 4), ("A", 7)]
PERTURBS = [("released", 0.0, 0.0), ("p2", 2.0, 1.0), ("p5", 5.0, 3.0)]
STEP = 10


def canonicalize(vt):
    vt = np.asarray(vt, dtype=float).copy()
    if vt[2] < 0:
        vt = -vt
    return vt


def read_axes(path):
    rows = []
    with open(path) as fh:
        for ln in fh:
            p = ln.split()
            if len(p) >= 6:
                rows.append([float(x) for x in p[:6]])
    return np.asarray(rows).T if rows else np.zeros((6, 0))


def load_surface(path):
    a = np.loadtxt(path, usecols=(0, 1, 2, 3, 4, 5), ndmin=2)
    return np.asarray(a, dtype=float).T


def rot_about(v, axis, deg):
    a = np.deg2rad(deg)
    k = axis / np.linalg.norm(axis)
    return (v * np.cos(a) + np.cross(k, v) * np.sin(a)
            + k * np.dot(k, v) * (1 - np.cos(a)))


def main(outdir):
    cells = os.path.join(outdir, "CELLS")
    os.makedirs(cells, exist_ok=True)
    rng = np.random.default_rng(302)
    with open(os.path.join(outdir, "cells.tsv"), "w") as man:
        man.write("cell\tpot\tpiece\tprobe\tn\n")
        for pot, piece in PIECES:
            stem = "Pot_%s_Piece_%02d" % (pot, piece)
            C0 = load_surface(os.path.join(CORPUS, "Surfaces", stem + "_Surface_0.xyz"))
            C1 = load_surface(os.path.join(CORPUS, "Surfaces", stem + "_Surface_1.xyz"))
            X = np.concatenate([C0, C1], axis=1)
            X = X[:, ::STEP]
            nrm = X[3:6]
            ln = np.linalg.norm(nrm, axis=0)
            ok = ln > 1e-12
            X[3:6, ok] = nrm[:, ok] / ln[ok]
            X[3:6, ~ok] = 0.0
            rel = canonicalize(read_axes(os.path.join(CORPUS, "Axes", stem + "_Axis.xyz"))[:, 0])
            for tag, ang, mm in PERTURBS:
                vt = rel.copy()
                if ang > 0 or mm > 0:
                    d = vt[0:3]
                    t = rng.standard_normal(3)
                    t = t - d * np.dot(d, t)
                    vt[0:3] = rot_about(d, t, ang)
                    q = rng.standard_normal(3)
                    q = q - d * np.dot(d, q)
                    q /= np.linalg.norm(q)
                    vt[3:6] = vt[3:6] + q * mm
                cell = "pa%02d_%s" % (piece, tag)
                cd = os.path.join(cells, cell)
                os.makedirs(cd, exist_ok=True)
                np.savetxt(os.path.join(cd, "X.tsv"), X.T, fmt="%.17g", delimiter="\t")
                np.savetxt(os.path.join(cd, "vt.tsv"), vt, fmt="%.17g", delimiter="\t")
                man.write("%s\t%s\t%d\t%s\t%d\n" % (cell, pot, piece, tag, X.shape[1]))
    print("inputs written to", outdir)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "inputs")
