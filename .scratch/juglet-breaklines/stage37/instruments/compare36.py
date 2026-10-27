#!/usr/bin/env python3
"""ticket 34 follow-up -- the checks the first grid either could not finish or got wrong, run
over the cells that grid already wrote. The pipeline itself is not run again here.

  defaults2   byte identity and sorted-point-set identity of every surface written by the arms
              that ran with no switches: AO (the pre-change binary) against A (this commit), and
              A against A2 (the same arm twice = the piece's own run-to-run spread). Also the
              segmentation lines of those arms, so anything that differs can be named.
  lines34     every [NORMAL-33] / [PAPER-234] / [RETRY-23] / [FLOOR-23] / [STATUS-23] /
              [SPLITTER-234] line each cell printed, one row per line.
  counts34    the per-cell geometry record each cell wrote BEFORE it deleted its stage and rung
              dump (per-extension file counts and bytes).

The pair statistic is deliberately NOT reimplemented here. pair_ref30.py is ticket 30's
reference implementation, copied unchanged; run it over the same cell tree with
  pair_ref30.py <cellroot> [armcells.tsv]
and it writes <cellroot>/measure30.tsv. This file used to carry its own copy and that copy had
the across component built from the ABSOLUTE along projection, which is not a component of the
step; the numbers it produced are in results/pairs34.tsv and are superseded by measure30.tsv.

usage:
  compare34.py defaults2 --cells <cellroot> [--cells <cellroot> ...] --out <tsv>
  compare34.py lines34   --cells <cellroot> [--cells ...] --out <tsv>
  compare34.py counts34  --cells <cellroot> [--cells ...] --out <tsv>
  compare34.py selftest
"""
import argparse
import glob
import hashlib
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import measure34 as m34

DEFAULT_ARMS = (("AO", "A"), ("A", "A2"))
SEG = ("[RETRY-23]", "[STATUS-23]", "[FLOOR-23]", "[PAPER-234] pass", "pass ", "[SPLITTER-234]")
KINDS = ("[SPACING-22]", "[COUNT-22]", "[SWITCH-23]", "[NORMAL-33]", "[NORMAL-34]",
         "[PAPER-234]", "[RETRY-23]", "[FLOOR-23]", "[STATUS-23]", "[SPLITTER-234]")


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def cells(cellroot):
    """arm -> pot -> piece -> cell dir"""
    out = {}
    for path in glob.glob(os.path.join(cellroot, "*", "*", "*")):
        parts = os.path.relpath(path, cellroot).split(os.sep)
        if len(parts) != 3 or not os.path.isdir(path):
            continue
        arm, pot, piece = parts
        out.setdefault(arm, {}).setdefault(pot, {})[piece] = path
    return out


def surfaces(cell):
    return os.path.join(cell, "surfaces")


def sorted_rows(d, cols):
    keys = [d[c] for c in cols]
    order = np.lexsort(tuple(reversed(keys)))
    return np.stack([d[c][order] for c in cols], axis=1)


def compare_file(fa, fb):
    """byte identity, then the same points after sorting the rows."""
    row = {"present_a": int(os.path.isfile(fa)), "present_b": int(os.path.isfile(fb)),
           "bytes_a": os.path.getsize(fa) if os.path.isfile(fa) else 0,
           "bytes_b": os.path.getsize(fb) if os.path.isfile(fb) else 0,
           "md5_a": "", "md5_b": "", "md5_equal": 0, "points_a": 0, "points_b": 0,
           "sorted_identical": 0, "max_abs_diff": 0.0, "detail": ""}
    if not (row["present_a"] and row["present_b"]):
        row["detail"] = "a surface written by only one of the two arms"
        return row
    row["md5_a"] = md5(fa)
    row["md5_b"] = md5(fb)
    row["md5_equal"] = int(row["md5_a"] == row["md5_b"])
    try:
        da = m34.read_ply(fa)
        db = m34.read_ply(fb)
    except Exception as exc:                                    # noqa: BLE001
        row["detail"] = "unreadable: %s" % exc
        return row
    cols = [c for c in ("x", "y", "z", "nx", "ny", "nz", "normal_x", "normal_y", "normal_z",
                        "curvature") if c in da and c in db]
    row["points_a"] = int(len(da[cols[0]])) if cols else 0
    row["points_b"] = int(len(db[cols[0]])) if cols else 0
    row["detail"] = "columns compared: %s" % ",".join(cols)
    if not cols or row["points_a"] != row["points_b"] or row["points_a"] == 0:
        return row
    sa = sorted_rows(da, cols)
    sb = sorted_rows(db, cols)
    row["max_abs_diff"] = float(np.max(np.abs(sa - sb))) if sa.size else 0.0
    row["sorted_identical"] = int(np.array_equal(sa, sb))
    return row


