#!/usr/bin/env python3
"""corpus70.py -- ticket 70 stage 2: the port's MULTI-line PotSAC output against the
released multi-line axis files, piece by piece, on the authors' own released surfaces.

Inputs (read-only), CORPUS = .../sfs_main/original_samples/SfS_pp:
  Surfaces/Pot_X_Piece_NN_Surface_{0,1}.xyz   the surfaces the authors' axes were fitted on
  Axes/Pot_X_Piece_NN_Axis.xyz                the released axes (1-6 lines, px py pz dx dy dz)
  Ground Truth Axes/Pot_X_Piece_NN_Axis.xyz   GT axis (141 pieces), diagnostic only
  Ground Truth/Pot_X_Piece_N_T.txt + Pot_X_simple_graph.txt   GT poses + true edges

Arms (sfs_axes.potsac.run_potsac, all K surviving lines written with io_axes.write_axes):
  M0 M1 M2  step=10 (paper 10 %), no equal-count truncation, seeds 0/1/2 -- the MATLAB in
            this repo: run_potsac.m:18 strides 1:10:end, read_surfaces.m reads both walls whole
  T0        step=10, equal-count truncation, seed 0 -- sfs_axes.cli's default path
            (io_surfaces.read_surfaces truncate=True)

Match rule (the ticket's standing gate): a released line r has a counterpart among ours when
some line o has direction_angle_deg(o, r) <= 5 AND radial_axial_errors(o_pos, r_dir, r_pos)
radial <= 2 mm. Axial offset is not gated: a position anywhere along the same line is the
same axis.

usage: corpus70.py CORPUS OUTDIR [--jobs N] [--arms M0,M1,M2,T0]
"""
import argparse
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.abspath(os.path.join(_HERE, "..", "..", "..")))
from sfs_axes.io_axes import (direction_angle_deg, radial_axial_errors,  # noqa: E402
                              read_axes, write_axes)
from sfs_axes.potsac import run_potsac  # noqa: E402

ARMS = {"M0": (10, False, 0), "M1": (10, False, 1), "M2": (10, False, 2),
        "T0": (10, True, 0)}
ANG_TOL = 5.0
RAD_TOL = 2.0
GATE_DEG = 25.0
GOOD = "ABDEGI"


def load_surface(path):
    a = np.loadtxt(path, usecols=(0, 1, 2, 3, 4, 5), ndmin=2)
    return a.T


def lines_of(vt):
    """vt (6, K) [dir; pos] -> list of (dir unit, pos)."""
    out = []
    for k in range(vt.shape[1]):
        d = vt[0:3, k] / np.linalg.norm(vt[0:3, k])
        out.append((d, vt[3:6, k].copy()))
    return out


def match(rel_line, ours):
    """Best counterpart of one released line among our lines."""
    rd, rp = rel_line
    best = None
    for od, op in ours:
        ang = direction_angle_deg(od, rd)
        rad, _ax = radial_axial_errors(op, rd, rp)
        ok = ang <= ANG_TOL and rad <= RAD_TOL
        key = (not ok, ang)
        if best is None or key < best[0]:
            best = (key, ang, rad, ok)
    return best[1], best[2], best[3]


def one(job):
    corpus, outdir, pot, piece, arm = job
    step, trunc, seed = ARMS[arm]
    stem = "Pot_%s_Piece_%02d" % (pot, piece)
    C0 = load_surface(os.path.join(corpus, "Surfaces", stem + "_Surface_0.xyz"))
    C1 = load_surface(os.path.join(corpus, "Surfaces", stem + "_Surface_1.xyz"))
    if trunc:
        m = min(C0.shape[1], C1.shape[1])
        C0, C1 = C0[:, :m], C1[:, :m]
    t0 = time.time()
    vt = run_potsac(C0, C1, rng=np.random.default_rng(seed), step=step)
    secs = time.time() - t0
    adir = os.path.join(outdir, "axes", arm)
    os.makedirs(adir, exist_ok=True)
    if vt.shape[1] > 0:
        write_axes(os.path.join(adir, stem + "_Axis.xyz"), vt)
    return (pot, piece, arm, vt, secs, C0.shape[1] + C1.shape[1])


def read_R(path):
    return np.loadtxt(path, ndmin=2).reshape(4, 4)[0:3, 0:3]


def read_graph(path):
    A = []
    with open(path) as fh:
        for line in fh:
            c = [x for x in line.strip().split("\t") if x != ""]
            if c:
                A.append([int(float(x)) for x in c])
    return np.array(A, dtype=int)


