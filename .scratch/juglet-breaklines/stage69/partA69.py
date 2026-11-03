#!/usr/bin/env python3
"""partA69.py -- ticket 69 Part A: the ticket-68 axis estimators against the released
ground-truth axes of all ten corpus pots.

For every released piece that has a GT axis (141 of them), compute the folded angle between
the GT axis and
  rel0      the first line of the released Axes/ file (the axis the shipped pipeline ships)
  relbest   the best-matching line of that file (37 of 163 released files carry 2-6 lines;
            BreakLine::ReadAxis (class/data_structure.cpp:142-176) loads every line into
            axis_point_/axis_norm_, so the assembler can use any of them)
  nperp     control: direction minimising sum (n.d)^2 over both walls' normals
  nperpS1   the same on Surface_1 alone
  pottS1    Pottmann 6-point solver on Surface_1 alone
  potsac_s0 run_potsac(S0, S1) first candidate (seed 0), the authors' own method re-run
and the angle between rel0 and GT is the baseline the lead verified.

NO TRANSFORM is applied to either side (lead correction 2026-11-03): both axes live in the
piece's own frame; a rotation preserves the angle between two directions, so rotating one
side would be meaningless.  _T.txt is the pose into the assembled pot frame, a different
question, and is not used here.

Estimators are FIXED across every pot: no per-piece choice is made by GT.  The only GT in a
selection is the labelled diagnostic at the end (blind = pick per piece by the fit residual,
then compare that choice with the GT-optimal one).

usage: partA69.py CORPUS OUTDIR [--jobs N]
  CORPUS = .../sfs_main/original_samples/SfS_pp  (read-only)
"""
import argparse
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)                                    # staged sfs_axes beside the script
sys.path.insert(0, os.path.abspath(os.path.join(_HERE, "..", "..", "..")))  # in-repo layout
from sfs_axes.potsac import run_potsac            # noqa: E402
from sfs_axes.pottmann import compute_pottmann_axis  # noqa: E402


def read_surface(path):
    """6-column x y z nx ny nz surface, CRLF tolerant -> (6, n) float array."""
    a = np.loadtxt(path, usecols=(0, 1, 2, 3, 4, 5))
    if a.ndim == 1:
        a = a[None, :]
    return a.T


def read_axes(path):
    """All lines of an axis file -> (k, 6) array of [point; direction]."""
    a = np.loadtxt(path, ndmin=2)
    return np.atleast_2d(a)


def unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 0 else v


def fold(a, b):
    return float(np.degrees(np.arccos(np.clip(abs(unit(a) @ unit(b)), 0.0, 1.0))))


def nperp(C):
    """Direction minimising sum (n.d)^2 over the wall normals (the t68 control)."""
    n = C[3:6].T
    n = n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    w, v = np.linalg.eigh(n.T @ n)
    return v[:, 0], float(w[0] / max(w.sum(), 1e-30))


def npar(C):
    """Direction MAXIMISING sum (n.d)^2 -- the complementary eigenvector.

    EXTRA, not in the ticket's fixed list.  nperp is right only for a cylindrical wall
    (normals perpendicular to the axis); on a flat/base-like fragment the normals are
    parallel to the axis, and then nperp returns a direction in the flat's own plane,
    ~90 deg off.  npar is the estimator that is right in that case.  Measured, not
    assumed: see stage69/Results.md, column "median |n.d_gt|".
    """
    n = C[3:6].T
    n = n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    w, v = np.linalg.eigh(n.T @ n)
    return v[:, -1], float(w[-1] / max(w.sum(), 1e-30))


def pos_from_normals(C, d):
    """Least-squares point the projected normal lines pass closest to (hybrid68.py:29)."""
    x, n = C[0:3].T, C[3:6].T
    P = np.eye(3) - np.outer(d, d)
    xp, nps = x @ P, n @ P
    nps = nps / np.maximum(np.linalg.norm(nps, axis=1, keepdims=True), 1e-9)
    A = np.zeros((3, 3))
    b = np.zeros(3)
    for xi, ni in zip(xp, nps):
        Q = P - np.outer(ni, ni)
        A += Q
        b += Q @ xi
    return np.linalg.lstsq(A, b, rcond=None)[0]


