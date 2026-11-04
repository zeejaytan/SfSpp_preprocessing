#!/usr/bin/env python3
"""Ticket 303 scorer: one Pot A arm, per-piece placement error and joins.

    score303.py <result_dir> <gt_dir> <out_tsv> <label>

Piece k (0-based file T_<k>to_<k>.txt) is compared with
<gt_dir>/Pot_A_Piece_<k+1>_T.txt:
    ang_deg = angle of R_est * R_gt^T
    t_mm    = |t_est - t_gt|
PASS iff ang_deg <= 20.05 and t_mm <= 50.0 -- the assembler's own counting bar
(class/data_structure.cpp:966: rad_threshold 0.35 rad, t_threshold 50.0 mm).

Joins: for every one-edge (i,j) of Pot_A_simple_graph.txt, the assembled
relative pose of j in i's frame (T_i^-1 T_j) is compared with the GT relative
pose, same bar.
"""
import os
import sys

import numpy as np

ANG_BAR = 20.05
T_BAR = 50.0
NPIECE = 8


def read_T(path):
    a = np.loadtxt(path, ndmin=2)
    T = np.eye(4)
    T[0:3, 0:3] = a[0:3, 0:3]
    T[0:3, 3] = a[0:3, 3]
    return T


def angle_deg(R):
    c = (np.trace(R) - 1.0) / 2.0
    return float(np.degrees(np.arccos(np.clip(c, -1.0, 1.0))))


def main(result, gt, out_tsv, label):
    lines = ["# label\t%s" % label]
    T_est, T_gt = {}, {}
    for k in range(NPIECE):
        pe = os.path.join(result, "T_%dto_%d.txt" % (k, k))
        pg = os.path.join(gt, "Pot_A_Piece_%d_T.txt" % (k + 1))
        if os.path.isfile(pe):
            T_est[k] = read_T(pe)
        if os.path.isfile(pg):
            T_gt[k] = read_T(pg)

    n_piece = 0
    lines.append("piece\tang_deg\tt_mm\tverdict")
    for k in range(NPIECE):
        if k not in T_est or k not in T_gt:
            lines.append("%d\t\t\tMISSING" % (k + 1))
            continue
        a = angle_deg(T_est[k][0:3, 0:3] @ T_gt[k][0:3, 0:3].T)
        d = float(np.linalg.norm(T_est[k][0:3, 3] - T_gt[k][0:3, 3]))
        ok = a <= ANG_BAR and d <= T_BAR
        n_piece += ok
        lines.append("%d\t%.3f\t%.3f\t%s" % (k + 1, a, d, "PASS" if ok else "FAIL"))

    n_join = n_edge = 0
    gp = os.path.join(gt, "Pot_A_simple_graph.txt")
    if os.path.isfile(gp):
        G = np.loadtxt(gp, ndmin=2)
        lines.append("join_i\tjoin_j\tang_deg\tt_mm\tverdict")
        for i in range(NPIECE):
            for j in range(i + 1, NPIECE):
                if int(G[i, j]) == 0:
                    continue
                n_edge += 1
                if i not in T_est or j not in T_est:
                    lines.append("%d\t%d\t\t\tMISSING" % (i + 1, j + 1))
                    continue
                Re = np.linalg.inv(T_est[i]) @ T_est[j]
                Rg = np.linalg.inv(T_gt[i]) @ T_gt[j]
                a = angle_deg(Re[0:3, 0:3] @ Rg[0:3, 0:3].T)
                d = float(np.linalg.norm(Re[0:3, 3] - Rg[0:3, 3]))
                ok = a <= ANG_BAR and d <= T_BAR
                n_join += ok
                lines.append("%d\t%d\t%.3f\t%.3f\t%s"
                             % (i + 1, j + 1, a, d, "PASS" if ok else "FAIL"))

    lines.append("SUMMARY\tpieces=%d/%d\tjoins=%d/%d"
                 % (n_piece, NPIECE, n_join, n_edge))
    text = "\n".join(lines) + "\n"
    with open(out_tsv, "w") as fh:
        fh.write(text)
    sys.stdout.write(text)
    print("RESULT %s pieces %d/%d joins %d/%d"
          % (label, n_piece, NPIECE, n_join, n_edge))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3],
                  sys.argv[4] if len(sys.argv) > 4 else "arm"))
