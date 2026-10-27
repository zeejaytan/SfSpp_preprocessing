#!/usr/bin/env python3
"""Ticket 31: compare gate-probe outputs line by line, with BOTH numbers on any difference.

The reference is the laptop's measured output (fetched with CRLF line endings);
the candidates are the compute node's outputs. Every per-pair number the probe
prints is compared: the 2.0 mm / 0.85 gate and the 20.0 deg / 0.7 gate, raw and
absolute inlier counts, and min_d.

raw and abs are integers and are compared exactly. min_d is compared as printed:
the probe formats it with %.2f, so the laptop's record of it IS the two-digit
string, and a node run cannot be said to reproduce a value the laptop never
recorded. That limit is stated in the output rather than papered over.

Exit 0 only when the header count, the fifteen rows and the pass-rate line all
match exactly. Exit 1 otherwise, with every difference printed as
"<pair> <gate> <field>: laptop=X node=Y".
"""
import argparse
import re
import sys

PAIR = re.compile(
    r"^\s*(\d+)-(\d+): "
    r"d<([0-9.]+)/n>([0-9.]+) raw=(\d+) abs=(\d+) min_d=([0-9.]+); "
    r"d<([0-9.]+)/n>([0-9.]+) raw=(\d+) abs=(\d+) min_d=([0-9.]+)\s*$")
HEAD = re.compile(r"^(\S+) mates: (\d+) \(_0-only\)\s*$")
PASS = re.compile(r"^STRICT pass rate at GT \(_0-only\): (\d+)/(\d+)\s*$")


def load(path):
    """(label, mates, rows, pass) from one probe output; CRLF tolerated."""
    text = open(path, "r", encoding="utf-8", errors="replace").read()
    lines = [ln.rstrip("\r") for ln in text.split("\n")]
    label, mates, rows, strict = "", None, {}, None
    for ln in lines:
        m = HEAD.match(ln)
        if m:
            label, mates = m.group(1), int(m.group(2))
            continue
        m = PASS.match(ln)
        if m:
            strict = (int(m.group(1)), int(m.group(2)))
            continue
        m = PAIR.match(ln)
        if m:
            g = m.groups()
            rows[g[0] + "-" + g[1]] = {
                "g1": {"raw": int(g[4]), "abs": int(g[5]), "min_d": g[6]},
                "g2": {"raw": int(g[9]), "abs": int(g[10]), "min_d": g[11]},
            }
    return {"label": label, "mates": mates, "rows": rows, "pass": strict,
            "lines": [ln for ln in lines if ln.strip()]}


def compare(ref, cand):
    """(pair, gate, field, ref value, cand value) for every difference."""
    diffs = []
    if cand["mates"] != ref["mates"]:
        diffs.append(("header", "mates", "count", ref["mates"], cand["mates"]))
    if cand["pass"] != ref["pass"]:
        diffs.append(("pass-rate", "both gates", "strict", ref["pass"], cand["pass"]))
    for pair in ref["rows"]:
        if pair not in cand["rows"]:
            diffs.append((pair, "both gates", "row", "present", "missing"))
            continue
        for gate in ("g1", "g2"):
            for field in ("raw", "abs", "min_d"):
                a = ref["rows"][pair][gate][field]
                b = cand["rows"][pair][gate][field]
                if a != b:
                    diffs.append((pair, gate, field, a, b))
    for pair in cand["rows"]:
        if pair not in ref["rows"]:
            diffs.append((pair, "both gates", "row", "not in laptop", "present"))
    if cand["label"] != ref["label"]:
        diffs.append(("header", "bundle", "label", ref["label"], cand["label"]))
    return diffs


def is_numeric(d):
    return d[1:3] != ("bundle", "label")


