#!/usr/bin/env python3
"""summary292.py -- collect the array output into out/lanes.tsv and out/summary.md (ticket 292).

Writes the five pre-registered headline numbers before any interpretation sentence, then the
per-pot table, the below-bar list, the error list, ledger O, the hand recompute, the corpus and
geometry assertions, and the exclusions verbatim."""
import glob
import json
import os
import sys

COLS = ["pot", "piece", "lane", "n_ours", "n_auth", "median", "cov_ours", "cov_auth",
        "jumps", "max_step", "len_ours", "len_auth", "at_bar"]

J09 = "Pot_J_Piece_09"
INTERIOR_DEFECT = {("Pot_C_Piece_01", "0"), ("Pot_J_Piece_01", "0")}
AUTHORS_EXCLUDED = {"Pot_F_Piece_07", "Pot_I_Piece_28", "Pot_I_Piece_29", "Pot_I_Piece_30", "Pot_J_Piece_12"}

EXCLUSIONS = [
    "Pot J 09, both lanes: excluded from the tally. The conservator ruled its reference line wrong",
    "(ticket 289); it is measured and reported, never counted.",
    "Pot C 01 and Pot J 01, lane 0 (interior) only: reported, excluded from the headline. Both pieces",
    "are not watertight in the interior surface (ticket 285), so an interior-lane number is evidence",
    "about the input, not the method. Their lane 1 (exterior) counts normally.",
    "Five pieces are outside the authors evaluation set (Pot F 07, Pot I 28, Pot I 29, Pot I 30,",
    "Pot J 12): they were removed by the authors own rule (paper :329), so their lanes are scored and",
    "listed, and never compared with the paper numbers (ledger section O).",
]


def rows_of(path):
    out = []
    with open(path) as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 13:
                out.append(dict(zip(COLS, parts)))
    return out


def num(r, k):
    try:
        return float(r[k])
    except (KeyError, ValueError):
        return float("nan")


def at_bar(r):
    return r.get("at_bar") == "yes"


