#!/usr/bin/env python3
"""ticket 48 PART 1 -- run_pair48: the frozen pair statistics for every two-surface cell.

The pair commands are byte-for-byte the stage44 protocol (run_cell44.sh:238-261):
  grow38.py surfacepair --a <piece>_Surface_0.ply --b <piece>_Surface_1.ply --tag <tag> --outdir <cell>/measure
  nest39.py  pair        --a <piece>_Surface_0.ply --b <piece>_Surface_1.ply --tag <tag> --outdir <cell>/measure
run on the surfaces the cells KEPT (the stage is deleted after each cell; surfaces/ is the record).

Honesty line carried from the ticket: a Juglet grown pair sits ~0.2-0.3 mm apart because it is
two layers of ONE face, not the wall's two faces -- the pair table measures that fact, it does
not undo it.  Cells that grew only one surface get a surfaces48.tsv row and no pair row.

Writes: <out>/pairs48.tsv, <out>/nests48.tsv, <out>/surfaces48.tsv, per-cell measure/*.json.
Exit 0 ok; 1 if any pair command failed; 2 if no pair rows AND no cells found.
"""
import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GROW38 = os.path.join(HERE, "grow38.py")
NEST39 = os.path.join(HERE, "nest39.py")

PAIR_COLS = ["n0", "n1", "med_nn", "med_along", "med_across", "med_angle_deg", "coin",
             "med_t_signed", "p05_t_signed", "p95_t_signed", "normal_src_a", "normal_src_b"]
NEST_COLS = ["n0", "n0_distinct", "n1", "n1_distinct", "shared", "shared_over_a",
             "shared_over_b", "shared_over_smaller", "mean_normal_dot", "matched"]
NEST_NA_OK = ["median_point_normal_angle_deg"]


def log(msg):
    sys.stdout.write("[PAIR48] %s\n" % msg)
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


def jget(path, key, na_ok=False):
    try:
        with open(path, "r") as fh:
            j = json.load(fh)
        v = j.get(key)
        if v is None:
            return "na" if na_ok else "na"
        if isinstance(v, float):
            return "%.6f" % v
        return str(v)
    except (OSError, ValueError):
        return "na"


def ply_vertex_count(path):
    try:
        with open(path, "rb") as fh:
            for _ in range(64):
                line = fh.readline()
                if not line:
                    break
                m = re.search(rb"element vertex (\d+)", line)
                if m:
                    return int(m.group(1)).__str__()
    except OSError:
        pass
    return "na"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="run out/ directory")
    ap.add_argument("--cells", required=True, help="out/cells-pipeline of this run")
    ap.add_argument("--py", default=sys.executable, help="python that runs grow38/nest39")
    a = ap.parse_args(argv)

    cells = []
    for name in sorted(os.listdir(a.cells)):
        c = os.path.join(a.cells, name, "cell.tsv")
        if os.path.exists(c):
            cells.append(c)
    if not cells:
        log("no cell.tsv under %s -- nothing to pair" % a.cells)
        return 2

    pairs_path = os.path.join(a.out, "pairs48.tsv")
    nests_path = os.path.join(a.out, "nests48.tsv")
    surf_path = os.path.join(a.out, "surfaces48.tsv")
    with open(pairs_path, "w", encoding="utf-8", newline="") as fh:
        fh.write("\t".join(["pot", "piece", "arm"] + PAIR_COLS) + "\n")
    with open(nests_path, "w", encoding="utf-8", newline="") as fh:
        fh.write("\t".join(["pot", "piece", "arm"] + NEST_COLS + NEST_NA_OK) + "\n")
    with open(surf_path, "w", encoding="utf-8", newline="") as fh:
        fh.write("pot\tpiece\tarm\toutcome\tsurf0_points\tsurf1_points\tsurf0_ply_bytes\tsurf1_ply_bytes\tnote\n")

    bad = []
    n_pair = 0
    for c in cells:
        info = read_cell(c)
        pot, piece, arm = info.get("pot", "?"), info.get("piece", "?"), info.get("arm", "?")
        disp = {"V": "formula"}.get(arm, "arm" + arm)
        cell = os.path.dirname(c)
        sdir = os.path.join(cell, "surfaces")
        s0 = os.path.join(sdir, "%s_Surface_0.ply" % piece)
        s1 = os.path.join(sdir, "%s_Surface_1.ply" % piece)
        out0, out1 = info.get("status_outcome", ""), info.get("status_surf1_points", "")
        if os.path.isfile(s0) and os.path.isfile(s1):
            tag = "%s_arm%s" % (piece, arm)
            mdir = os.path.join(cell, "measure")
            os.makedirs(mdir, exist_ok=True)
            rc1 = subprocess.call([a.py, GROW38, "surfacepair", "--a", s0, "--b", s1,
                                   "--tag", tag, "--outdir", mdir])
            rc2 = subprocess.call([a.py, NEST39, "pair", "--a", s0, "--b", s1,
                                   "--tag", tag, "--outdir", mdir])
            if rc1 == 0 and rc2 == 0:
                pj = os.path.join(mdir, "surfacepair_%s.json" % tag)
                nj = os.path.join(mdir, "nest_%s.json" % tag)
                with open(pairs_path, "a", encoding="utf-8", newline="") as fh:
                    fh.write("\t".join([pot, piece, disp] + [jget(pj, k) for k in PAIR_COLS]) + "\n")
                with open(nests_path, "a", encoding="utf-8", newline="") as fh:
                    fh.write("\t".join([pot, piece, disp] + [jget(nj, k) for k in NEST_COLS]
                                       + [jget(nj, NEST_NA_OK[0], na_ok=True)]) + "\n")
                n_pair += 1
                log("%s/%s: paired (surf0 %s pts, surf1 %s pts)" % (
                    pot, piece, ply_vertex_count(s0), ply_vertex_count(s1)))
                note = "two surfaces: pair row written"
            else:
                log("%s/%s: WARN pair commands rc surfacepair=%d nest=%d" % (pot, piece, rc1, rc2))
                bad.append("%s/%s/%s" % (pot, piece, arm))
                note = "pair command failed (rc %d/%d)" % (rc1, rc2)
        else:
            log("%s/%s: did not grow two surfaces (Surface_0=%s Surface_1=%s) -- no pair row" % (
                pot, piece, os.path.isfile(s0), os.path.isfile(s1)))
            note = "no pair: Surface_0=%s Surface_1=%s" % (os.path.isfile(s0), os.path.isfile(s1))
        with open(surf_path, "a", encoding="utf-8", newline="") as fh:
            fh.write("\t".join([
                pot, piece, disp, out0 or "na",
                ply_vertex_count(s0) if os.path.isfile(s0) else "-",
                ply_vertex_count(s1) if os.path.isfile(s1) else "-",
                str(os.path.getsize(s0)) if os.path.isfile(s0) else "-",
                str(os.path.getsize(s1)) if os.path.isfile(s1) else "-",
                note]) + "\n")

    log("pair rows: %d of %d cells (tables: %s, %s, %s)" % (n_pair, len(cells), pairs_path, nests_path, surf_path))
    if bad:
        log("pair commands that failed:%s" % ("".join("\n  " + b for b in bad)))
        return 1
    if n_pair == 0:
        log("no pair rows: no cell grew two surfaces, so there is no pair table (reported, not fatal)")
    log("done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
