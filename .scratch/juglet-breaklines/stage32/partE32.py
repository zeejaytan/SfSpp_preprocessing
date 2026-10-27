#!/usr/bin/env python3
"""Ticket 32, part E -- the pipeline's own answer, assembled.

Joins four things, and adds nothing of its own arithmetic:

  cells23.tsv     ticket 23's run_cell23.sh, run verbatim: every [FLOOR-23] and [STATUS-23]
                  line the pipeline printed, the exit code and the elapsed time.
  coverage23.tsv  ticket 23's coverage23.py, run verbatim: for any surface the pipeline wrote,
                  its point count, bbox extent, bbox diagonal and the fraction of the piece's
                  own cloud within 2 mm of it.
  mesh.log        the cell's own log, for every "Number of clusters is equal to N" the
                  pipeline printed (interior and exterior are clustered separately, so there
                  can be more than one) and for the count of [RETRY-23] lines.
  the cloud       the piece's mm cloud, read with io32, for its own point count and extent.

Nothing here decides whether a surviving surface is a face.  Numbers only.

usage: partE32.py --cells <cellroot> --dataset <Dataset> --out <partE32.tsv>
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import io32  # noqa: E402
from measure_arm23 import read_cells  # noqa: E402

COLS = ["tag", "pot", "piece", "floor_requested", "arm", "mesh_exit", "elapsed_s",
        "npts", "retries", "clusters", "sizes", "outcome", "floor", "floor_from", "capped",
        "surf0", "surf1", "surf0_points", "surf1_points",
        "n_surf", "n0", "n1", "diag0_mm", "cov0_2mm", "diag1_mm", "cov1_2mm",
        "cov_union_2mm", "cloud_points", "cloud_extent_mm",
        "clusters_lines", "n_retry_lines",
        "switch_line", "floor_line", "single_line", "status_line",
        "spacing_line", "count_line", "warn_missing", "cell_dir"]

CL_RE = re.compile(r"Number of clusters is equal to (\d+)")


def clean(v):
    """A tab inside a verbatim pipeline line would break the table; nothing else is touched."""
    return str(v).replace("\t", " ").replace("\n", " ")


def floor_of(envs):
    for tok in envs.split():
        if tok.startswith("SFS_FLOOR_CEILING="):
            return tok.split("=", 1)[1]
    return "NA"


def arm_of(envs):
    return "single" if "SFS_SINGLE_CLUSTER=write" in envs else "plain"


def cloud_of(dataset, pot, piece):
    return os.path.join(dataset, "Point", pot, piece + "_Point.pcd")


def log_facts(cell_dir):
    """Every cluster count the pipeline printed, and how many retry lines it printed."""
    p = os.path.join(cell_dir, "logs", "mesh.log")
    if not os.path.exists(p):
        return "na", "na"
    nums, retry = [], 0
    with open(p, "r", errors="replace") as fh:
        for line in fh:
            m = CL_RE.search(line)
            if m:
                nums.append(m.group(1))
            if "[RETRY-23]" in line:
                retry += 1
    return ("|".join(nums) if nums else "none"), retry


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", required=True)
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    cells = read_cells(os.path.join(a.cells, "cells23.tsv"))
    cov = {}
    cpath = os.path.join(a.cells, "coverage23.tsv")
    if os.path.exists(cpath):
        for r in read_cells(cpath):
            cov[(r["tag"], r["pot"], r["piece"])] = r
    ccloud = {}
    rows = []
    for r in cells:
        pot, piece, tag = r["pot"], r["piece"], r["tag"]
        c = cov.get((tag, pot, piece), {})
        cell_dir = os.path.join(a.cells, tag, pot, piece)
        cl_line, n_retry = log_facts(cell_dir)
        if (pot, piece) not in ccloud:
            try:
                cl = io32.read_pcd(cloud_of(a.dataset, pot, piece))
                ccloud[(pot, piece)] = (cl["n_points"], io32.extent_mm(cl["xyz"]))
            except Exception as exc:  # a missing cloud is recorded, not hidden
                ccloud[(pot, piece)] = ("na", "na")
                print("[E32] cloud read failed %s/%s: %s" % (pot, piece, exc))
        cn, ce = ccloud[(pot, piece)]
        vals = [tag, pot, piece, floor_of(r.get("envs", "")), arm_of(r.get("envs", "")),
                r.get("mesh_exit", "NA"), r.get("elapsed_s", "NA"), r.get("npts", "NA"),
                r.get("retries", "NA"), r.get("clusters", "NA"), r.get("sizes", "NA"),
                r.get("outcome", "NA"), r.get("floor", "NA"), r.get("floor_from", "NA"),
                r.get("capped", "NA"), r.get("surf0", "NA"), r.get("surf1", "NA"),
                r.get("surf0_points", "NA"), r.get("surf1_points", "NA"),
                c.get("n_surf", "na"), c.get("n0", "na"), c.get("n1", "na"),
                c.get("diag0", "na"), c.get("cov0_2mm", "na"), c.get("diag1", "na"),
                c.get("cov1_2mm", "na"), c.get("cov_union_2mm", "na"),
                cn, ("%.6f" % ce) if isinstance(ce, float) else ce,
                cl_line, n_retry,
                r.get("switch", "NA"), r.get("floor_line", "NA"), r.get("single", "NA"),
                r.get("status", "NA"), r.get("spacing", "NA"), r.get("count", "NA"),
                r.get("warn_missing", "NA"), cell_dir]
        rows.append([clean(v) for v in vals])
    with open(a.out, "w") as fh:
        fh.write("\t".join(COLS) + "\n")
        for v in rows:
            fh.write("\t".join(v) + "\n")
    nsurf = sum(1 for v in rows if v[19] not in ("0", "na"))
    print("[E32] wrote %s: %d rows, %d cells wrote at least one surface" % (a.out, len(rows), nsurf))
    for v in rows:
        print("[E32] %s %s/%s floor=%s %s exit=%s outcome=%s clusters=%s sizes=%s "
              "clusters_lines=%s surf=%s/%s cov0=%s diag0=%s"
              % (v[0], v[1], v[2], v[3], v[4], v[5], v[11], v[9], v[10], v[29],
                 v[15], v[16], v[23], v[22]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
