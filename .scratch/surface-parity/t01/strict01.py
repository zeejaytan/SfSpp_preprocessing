#!/usr/bin/env python3
"""strict01.py — Ticket 01 strict acceptance replay (turn 2).

Independent replay of the pinned scorer's arithmetic (score305.py, unmodified)
from the archived pose exports of run 20261124-1431_1233d62_t01-surface-parity,
plus the missing-pose acceptance record the cell wrapper now enforces.

A cell is usable only when all 31 nonempty T_<i>to_<i>.txt exports exist
(i = 0..30, the names score305.py reads).  An unusable cell gets NO scored join
rows here: it appears only in strict_poses.tsv / strict_replay.tsv with its
missing piece ids.  Its turn-1 scorer rows stay in the run as the historical
diagnostic result and are never counted as acceptance evidence.

Writes into --out (a supplement directory; the frozen run is not modified):
  strict_poses.tsv   cell, expected, present, missing_ids, empty_ids, status
  strict_joins.tsv   usable cells only: recomputed angle/t, pass, delta vs the
                     archived scorer row, plus the pass the archive recorded
  strict_seams.tsv   usable cells only: the three E28 joins per cell
  strict_replay.tsv  per cell: replay vs archived agreement, status
  strict_summary.tsv one line: usable cells, their join tallies, unusable cells
"""
import argparse
import os
import sys

import numpy as np

ANG_BAR = 20.05
T_BAR = 50.0
NP = 31
POT = "E"
SEAMS = [("27-28", 27, 28, 1), ("13-28", 13, 28, 2), ("28-31", 28, 31, 2)]


def read_T(path):
    a = np.loadtxt(path, ndmin=2)
    T = np.eye(4)
    T[0:3, 0:3] = a[0:3, 0:3]
    T[0:3, 3] = a[0:3, 3]
    return T


def angle_deg(R):
    c = (np.trace(R) - 1.0) / 2.0
    return float(np.degrees(np.arccos(np.clip(c, -1.0, 1.0))))


def pose_inventory(result):
    """(present list, missing 1-based ids, empty 1-based ids) for one cell."""
    present, missing, empty = [], [], []
    for p in range(1, NP + 1):
        f = os.path.join(result, "T_%dto_%d.txt" % (p - 1, p - 1))
        if not os.path.isfile(f):
            missing.append(p)
        elif os.path.getsize(f) == 0:
            empty.append(p)
        else:
            present.append(p)
    return present, missing, empty


