#!/usr/bin/env python3
"""Ticket 323 fast loop: label the extra lines (rank 1-2) the profile ranking ships, offline.

usage: line_labels.py basins_all.json profile_rank.json [K] [dedup_deg]
Rebuilds each piece's shipped list (pool sorted by mean wall thickness, deduplicated at
dedup_deg, first K), labels each line good (<= 10 deg of the reference) or bad, and prints
per-line scale-free signals: cost ratio to rank 0, basin-support ratio to rank 0, angle to
rank 0. Every signal is a ratio within one piece: no millimetres, no per-pot constant.
"""

import json
import sys

import numpy as np

TOL = 10.0


def unit(v):
    v = np.asarray(v[:3], float)
    return v / np.linalg.norm(v)


def ang(a, b):
    return float(np.degrees(np.arccos(min(1.0, abs(float(a @ b))))))


def shipped(brow, prow, K, dd):
    out = []
    for p in prow["ranked"]:
        d = unit(p["v"])
        if all(ang(d, o["d"]) >= dd for o in out):
            out.append({"d": d, "cost": p["s"], "err": p["err"], "size": p["size"]})
        if len(out) == K:
            break
    return out


def main():
    B = {r["stem"]: r for r in json.load(open(sys.argv[1]))}
    P = {r["stem"]: r for r in json.load(open(sys.argv[2]))}
    K = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    dd = float(sys.argv[4]) if len(sys.argv) > 4 else 15.0
    rows = []
    for stem, prow in P.items():
        s = shipped(B[stem], prow, K, dd)
        if not s:
            continue
        g0 = s[0]["err"] <= TOL
        for k, x in enumerate(s):
            rows.append({"stem": stem, "pot": prow["pot"], "k": k, "good": x["err"] <= TOL,
                         "err": x["err"], "r0good": g0,
                         "cratio": x["cost"] / s[0]["cost"],
                         "sratio": x["size"] / s[0]["size"],
                         "a0": ang(x["d"], s[0]["d"])})
    json.dump(rows, open("line_labels.json", "w"), indent=0)
    pots = sorted({r["pot"] for r in rows})
    print("pot | rank0 good/n | extra lines: good bad | rescue (rank0 bad, extra good)")
    for pot in pots:
        rs = [r for r in rows if r["pot"] == pot]
        r0 = [r for r in rs if r["k"] == 0]
        ex = [r for r in rs if r["k"] > 0]
        resc = sorted({r["stem"] for r in ex if r["good"] and not r["r0good"]})
        print("%-4s| %2d/%2d | %2d %2d | %s" % (pot, sum(r["good"] for r in r0), len(r0),
              sum(r["good"] for r in ex), sum(not r["good"] for r in ex),
              " ".join(s.split("_")[-1] for s in resc)))
    ex = [r for r in rows if r["k"] > 0 and r["pot"] != "JUG"]
    for name in ("cratio", "sratio", "a0"):
        g = np.array([r[name] for r in ex if r["good"]])
        b = np.array([r[name] for r in ex if not r["good"]])
        print("%-7s good n=%3d p10/50/90 %.3f %.3f %.3f | bad n=%3d p10/50/90 %.3f %.3f %.3f" % (
            name, len(g), *np.percentile(g, [10, 50, 90]), len(b), *np.percentile(b, [10, 50, 90])))


if __name__ == "__main__":
    main()