def cmd_defaults(a):
    trees = [cells(c) for c in a.cells]
    rows = []
    for arm_a, arm_b in DEFAULT_ARMS:
        pieces = {}
        for t in trees:
            for arm in (arm_a, arm_b):
                for pot, d in t.get(arm, {}).items():
                    for piece, cell in d.items():
                        pieces.setdefault((pot, piece), {})[arm] = cell
        for (pot, piece), have in sorted(pieces.items()):
            if arm_a not in have or arm_b not in have:
                continue
            fa = sorted(os.path.basename(p) for p in glob.glob(os.path.join(surfaces(have[arm_a]), "*.ply")))
            fb = sorted(os.path.basename(p) for p in glob.glob(os.path.join(surfaces(have[arm_b]), "*.ply")))
            for name in sorted(set(fa) | set(fb)):
                r = compare_file(os.path.join(surfaces(have[arm_a]), name),
                                 os.path.join(surfaces(have[arm_b]), name))
                r.update({"check": "surface", "arm_a": arm_a, "arm_b": arm_b,
                          "pot": pot, "piece": piece, "file": name})
                rows.append(r)
            la = os.path.join(have[arm_a], "logs", "lines36.log")
            lb = os.path.join(have[arm_b], "logs", "lines36.log")
            differ = 0
            first = ""
            if os.path.isfile(la) and os.path.isfile(lb):
                sa = [l.rstrip("\n") for l in open(la) if any(k in l for k in SEG)]
                sb = [l.rstrip("\n") for l in open(lb) if any(k in l for k in SEG)]
                sa = [l for l in sa if "minPairs=" not in l]
                sb = [l for l in sb if "minPairs=" not in l]
                if sa != sb:
                    differ = sum(1 for x, y in zip(sa, sb) if x != y) + abs(len(sa) - len(sb))
                    for x, y in zip(sa, sb):
                        if x != y:
                            first = "A: %s | B: %s" % (x, y)
                            break
                rows.append({"check": "segmentation_lines", "arm_a": arm_a, "arm_b": arm_b,
                             "pot": pot, "piece": piece, "file": "logs/lines36.log",
                             "present_a": 1, "present_b": 1, "bytes_a": 0, "bytes_b": 0,
                             "md5_a": "", "md5_b": "", "md5_equal": 0,
                             "points_a": len(sa), "points_b": len(sb),
                             "sorted_identical": int(differ == 0), "max_abs_diff": 0.0,
                             "detail": ("%d differing lines%s" % (differ, ("; " + first) if first else ""))})
            else:
                rows.append({"check": "segmentation_lines", "arm_a": arm_a, "arm_b": arm_b,
                             "pot": pot, "piece": piece, "file": "logs/lines36.log",
                             "present_a": int(os.path.isfile(la)), "present_b": int(os.path.isfile(lb)),
                             "bytes_a": 0, "bytes_b": 0, "md5_a": "", "md5_b": "", "md5_equal": 0,
                             "points_a": 0, "points_b": 0, "sorted_identical": 0,
                             "max_abs_diff": 0.0, "detail": "no lines36.log"})
    cols = ["check", "arm_a", "arm_b", "pot", "piece", "file", "present_a", "present_b",
            "bytes_a", "bytes_b", "md5_a", "md5_b", "md5_equal", "points_a", "points_b",
            "sorted_identical", "max_abs_diff", "detail"]
    with open(a.out, "w") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(str(r.get(c, "")) for c in cols) + "\n")
    bad = [r for r in rows if r["check"] == "surface" and (not r["present_a"] or not r["present_b"]
                                                          or not r["md5_equal"]
                                                          or not r["sorted_identical"])]
    seg = [r for r in rows if r["check"] == "segmentation_lines" and not r["sorted_identical"]]
    print("[DEFAULTS2] surface rows=%d, not identical=%d; segmentation comparisons=%d, differing=%d"
          % (len([r for r in rows if r["check"] == "surface"]), len(bad),
             len([r for r in rows if r["check"] == "segmentation_lines"]), len(seg)))
    for r in bad[:12]:
        print("[DEFAULTS2] %s %s %s %s md5_equal=%s sorted_identical=%s detail=%s"
              % (r["arm_a"], r["arm_b"], r["piece"], r["file"], r["md5_equal"],
                 r["sorted_identical"], r["detail"]))
    for r in seg[:6]:
        print("[DEFAULTS2] seg %s %s %s %s" % (r["arm_a"], r["arm_b"], r["piece"], r["detail"]))
    return 0


