#!/usr/bin/env python3
"""score305.py RESULT GT POT PIECES_TSV OUT_TSV LABEL

Ticket 305 strict relative-edge table (diagnostic; the reported number is the
assembler's own '1. Acc.txt').  Generalises score303.py from Pot A to any pot.

Result file k (0-based) belongs to the k-th entry of the pot's data_path.h block,
which for our trees is piece k+1 in stage305.py shard order.  Piece p is scored
against <GT>/Pot_<P>_Piece_<p>_T.txt.  Eligibility comes from the arm's
arm_pieces_<P>.tsv: only rows with on_off == on enter the denominators (an
ineligible piece is a zero-byte axis file, i.e. shard_on_off=false).

PASS iff ang <= 20.05 deg AND |t| <= 50 mm (class/data_structure.cpp:970).
Joins: every one-edge (i,j) of Pot_<P>_simple_graph.txt with both ends on.
"""
import os
import sys

import numpy as np

ANG_BAR = 20.05
T_BAR = 50.0


def read_T(path):
    a = np.loadtxt(path, ndmin=2)
    T = np.eye(4)
    T[0:3, 0:3] = a[0:3, 0:3]
    T[0:3, 3] = a[0:3, 3]
    return T


def angle_deg(R):
    c = (np.trace(R) - 1.0) / 2.0
    return float(np.degrees(np.arccos(np.clip(c, -1.0, 1.0))))


def main():
    result, gt, pot, ptsv, out_tsv, label = sys.argv[1:7]
    # the tsv carries every arm of the pot (4 x N rows); score only this label's arm
    arm = label[:2] if label[:2] in ("OO", "MO", "OM", "MM") else ""
    on = []
    with open(ptsv) as fh:
        next(fh)
        for ln in fh:
            f = ln.rstrip("\n").split("\t")
            if len(f) < 6:
                continue
            if f[0] == pot and f[4] == "on" and (not arm or f[1] == arm):
                if int(f[2]) not in on:
                    on.append(int(f[2]))
    on.sort()
    T_est, T_gt = {}, {}
    for p in on:
        pe = os.path.join(result, "T_%dto_%d.txt" % (p - 1, p - 1))
        pg = os.path.join(gt, "Pot_%s_Piece_%d_T.txt" % (pot, p))
        if os.path.isfile(pe):
            T_est[p] = read_T(pe)
        if os.path.isfile(pg):
            T_gt[p] = read_T(pg)

    lines = ["# label\t%s" % label,
             "# eligible pieces %d: %s" % (len(on), " ".join(str(x) for x in on)),
             "piece\tang_deg\tt_mm\tverdict"]
    n_piece = 0
    for p in on:
        if p not in T_est or p not in T_gt:
            lines.append("%d\t\t\tMISSING" % p)
            continue
        a = angle_deg(T_est[p][0:3, 0:3] @ T_gt[p][0:3, 0:3].T)
        d = float(np.linalg.norm(T_est[p][0:3, 3] - T_gt[p][0:3, 3]))
        ok = a <= ANG_BAR and d <= T_BAR
        n_piece += ok
        lines.append("%d\t%.3f\t%.3f\t%s" % (p, a, d, "PASS" if ok else "FAIL"))

    n_join = n_edge = 0
    gp = os.path.join(gt, "Pot_%s_simple_graph.txt" % pot)
    if os.path.isfile(gp):
        G = np.loadtxt(gp, ndmin=2)
        lines.append("join_i\tjoin_j\tang_deg\tt_mm\tverdict")
        for ii in range(len(on)):
            for jj in range(ii + 1, len(on)):
                i, j = on[ii], on[jj]
                if i - 1 >= G.shape[0] or j - 1 >= G.shape[1]:
                    continue
                if int(G[i - 1, j - 1]) == 0:
                    continue
                n_edge += 1
                if i not in T_est or j not in T_est:
                    lines.append("%d\t%d\t\t\tMISSING" % (i, j))
                    continue
                Re = np.linalg.inv(T_est[i]) @ T_est[j]
                Rg = np.linalg.inv(T_gt[i]) @ T_gt[j]
                a = angle_deg(Re[0:3, 0:3] @ Rg[0:3, 0:3].T)
                d = float(np.linalg.norm(Re[0:3, 3] - Rg[0:3, 3]))
                ok = a <= ANG_BAR and d <= T_BAR
                n_join += ok
                lines.append("%d\t%d\t%.3f\t%.3f\t%s"
                             % (i, j, a, d, "PASS" if ok else "FAIL"))

    lines.append("SUMMARY\tpieces=%d/%d\tjoins=%d/%d"
                 % (n_piece, len(on), n_join, n_edge))
    text = "\n".join(lines) + "\n"
    with open(out_tsv, "w") as fh:
        fh.write(text)
    print("RESULT %s pieces %d/%d joins %d/%d"
          % (label, n_piece, len(on), n_join, n_edge))
    return 0


if __name__ == "__main__":
    sys.exit(main())
