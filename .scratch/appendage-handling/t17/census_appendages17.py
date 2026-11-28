#!/usr/bin/env python3
"""Ticket 17 deliverable 1: attached-appendage census over the 157 canonical t09 pieces.

Per piece: cluster sizes from the t09 mesh.log [RETRY-23] line, S0/S1 point
counts from the PLY headers, mesh vertices covered within 2.0 mm of S0|S1,
fraction of S1 further than 5.0 mm from the Author wall, and the rank-0 /
best-of-3 t09 axis angle against the ground-truth axis.

READ-ONLY on the corpus and on the canonical t09 run.
"""
import argparse
import json
import os
import re
import sys
from multiprocessing import Pool

import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import t17_common as tc  # noqa: E402

HEADER = [
    "stem", "vessel", "npts_cloud", "clusters_total", "c1_pts", "c2_pts", "c3_pts",
    "c3_frac", "s0_pts", "s1_pts", "s1_over_s0", "mesh_verts",
    "mesh_covered_2mm_pct", "mesh_uncovered_verts", "s1_off_author_5mm_pct",
    "gt_rank0_deg", "gt_best_deg", "flag_reason",
]
RE_RETRY = re.compile(
    r"\[RETRY-23\] piece=(\S+) retry=\d+ npts=(\d+) clusters_pre=\d+ clusters=(\d+) sizes=([\d,]*)")
COVER_MM = 2.0
AUTHOR_MM = 5.0
C3_FRAC = 0.05
C3_PTS = 2000
S1_LOBE_PCT = 5.0
ASYM = 1.35
UNCOVERED_PCT = 82.0


def parse_clusters(stem):
    """(npts, clusters_total, [sizes desc]) from the single [RETRY-23] line."""
    path = tc.mesh_log(stem)
    txt = open(path, "r", errors="replace").read()
    hits = RE_RETRY.findall(txt)
    if not hits:
        raise RuntimeError("no [RETRY-23] line in %s" % path)
    _, npts, nclust, sizes = hits[-1]
    sizes = sorted((int(s) for s in sizes.split(",") if s), reverse=True)
    return int(npts), int(nclust), sizes


# the five stems the paper keeps out of its set: their Author walls exist but are
# not the released answer, so the ticket asks for the -1.0 sentinel there
AUTHOR_EXCLUDED = {"Pot_F_Piece_07", "Pot_I_Piece_28", "Pot_I_Piece_29",
                   "Pot_I_Piece_30", "Pot_J_Piece_12"}


def pct(frac, total):
    return float(100.0 * frac / total) if total else float("nan")


