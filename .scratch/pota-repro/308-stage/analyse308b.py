#!/usr/bin/env python3
"""analyse308b.py -- collect the Stage B numbers into the ticket's delta table.

Reads each run dir's score/acc.tsv (the assembler's own "1. Acc.txt": sherd k/n,
edge k/n) and score/<LABEL>.tsv (strict relative-edge SUMMARY: pieces k/n, joins k/n).
Groups labels into arms (MOR / MMR / MMpR / PAs<seed>), takes best-of-N by
(sherd, joins) -- never the median -- and prints:
  1. every repeat,
  2. per-arm best-of-N,
  3. the delta table against ticket 305's prune-ON grid.

Usage: analyse308b.py RUNID [RUNID ...]
       analyse308b.py --from-list /tmp/t308b_jobs.txt
"""
import json
import os
import re
import sys

RUNS = "/data/gpfs/projects/punim2657/SfSpp/runs"

# ticket 305's grid, prune ON, truncation ON (its own best-of-N; see the ticket).
# (sherd, pieces_den, edge, edge_den) for the control and the axes arm.
B305 = {
    "A": {"OO": (8, 8, 15, 15), "MM": (6, 8, 10, 15)},
    "B": {"OO": (9, 9, 15, 15), "MM": (7, 9, 10, 15)},
    "C": {"OO": (4, 4, 5, 5), "MM": (4, 4, 5, 5)},
    "D": {"OO": (22, 27, 53, 66), "MM": (19, 28, 33, 69)},
    "E": {"OO": (31, 31, 62, 62), "MM": (23, 31, 37, 62)},
    "F": {"OO": (6, 6, 9, 9), "MM": (5, 5, 7, 7)},
    "G": {"OO": (7, 7, 10, 10), "MM": (5, 7, 2, 10)},
    "I": {"OO": (25, 27, 59, 65), "MM": (18, 26, 26, 62)},
    "J": {"OO": (8, 11, 16, 21), "MM": (5, 11, 7, 21)},
}


def arm_of(label):
    if label.startswith("MMpR"):
        return "MMp"
    if label.startswith("MMR"):
        return "MM"
    if label.startswith("MOR"):
        return "MO"
    if label.startswith("PAs"):
        return "PAseed" + label[3:]
    return label


def read_acc(path):
    rows = {}
    if not os.path.isfile(path):
        return rows
    with open(path) as fh:
        for ln in fh:
            f = ln.rstrip("\n").split("\t")
            if len(f) < 4 or f[0] == "label":
                continue
            try:
                sherd = int(f[2].split("/")[0]); sden = int(f[2].split("/")[1])
                edge = int(f[3].split("/")[0]); eden = int(f[3].split("/")[1])
            except (ValueError, IndexError):
                continue
            rows[f[0]] = (sherd, sden, edge, eden)
    return rows


def read_summary(path):
    if not os.path.isfile(path):
        return None
    for ln in open(path):
        if ln.startswith("SUMMARY"):
            m = re.findall(r"(\d+)/(\d+)", ln)
            if len(m) >= 2:
                return (int(m[0][0]), int(m[0][1]), int(m[1][0]), int(m[1][1]))
    return None


def main():
    args = sys.argv[1:]
    if args and args[0] == "--from-list":
        runids = [ln.split()[2] for ln in open(args[1]) if len(ln.split()) >= 3]
    else:
        runids = args
    out = []
    for rid in runids:
        rd = os.path.join(RUNS, rid)
        if not os.path.isdir(rd):
            out.append({"runid": rid, "error": "no run dir"})
            continue
        pot = rid.rsplit("-", 1)[-1]
        acc = read_acc(os.path.join(rd, "score", "acc.tsv"))
        rec = {"runid": rid, "pot": pot, "arms": {}}
        for label, val in sorted(acc.items()):
            arm = arm_of(label)
            s = read_summary(os.path.join(rd, "score", label + ".tsv"))
            rec["arms"].setdefault(arm, []).append({
                "label": label, "acc": val, "strict": s})
        out.append(rec)

    print("== every repeat (assembler's own 1. Acc.txt | strict relative-edge)")
    for rec in out:
        if "error" in rec:
            print("%s: %s" % (rec["runid"], rec["error"])); continue
        print("-- pot %s  %s" % (rec["pot"], rec["runid"]))
        for arm in sorted(rec["arms"]):
            for r in rec["arms"][arm]:
                a = r["acc"]; s = r["strict"]
                print("   %-8s %-9s sherd %d/%d  edge %d/%d   strict %s"
                      % (arm, r["label"], a[0], a[1], a[2], a[3],
                         ("%d/%d + %d/%d" % s) if s else "n/a"))

    print()
    print("== best-of-N per arm (by sherd then joins; never the median)")
    best = {}
    for rec in out:
        if "error" in rec:
            continue
        for arm, rows in rec["arms"].items():
            def key(r):
                a = r["acc"]; s = r["strict"] or (0, 0, 0, 0)
                return (a[0] / max(a[1], 1), a[2] / max(a[3], 1), s[0], s[2])
            b = max(rows, key=key)
            best.setdefault(rec["pot"], {})[arm] = (b, len(rows))
    for pot in sorted(best):
        for arm in sorted(best[pot]):
            b, n = best[pot][arm]
            a = b["acc"]; s = b["strict"]
            print("   %s %-6s best of %d: %-8s sherd %d/%d edge %d/%d strict %s"
                  % (pot, arm, n, b["label"], a[0], a[1], a[2], a[3],
                     ("%d/%d + %d/%d" % s) if s else "n/a"))

    print()
    print("== DELTA TABLE  (sherd | edge)  -- 308 OO is arm MO")
    print("pot\t305 MM (prune on)\t308 MM\t308 MMp\t308 OO (MO)\t305 OO (control)")
    def fmt(t):
        if not t:
            return "-"
        return "%d/%d | %d/%d" % t
    for pot in sorted(best):
        g = best[pot]
        def gv(arm):
            if arm not in g:
                return None
            a = g[arm][0]["acc"]
            return (a[0], a[1], a[2], a[3])
        row = [pot, fmt(B305.get(pot, {}).get("MM")), fmt(gv("MM")), fmt(gv("MMp")),
               fmt(gv("MO")), fmt(B305.get(pot, {}).get("OO"))]
        print("\t".join(row))
    print()
    print("== pot A seed sweep (one run per axis seed, MM chain)")
    for pot in ["A"]:
        for arm in sorted(best.get(pot, {})):
            if arm.startswith("PAseed"):
                b, n = best[pot][arm]
                a = b["acc"]
                print("   %s %s sherd %d/%d edge %d/%d" % (arm, b["label"], a[0], a[1], a[2], a[3]))
    return 0


if __name__ == "__main__":
    sys.exit(main())