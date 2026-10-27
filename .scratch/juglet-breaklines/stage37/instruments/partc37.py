#!/usr/bin/env python3
"""Part C of ticket 37: the region-size distribution BEFORE any floor, from the python replica.

The pipeline passes the floor into growPaper234 (mesh_processing_headless.cpp:3647), so it cannot
report the regions it discarded; replica37.py grows from the pipeline's own rung-2 dump and is the
only instrument that sees them. This script only joins and formats what the job already wrote --
it computes no geometry.

Columns the ticket names, per group of cells:
  npts, regions (before any floor), largest, how many regions reach >=10 / >=20 / >=30 / >=50 points,
  how many reach >=1% / 5% / 10% of the cloud, angle refusals per point, depth of the largest region.

Groups (a cell's tag decides, see run.json of the phase-2 run):
  N = adaptive spacing + honest nearest-carry normals  (arms NA and PDN)  -- the main column, part D's config
  F = fixed 0.6 mm + honest nearest-carry normals      (arm FX)           -- spacing is the only difference
  R = adaptive spacing + the pipeline's own re-estimated normals (arm RA) -- the new default configuration
"""

import argparse
import glob
import json
import os
import sys

HEADER = ["config", "piece", "npts", "regions_before", "largest", "ge10", "ge20", "ge30", "ge50",
          "ge_pct1", "ge_pct5", "ge_pct10", "largest_depth", "fail_angle", "af_per_point",
          "largest_pops", "floor", "survivors", "sizes_ge_floor", "validation", "pipeline_clusters"]

GROUPS = [("N", "adaptive+nearest"), ("F", "fixed0.6+nearest"), ("R", "adaptive+reestimated")]


def group_of(tag):
    t = tag.upper()
    if t in ("NA", "PDN") or t.startswith("PDN") or t.startswith("NA"):
        return "N"
    if t.startswith("FX"):
        return "F"
    if t.startswith("RA"):
        return "R"
    return None


def read_rows(rundir):
    """Every replica.tsv the job left, wherever it left it. Header lines start with '#'."""
    paths = []
    flat = os.path.join(rundir, "replica37.tsv")
    flat2 = os.path.join(rundir, "out", "replica37.tsv")
    for cand in (flat2, flat):
        if os.path.exists(cand):
            paths.append(cand)
            break
    if not paths:
        # no flattened table: fall back to the per-cell files the job left behind
        paths += sorted(glob.glob(os.path.join(rundir, "**", "replica.tsv"), recursive=True))
        paths += sorted(glob.glob(os.path.join(rundir, "**", "replica37.tsv"), recursive=True))
    seen, rows, bad = set(), [], []
    for p in paths:
        if os.path.realpath(p) in seen:
            continue
        seen.add(os.path.realpath(p))
        with open(p) as f:
            for line in f:
                line = line.rstrip("\n")
                if not line or line.startswith("#"):
                    continue
                parts = line.split("\t")
                if len(parts) != len(HEADER):
                    bad.append("%s: %d columns" % (p, len(parts)))
                    continue
                rows.append(dict(zip(HEADER, parts)))
    return rows, bad


def as_int(row, key):
    try:
        return int(row[key])
    except Exception:
        return -1


def long_table(rows):
    out = []
    for r in rows:
        g = group_of(r["config"])
        if g is None:
            continue
        out.append({"group": g, "config": r["config"], "piece": r["piece"],
                    "npts": as_int(r, "npts"), "regions": as_int(r, "regions_before"),
                    "largest": as_int(r, "largest"), "ge10": as_int(r, "ge10"),
                    "ge20": as_int(r, "ge20"), "ge30": as_int(r, "ge30"),
                    "ge50": as_int(r, "ge50"), "ge_pct1": as_int(r, "ge_pct1"),
                    "ge_pct5": as_int(r, "ge_pct5"), "ge_pct10": as_int(r, "ge_pct10"),
                    "largest_depth": as_int(r, "largest_depth"),
                    "fail_angle": as_int(r, "fail_angle"),
                    "af_per_point": r["af_per_point"], "largest_pops": as_int(r, "largest_pops"),
                    "floor": as_int(r, "floor"), "survivors": as_int(r, "survivors"),
                    "sizes_ge_floor": r["sizes_ge_floor"], "validation": r["validation"],
                    "pipeline_clusters": as_int(r, "pipeline_clusters")})
    out.sort(key=lambda d: (d["piece"], ["N", "F", "R"].index(d["group"])))
    return out


