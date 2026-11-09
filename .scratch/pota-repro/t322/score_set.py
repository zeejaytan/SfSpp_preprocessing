#!/usr/bin/env python3
"""Ticket 322: score one or more axis sets against the dump_basins reference, per pot.

usage: score_set.py JUGKEY LABEL=DIR [LABEL=DIR ...]
Reference and error exactly as dump_basins.ref_errors (pots: min over released lines and
Ground Truth line 0; Juglet: mesh-derived key). Prints rank-0 / best-of-3 / best-of-6 within
10 deg per pot and the worst rank-0 pieces, and a per-piece TSV to stdout's tail.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dump_basins import CORPUS, load_wall, piece_paths, ref_errors  # noqa: E402
from sfs_axes.io_axes import read_axes  # noqa: E402

POTS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "JUG"]


def main():
    jugkey = sys.argv[1]
    sets = [s.split("=", 1) for s in sys.argv[2:]]
    stems = sorted(fn[:-len("_Surface_0.xyz")] for fn in os.listdir(os.path.join(CORPUS, "Surfaces"))
                   if fn.endswith("_Surface_0.xyz"))
    stems += ["Juglet_Piece_%d" % i for i in range(1, 10)]
    errs = {lab: {} for lab, _ in sets}
    for stem in stems:
        pot, p0, p1, relp, gtp = piece_paths(stem, jugkey)
        C = np.concatenate([load_wall(p0), load_wall(p1)], axis=1)
        c = C[0:3].mean(1)
        rel = read_axes(relp[0])
        gt = read_axes(gtp)[:, 0] if gtp and os.path.isfile(gtp) else None
        for lab, d in sets:
            bp = os.path.join(d, stem + "_Axis.xyz")
            bv = read_axes(bp) if os.path.isfile(bp) else np.zeros((6, 0))
            errs[lab][stem] = (pot, [ref_errors(bv[:, k], rel, gt, c)["err"] for k in range(bv.shape[1])])
    for lab, _ in sets:
        print("== %s" % lab)
        print("pot    n | rank0 best3 best6")
        tot = np.zeros(3, int)
        worst = []
        for pot in POTS:
            rs = [(s, e) for s, (p, e) in errs[lab].items() if p == pot]
            k = np.zeros(3, int)
            for s, e in rs:
                e = e or [180.0]
                k += [e[0] <= 10, min(e[:3]) <= 10, min(e[:6]) <= 10]
                worst.append((e[0], min(e[:3]), s))
            if pot != "JUG":
                tot += k
            print("%-4s %3d | %3d %3d %3d" % (pot, len(rs), *k))
        print("pots %3d | %3d %3d %3d" % (sum(1 for p, _ in errs[lab].values() if p != "JUG"), *tot))
        worst.sort(reverse=True)
        print("worst rank0:", ", ".join("%s %.1f(b3 %.1f)" % (s, a, b) for a, b, s in worst[:12]))
    print("#stem\t" + "\t".join("%s_r0\t%s_b3" % (lab, lab) for lab, _ in sets))
    for stem in stems:
        row = []
        for lab, _ in sets:
            e = errs[lab][stem][1] or [180.0]
            row += ["%.2f" % e[0], "%.2f" % min(e[:3])]
        print(stem + "\t" + "\t".join(row))


if __name__ == "__main__":
    main()
