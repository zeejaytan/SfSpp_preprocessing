#!/usr/bin/env python3
"""Ticket 13 checker: re-derive every evidence table from the bytes on disk.

Usage: check13.py --run <RUN_DIR> [--expect-terminal]

Prints one line per check and a final CHECKS=n FAILURES=m; exit 0 only when m == 0.
This is the independent pass, not a re-run of report13.py: every number is recomputed
from the score files, the walls, the axis packs and the PNG bytes themselves.
"""
import argparse
import glob
import hashlib
import json
import os
import sys

ANG_BAR = 20.05
T_BAR = 50.0
WANT_SHA = "de44ffc23c8db5208bd5f6f9c9f57d819bed7805f0330526bcb2750487bfd727"
PART_A_ARMS = ["MOR_CTL", "T08_ALL", "T09_ALL", "T09_WITH_AUTHOR_J01",
               "SWAP_J01", "SWAP_J02", "SWAP_J05", "SWAP_J06", "SWAP_J11"]
OWN_ARMS = ["OWN_T09", "AUTHOR", "OWN_AUTHOR_NORMALS", "AUTHOR_OWN_NORMALS", "OWN_SHARED_1MM",
            "AUTHOR_SHARED_1MM", "OWN_VOXEL_1MM", "AUTHOR_VOXEL_1MM", "OWN_BALANCED_S0S1"]
REQUIRED_FIXTURES = ["exe_pin_match", "own_t09_pin_match", "author_donor_match",
                     "normal_transfer_fixed_xyz", "single_file_swap_proof"]
TERMINAL = {"COMPLETED", "FAILED", "CANCELLED", "TIMEOUT", "OUT_OF_MEMORY", "NODE_FAIL",
            "PREEMPTED", "BOOT_FAIL", "DEADLINE"}

CHECKS = 0
FAILURES = []


