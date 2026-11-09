#!/usr/bin/env python3
"""Ticket 323: write axes323 from axes322 by the pre-registered cost-ratio rule.

usage: build_axes323.py axes322_dir profile_rank.json out_dir [tau] [kmax]
Each axes322 file holds the first (at most 6) profile-ranked lines (15 deg apart), cheapest first. Keep line 0,
then every later line whose profile cost (mean wall thickness, profile_rank.json 'ranked'.s)
is <= tau x line 0's cost, at most kmax lines. The ratio is computed per piece from its own
costs: no millimetre threshold, no per-pot constant. Each file line is matched to its
'ranked' entry by direction (must agree within 0.5 deg) or the build aborts.
"""

import json
import os
import sys

import numpy as np


def main():
    src, prj, out = sys.argv[1:4]
    tau = float(sys.argv[4]) if len(sys.argv) > 4 else 1.2
    kmax = int(sys.argv[5]) if len(sys.argv) > 5 else 3
    P = {r["stem"]: r for r in json.load(open(prj))}
    os.makedirs(out, exist_ok=True)
    counts = {}
    for name in sorted(os.listdir(src)):
        if not name.endswith("_Axis.xyz"):
            continue
        stem = name[: -len("_Axis.xyz")]
        if stem not in P:
            print("skipped (no ranking): %s" % name)
            continue
        lines = [ln for ln in open(os.path.join(src, name)).read().splitlines() if ln.strip()]
        ranked = P[stem]["ranked"]
        if not 0 < len(lines) <= len(ranked):
            sys.exit("%s: %d file lines vs %d ranked" % (stem, len(lines), len(ranked)))
        cost = []
        for ln, rk in zip(lines, ranked):
            d = np.array(ln.split()[3:6], float)
            v = np.array(rk["v"][:3], float)
            a = np.degrees(np.arccos(min(1.0, abs(d @ v) / np.linalg.norm(d) / np.linalg.norm(v))))
            if a > 0.5:
                sys.exit("%s: file line and ranked entry differ by %.2f deg" % (stem, a))
            cost.append(rk["s"])
        keep = [lines[0]] + [ln for ln, c in zip(lines[1:], cost[1:]) if c <= tau * cost[0]]
        keep = keep[:kmax]
        with open(os.path.join(out, name), "w") as f:
            f.write("\n".join(keep) + "\n")
        pot = stem.split("_Piece")[0]
        counts.setdefault(pot, []).append(len(keep))
    if sum(len(n) for n in counts.values()) != len(P):
        sys.exit("wrote %d pieces, ranking has %d" % (sum(len(n) for n in counts.values()), len(P)))
    for pot, n in sorted(counts.items()):
        print("%-8s pieces %3d lines mean %.2f max %d" % (pot, len(n), np.mean(n), max(n)))


if __name__ == "__main__":
    main()
