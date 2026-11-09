#!/usr/bin/env python3
"""Ticket 322 fast loop, step 2: score ranking rules on the basin dump, offline.

usage: rank_rules.py basins_all.json [rule ...]
Prints the before column (the --before axis set, e.g. axes320) and, for each rule, rank-0 /
best-of-3 / best-of-6 within 10 deg per pot, the pool ceiling, and the worst pieces.
A rule maps one piece's row to an ordered list of axes (each a dict with 'err').
"""

import json
import sys

import numpy as np

POTS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "JUG"]
TOL = 10.0


def dedup(items, key_dir, tol=15.0):
    out = []
    for it in items:
        d = np.asarray(key_dir(it))
        d = d / np.linalg.norm(d)
        if all(np.degrees(np.arccos(min(1.0, abs(d @ o)))) >= tol for o in
               [np.asarray(key_dir(x)) / np.linalg.norm(key_dir(x)) for x in out]):
            out.append(it)
    return out


def table(rows, ranked, label):
    tot = np.zeros(4, int)
    lines = []
    worst = []
    for pot in POTS:
        rs = [r for r in rows if r["pot"] == pot]
        if not rs:
            continue
        k = np.zeros(4, int)
        for r in rs:
            errs = ranked[r["stem"]]
            if not errs:
                errs = [180.0]
            e0, e3, e6 = errs[0], min(errs[:3]), min(errs[:6])
            pool = min(b["ref_e"]["err"] for b in r["basins"])
            k += [e0 <= TOL, e3 <= TOL, e6 <= TOL, pool <= TOL]
            worst.append((e0, e3, r["stem"]))
        if pot != "JUG":
            tot += k
        lines.append("%-4s %3d | %3d %3d %3d | pool %3d" % (pot, len(rs), *k))
    n = sum(1 for r in rows if r["pot"] != "JUG")
    print("== %s" % label)
    print("pot    n | rank0 best3 best6 | pool<=10")
    for ln in lines:
        print(ln)
    print("pots %3d | %3d %3d %3d | pool %3d" % (n, *tot))
    worst.sort(reverse=True)
    print("worst rank0:", ", ".join("%s %.1f(b3 %.1f)" % (s, e0, e3) for e0, e3, s in worst[:12]))
    return tot


def before(rows):
    return {r["stem"]: [e["err"] for e in (r["before"] or [])] for r in rows}


def profile_ranked(prof, combine):
    out = {}
    for p in prof:
        rk = sorted(p["ranked"], key=lambda x: combine(x["w"]))
        kept = []
        for x in rk:
            d = np.asarray(x["v"][0:3])
            if all(np.degrees(np.arccos(min(1.0, abs(d @ np.asarray(k["v"][0:3]) /
                                                 (np.linalg.norm(d) * np.linalg.norm(k["v"][0:3])))))) >= 15.0
                   for k in kept):
                kept.append(x)
        out[p["stem"]] = [x["err"] for x in kept[:6]]
    return out


def main():
    rows = json.load(open(sys.argv[1]))
    table(rows, before(rows), "before (axes320 file)")
    if len(sys.argv) > 2:
        prof = json.load(open(sys.argv[2]))
        have = {p["stem"] for p in prof}
        rows = [r for r in rows if r["stem"] in have]
        print("\n(profile file covers %d pieces)" % len(rows))
        table(rows, before(rows), "before, same pieces")
        table(rows, profile_ranked(prof, np.mean), "profile thickness, mean of walls")
        table(rows, profile_ranked(prof, np.max), "profile thickness, worse wall")


if __name__ == "__main__":
    main()