def residuals(C, p, d):
    """(median cylindricality deg, median meridional deg, median radius mm) -- hybrid68.py:49."""
    x, n = C[0:3].T - p, C[3:6].T
    n = n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    cyl = np.degrees(np.arcsin(np.clip(np.abs(n @ d), 0, 1)))
    m = np.cross(d, x)
    m = m / np.maximum(np.linalg.norm(m, axis=1, keepdims=True), 1e-9)
    mer = np.degrees(np.arcsin(np.clip(np.abs(np.sum(n * m, axis=1)), 0, 1)))
    r = np.linalg.norm(x - np.outer(x @ d, d), axis=1)
    return float(np.median(cyl)), float(np.median(mer)), float(np.median(r))


def one_piece(job):
    pot, piece, corpus, seed = job
    surf = os.path.join(corpus, "Surfaces")
    s0 = os.path.join(surf, "Pot_%s_Piece_%02d_Surface_0.xyz" % (pot, piece))
    s1 = os.path.join(surf, "Pot_%s_Piece_%02d_Surface_1.xyz" % (pot, piece))
    rel = read_axes(os.path.join(corpus, "Axes", "Pot_%s_Piece_%02d_Axis.xyz" % (pot, piece)))
    gt = read_axes(os.path.join(corpus, "Ground Truth Axes",
                                "Pot_%s_Piece_%02d_Axis.xyz" % (pot, piece)))[0]
    dgt = unit(gt[3:6])
    C0 = read_surface(s0)
    C1 = read_surface(s1)
    C = np.hstack([C0, C1])

    out = {"pot": pot, "piece": piece, "n0": C0.shape[1], "n1": C1.shape[1],
           "rel_lines": int(rel.shape[0])}

    rel_dirs = [unit(r[3:6]) for r in rel]
    out["rel0"] = fold(rel_dirs[0], dgt)
    out["relbest"] = min(fold(d, dgt) for d in rel_dirs)
    out["rel0_vs_bestline"] = min(fold(rel_dirs[0], d) for d in rel_dirs)

    est = {}
    d, _ev = nperp(C)
    est["nperp"] = (pos_from_normals(C, d), d)
    d1, _ev1 = nperp(C1)
    est["nperpS1"] = (pos_from_normals(C1, d1), d1)
    dp_, _evp = npar(C)
    est["npar"] = (pos_from_normals(C, dp_), dp_)
    dp1, _evp1 = npar(C1)
    est["nparS1"] = (pos_from_normals(C1, dp1), dp1)
    vt = compute_pottmann_axis(C1)
    est["pottS1"] = (np.asarray(vt[3:6], dtype=float).reshape(3), unit(np.asarray(vt[0:3],
                                                                            dtype=float).reshape(3)))
    t0 = time.time()
    m = min(C0.shape[1], C1.shape[1])
    vs = run_potsac(C0[:, :m], C1[:, :m], rng=np.random.default_rng(seed), step=None)
    dp = unit(np.asarray(vs[0:3, 0], dtype=float).reshape(3))
    pp = np.asarray(vs[3:6, 0], dtype=float).reshape(3)
    est["potsac_s0"] = (pp, dp)
    out["potsac_secs"] = round(time.time() - t0, 2)
    out["potsac_ncand"] = int(vs.shape[1])

    for name, (p, d) in est.items():
        out[name] = fold(d, dgt)
        c, mm, r = residuals(C, p, d)
        out[name + "_cyl"], out[name + "_mer"], out[name + "_r"] = c, mm, r

    # geometry of the piece against TRUTH -- diagnostic only, never used to select
    nn = C[3:6].T
    nn = nn / np.maximum(np.linalg.norm(nn, axis=1, keepdims=True), 1e-12)
    out["abs_nd_gt"] = float(np.median(np.abs(nn @ dgt)))   # 1.0 = flat/base, 0.0 = cylinder
    x = C[0:3].T - gt[0:3]
    out["r_gt_med"] = float(np.median(np.linalg.norm(x - np.outer(x @ dgt, dgt), axis=1)))
    return out