def cmd_lines(a):
    rows = []
    for root in a.cells:
        for arm, pots in sorted(cells(root).items()):
            for pot, pieces in sorted(pots.items()):
                for piece, cell in sorted(pieces.items()):
                    log = os.path.join(cell, "logs", "lines36.log")
                    if not os.path.isfile(log):
                        continue
                    for line in open(log):
                        s = line.rstrip("\n")
                        if any(s.startswith(k) or (k in s and k.startswith("[")) for k in KINDS):
                            kind = next((k for k in KINDS if k in s), "other")
                            rows.append((arm, pot, piece, kind, s))
    with open(a.out, "w") as f:
        f.write("arm\tpot\tpiece\tkind\tline\n")
        for r in rows:
            f.write("\t".join(r) + "\n")
    print("[LINES34] rows=%d" % len(rows))
    return 0


def cmd_counts(a):
    rows = []
    for root in a.cells:
        for arm, pots in sorted(cells(root).items()):
            for pot, pieces in sorted(pots.items()):
                for piece, cell in sorted(pieces.items()):
                    p = os.path.join(cell, "logs", "geometry_counts.tsv")
                    if not os.path.isfile(p):
                        continue
                    files = bytes_ = 0
                    for line in open(p):
                        s = line.rstrip("\n")
                        if not s or s.startswith("#"):
                            continue
                        parts = s.split("\t")
                        if parts[0] == "path" or parts[0] == "frac":
                            continue
                        if parts[0].endswith("dump_bytes") or parts[0].startswith("after:"):
                            continue
                        if len(parts) >= 4:
                            try:
                                files += int(parts[2])
                                bytes_ += int(parts[3])
                            except ValueError:
                                continue
                            rows.append((arm, pot, piece, parts[0], parts[1], parts[2], parts[3]))
                    rows.append((arm, pot, piece, "TOTAL", "all", str(files), str(bytes_)))
    with open(a.out, "w") as f:
        f.write("arm\tpot\tpiece\tpath\text\tfiles\tbytes\n")
        for r in rows:
            f.write("\t".join(r) + "\n")
    tot = [r for r in rows if r[3] == "TOTAL"]
    print("[COUNTS34] cells=%d files=%d bytes=%d" % (len(tot), sum(int(r[5]) for r in tot),
                                                     sum(int(r[6]) for r in tot)))
    return 0


def selftest():
    import tempfile
    tmp = tempfile.mkdtemp(prefix="c34-")
    ok = 0
    body = "\n".join(["ply", "format ascii 1.0", "element vertex 2",
                      "property float x", "property float y", "property float z",
                      "property float nx", "property float ny", "property float nz", "end_header",
                      "0 0 0 0 0 1", "1 0 0 0 0 1", ""])
    p = os.path.join(tmp, "a.ply")
    open(p, "w").write(body)
    r = compare_file(p, p)
    ok += r["md5_equal"] and r["sorted_identical"] and r["points_a"] == 2
    print("[SELFTEST] ok   identical file md5_equal=%s sorted_identical=%s" % (r["md5_equal"], r["sorted_identical"]))
    q = os.path.join(tmp, "b.ply")
    open(q, "w").write(body.replace("1 0 0 0 0 1", "1 0 0.5 0 0 1"))
    r = compare_file(p, q)
    ok += (not r["sorted_identical"]) and abs(r["max_abs_diff"] - 0.5) < 1e-12
    print("[SELFTEST] ok   one coordinate moved 0.5: sorted_identical=%s max_abs_diff=%.3f"
          % (r["sorted_identical"], r["max_abs_diff"]))
    s = os.path.join(tmp, "c.ply")
    swapped = (body.replace("0 0 0 0 0 1", "TMPROW")
                   .replace("1 0 0 0 0 1", "0 0 0 0 0 1")
                   .replace("TMPROW", "1 0 0 0 0 1"))
    open(s, "w").write(swapped)
    r = compare_file(p, s)
    ok += r["sorted_identical"] and not r["md5_equal"]
    print("[SELFTEST] ok   two rows swapped: sorted_identical=%s md5_equal=%s"
          % (r["sorted_identical"], r["md5_equal"]))
    print("[SELFTEST] %s" % ("PASS" if ok == 3 else "FAIL %d of 3" % ok))
    return 0 if ok == 3 else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("defaults2", "lines34", "counts34"):
        p = sub.add_parser(name)
        p.add_argument("--cells", action="append", required=True)
        p.add_argument("--out", required=True)
    sub.add_parser("selftest")
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "defaults2":
        return cmd_defaults(a)
    if a.cmd == "lines34":
        return cmd_lines(a)
    return cmd_counts(a)


if __name__ == "__main__":
    sys.exit(main())
