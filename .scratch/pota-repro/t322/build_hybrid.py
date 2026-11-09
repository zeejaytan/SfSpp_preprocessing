#!/usr/bin/env python3
"""Ticket 322 hybrid axis set: line 1 from the profile ranker, lines 2..K from the old ranker.

usage: build_hybrid.py AXES322 AXES320 OUT
Per piece: the first line of AXES322, then the lines of AXES320 in their own order, dropping any
within 10 deg of a line already kept (the union's duplicate rule, DEDUP_COS), capped at 6
(UNION_MAX). Lines are copied as text, byte for byte, so a K-line head is comparable with any
other arm built from the same files.
"""
import os
import sys

import numpy as np

TOL_DEG = 10.0
CAP = 6


def direction(line):
    v = np.array([float(x) for x in line.split()[3:6]])
    return v / np.linalg.norm(v)


def main():
    a322, a320, out = sys.argv[1:4]
    os.makedirs(out, exist_ok=True)
    dropped = 0
    for fn in sorted(os.listdir(a322)):
        if not fn.endswith("_Axis.xyz"):
            continue
        new = [ln for ln in open(os.path.join(a322, fn)) if ln.strip()]
        old = [ln for ln in open(os.path.join(a320, fn)) if ln.strip()]
        kept = [new[0]]
        for ln in old:
            d = direction(ln)
            if all(np.degrees(np.arccos(min(1.0, abs(d @ direction(k))))) >= TOL_DEG for k in kept):
                kept.append(ln)
            else:
                dropped += 1
            if len(kept) == CAP:
                break
        with open(os.path.join(out, fn), "w") as fh:
            fh.writelines(k if k.endswith("\n") else k + "\n" for k in kept)
    print("wrote", len(os.listdir(out)), "files; old lines dropped as duplicates of a kept line:", dropped)


if __name__ == "__main__":
    main()
