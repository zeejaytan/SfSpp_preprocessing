#!/usr/bin/env python3
"""Ticket 295 -- is the authors' reconstructed surface a boundary at the break?

Q3 asks where the authors' own surface ends, and the plan was to measure the distance from their breakline
dots to the boundary loop of their DS mesh.  This script answers the PRIOR question: does that mesh have a
boundary loop at all?

Measured on nine pieces: every edge of every authors' DS mesh is shared by exactly two triangles -- the
surface is CLOSED.  A closed surface has no boundary, so "where does the authors' mesh end" has no answer on
this artefact: the break is not represented as a mesh boundary, and the reference line's edge can only be
read on the surface's own geometry (the >100 deg tangent-plane gap used throughout ticket 295), never on a
mesh rim.  The distance measurement is therefore dropped, not fudged.

Columns: piece, V, T, edges, edges_shared_by_2, edges_shared_by_1 (a boundary), edges_shared_by_gt2
(non-manifold), edge_len_med_mm, CLOSED/OPEN.
"""
import math
import os
import sys

import numpy as np

import p295_lib as L

PIECES = ["Pot_C_Piece_03", "Pot_D_Piece_22", "Pot_D_Piece_27", "Pot_E_Piece_16", "Pot_H_Piece_02",
          "Pot_H_Piece_10", "Pot_I_Piece_06", "Pot_I_Piece_13", "Pot_I_Piece_25"]


def edge_census(idx):
    e = np.vstack([idx[:, [0, 1]], idx[:, [1, 2]], idx[:, [2, 0]]])
    e = np.sort(e, axis=1)
    uniq, cnt = np.unique(e, axis=0, return_counts=True)
    return uniq, cnt


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "outf_extra"
    os.makedirs(out, exist_ok=True)
    rows = []
    for piece in PIECES:
        mp = os.path.join(L.CORP, "Mesh", piece + "_Mesh_DS.obj")
        if not os.path.exists(mp):
            print("%s: no DS mesh at %s" % (piece, mp))
            continue
        V, idx = L.read_obj(mp)
        uniq, cnt = edge_census(idx)
        elen = np.linalg.norm(V[uniq[:, 0]] - V[uniq[:, 1]], axis=1)
        n1 = int((cnt == 1).sum())
        n2 = int((cnt == 2).sum())
        ng = int((cnt > 2).sum())
        rows.append(dict(piece=piece, V=len(V), T=len(idx), edges=len(uniq), shared_2=n2,
                         shared_1=n1, shared_gt2=ng,
                         edge_len_med=round(float(np.median(elen)), 4),
                         closure=("CLOSED" if n1 == 0 and ng == 0 else "OPEN")))
        print("%s V=%d T=%d edges=%d shared_by_2=%d boundary_edges=%d non_manifold=%d "
              "edge_len_med=%.4f -> %s"
              % (piece, len(V), len(idx), len(uniq), n2, n1, ng,
                 float(np.median(elen)), rows[-1]["closure"]))
    L.write_tsv(os.path.join(out, "meshrim.tsv"), rows,
                ["piece", "V", "T", "edges", "shared_2", "shared_1", "shared_gt2",
                 "edge_len_med", "closure"])


if __name__ == "__main__":
    main()
