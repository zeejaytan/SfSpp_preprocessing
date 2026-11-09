#!/usr/bin/env python3
"""Ticket 323: classify each pot's K=1 (ticket 322) failures as line-caused or not, against axes323.

usage: predict_k1.py k1_failures.json k1_arm_pieces.txt line_labels.json [tau] [kmax]
A failed join is "line-caused" if at least one of its two pieces has a first line > 10 deg from the
reference; it is "fixable" if every such piece gets a <= 10 deg line in axes323 (kept at <= tau x
cost, first kmax). Graph index i = the i-th 'on' row of the staged arm_pieces table.
"""

import json
import re
import sys

TOL = 10.0


def main():
    F = json.load(open(sys.argv[1]))
    L = json.load(open(sys.argv[3]))
    tau = float(sys.argv[4]) if len(sys.argv) > 4 else 1.2
    kmax = int(sys.argv[5]) if len(sys.argv) > 5 else 3
    on = {}
    for ln in open(sys.argv[2]):
        c = ln.rstrip("\n").split("\t")
        if len(c) >= 5 and c[4] == "on":
            on.setdefault(c[0], []).append(c[3])
    lines = {}
    for x in L:
        lines.setdefault(x["stem"], []).append(x)
    for v in lines.values():
        v.sort(key=lambda x: x["k"])

    def info(stem):
        v = lines[stem]
        kept = [x for x in v if x["k"] == 0 or x["cratio"] <= tau][:kmax]
        return v[0]["err"], min(x["err"] for x in kept), len(kept)

    for P in "ABCDEFGHIJ":
        stems = on[P]
        acc = F[P]["acc"]
        print("== %s  K=1 acc: %s" % (P, " | ".join("%s %s" % (a[2], a[3]) for a in acc)))
        bad0 = {i + 1: info(s) for i, s in enumerate(stems) if info(s)[0] > TOL}
        print("   wrong first line: " + (", ".join("%d(%s) r0 %.1f -> axes323 best %.1f (%d lines)" % (
            i, stems[i - 1].split("_")[-1], *bad0[i]) for i in sorted(bad0)) or "none"))
        for r, rep in enumerate(F[P]["reps"], 1):
            fix, nofix, other = [], [], []
            for fj in rep["fj"]:
                i, j = map(int, re.match(r"(\d+)-(\d+)", fj).groups())
                cause = [p for p in (i, j) if p in bad0]
                if not cause:
                    other.append("%d-%d" % (i, j))
                elif all(bad0[p][1] <= TOL for p in cause):
                    fix.append("%d-%d" % (i, j))
                else:
                    nofix.append("%d-%d" % (i, j))
            print("   R%d %d/%d %d/%d failed %d: line-caused fixable %d [%s] | line-caused NOT fixable %d [%s] | other %d [%s]" % (
                r, rep["ns"], rep["ts"], rep["nj"], rep["tj"], len(rep["fj"]), len(fix), " ".join(fix),
                len(nofix), " ".join(nofix), len(other), " ".join(other)))


if __name__ == "__main__":
    main()