def fold(a, b):
    return direction_angle_deg(a, b)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus")
    ap.add_argument("outdir")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--arms", default="M0,M1,M2,T0")
    a = ap.parse_args()
    arms = a.arms.split(",")
    os.makedirs(a.outdir, exist_ok=True)

    pieces = []
    for fn in sorted(os.listdir(os.path.join(a.corpus, "Axes"))):
        if not fn.endswith("_Axis.xyz"):
            continue
        t = fn.split("_")
        pot, piece = t[1], int(t[3])
        stem = "Pot_%s_Piece_%02d" % (pot, piece)
        if all(os.path.isfile(os.path.join(a.corpus, "Surfaces", stem + "_Surface_%d.xyz" % k))
               for k in (0, 1)):
            pieces.append((pot, piece))
    print("[T70] pieces with released axis + both surfaces: %d" % len(pieces), flush=True)

    jobs = [(a.corpus, a.outdir, p, k, arm) for (p, k) in pieces for arm in arms]
    res = {}
    with Pool(a.jobs) as pool:
        for i, (pot, piece, arm, vt, secs, n) in enumerate(pool.imap_unordered(one, jobs)):
            res[(pot, piece, arm)] = (vt, secs, n)
            if i % 50 == 0:
                print("[T70] %d/%d done (%s %02d %s K=%d %.1fs)"
                      % (i + 1, len(jobs), pot, piece, arm, vt.shape[1], secs), flush=True)

    rel, gt = {}, {}
    for pot, piece in pieces:
        stem = "Pot_%s_Piece_%02d" % (pot, piece)
        rel[(pot, piece)] = lines_of(read_axes(os.path.join(a.corpus, "Axes", stem + "_Axis.xyz")))
        g = os.path.join(a.corpus, "Ground Truth Axes", stem + "_Axis.xyz")
        if os.path.isfile(g):
            gt[(pot, piece)] = lines_of(read_axes(g))[0][0]

    selfok = sum(int(all(match(rl, rel[p])[2] for rl in rel[p])) for p in pieces)
    print("[T70] selftest: released file matched against itself on %d/%d pieces"
          % (selfok, len(pieces)), flush=True)
    if selfok != len(pieces):
        raise SystemExit("selftest failed: the match rule rejects a file against itself")

    # ---- per piece, per arm
    rows = []
    for pot, piece in pieces:
        R = rel[(pot, piece)]
        for arm in arms:
            vt, secs, n = res[(pot, piece, arm)]
            O = lines_of(vt)
            r = {"pot": pot, "piece": piece, "arm": arm, "n": n, "secs": round(secs, 2),
                 "K_rel": len(R), "K_ours": len(O)}
            if O:
                ang11 = direction_angle_deg(O[0][0], R[0][0])
                rad11 = radial_axial_errors(O[0][1], R[0][0], R[0][1])[0]
                r["l1_ang"], r["l1_rad"] = ang11, rad11
                r["l1_match"] = int(ang11 <= ANG_TOL and rad11 <= RAD_TOL)
                ms = [match(rl, O) for rl in R]
                r["rel1_any_ang"], r["rel1_any_rad"], r["rel1_any_match"] = ms[0][0], ms[0][1], int(ms[0][2])
                r["rel_lines_matched"] = sum(int(m[2]) for m in ms)
                r["any_match"] = int(any(m[2] for m in ms))
                r["all_match"] = int(all(m[2] for m in ms))
                r["dir_only_any"] = int(any(m[0] <= ANG_TOL for m in ms))
            else:
                for k in ("l1_ang", "l1_rad", "rel1_any_ang", "rel1_any_rad"):
                    r[k] = float("nan")
                for k in ("l1_match", "rel1_any_match", "rel_lines_matched", "any_match",
                          "all_match", "dir_only_any"):
                    r[k] = 0
            if (pot, piece) in gt:
                dg = gt[(pot, piece)]
                r["gt_rel1"] = fold(R[0][0], dg)
                r["gt_relbest"] = min(fold(d, dg) for d, _ in R)
                r["gt_ours1"] = fold(O[0][0], dg) if O else float("nan")
                r["gt_oursbest"] = min(fold(d, dg) for d, _ in O) if O else float("nan")
            else:
                r["gt_rel1"] = r["gt_relbest"] = r["gt_ours1"] = r["gt_oursbest"] = float("nan")
            rows.append(r)
    cols = ["pot", "piece", "arm", "n", "secs", "K_rel", "K_ours", "l1_ang", "l1_rad", "l1_match",
            "rel1_any_ang", "rel1_any_rad", "rel1_any_match", "rel_lines_matched", "any_match",
            "all_match", "dir_only_any", "gt_rel1", "gt_relbest", "gt_ours1", "gt_oursbest"]
    with open(os.path.join(a.outdir, "pieces70.tsv"), "w") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join(("%.3f" % r[c]) if isinstance(r[c], float) else str(r[c])
                               for c in cols) + "\n")

    # ---- per pot summary
    def summ(sub):
        n = len(sub)
        if n == 0:
            return None
        g = [x for x in sub if not np.isnan(x["gt_ours1"])]
        return dict(n=n,
                    l1=sum(x["l1_match"] for x in sub),
                    rel1any=sum(x["rel1_any_match"] for x in sub),
                    anyl=sum(x["any_match"] for x in sub),
                    alll=sum(x["all_match"] for x in sub),
                    dironly=sum(x["dir_only_any"] for x in sub),
                    relmatched=sum(x["rel_lines_matched"] for x in sub),
                    rellines=sum(x["K_rel"] for x in sub),
                    Krel=sum(x["K_rel"] for x in sub), Kours=sum(x["K_ours"] for x in sub),
                    l1ang=float(np.nanmedian([x["l1_ang"] for x in sub])),
                    ngt=len(g),
                    gt_rel1=float(np.median([x["gt_rel1"] for x in g])) if g else float("nan"),
                    gt_relbest=float(np.median([x["gt_relbest"] for x in g])) if g else float("nan"),
                    gt_ours1=float(np.median([x["gt_ours1"] for x in g])) if g else float("nan"),
                    gt_oursbest=float(np.median([x["gt_oursbest"] for x in g])) if g else float("nan"))

    with open(os.path.join(a.outdir, "per_pot70.tsv"), "w") as fh:
        hdr = ["arm", "pot", "n", "l1_match", "rel1_any_match", "any_match", "all_match",
               "dir_only_any", "rel_lines_matched", "rel_lines", "K_rel_sum", "K_ours_sum",
               "l1_ang_med", "n_gt", "gt_rel1_med", "gt_relbest_med", "gt_ours1_med",
               "gt_oursbest_med"]
        fh.write("\t".join(hdr) + "\n")
        for arm in arms:
            groups = [(p, [x for x in rows if x["arm"] == arm and x["pot"] == p])
                      for p in "ABCDEFGHIJ"]
            groups.append(("GOOD", [x for x in rows if x["arm"] == arm and x["pot"] in GOOD]))
            groups.append(("ALL", [x for x in rows if x["arm"] == arm]))
            for p, sub in groups:
                s = summ(sub)
                if s is None:
                    continue
                fh.write("\t".join(str(v) for v in [
                    arm, p, s["n"], s["l1"], s["rel1any"], s["anyl"], s["alll"], s["dironly"],
                    s["relmatched"], s["rellines"], s["Krel"], s["Kours"], "%.2f" % s["l1ang"],
                    s["ngt"], "%.2f" % s["gt_rel1"], "%.2f" % s["gt_relbest"],
                    "%.2f" % s["gt_ours1"], "%.2f" % s["gt_oursbest"]]) + "\n")
                print("[T70] %s %-4s n=%3d l1=%3d rel1any=%3d any=%3d all=%3d dironly=%3d "
                      "Krel=%3d Kours=%3d | GT med rel1 %.2f relbest %.2f ours1 %.2f oursbest %.2f"
                      % (arm, p, s["n"], s["l1"], s["rel1any"], s["anyl"], s["alll"], s["dironly"],
                         s["Krel"], s["Kours"], s["gt_rel1"], s["gt_relbest"], s["gt_ours1"],
                         s["gt_oursbest"]), flush=True)

    # ---- K distributions
    with open(os.path.join(a.outdir, "K_dist70.tsv"), "w") as fh:
        fh.write("who\tK\tpieces\n")
        from collections import Counter
        c = Counter(len(rel[p]) for p in pieces)
        for k in sorted(c):
            fh.write("released\t%d\t%d\n" % (k, c[k]))
        for arm in arms:
            c = Counter(res[(p, q, arm)][0].shape[1] for p, q in pieces)
            for k in sorted(c):
                fh.write("%s\t%d\t%d\n" % (arm, k, c[k]))

    # ---- edge gate: released vs each arm, line-1 pair and any-line pair, GT poses
    gtd = os.path.join(a.corpus, "Ground Truth")
    with open(os.path.join(a.outdir, "edge_gate70.tsv"), "w") as fh:
        fh.write("who\tpot\tedges\tline1_pass\tany_pass\n")
        whos = ["released"] + arms
        tot = {w: [0, 0, 0] for w in whos}
        good = {w: [0, 0, 0] for w in whos}
        for pot in "ABCDEFGHIJ":
            gp = os.path.join(gtd, "Pot_%s_simple_graph.txt" % pot)
            if not os.path.exists(gp):
                continue
            A = read_graph(gp)
            n = A.shape[0]
            edges = [(i + 1, j + 1) for i in range(n) for j in range(i + 1, n) if A[i, j]]
            Rs = {}
            for k in range(1, n + 1):
                t = os.path.join(gtd, "Pot_%s_Piece_%d_T.txt" % (pot, k))
                if os.path.exists(t) and (pot, k) in rel:
                    Rs[k] = read_R(t)
            usable = [e for e in edges if e[0] in Rs and e[1] in Rs]
            for w in whos:
                L = {}
                for k in Rs:
                    if w == "released":
                        L[k] = [d for d, _ in rel[(pot, k)]]
                    else:
                        L[k] = [d for d, _ in lines_of(res[(pot, k, w)][0])]
                l1 = anyp = 0
                for i, j in usable:
                    if not L[i] or not L[j]:
                        continue
                    if fold(Rs[i] @ L[i][0], Rs[j] @ L[j][0]) <= GATE_DEG:
                        l1 += 1
                    if any(fold(Rs[i] @ x, Rs[j] @ y) <= GATE_DEG for x in L[i] for y in L[j]):
                        anyp += 1
                fh.write("%s\t%s\t%d\t%d\t%d\n" % (w, pot, len(usable), l1, anyp))
                for acc in ([tot] + ([good] if pot in GOOD else [])):
                    acc[w][0] += len(usable)
                    acc[w][1] += l1
                    acc[w][2] += anyp
        for w in whos:
            fh.write("%s\tGOOD\t%d\t%d\t%d\n" % (w, good[w][0], good[w][1], good[w][2]))
            fh.write("%s\tALL\t%d\t%d\t%d\n" % (w, tot[w][0], tot[w][1], tot[w][2]))
            print("[T70] edge gate %-8s GOOD %d/%d line1, %d/%d any | ALL %d/%d line1, %d/%d any"
                  % (w, good[w][1], good[w][0], good[w][2], good[w][0],
                     tot[w][1], tot[w][0], tot[w][2], tot[w][0]), flush=True)

    # ---- seed sensitivity across M0/M1/M2 (line-1 direction spread and K)
    seeds = [x for x in ("M0", "M1", "M2") if x in arms]
    if len(seeds) == 3:
        with open(os.path.join(a.outdir, "seeds70.tsv"), "w") as fh:
            fh.write("pot\tpiece\tK_M0\tK_M1\tK_M2\tl1_spread_deg\tl1_match_M0\tl1_match_M1\tl1_match_M2\n")
            spreads, kdiff = [], 0
            for pot, piece in pieces:
                L = [lines_of(res[(pot, piece, s)][0]) for s in seeds]
                Ks = [len(x) for x in L]
                sp = max(direction_angle_deg(L[i][0][0], L[j][0][0])
                         for i in range(3) for j in range(i + 1, 3)) if all(Ks) else float("nan")
                spreads.append(sp)
                kdiff += int(len(set(Ks)) > 1)
                lm = [x["l1_match"] for x in rows
                      if x["pot"] == pot and x["piece"] == piece and x["arm"] in seeds]
                fh.write("%s\t%d\t%d\t%d\t%d\t%.3f\t%d\t%d\t%d\n"
                         % (pot, piece, Ks[0], Ks[1], Ks[2], sp, lm[0], lm[1], lm[2]))
            sp = np.array(spreads)
            print("[T70] seeds: line-1 direction spread across seeds 0/1/2 median %.2f p90 %.2f "
                  "max %.2f deg; >5deg on %d/%d pieces; K differs across seeds on %d/%d"
                  % (np.nanmedian(sp), np.nanpercentile(sp, 90), np.nanmax(sp),
                     int(np.sum(sp > 5)), len(sp), kdiff, len(pieces)), flush=True)
    print("[T70] done", flush=True)


if __name__ == "__main__":
    main()