def gather(stem):
    d = tc.geom_dir(stem)
    s0 = tc.read_wall(os.path.join(d, stem + ".S0"), with_normals=False)[0:3]
    s1 = tc.read_wall(os.path.join(d, stem + ".S1"), with_normals=False)[0:3]
    if tc.is_jug(stem):
        s0 = s0 / tc.JUG_ROWS
        s1 = s1 / tc.JUG_ROWS
    n0, n1 = int(s0.shape[1]), int(s1.shape[1])

    npts, nclust, sizes = parse_clusters(stem)
    c = (sizes + [0, 0, 0])[0:3]
    c3_frac = c[2] / float(max(npts, 1))

    # the Juglet mesh in Dataset/Mesh/Juglet is already in 1x mm, like the pots;
    # only the 3x walls above need dividing, or coverage comes out 0% for every juglet
    verts = tc.read_obj_vertices(tc.mesh_obj(stem))
    tree = cKDTree(np.hstack([s0, s1]).T) if (n0 + n1) else None
    if tree is not None and verts.shape[0]:
        dmin = tree.query(verts, k=1)[0]
        covered = dmin <= COVER_MM
    else:
        dmin = np.zeros(0)
        covered = np.zeros(0, dtype=bool)
    cov_pct = pct(float(covered.sum()), verts.shape[0])
    uncov = int((~covered).sum()) if verts.shape[0] else 0

    if tc.is_jug(stem) or stem in AUTHOR_EXCLUDED:
        author_pct = -1.0
    else:
        aw = tc.author_wall(stem)
        if os.path.isfile(aw) and n1:
            w1 = tc.read_wall(aw, with_normals=False)[0:3]
            dd = cKDTree(w1.T).query(s1.T, k=1)[0]
            author_pct = pct(float((dd > AUTHOR_MM).sum()), n1)
        else:
            author_pct = -1.0

    gt = tc.gt_axis(stem)
    v = tc.read_axis_lines(tc.axis09_path(stem))
    if gt is not None and v.shape[1] > 0:
        pos = v[3:6].T / (tc.JUG_ROWS if tc.is_jug(stem) else 1.0)
        dirs = v[0:3].T
        rank0 = tc.line_angle_deg(dirs[0], gt[0:3])
        best = min(tc.line_angle_deg(dirs[i], gt[0:3]) for i in range(min(3, dirs.shape[0])))
        rank0, best = float(rank0), float(best)
    else:
        rank0, best = -1.0, -1.0
        pos = np.zeros((0, 3))

    trig = []
    if c3_frac >= C3_FRAC or c[2] >= C3_PTS:
        trig.append("c3_large")
    if author_pct >= S1_LOBE_PCT:
        trig.append("s1_lobe")
    if (n1 / float(max(n0, 1))) >= ASYM:
        trig.append("asym_walls")
    if cov_pct <= UNCOVERED_PCT:
        trig.append("mesh_uncovered")

    raw = {
        "stem": stem, "npts_cloud": npts, "clusters_total": nclust,
        "sizes": sizes, "s0_pts": n0, "s1_pts": n1, "mesh_verts": int(verts.shape[0]),
        "mesh_uncovered_verts": uncov, "s1_off_author_5mm_pct": author_pct,
        "gt_rank0_deg": rank0, "gt_best_deg": best,
        "s0_pts_raw": n0, "axis_candidates": int(v.shape[1]),
    }
    vals = [npts, nclust, c[0], c[1], c[2], c3_frac, n0, n1,
            n1 / float(max(n0, 1)), int(verts.shape[0]), cov_pct, uncov,
            author_pct, rank0, best]
    for k, val in enumerate(vals):
        if isinstance(val, float) and not np.isfinite(val):
            vals[k] = -1.0
    row = [stem, tc.pot_of(stem)] + [str(int(x)) for x in vals[0:2]] + \
          [str(int(x)) for x in vals[2:4]] + [str(int(vals[4]))] + \
          ["%.6f" % vals[5]] + [str(int(vals[6])), str(int(vals[7]))] + \
          ["%.6f" % vals[8]] + [str(int(vals[9])), "%.6f" % vals[10], str(int(vals[11]))] + \
          ["%.6f" % vals[12], "%.6f" % vals[13], "%.6f" % vals[14]] + \
          [",".join(trig) if trig else "ok"]
    return row, raw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--json", required=True)
    ap.add_argument("--jobs", type=int, default=8)
    a = ap.parse_args()
    allstems = tc.stems()
    print("pieces to census: %d" % len(allstems), flush=True)
    raws = []
    rows = []
    with Pool(a.jobs) as pool:
        for i, (row, raw) in enumerate(pool.imap(gather, allstems, chunksize=1)):
            rows.append(row)
            raws.append(raw)
            print("[%3d] %s flags=%s" % (i + 1, row[0], row[-1]), flush=True)
    tc.write_tsv(a.out, HEADER, rows)
    with open(a.json, "w") as fh:
        json.dump({"pieces": raws, "cover_mm": COVER_MM, "author_mm": AUTHOR_MM}, fh, indent=1)
    nflag = sum(1 for r in rows if r[-1] != "ok")
    print("wrote %s rows=%d flagged=%d" % (a.out, len(rows), nflag), flush=True)


if __name__ == "__main__":
    main()
