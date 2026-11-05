#!/usr/bin/env python3
"""analyse306c.py -- ticket 306 Stage C3: our union axes vs the released axis files.

usage: analyse306c.py --ours DIR --released DIR --out TSV [--summary TSV]

Both directories hold Pot_<P>_Piece_<NN>_Axis.xyz (position-first, 6 cols, K rows).
Angles are sign-agnostic (arccos |a.b|), the same measure io_axes.direction_angle_deg uses.
Tiers:
  gt_close : a released file exists and every released line has one of ours within 5 deg
  gt_off   : a released file exists but at least one released line is >5 deg from all of ours
  no_gt    : no released axis file
"""
import argparse, glob, os, sys
import numpy as np


def read_axes(path):
    A = np.loadtxt(path, ndmin=2)
    if A.size == 0:
        return np.zeros((6, 0))
    return A.T  # (6, K) position-first


def ang(a, b):
    na = np.linalg.norm(a); nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return float("nan")
    c = abs(float(np.dot(a, b)) / (na * nb))
    return float(np.degrees(np.arccos(min(1.0, c))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ours", required=True)
    ap.add_argument("--released", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--summary", default=None)
    a = ap.parse_args()

    rows = []
    for p in sorted(glob.glob(os.path.join(a.ours, "Pot_*_Piece_*_Axis.xyz"))):
        stem = os.path.basename(p)[:-4]
        pot = stem.split("_")[1]
        nn = int(stem.split("_")[3])
        O = read_axes(p)
        rel = os.path.join(a.released, stem + ".xyz")
        if not os.path.exists(rel):
            rows.append(dict(pot=pot, piece=nn, K=O.shape[1], n_rel=0, tier="no_gt",
                             best=float("nan"), med=float("nan"), covered5=0, covered10=0,
                             covered20=0, cov_frac5=float("nan")))
            continue
        R = read_axes(rel)
        # our best angle to any released line, per our line
        # direction is columns 3:6 (position-first 6-column file); rows 0:3 are
        # positions and an angle between positions means nothing.
        bests = [min(ang(O[3:6, i], R[3:6, j]) for j in range(R.shape[1]))
                 for i in range(O.shape[1])]
        # each released line's distance to the nearest of ours
        cov = [min(ang(R[3:6, j], O[3:6, i]) for i in range(O.shape[1]))
               for j in range(R.shape[1])]
        tier = "gt_close" if max(cov) <= 5.0 else "gt_off"
        rows.append(dict(pot=pot, piece=nn, K=O.shape[1], n_rel=R.shape[1], tier=tier,
                         best=min(bests), med=float(np.median(bests)),
                         covered5=sum(1 for c in cov if c <= 5.0),
                         covered10=sum(1 for c in cov if c <= 10.0),
                         covered20=sum(1 for c in cov if c <= 20.0),
                         cov_frac5=sum(1 for c in cov if c <= 5.0) / R.shape[1]))

    cols = ["pot", "piece", "K", "n_rel", "tier", "best", "med", "covered5",
            "covered10", "covered20", "cov_frac5"]
    with open(a.out, "w", newline="\n") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(("%s" % r[c]) if isinstance(r[c], str) else
                               (("%.4f" % r[c]) if isinstance(r[c], float) else str(r[c]))
                               for c in cols) + "\n")

    # summary by tier
    lines = ["tier\tpieces\tmedian_best_deg\tpct_best_within5\tmedian_K\tmedian_cov_frac5"]
    for t in ("gt_close", "gt_off", "no_gt"):
        sub = [r for r in rows if r["tier"] == t]
        if not sub:
            lines.append("%s\t0\t-\t-\t-\t-" % t); continue
        b = np.array([r["best"] for r in sub if r["best"] == r["best"]], float)
        K = np.array([r["K"] for r in sub], float)
        cf = np.array([r["cov_frac5"] for r in sub if r["cov_frac5"] == r["cov_frac5"]], float)
        lines.append("%s\t%d\t%.2f\t%.1f%%\t%.0f\t%s" % (
            t, len(sub), float(np.median(b)) if len(b) else float("nan"),
            100.0 * float((b <= 5).mean()) if len(b) else float("nan"),
            float(np.median(K)),
            ("%.2f" % float(np.median(cf))) if len(cf) else "-"))
    allb = np.array([r["best"] for r in rows if r["best"] == r["best"]], float)
    lines.append("all\t%d\t%.2f\t%.1f%%\t%.0f\t%s" % (
        len(rows), float(np.median(allb)), 100.0 * float((allb <= 5).mean()),
        float(np.median([r["K"] for r in rows])), "-"))
    txt = "\n".join(lines) + "\n"
    print(txt)
    if a.summary:
        open(a.summary, "w", newline="\n").write(txt)


if __name__ == "__main__":
    main()