LONG_COLS = ["piece", "group", "config", "npts", "regions", "largest", "ge10", "ge20", "ge30", "ge50",
             "ge_pct1", "ge_pct5", "ge_pct10", "af_per_point", "fail_angle", "largest_depth",
             "largest_pops", "floor", "survivors", "sizes_ge_floor", "validation", "pipeline_clusters"]


def write_tsv(path, cols, rows):
    with open(path, "w", newline="\n") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(str(r[c]) for c in cols) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, help="phase-2 run directory (the job's out/)")
    ap.add_argument("--out", default=None, help="directory for partc37.tsv / partc37_wide.tsv")
    a = ap.parse_args(argv)
    outdir = a.out or os.path.join(a.run, "out")
    rows, bad = read_rows(a.run)
    long = long_table(rows)
    if not long:
        print("[PARTC] no replica rows found under %s" % a.run)
        return 2
    for b in bad:
        print("[PARTC] skipped a malformed row: %s" % b)
    os.makedirs(outdir, exist_ok=True)
    write_tsv(os.path.join(outdir, "partc37.tsv"), LONG_COLS, long)

    # wide: one row per piece, the three groups side by side
    by = {}
    for r in long:
        by.setdefault(r["piece"], {})[r["group"]] = r
    metrics = [("npts", "npts"), ("regions", "regions"), ("largest", "largest"),
               ("ge10", "n>=10"), ("ge20", "n>=20"), ("ge30", "n>=30"), ("ge50", "n>=50"),
               ("ge_pct1", "n>=1%"), ("ge_pct5", "n>=5%"), ("ge_pct10", "n>=10%"),
               ("af_per_point", "ang/pt"), ("largest_depth", "depth"), ("floor", "floor"),
               ("validation", "verdict")]
    cols = ["piece"]
    for g, _label in GROUPS:
        cols += ["%s_%s" % (g, m) for m, _ in metrics]
    wide = []
    for piece in sorted(by):
        row = {"piece": piece}
        for g, _label in GROUPS:
            r = by[piece].get(g)
            for m, _ in metrics:
                row["%s_%s" % (g, m)] = "" if r is None else r[m]
        wide.append(row)
    write_tsv(os.path.join(outdir, "partc37_wide.tsv"), cols, wide)

    # the ticket's table, printed
    print("")
    print("PART C - regions before any floor. N = adaptive+nearest (the part D config), "
          "F = fixed 0.6 mm+nearest, R = adaptive+re-estimated (the new default config).")
    print("")
    hdr = "| piece | grp | npts | regions | largest | >=10 | >=20 | >=30 | >=50 | >=1% | >=5% | >=10% | ang/ref pt | depth | floor | survivors | verdict |"
    print(hdr)
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in long:
        print("| %s | %s | %d | %d | %d | %d | %d | %d | %d | %d | %d | %d | %s | %d | %d | %d | %s |"
              % (r["piece"], r["group"], r["npts"], r["regions"], r["largest"], r["ge10"], r["ge20"],
                 r["ge30"], r["ge50"], r["ge_pct1"], r["ge_pct5"], r["ge_pct10"],
                 r["af_per_point"], r["largest_depth"], r["floor"], r["survivors"],
                 r["validation"]))

    # the re-validation verdict, stated once, explicitly
    print("")
    vals = {}
    for r in long:
        vals.setdefault(r["validation"], []).append("%s/%s" % (r["piece"], r["group"]))
    for v in sorted(vals):
        print("[PARTC] verdict %s: %s" % (v, ", ".join(sorted(vals[v]))))
    gate = [r for r in long if r["group"] == "R"]
    if gate:
        ok = all(r["validation"] == "MATCH" for r in gate)
        near = all(r["validation"] in ("MATCH", "NEAR") for r in gate)
        if ok:
            print("[PARTC] REPLICA VALIDATED: every gate cell (group R, the new default configuration) "
                  "reproduces the pipeline's own cluster sizes exactly")
        elif near:
            print("[PARTC] REPLICA VALIDATED (with a tolerance): every gate cell within max(2 points, 10%); "
                  "the exact deltas are in the per-cell replica json")
        else:
            print("[PARTC] REPLICA UNVALIDATED: at least one gate cell does not reproduce the pipeline's "
                  "cluster sizes; report the replica numbers as unvalidated")
    else:
        print("[PARTC] no group R rows: the replica is UNVALIDATED in this run")
    return 0


if __name__ == "__main__":
    sys.exit(main())