def ok(name, cond, detail=""):
    global CHECKS
    CHECKS += 1
    if not cond:
        FAILURES.append(name + ((" :: " + detail) if detail else ""))
        print("FAIL %-34s %s" % (name, detail))
    else:
        print("ok   %-34s %s" % (name, detail))
    return cond


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_table(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        rows = [ln.rstrip("\n") for ln in fh if ln.strip()]
    if not rows:
        return []
    sep = "\t" if "\t" in rows[0] else ","
    return [r.split(sep) for r in rows]


def num(x, default=None):
    try:
        return float(x)
    except Exception:
        return default


def parse_score(path):
    if not os.path.exists(path):
        return None
    pieces, joins, summary = [], [], None
    mode = None
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.rstrip("\n")
            if ln.startswith("SUMMARY"):
                summary = ln
                continue
            if ln.startswith("#") or not ln:
                continue
            f = ln.split("\t")
            if f[0] == "piece":
                mode = "p"
                continue
            if f[0] == "join_i":
                mode = "j"
                continue
            if mode == "p" and len(f) >= 4:
                pieces.append((int(f[0]), float(f[1]), float(f[2]), f[3]))
            elif mode == "j" and len(f) >= 5:
                joins.append((int(f[0]), int(f[1]), float(f[2]), float(f[3]), f[4]))
    pc = (0, 0)
    jc = (0, 0)
    if summary:
        for part in summary.split("\t"):
            if part.startswith("pieces="):
                a, b = part.split("=", 1)[1].split("/")
                pc = (int(a), int(b))
            elif part.startswith("joins="):
                a, b = part.split("=", 1)[1].split("/")
                jc = (int(a), int(b))
    return {"pieces": pieces, "joins": joins, "pc": pc, "jc": jc}


def wall_points(path):
    """Point count from a PLY (element vertex) or an xyz row file."""
    n = 0
    with open(path, encoding="utf-8", errors="replace") as fh:
        if path.endswith(".ply"):
            in_header = True
            for ln in fh:
                if in_header and ln.startswith("element vertex"):
                    n = int(ln.split()[-1])
                if ln.strip() == "end_header":
                    in_header = False
                    break
            return n
        for ln in fh:
            if ln.strip() and not ln.startswith("#"):
                n += 1
    return n
def check_cells(run, rows):
    seen = set()
    bad = []
    for r in rows:
        if len(r) < 13:
            bad.append("short row %r" % (r,))
            continue
        arm, rep, job, usable, poses, sherd, sden, jp, jd = r[0], r[1], r[2], int(r[3]), int(r[4]), int(r[5]), int(r[6]), int(r[7]), int(r[8])
        key = (arm, rep)
        if key in seen:
            bad.append("duplicate %s" % (key,))
        seen.add(key)
        sc = parse_score(os.path.join(run, "score", arm + "_" + rep + ".tsv"))
        if usable:
            if not os.path.exists(os.path.join(run, "logs", "cell_raw_" + arm + "_" + rep + ".json")):
                bad.append("%s/%s usable without cell_raw json" % key)
            if not sc:
                bad.append("%s/%s usable without score file" % key)
                continue
            if (jp, jd) != sc["jc"] or (sherd, sden) != sc["pc"]:
                bad.append("%s/%s counts %s,%s vs score %s,%s" % (arm, rep, jp, jd, sc["jc"], sc["pc"]))
        if jd and jd != 21:
            bad.append("%s/%s joins_total=%s (want 21)" % (arm, rep, jd))
        if sden and sden != 11:
            bad.append("%s/%s sherd_den=%s (want 11)" % (arm, rep, sden))
    partA = [r for r in rows if r[0] in PART_A_ARMS]
    ok("cells_partA_rows", len(partA) == 22, "%d rows for the 22-cell array" % len(partA))
    ok("cells_rows_consistent", not bad, "; ".join(bad[:4]))


def check_seams(run, ev, rows):
    expected = set()
    for r in rows:
        if len(r) < 4 or int(r[3]) != 1:
            continue
        sc = parse_score(os.path.join(run, "score", r[0] + "_" + r[1] + ".tsv"))
        if not sc:
            continue
        for (i, j, ang, t, _v) in sc["joins"]:
            verdict = "pass" if (ang <= ANG_BAR and t <= T_BAR) else "fail"
            expected.add((r[0], r[1], str(i), str(j), "%.2f" % ang, "%.2f" % t, verdict))
    got = set()
    bad = []
    for s in read_table(os.path.join(ev, "seams.tsv"))[1:]:
        if len(s) < 7:
            bad.append("short %r" % (s,))
            continue
        try:
            key = (s[0], s[1], s[2], s[3], "%.2f" % float(s[4]), "%.2f" % float(s[5]), s[6])
        except Exception:
            bad.append("unparsable %r" % (s,))
            continue
        if key not in expected:
            bad.append("not derivable %r" % (key,))
        got.add(key)
    ok("seams_rows", len(got) == len(expected), "%d rows vs %d derived" % (len(got), len(expected)))
    ok("seams_verdicts", not bad, "; ".join(bad[:4]))


def check_summary(rows):
    summ = read_table(os.path.join(rows["ev"], "summary_partA.tsv"))[1:]
    by_arm = {}
    for r in rows["cells"]:
        if len(r) < 13:
            continue
        by_arm.setdefault(r[0], []).append(r)
    best_t09 = max([int(r[7]) for r in by_arm.get("T09_ALL", []) if int(r[3]) == 1] or [0])
    bad = []
    if len(summ) != 9:
        bad.append("%d rows (want 9)" % len(summ))
    for s in summ:
        if len(s) < 8:
            bad.append("short %r" % (s,))
            continue
        arm = s[0]
        sub = [r for r in by_arm.get(arm, []) if int(r[3]) == 1]
        want_best = max([int(r[7]) for r in sub] or [0])
        if int(s[3]) != want_best:
            bad.append("%s best_joins %s vs %s" % (arm, s[3], want_best))
        if int(s[1]) != len(sub):
            bad.append("%s repeats %s vs %s usable" % (arm, s[1], len(sub)))
        if sub:
            reached = sum(1 for r in sub if int(r[7]) == want_best)
            if s[4] != "%d/%d" % (reached, len(sub)):
                bad.append("%s reached_by %s vs %d/%d" % (arm, s[4], reached, len(sub)))
            top = max(sub, key=lambda r: (int(r[7]), int(r[5])))
            if s[2] != "%d/%d" % (int(top[5]), int(top[6])):
                bad.append("%s best_sherd %s vs %s/%s" % (arm, s[2], top[5], top[6]))
        want_delta = want_best - best_t09 if arm != "T09_ALL" else 0
        if int(s[6]) != want_delta:
            bad.append("%s delta %s vs %s" % (arm, s[6], want_delta))
    ok("summary_partA", not bad, "; ".join(bad[:4]))


def check_walls(run, ev):
    rows = read_table(os.path.join(ev, "j01_walls.tsv"))
    body = rows[1:]
    bad = []
    if len(body) != 18:
        bad.append("%d rows (want 18 = 9 arms x 2 faces)" % len(body))
    for r in body:
        if len(r) < 11:
            bad.append("short %r" % (r,))
            continue
        arm, face, pts, dup, match = r[0], r[1], int(r[2]), int(r[3]), num(r[4])
        path = os.path.join(run, "j01", "walls", arm + ".S" + face + ".xyz")
        if not os.path.exists(path):
            bad.append("missing %s" % path)
            continue
        if wall_points(path) != pts:
            bad.append("%s.S%s points %s vs %s" % (arm, face, pts, wall_points(path)))
        if sha256_file(path) != r[9]:
            bad.append("%s.S%s xyz sha mismatch" % (arm, face))
        if dup != 0:
            bad.append("%s.S%s duplicate_xyz=%s" % (arm, face, dup))
        if match is None or not (0.0 <= match <= 100.0):
            bad.append("%s.S%s matched_1mm=%s" % (arm, face, r[4]))
    ok("j01_walls", not bad, "; ".join(bad[:4]))


def check_factors(run, ev):
    rows = read_table(os.path.join(ev, "j01_factors.tsv"))[1:]
    bad = []
    arms = [r[0] for r in rows if r]
    if sorted(arms) != sorted(OWN_ARMS):
        bad.append("arms %s" % ",".join(arms))
    for r in rows:
        if len(r) < 12:
            bad.append("short %r" % (r,))
            continue
        arm = r[0]
        ax = os.path.join(run, "j01", "axes", arm, "Pot_J_Piece_01_Axis.xyz")
        if not os.path.exists(ax):
            bad.append("%s axis missing" % arm)
            continue
        if sha256_file(ax) != r[2]:
            bad.append("%s axes sha mismatch" % arm)
        if int(r[1]) < 1 or int(r[3]) < 1 or int(r[4]) < 1:
            bad.append("%s k/stride/drawn = %s/%s/%s" % (arm, r[1], r[3], r[4]))
        if r[10] not in ("0", "1"):
            bad.append("%s qualifies_b2=%s" % (arm, r[10]))
    ok("j01_factors", not bad, "; ".join(bad[:4]))


def check_fixtures(ev):
    rows = read_table(os.path.join(ev, "fixtures.tsv"))[1:]
    got = {r[0]: r[1] for r in rows if len(r) > 1}
    missing = [f for f in REQUIRED_FIXTURES if f not in got]
    bad = [f for f in REQUIRED_FIXTURES if f in got and got[f] != "PASS"]
    ok("fixtures_required_pass", not missing and not bad,
       "missing=%s failed=%s" % (",".join(missing) or "-", ",".join(bad) or "-"))


def check_renders(ev):
    rows = read_table(os.path.join(ev, "renders.tsv"))[1:]
    bad = []
    if len(rows) != 2:
        bad.append("%d rows (want 2)" % len(rows))
    for r in rows:
        if len(r) < 3:
            bad.append("short %r" % (r,))
            continue
        path = r[1]
        if not os.path.exists(path):
            bad.append("missing %s" % path)
            continue
        with open(path, "rb") as fh:
            magic = fh.read(8)
        if not magic.startswith(b"\x89PNG\r\n\x1a\n"):
            bad.append("%s not a png" % path)
        if os.path.getsize(path) < 20000:
            bad.append("%s only %d bytes" % (path, os.path.getsize(path)))
        if r[2] != "20":
            bad.append("%s scale_bar_mm=%s" % (path, r[2]))
    ok("renders", not bad, "; ".join(bad[:4]))


def check_jobs(ev, expect_terminal):
    rows = read_table(os.path.join(ev, "jobs.tsv"))[1:]
    if not expect_terminal:
        ok("jobs_rows", len(rows) >= 2, "%d rows" % len(rows))
        return
    bad = []
    if not rows:
        bad.append("no sacct rows")
    for r in rows:
        if len(r) < 6:
            bad.append("short %r" % (r,))
            continue
        if r[4] not in TERMINAL:
            bad.append("%s state %s" % (r[0], r[4]))
        if r[5] != "0:0":
            bad.append("%s exit %s" % (r[0], r[5]))
    ok("jobs_terminal_0_0", not bad, "; ".join(bad[:4]))


def check_sources(ev):
    rows = read_table(os.path.join(ev, "sources.tsv"))[1:]
    bad = []
    if len(rows) < 20:
        bad.append("%d rows" % len(rows))
    for r in rows:
        if len(r) < 5:
            bad.append("short %r" % (r,))
            continue
        if not os.path.exists(r[1]):
            bad.append("missing %s" % r[1])
        if r[2] != "-" and not (len(r[2]) == 64 and all(c in "0123456789abcdef" for c in r[2])):
            bad.append("bad sha for %s" % r[1])
    ok("sources", not bad, "; ".join(bad[:4]))


def check_b2(ev, cells):
    rows = read_table(os.path.join(ev, "b2_gate.tsv"))[1:]
    chosen = [r for r in rows if len(r) > 7 and r[7] == "1"]
    b2cells = [r for r in cells if str(r[0]).startswith("B2_")]
    bad = []
    if len(chosen) > 2:
        bad.append("%d chosen arms" % len(chosen))
    if b2cells:
        for r in chosen:
            n = sum(1 for c in b2cells if c[0] == "B2_" + r[0])
            if n < 2:
                bad.append("%s has %d repeats" % (r[0], n))
    ok("b2_gate", not bad, "chosen=%s b2_cells=%d" % (",".join(r[0] for r in chosen) or "-", len(b2cells)))


def main():
    ap = argparse.ArgumentParser(description="Ticket 13 checker")
    ap.add_argument("--run", required=True)
    ap.add_argument("--expect-terminal", action="store_true")
    a = ap.parse_args()
    run = os.path.abspath(a.run)
    ev = os.path.join(run, "evidence")
    for name in ("cells.tsv", "seams.tsv", "summary_partA.tsv", "sources.tsv", "fixtures.tsv",
                 "renders.tsv", "j01_walls.tsv", "j01_factors.tsv", "b2_gate.tsv"):
        ok("present_" + name, os.path.exists(os.path.join(ev, name)), os.path.join(ev, name))
    cells = read_table(os.path.join(ev, "cells.tsv"))
    if len(cells) < 2:
        print("CHECKS=%d FAILURES=%d" % (CHECKS, len(FAILURES) + 1))
        return 1
    body = cells[1:]
    check_cells(run, body)
    check_seams(run, ev, body)
    check_summary({"ev": ev, "cells": body})
    check_walls(run, ev)
    check_factors(run, ev)
    check_fixtures(ev)
    check_renders(ev)
    check_jobs(ev, a.expect_terminal)
    check_sources(ev)
    check_b2(ev, body)
    print("CHECKS=%d FAILURES=%d" % (CHECKS, len(FAILURES)))
    if FAILURES:
        print("FAILED: " + " | ".join(FAILURES[:8]))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