def table(ref, cand, gate):
    out = ["| pair | laptop raw | node raw | d | laptop abs | node abs | d "
           "| laptop min_d | node min_d | d |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    nd = 0
    for pair in ref["rows"]:
        a = ref["rows"][pair][gate]
        b = cand["rows"].get(pair, {}).get(gate)
        if b is None:
            out.append("| " + pair + " | " + str(a["raw"]) + " | - | - | "
                       + str(a["abs"]) + " | - | - | " + a["min_d"] + " | - | - |")
            nd += 1
            continue
        same = (a["raw"] == b["raw"] and a["abs"] == b["abs"]
                and a["min_d"] == b["min_d"])
        nd += 0 if same else 1
        out.append("| " + pair
                   + " | " + str(a["raw"]) + " | " + str(b["raw"])
                   + " | " + format(b["raw"] - a["raw"], "+d")
                   + " | " + str(a["abs"]) + " | " + str(b["abs"])
                   + " | " + format(b["abs"] - a["abs"], "+d")
                   + " | " + a["min_d"] + " | " + b["min_d"]
                   + " | " + ("" if a["min_d"] == b["min_d"] else "DIFF") + " |")
    return out, nd


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", required=True, help="laptop reference output")
    ap.add_argument("--cand", action="append", default=[], metavar="NAME=PATH",
                    help="a node output to compare against the reference")
    ap.add_argument("--out", required=True, help="markdown report to write")
    args = ap.parse_args(argv)

    ref = load(args.ref)
    cands = []
    for spec in args.cand:
        name, _, path = spec.partition("=")
        if not path:
            ap.error("--cand needs NAME=PATH, got '" + spec + "'")
        cands.append((name, path, load(path)))

    md = ["# Ticket 31 - the laptop's fifteen per-pair lines vs the compute node", ""]
    md.append("Reference (laptop, run 2026-10-27): " + args.ref)
    if ref["pass"]:
        md.append("- bundle label " + ref["label"] + ", mates " + str(ref["mates"])
                  + ", strict pass rate " + str(ref["pass"][0]) + "/"
                  + str(ref["pass"][1]))
    md.append("")
    md.append("raw and abs are integers and are compared exactly. min_d is "
              "compared as printed, because the probe formats it with %.2f and "
              "the laptop recorded nothing finer than that.")
    md.append("")

    failures = 0
    for name, path, cand in cands:
        diffs = compare(ref, cand)
        hard = [d for d in diffs if is_numeric(d)]
        failures += len(hard)
        md.append("## " + name)
        md.append("")
        md.append(path)
        md.append("")
        if not diffs:
            md.append("**EXACT** - header, all fifteen rows and the pass-rate "
                      "line are identical to the laptop.")
        elif not hard:
            md.append("**EXACT on every number** - the only difference is the "
                      "header's bundle label, which is the key the probe was "
                      "asked for, not a measurement.")
        else:
            md.append("**" + str(len(hard)) + " difference(s):**")
            md.append("")
            for pair, gate, field, a, b in diffs:
                where = {"g1": "2.0mm/0.85", "g2": "20deg/0.7"}.get(gate, gate)
                md.append("- " + pair + " " + where + " " + field
                          + ": laptop=" + str(a) + " node=" + str(b))
        md.append("")
        for gate, title in (("g1", "2.0 mm / 0.85 gate"),
                            ("g2", "20.0 deg / 0.7 gate")):
            rows, nd = table(ref, cand, gate)
            md.append("### " + title + " - " + name + " (" + str(nd)
                      + " row(s) differ)")
            md.append("")
            md.extend(rows)
            md.append("")
        md.append("> laptop last line: " + ref["lines"][-1])
        md.append(">")
        md.append("> node last line:   " + cand["lines"][-1])
        md.append("")

    open(args.out, "w", encoding="utf-8").write("\n".join(md) + "\n")

    print("[compare] reference: " + args.ref + " ("
          + str(ref["mates"]) + " mates, " + str(len(ref["rows"])) + " rows)")
    for name, path, cand in cands:
        diffs = compare(ref, cand)
        hard = [d for d in diffs if is_numeric(d)]
        print("[compare] " + name + ": " + str(len(cand["rows"])) + " rows, "
              + str(len(hard)) + " numeric difference(s), "
              + str(len(diffs) - len(hard)) + " label difference(s)")
        for pair, gate, field, a, b in diffs:
            print("[compare]   " + pair + " " + gate + " " + field
                  + ": laptop=" + str(a) + " node=" + str(b))
    print("[compare] report: " + args.out)
    if failures:
        print("[compare] RESULT: " + str(failures)
              + " difference(s) - NOT an exact reproduction")
        return 1
    print("[compare] RESULT: exact reproduction on every number")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