def pct(a, q):
    return float(np.percentile(a, q)) if len(a) else float("nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus")
    ap.add_argument("outdir")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--pots", default="ABCDEFGHIJ")
    a = ap.parse_args()

    os.makedirs(a.outdir, exist_ok=True)
    gtd = os.path.join(a.corpus, "Ground Truth Axes")
    jobs = []
    for pot in a.pots:
        for f in sorted(os.listdir(gtd)):
            if not f.startswith("Pot_%s_Piece_" % pot) or not f.endswith("_Axis.xyz"):
                continue
            piece = int(f.split("_Piece_")[1].split("_")[0])
            jobs.append((pot, piece, a.corpus, a.seed))
    print("pieces with a GT axis: %d" % len(jobs), flush=True)

    t0 = time.time()
    with Pool(a.jobs) as pool:
        rows = []
        for i, r in enumerate(pool.imap_unordered(one_piece, jobs), 1):
            rows.append(r)
            print("[%3d/%3d] %s %02d  rel0 %.2f  relbest %.2f  nperp %.2f  nperpS1 %.2f "
                  " npar %.2f  nparS1 %.2f  pottS1 %.2f  potsac %.2f  |n.d| %.2f (%.1fs)" % (
                      i, len(jobs), r["pot"], r["piece"], r["rel0"], r["relbest"],
                      r["nperp"], r["nperpS1"], r["npar"], r["nparS1"], r["pottS1"],
                      r["potsac_s0"], r["abs_nd_gt"], r["potsac_secs"]), flush=True)
    rows.sort(key=lambda r: (r["pot"], r["piece"]))
    print("elapsed %.1f s" % (time.time() - t0), flush=True)

    names = ["rel0", "relbest", "nperp", "nperpS1", "npar", "nparS1", "pottS1", "potsac_s0"]
    cols = ["pot", "piece", "n0", "n1", "rel_lines", "rel0_vs_bestline",
            "abs_nd_gt", "r_gt_med"] + names
    cols += [n + s for n in ("nperp", "nperpS1", "npar", "nparS1", "pottS1", "potsac_s0")
             for s in ("_cyl", "_mer", "_r")] + ["potsac_secs", "potsac_ncand"]
    with open(os.path.join(a.outdir, "pieces.tsv"), "w") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join(str(r.get(c, "")) for c in cols) + "\n")

    # ---- blind (label-free) selection: lowest residual score, GT never consulted ----
    est_names = ["nperp", "nperpS1", "npar", "nparS1", "pottS1", "potsac_s0"]

    def blind_score(r, n):
        # cylindricality + meridional are degrees on the same footing; radius is a sanity
        # term only (it is a length, so it is normalised by the piece's own median radius).
        return r[n + "_cyl"] + r[n + "_mer"] + 0.1 * r[n + "_r"]

    with open(os.path.join(a.outdir, "selection.tsv"), "w") as fh:
        fh.write("pot\tpiece\tblind\tblind_deg\tgt_best\tgt_best_deg\tagrees\trel0\n")
        for r in rows:
            blind = min(est_names, key=lambda n: blind_score(r, n))
            gtbest = min(est_names, key=lambda n: r[n])
            fh.write("%s\t%02d\t%s\t%.2f\t%s\t%.2f\t%d\t%.2f\n" % (
                r["pot"], r["piece"], blind, r[blind], gtbest, r[gtbest],
                int(blind == gtbest), r["rel0"]))

    # ---- per-pot table ----
    def block(sub):
        d = {}
        for n in names:
            v = np.array([r[n] for r in sub])
            d[n] = (len(v), float(np.median(v)), pct(v, 90), float(v.max()),
                    int((v <= 5).sum()), int((v <= 10).sum()))
        blind = np.array([min(r[n] for n in est_names) for r in sub])  # GT-optimal oracle
        d["oracle"] = (len(blind), float(np.median(blind)), pct(blind, 90), float(blind.max()),
                       int((blind <= 5).sum()), int((blind <= 10).sum()))
        bs = []
        for r in sub:
            b = min(est_names, key=lambda n: blind_score(r, n))
            bs.append(r[b])
        bs = np.array(bs)
        d["blind"] = (len(bs), float(np.median(bs)), pct(bs, 90), float(bs.max()),
                      int((bs <= 5).sum()), int((bs <= 10).sum()))
        worse = {n: int(sum(1 for r in sub if r[n] > r["rel0"] + 10.0)) for n in est_names}
        return d, worse

    pots = sorted({r["pot"] for r in rows})
    lines = []
    hdr = ("pot\tn\t" + "\t".join("%s_med\t%s_p90\t%s_max\t%s_le5\t%s_le10" % (n, n, n, n, n)
                                  for n in names) +
           "\toracle_med\tblind_med\tblind_p90\tblind_max")
    lines.append(hdr)
    for pot in pots + ["ALL"]:
        sub = rows if pot == "ALL" else [r for r in rows if r["pot"] == pot]
        d, worse = block(sub)
        cells = [pot, str(d["rel0"][0])]
        for n in names:
            cells += ["%.2f" % d[n][1], "%.2f" % d[n][2], "%.2f" % d[n][3],
                      str(d[n][4]), str(d[n][5])]
        cells += ["%.2f" % d["oracle"][1], "%.2f" % d["blind"][1],
                  "%.2f" % d["blind"][2], "%.2f" % d["blind"][3]]
        lines.append("\t".join(cells))
        print("POT %s n=%d  rel0 med %.2f p90 %.2f | " % (pot, d["rel0"][0], d["rel0"][1],
                                                          d["rel0"][2]) +
              " ".join("%s %.2f" % (n, d[n][1]) for n in names[2:]) +
              " | oracle %.2f blind %.2f | worse>10deg vs rel0: %s" % (
                  d["oracle"][1], d["blind"][1],
                  " ".join("%s=%d" % (k, v) for k, v in worse.items())), flush=True)
    with open(os.path.join(a.outdir, "per_pot.tsv"), "w") as fh:
        fh.write("\n".join(lines) + "\n")

    # ---- the same table restricted to the lead's baseline-good pots ----
    good = ["A", "B", "D", "E", "G", "I"]
    sub = [r for r in rows if r["pot"] in good]
    d, worse = block(sub)
    print("\nBASELINE-GOOD POTS %s n=%d" % ("".join(good), len(sub)))
    for n in names:
        print("  %-9s median %6.2f  p90 %6.2f  max %6.2f  <=5deg %3d  <=10deg %3d  "
              "worse-than-rel0-by>10deg %3d" % (n, d[n][1], d[n][2], d[n][3], d[n][4],
                                                d[n][5], worse.get(n, 0)))
    print("  oracle    median %6.2f   blind median %6.2f" % (d["oracle"][1], d["blind"][1]))
    with open(os.path.join(a.outdir, "baseline_good.tsv"), "w") as fh:
        fh.write("estimator\tmedian\tp90\tmax\tle5\tle10\tworse_than_rel0_by_10deg\n")
        for n in names:
            fh.write("%s\t%.3f\t%.3f\t%.3f\t%d\t%d\t%d\n" % (
                n, d[n][1], d[n][2], d[n][3], d[n][4], d[n][5], worse.get(n, 0)))
        fh.write("oracle\t%.3f\t%.3f\t%.3f\t%d\t%d\t\n" % d["oracle"][:5])
        fh.write("blind\t%.3f\t%.3f\t%.3f\t%d\t%d\t\n" % d["blind"][:5])
    print("PART A DONE", a.outdir)


if __name__ == "__main__":
    main()
