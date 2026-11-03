#!/usr/bin/env python3
"""gatepass69.py -- ticket 69 Part A, the assembler's own axis test on the corpus.

Two label-free-ish instruments, both built from the directions partA69.py measured
(out/dirs.tsv) and the released GT poses (Ground Truth/Pot_X_Piece_N_T.txt):

  A. the EDGE GATE -- the test the assembler actually applies.  For every true edge of the
     pot's own simple_graph, rotate each piece's axis into the assembled frame with its GT
     pose and take the folded angle between the two axes.  feature_matching.cpp:1715 admits
     an edge at <= 25 deg.  Report per pot, per estimator: edges measured, median, pass
     count.  This is the column the merge decision should turn on.
  B. the t68 GATE -- the per-piece cross-piece consistency used by ticket 68 to CHOOSE an
     estimator (median folded angle to the other pieces of the same pot, after the same
     rotation).  Report the pot-level median and whether the gate's ranking of estimators
     agrees with the truth's.

Neither instrument reads a GT AXIS.  The gt column in dirs.tsv is used only for the
diagnostic printout, never for a selection.

usage: gatepass69.py CORPUS OUTDIR
"""
import os
import sys

import numpy as np

EST = ["rel0", "relbest", "nperp", "nperpS1", "npar", "nparS1", "pottS1", "potsac_s0"]
GATE_DEG = 25.0


def unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 0 else v


def fold(a, b):
    return float(np.degrees(np.arccos(np.clip(abs(unit(a) @ unit(b)), 0.0, 1.0))))


def read_dirs(path):
    with open(path) as fh:
        hdr = fh.readline().rstrip("\n").split("\t")
        rows = []
        for line in fh:
            c = line.rstrip("\n").split("\t")
            if len(c) < 4:
                continue
            r = {"pot": c[0], "piece": int(c[1])}
            for e in EST + ["gt"]:
                i = hdr.index(e + "_x")
                r[e] = np.array([float(c[i]), float(c[i + 1]), float(c[i + 2])])
            rows.append(r)
    return rows


def read_gt_err(outdir):
    d = {}
    with open(os.path.join(outdir, "pieces.tsv")) as fh:
        hdr = fh.readline().rstrip("\n").split("\t")
        for line in fh:
            c = line.rstrip("\n").split("\t")
            r = dict(zip(hdr, c))
            d[(r["pot"], int(r["piece"]))] = {e: float(r[e]) for e in EST}
    return d


def read_R(path):
    return np.loadtxt(path, ndmin=2).reshape(4, 4)[0:3, 0:3]


def read_graph(path):
    """Simple-graph adjacency: rows of tab-separated 0/1 (trailing tab tolerated)."""
    A = []
    with open(path) as fh:
        for line in fh:
            c = [x for x in line.strip().split("\t") if x != ""]
            if c:
                A.append([int(float(x)) for x in c])
    return np.array(A, dtype=int)


def main():
    corpus, outdir = sys.argv[1], sys.argv[2]
    rows = read_dirs(os.path.join(outdir, "dirs.tsv"))
    err = read_gt_err(outdir)
    gtdir = os.path.join(corpus, "Ground Truth")
    bypot = {}
    for r in rows:
        bypot.setdefault(r["pot"], []).append(r)

    print("EDGE GATE: folded angle between two pieces' axes after each is rotated into the")
    print("assembled frame by its own GT pose; the assembler admits an edge at <= %.0f deg"
          % GATE_DEG)
    print("(feature_matching.cpp:1715).  Only edges whose BOTH pieces have a GT axis count.")
    print("")
    print("%-4s %5s %6s  %s" % ("pot", "edges", "graph", " ".join("%22s" % e for e in EST)))
    print("%-4s %5s %6s  %s" % ("", "", "", " ".join("%10s %11s" % ("med", "pass") for _ in EST)))

    edge_out = []
    gate_out = []
    for pot in sorted(bypot):
        sub = {r["piece"]: r for r in bypot[pot]}
        gpath = os.path.join(gtdir, "Pot_%s_simple_graph.txt" % pot)
        if not os.path.exists(gpath):
            continue
        A = read_graph(gpath)
        npieces = A.shape[0]
        edges = [(i + 1, j + 1) for i in range(npieces) for j in range(i + 1, npieces)
                 if A[i, j]]
        Rs = {}
        for k in sub:
            t = os.path.join(gtdir, "Pot_%s_Piece_%d_T.txt" % (pot, k))
            if os.path.exists(t):
                Rs[k] = read_R(t)
        usable = [e for e in edges if e[0] in Rs and e[1] in Rs]
        cells = []
        for e in EST:
            ang = [fold(Rs[i] @ sub[i][e], Rs[j] @ sub[j][e]) for i, j in usable]
            med = float(np.median(ang)) if ang else float("nan")
            npass = int(sum(1 for a in ang if a <= GATE_DEG))
            cells.append("%10.1f %4d/%-6d" % (med, npass, len(ang)))
            edge_out.append((pot, e, len(ang), med, npass,
                             float(np.median([err[(pot, i)][e] for i, j in usable] +
                                             [err[(pot, j)][e] for i, j in usable]))))
        print("%-4s %5d %6s  %s" % (pot, len(usable), "%d/%d" % (len(usable), len(edges)),
                                    " ".join(cells)))

        # t68 cross-piece gate: median folded angle to the other pieces, per estimator
        gcells = []
        gmed = {}
        for e in EST:
            per = [float(np.median([fold(Rs[k] @ sub[k][e], Rs[o] @ sub[o][e])
                                    for o in sub if o != k])) for k in sub]
            gmed[e] = float(np.median(per))
            gcells.append("%10.1f" % gmed[e])
            gate_out.append((pot, e, gmed[e]))
        best_gate = min(EST, key=lambda x: gmed[x])
        print("%-4s %5s %6s  %s   <- t68 cross-piece gate; its pick %s" % (
            "", "", "", " ".join(gcells), best_gate))

    with open(os.path.join(outdir, "edge_gate.tsv"), "w") as fh:
        fh.write("pot\testimator\tedges_measured\tgate_med_deg\tpass25\tpass_frac\tgt_med_deg\n")
        for pot, e, n, med, npass, gtmed in edge_out:
            fh.write("%s\t%s\t%d\t%.3f\t%d\t%.3f\t%.3f\n" % (
                pot, e, n, med, npass, npass / max(n, 1), gtmed))
    with open(os.path.join(outdir, "crosspiece_gate.tsv"), "w") as fh:
        fh.write("pot\testimator\tgate_med_deg\n")
        for pot, e, g in gate_out:
            fh.write("%s\t%s\t%.3f\n" % (pot, e, g))
    print("\nwrote edge_gate.tsv and crosspiece_gate.tsv")


if __name__ == "__main__":
    main()
