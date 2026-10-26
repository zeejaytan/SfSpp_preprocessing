#!/usr/bin/env python3
"""Ticket 301 Phase 0 -- reconstruct the Pot D vessel axis exactly as ticket 299 section 6 did,
and derive, for each target piece, the axis direction its own reference pose implies.

The construction is 299's (axis299.py lines 29-31, cited in the ticket):
the pot axis in the GT/world frame is the first right singular vector of the stack
   { R_GT_i @ d_i }  over every piece that has a reference transform and exactly ONE axis line,
where d_i is that piece's released axis direction and R_GT_i its released rotation. Because
p_world = R p_local + t and a wheel-thrown pot has one axis, R_GT_i @ d_i should be the same
direction for every piece; the SVD gives the best common direction a_world.

A piece's pose-implied axis direction in its own local frame is then  d_swap = R_GT^T @ a_world.

Writes p301-constants.json (a_world, per-piece deviations, the five swap vectors, corpus md5s).
Read-only with respect to the corpus.
"""
import argparse, hashlib, json, os
import numpy as np

TARGETS = [18, 25, 26, 28, 29]
NP = 29


def read_T(path):
    M = np.eye(4)
    rows = [l.split() for l in open(path) if l.strip()]
    for i in range(len(rows) - 1):          # Trans::Read reads num-1 rows (data_structure.cpp:648)
        M[i, :] = [float(x) for x in rows[i][:4]]
    return M


def axis_lines(path):
    """(point, direction) per line, direction normalised -- the loader's own reading of the file
    (BreakLine::ReadAxis, class/data_structure.cpp:142)."""
    out = []
    for l in open(path):
        v = [float(x) for x in l.split()]
        if len(v) >= 6:
            d = np.array(v[3:6], float)
            out.append((np.array(v[0:3], float), d / np.linalg.norm(d)))
    return out


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def ang(u, v):
    """angle between two directions, minimised over the two signs -- an axis is a line."""
    return float(np.degrees(np.arccos(min(1.0, abs(float(np.dot(u, v)))))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True, help="local copy holding Axes/ and Ground Truth/")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    gtd = os.path.join(a.corpus, "Ground Truth")
    axd = os.path.join(a.corpus, "Axes")

    gt, lines, present, axmd5 = {}, {}, {}, {}
    for i in range(1, NP + 1):
        q = os.path.join(gtd, "Pot_D_Piece_%d_T.txt" % i)
        present[i] = os.path.exists(q)
        gt[i] = read_T(q) if present[i] else None
        f = os.path.join(axd, "Pot_D_Piece_%02d_Axis.xyz" % i)
        lines[i] = axis_lines(f)
        axmd5[i] = md5(f)

    # 299 section 6, unchanged: single-axis pieces with a reference transform
    single = [i for i in range(1, NP + 1) if present[i] and len(lines[i]) == 1]
    V = np.array([gt[i][:3, :3] @ lines[i][0][1] for i in single])
    u, s, vt = np.linalg.svd(V)
    a_world = vt[0] / np.linalg.norm(vt[0])
    if a_world[2] < 0:
        a_world = -a_world                     # canonical sign; the angle is sign-free anyway

    # the fitted world axis LINE (only a diagnostic; the swap moves the direction only)
    P = np.array([gt[i][:3, :3] @ lines[i][0][0] + gt[i][:3, 3] for i in single])
    resid = P - np.outer(P @ a_world, a_world)
    q_world = resid.mean(axis=0)

    pieces = {}
    for i in range(1, NP + 1):
        devs = [ang(gt[i][:3, :3] @ d, a_world) for (_, d) in lines[i]] if present[i] else []
        # perpendicular offset of each corpus axis POINT from the fitted world axis line
        offs = []
        if present[i]:
            for (p, _) in lines[i]:
                pw = gt[i][:3, :3] @ p + gt[i][:3, 3]
                d = pw - q_world
                offs.append(float(np.linalg.norm(d - float(np.dot(d, a_world)) * a_world)))
        pieces[i] = dict(gt_present=present[i], n_lines=len(lines[i]),
                         dev_min=round(min(devs), 2) if devs else None,
                         dev_max=round(max(devs), 2) if devs else None,
                         dev_all=[round(x, 2) for x in devs],
                         point_off_mm=[round(x, 2) for x in offs],
                         corpus_dirs=[[round(float(c), 15) for c in d] for (_, d) in lines[i]],
                         axis_md5=axmd5[i])

    # The released files carry no consistent sign convention: R_GT @ d projects onto a_world with
    # 15 of 21 single-axis pieces NEGATIVE at |dot| ~ 1.0, so the sign of a line says nothing about
    # the pose. An axis is a line, so each line is given the pose-implied direction in ITS OWN
    # orientation (minimum rotation, sign preserved) -- the only thing corrected is the direction.
    swaps = {}
    for p in TARGETS:
        R = gt[p][:3, :3]
        d_imp = R.T @ a_world
        d_imp = d_imp / np.linalg.norm(d_imp)
        rows = []
        for k, (_, d) in enumerate(lines[p]):
            sg = 1.0 if float(np.dot(d, d_imp)) >= 0 else -1.0
            dn = sg * d_imp
            rows.append(dict(line=k,
                             d_corpus=[float("%.15g" % c) for c in d],
                             d_new=[float("%.15g" % c) for c in dn],
                             magnitude_deg=round(ang(dn, d), 2),
                             sign_applied=int(sg)))
        swaps[p] = dict(lines=rows,
                        d_pose_implied=[float("%.15g" % c) for c in d_imp],
                        n_lines=len(lines[p]),
                        axis_md5=axmd5[p],
                        gt_path="Ground Truth/Pot_D_Piece_%d_T.txt" % p)

    out = dict(a_world=[float("%.15g" % c) for c in a_world],
               sv_singular=[round(float(x), 4) for x in s],
               single_axis_pieces=single,
               q_world=[float("%.15g" % c) for c in q_world],
               pieces=pieces, swaps=swaps,
               construction="299 section 6 / axis299.py:29-31 -- SVD over R_GT_i @ d_i, single-axis pieces")
    json.dump(out, open(a.out, "w"), indent=1)

    print("a_world (GT frame):", np.round(a_world, 6), " singular:", np.round(s, 2))
    print("single-axis pieces used:", single, "(n=%d)" % len(single))
    print("piece  lines  dev_min  dev_max   point_off_mm            note")
    for i in range(1, NP + 1):
        d = pieces[i]
        if not d["gt_present"]:
            print("  %2d    %d    -- no reference transform --" % (i, d["n_lines"]))
            continue
        flag = "  <== TARGET" if i in TARGETS else ""
        print("  %2d    %d   %7.2f %8.2f   %-22s%s" % (
            i, d["n_lines"], d["dev_min"], d["dev_max"], d["point_off_mm"], flag))
    print("\nswap directions (R_GT^T . a_world, per line in the line's own sign):")
    for p in TARGETS:
        for r in swaps[p]["lines"]:
            print("  p%02d line %d  %s -> %s  (rotates by %.2f deg)" %
                  (p, r["line"], np.round(r["d_corpus"], 6), np.round(r["d_new"], 6), r["magnitude_deg"]))


if __name__ == "__main__":
    main()
