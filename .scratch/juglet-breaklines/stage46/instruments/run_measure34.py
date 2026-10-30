#!/usr/bin/env python3
"""Measure ticket 46's cells with the frozen measure34 protocol.

The cells of this run are two different inputs, so measure34 must be told which
cloud each piece actually ran on: the even covering for arm E, the released
cloud for the Pot A control.  measure34 reports coverage and fold against that
cloud and never mixes the two.

Layout: measure34.agg() walks <cellroot>/<tag>/<pot>/<piece>/measure/*.tsv, so
each cell is copied into that shape before the measurement runs.  The cell
directories themselves are left untouched (they are the run's record).

Usage:
  run_measure34.py --out OUT --cells OUT/cells-pipeline --cover OUT/cells-covering
                   --spec INSTR/spec46.tsv --corp CORP --ds DS --py PY
Exit 0 on success, 1 if any cell failed to measure, 2 if the aggregate is empty.
"""
import argparse
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
M34 = os.path.join(HERE, "measure34.py")


def log(msg):
    sys.stdout.write("[M46] %s\n" % msg)
    sys.stdout.flush()


def read_cell(path):
    d = {}
    with open(path, "r") as fh:
        for line in fh:
            line = line.rstrip("\n").rstrip("\r")
            if not line or "\t" not in line:
                continue
            k, v = line.split("\t", 1)
            d[k] = v
    return d


def mesh_path(corp, ds, pot, piece):
    if pot == "Pot_A":
        return os.path.join(corp, "Mesh", "%s_Mesh.obj" % piece)
    return os.path.join(ds, "Mesh", pot, "%s_Mesh.obj" % piece)


def cloud_paths(corp, ds, cover, pot, piece):
    rel = None
    if pot == "Pot_A":
        rel = os.path.join(corp, "Point", pot, "%s_Point.pcd" % piece)
    else:
        rel = os.path.join(ds, "Point", pot, "%s_Point.pcd" % piece)
    return {"E": os.path.join(cover, "%s_covering.pcd" % piece), "A": rel}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--cells", required=True)
    ap.add_argument("--cover", required=True)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--corp", required=True)
    ap.add_argument("--ds", required=True)
    ap.add_argument("--py", default=sys.executable)
    a = ap.parse_args(argv)

    spec = {}
    with open(a.spec, "r") as fh:
        head = fh.readline()
        for line in fh:
            p = line.rstrip("\n").rstrip("\r").split("\t")
            if len(p) >= 3:
                spec[(p[0], p[1])] = p[2]

    root = os.path.join(a.out, "measure34")
    tagof = {"E": "covering", "A": "control-released"}

    cells = []
    for name in sorted(os.listdir(a.cells)):
        c = os.path.join(a.cells, name, "cell.tsv")
        if os.path.exists(c):
            cells.append(c)
    if not cells:
        log("no cell.tsv under %s -- nothing to measure" % a.cells)
        return 2

    bad = []
    for c in cells:
        info = read_cell(c)
        pot, piece = info.get("pot", "?"), info.get("piece", "?")
        arm = info.get("arm", "?")
        tag = tagof.get(arm, "arm" + arm)
        src = os.path.dirname(c)
        dst = os.path.join(root, tag, pot, piece)
        os.makedirs(os.path.join(dst, "logs"), exist_ok=True)
        os.makedirs(os.path.join(dst, "surfaces"), exist_ok=True)
        logfile = os.path.join(src, "logs", "mesh.log")
        if os.path.exists(logfile):
            shutil.copy2(logfile, os.path.join(dst, "logs", "mesh.log"))
        sdir = os.path.join(src, "surfaces")
        nsurf = 0
        if os.path.isdir(sdir):
            for f in sorted(os.listdir(sdir)):
                if f.endswith(".ply") and "_Surface_" in f:
                    shutil.copy2(os.path.join(sdir, f), os.path.join(dst, "surfaces", f))
                    nsurf += 1
        mesh = mesh_path(a.corp, a.ds, pot, piece)
        cloud = cloud_paths(a.corp, a.ds, a.cover, pot, piece).get(arm, "")
        log("%s/%s arm %s (%s): %d surface ply, cloud %s" % (pot, piece, arm, tag, nsurf, cloud))
        if not os.path.exists(mesh) or not os.path.exists(cloud):
            log("  MISSING input (mesh=%s cloud=%s) -- skipped" % (os.path.exists(mesh), os.path.exists(cloud)))
            bad.append("%s/%s/%s" % (pot, piece, arm))
            continue
        cmd = [a.py, M34, "cell", "--cell", dst, "--pot", pot, "--piece", piece,
               "--arm", tag, "--mesh", mesh, "--cloud", cloud]
        rc = subprocess.call(cmd)
        if rc != 0:
            log("  measure34 cell rc=%d" % rc)
            bad.append("%s/%s/%s" % (pot, piece, arm))

    aggdir = os.path.join(a.out, "measure34", "agg")
    os.makedirs(aggdir, exist_ok=True)
    rc = subprocess.call([a.py, M34, "agg", "--cellroot", root, "--out", aggdir])
    if rc != 0:
        log("measure34 agg rc=%d" % rc)
        return 1
    pairs = os.path.join(aggdir, "pairs34.tsv")
    nrows = 0
    if os.path.exists(pairs):
        with open(pairs, "r") as fh:
            nrows = max(0, sum(1 for _ in fh) - 1)
    log("pair rows: %d" % nrows)
    if bad:
        log("cells that did not measure:%s" % ("".join("\n  " + b for b in bad)))
        return 1
    if nrows == 0:
        log("no pair rows: no cell grew two surfaces, so there is no pair table")
        return 2
    log("done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