def parse_archive(path):
    """archived scorer sheet -> {(i,j): (ang,t,verdict)}, summary string, pieces."""
    joins, summary = {}, ""
    with open(path) as fh:
        for ln in fh:
            f = ln.rstrip("\n").split("\t")
            if ln.startswith("#") or not f or f[0] in ("piece",):
                continue
            if f[0] == "SUMMARY":
                summary = ln.strip()
                continue
            if len(f) >= 5 and f[0].isdigit() and f[1].isdigit():
                try:
                    joins[(int(f[0]), int(f[1]))] = (float(f[2]), float(f[3]), f[4])
                except ValueError:
                    pass
    return joins, summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--gt", required=True)
    ap.add_argument("--pieces", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    on = []
    with open(a.pieces) as fh:
        next(fh)
        for ln in fh:
            f = ln.rstrip("\n").split("\t")
            if len(f) < 6 or f[0] != POT or f[4] != "on":
                continue
            if int(f[2]) not in on:
                on.append(int(f[2]))
    on.sort()
    gt_T = {}
    for p in on:
        gp = os.path.join(a.gt, "Pot_%s_Piece_%d_T.txt" % (POT, p))
        if os.path.isfile(gp):
            gt_T[p] = read_T(gp)
    G = np.loadtxt(os.path.join(a.gt, "Pot_%s_simple_graph.txt" % POT), ndmin=2)
    edges = []
    for ii in range(len(on)):
        for jj in range(ii + 1, len(on)):
            i, j = on[ii], on[jj]
            if i - 1 < G.shape[0] and j - 1 < G.shape[1] and int(G[i - 1, j - 1]) != 0:
                edges.append((i, j))

    cells = []
    for d in sorted(os.listdir(os.path.join(a.run, "out"))):
        if os.path.isdir(os.path.join(a.run, "out", d)):
            cells.append(d)

    poses, reph, joins_rows, seam_rows, summary_rows = [], [], [], [], []
    usable_joins = []
    for cell in cells:
        result = os.path.join(a.run, "out", cell)
        present, missing, empty = pose_inventory(result)
        status = "complete" if (len(present) == NP and not empty) else "incomplete"
        poses.append("%s\t%d\t%d\t%s\t%s\t%s" % (
            cell, NP, len(present),
            " ".join(str(x) for x in missing) or "-",
            " ".join(str(x) for x in empty) or "-", status))
        if status != "complete":
            reph.append("%s\t%s\t0\t\t\t\tunusable_missing_pose" % (cell, cell))
            summary_rows.append("%s\t0\t\t\tUNUSABLE: missing pieces %s" % (
                cell, " ".join(str(x) for x in missing + empty)))
            continue
        T_est = {}
        for p in present:
            T_est[p] = read_T(os.path.join(result, "T_%dto_%d.txt" % (p - 1, p - 1)))
        arch, arch_summary = parse_archive(os.path.join(a.run, "score", cell + ".tsv"))
        n_pass = 0
        max_da = max_dt = 0.0
        n_match = 0
        for (i, j) in edges:
            Re = np.linalg.inv(T_est[i]) @ T_est[j]
            Rg = np.linalg.inv(gt_T[i]) @ gt_T[j]
            ang = angle_deg(Re[0:3, 0:3] @ Rg[0:3, 0:3].T)
            t = float(np.linalg.norm(Re[0:3, 3] - Rg[0:3, 3]))
            ok = ang <= ANG_BAR and t <= T_BAR
            n_pass += ok
            arow = arch.get((i, j))
            da = dt = ""
            if arow is not None:
                da = "%.6f" % abs(ang - arow[0])
                dt = "%.6f" % abs(t - arow[1])
                max_da = max(max_da, abs(ang - arow[0]))
                max_dt = max(max_dt, abs(t - arow[1]))
                n_match += 1
            joins_rows.append("%s\t%d\t%d\t%.3f\t%.3f\t%d\t%s\t%s\t%s" % (
                cell, i, j, ang, t, 1 if ok else 0,
                arow[2] if arow else "-", da, dt))
            for (name, si, sj, prim) in SEAMS:
                if (i, j) == (si, sj):
                    seam_rows.append("%s\t%s\t%.3f\t%.3f\t%d\t%d\t%d" % (
                        cell, name, ang, t, 1 if ok else 0, prim,
                        1 if (arow and arow[2] == "PASS") else 0))
        usable_joins.append((cell, n_pass, len(edges)))
        reph.append("%s\t%s\t%d\t%d\t%s\t%s\t%s" % (
            cell, cell, len(present), n_match,
            "%.6f" % max_da, "%.6f" % max_dt,
            "replayed" if n_match == len(edges) else "partial_replay"))
        # the archived SUMMARY line is tab separated; keep one field per column
        summary_rows.append("%s\t1\t%d/%d\t%s\t%s" % (
            cell, n_pass, len(edges), arch_summary.replace("\t", "; "), ""))

    def wr(name, header, rows):
        with open(os.path.join(a.out, name), "w") as fh:
            fh.write(header + "\n")
            for r in rows:
                fh.write(r + "\n")

    wr("strict_poses.tsv",
       "cell\texpected\tpresent\tmissing_ids\tempty_ids\tstatus", poses)
    wr("strict_joins.tsv",
       "cell\tjoin_i\tjoin_j\tangle_deg\ttranslation_mm\tpass\tarchived_verdict"
       "\tdelta_angle_deg\tdelta_translation_mm", joins_rows)
    wr("strict_seams.tsv",
       "cell\tseam\tangle_deg\ttranslation_mm\tpass\tprimary\tarchived_pass", seam_rows)
    wr("strict_replay.tsv",
       "cell\tlabel\tposes_present\trows_matched\tmax_abs_angle_delta_deg"
       "\tmax_abs_translation_delta_mm\tstatus", reph)
    wr("strict_summary.tsv",
       "cell\tusable\tjoins\tarchived_summary\tnote", summary_rows)
    tot = sum(x[1] for x in usable_joins)
    den = sum(x[2] for x in usable_joins)
    print("STRICT-OK cells=%d usable=%d unusable=%d joins=%d/%d"
          % (len(cells), len(usable_joins), len(cells) - len(usable_joins), tot, den))
    return 0


if __name__ == "__main__":
    sys.exit(main())