def main(run):
    out = os.path.join(run, "out")
    lanes = []
    for p in sorted(glob.glob(os.path.join(out, "lanes", "*.tsv"))):
        lanes.extend(rows_of(p))
    lanes.sort(key=lambda r: (r["piece"], r["lane"]))

    with open(os.path.join(out, "lanes.tsv"), "w") as f:
        f.write("\t".join(COLS + ["set"]) + "\n")
        for r in lanes:
            st = "measured"
            if r["piece"] == J09:
                st = "excluded-j09"
            elif (r["piece"], r["lane"]) in INTERIOR_DEFECT:
                st = "excluded-interior"
            elif r["piece"] in AUTHORS_EXCLUDED:
                st = "authors-excluded"
            f.write("\t".join([r[c] for c in COLS] + [st]) + "\n")

    measured = lanes
    valid = [r for r in measured if r["piece"] != J09]
    sound = [r for r in valid if (r["piece"], r["lane"]) not in INTERIOR_DEFECT]
    n_pieces = len(set(r["piece"] for r in measured))
    jumps = [r for r in sound if int(r["jumps"]) > 0]
    biggest = max(sound, key=lambda r: num(r, "max_step")) if sound else None

    errors = []
    for p in sorted(glob.glob(os.path.join(out, "errors", "*.tsv"))):
        errors.extend([l.rstrip("\n") for l in open(p)])

    status = {}
    for p in sorted(glob.glob(os.path.join(out, "status", "*.tsv"))):
        parts = open(p).read().rstrip("\n").split("\t")
        status[parts[0]] = parts[1:]

    def bar_line(name, rows):
        k = sum(1 for r in rows if at_bar(r))
        return "%-9s %3d / %3d at bar (%.1f%%)" % (name, k, len(rows), 100.0 * k / max(len(rows), 1))

    L = []
    L.append("# 292 — the frozen corpus re-scored at the shipped defaults")
    L.append("")
    L.append("Run directory: `" + run + "`")
    try:
        b = json.load(open(os.path.join(out, "build.json")))
        L.append("Commit `" + b["commit"] + "`, built on `" + b["node"] + "`; edge md5 `" + b["edge_md5"]
                 + "`, mesh md5 `" + b["mesh_md5"] + "`.")
    except Exception as exc:
        L.append("build.json unreadable: " + str(exc))
    L.append("")
    L.append("## Headline (pre-registered; no interpretation in this section)")
    L.append("")
    L.append("1. lanes measured: **%d** (of 296 expected from 148 pieces)" % len(measured))
    L.append("2. lanes valid: **%d** (measured minus Pot J 09, 2 expected)" % len(valid))
    L.append("3. lanes sound: **%d** (valid minus Pot C 01 / Pot J 01 lane 0, 2 expected)" % len(sound))
    L.append("4. lanes at bar:")
    for nm, rs in (("measured", measured), ("valid", valid), ("sound", sound)):
        L.append("   - " + bar_line(nm, rs))
    L.append("5. lanes with at least one jump: **%d of %d sound lanes**; largest single step " % (len(jumps), len(sound))
             + ("**%.3f mm** on %s lane %s (median %s mm)." % (num(biggest, "max_step"), biggest["piece"],
                                                                 biggest["lane"], biggest["median"])
                if biggest else "n/a"))
    L.append("")
    L.append("Pieces that produced at least one scored lane: %d of 148." % n_pieces)
    L.append("")

    L.append("## Per-pot table (at bar counted on the sound lanes of the pot)")
    L.append("")
    L.append("| pot | pieces | lanes measured | valid | sound | at bar (sound) |")
    L.append("|---|---|---|---|---|---|")
    pots = sorted(set(r["pot"] for r in measured))
    for pot in pots:
        m = [r for r in measured if r["pot"] == pot]
        v = [r for r in valid if r["pot"] == pot]
        s = [r for r in sound if r["pot"] == pot]
        L.append("| %s | %d | %d | %d | %d | %d |" % (pot, len(set(r["piece"] for r in m)), len(m), len(v), len(s),
                                                     sum(1 for r in s if at_bar(r))))
    L.append("| **all** | %d | %d | %d | %d | %d |" % (n_pieces, len(measured), len(valid), len(sound),
                                                    sum(1 for r in sound if at_bar(r))))
    L.append("")

    L.append("## Lanes below bar")
    L.append("")
    L.append("| piece | lane | set | n ours | n auth | median mm | cov ours | cov auth | jumps | max step |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for r in lanes:
        if at_bar(r):
            continue
        st = "sound"
        if r["piece"] == J09:
            st = "excluded (J09)"
        elif (r["piece"], r["lane"]) in INTERIOR_DEFECT:
            st = "excluded (interior gap)"
        elif r["piece"] in AUTHORS_EXCLUDED:
            st = "authors-excluded"
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" %
                 (r["piece"], r["lane"], st, r["n_ours"], r["n_auth"], r["median"], r["cov_ours"], r["cov_auth"],
                  r["jumps"], r["max_step"]))
    L.append("")
    L.append("Below bar: %d lanes measured, %d of them sound." %
             (sum(1 for r in lanes if not at_bar(r)), sum(1 for r in sound if not at_bar(r))))
    L.append("")

    L.append("## Errors (a piece that produced no scorable lane)")
    L.append("")
    if errors:
        L.append("| pot | piece | lane | stage | exit | detail |")
        L.append("|---|---|---|---|---|---|")
        for e in errors:
            parts = e.split("\t")
            L.append("| " + " | ".join(parts[:6]) + " |")
    else:
        L.append("None: every piece staged, meshed with its classify line, ran both lanes and scored.")
    L.append("")

    L.append("## Ledger O — pieces outside the authors evaluation set")
    L.append("")
    L.append("Scored, listed, never compared with the paper (see Exclusions).")
    L.append("")
    L.append("| piece | lane | n ours | median mm | cov ours | cov auth | jumps | at bar |")
    L.append("|---|---|---|---|---|---|---|---|")
    for r in lanes:
        if r["piece"] in AUTHORS_EXCLUDED:
            L.append("| %s | %s | %s | %s | %s | %s | %s | %s |" %
                     (r["piece"], r["lane"], r["n_ours"], r["median"], r["cov_ours"], r["cov_auth"], r["jumps"],
                      r["at_bar"]))
    L.append("")

    L.append("## Recomputed by hand (independent parser and full distance matrix, before deletion)")
    L.append("")
    rec = sorted(glob.glob(os.path.join(out, "recheck", "*.txt")))
    if rec:
        L.append("```")
        for p in rec:
            L.append(open(p).read().rstrip("\n"))
        L.append("```")
    else:
        L.append("No recompute file was written.")
    L.append("")

    L.append("## Corpus and geometry assertions")
    L.append("")
    for nm in ("corpus_check.txt", "geometry_check.txt"):
        p = os.path.join(out, nm)
        L.append("`" + nm + "`:" if os.path.exists(p) else "`" + nm + "` missing:")
        L.append("```")
        if os.path.exists(p):
            L.append(open(p).read().rstrip("\n"))
        L.append("```")
        L.append("")

    L.append("## Exclusions carried verbatim")
    L.append("")
    for line in EXCLUSIONS:
        L.append("- " + line)
    L.append("")

    L.append("## What this run is")
    L.append("")
    L.append("A new baseline at the shipped defaults on the frozen corpus. It is not a comparison with")
    L.append("the 4.0-era 265-of-294 tally: the binary, the growth angle and the sampled cloud all changed,")
    L.append("so a difference in the count is not evidence of an improvement or a regression in either")
    L.append("direction. What it does buy is repeatability: the same commit, the same frozen clouds and")
    L.append("symlink staging reproduce this table, and the per-lane pictures record what the misses look")
    L.append("like at this commit.")
    L.append("")
    bad = [p for p, st in status.items() if not all(x.split("=")[-1] in ("0", "1") for x in st[:4])]
    if bad:
        L.append("Tasks with a non-zero stage/mesh/edge status: " + ", ".join(sorted(bad)))

    path = os.path.join(out, "summary.md")
    with open(path, "w") as f:
        f.write("\n".join(L) + "\n")
    print("[SUMMARY] " + path + " rows=" + str(len(lanes)) + " sound=" + str(len(sound))
          + " at_bar_sound=" + str(sum(1 for r in sound if at_bar(r))) + " errors=" + str(len(errors)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))