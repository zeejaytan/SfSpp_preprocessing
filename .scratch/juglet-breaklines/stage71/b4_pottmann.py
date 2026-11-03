#!/usr/bin/env python3
"""t71 stage B4 (lead): can the authors own candidate generator recover the axis on REAL surfaces?

Stage A: our port reproduces the released axis on 1 of 163 pieces over 20 seeds.
The released axis itself is 2.78 deg (median) from GT, so the released axes are good and ours are not.
B2: no Cao-family residual has the released axis at its minimum either.

This probe removes everything except the generator: Pottmann on 6 random points from the released
Surface files, no MLESAC, no scoring, no dedup, no refine. If the best of 400 draws lands near GT,
the generator is fine and the port loses the axis in SEARCH or SCORING. If it does not, the surfaces
or their normals are not what the released axes were built from.
"""
import os, sys, csv
import numpy as np

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
OUT = sys.argv[1] if len(sys.argv) > 1 else "."
DRAWS = 400
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))

from sfs_axes.pottmann import compute_pottmann_axis


def load(path):
    a = np.loadtxt(path, usecols=(0, 1, 2, 3, 4, 5), ndmin=2)
    return np.asarray(a, dtype=float).T


def unit(v):
    n = np.linalg.norm(v, axis=0)
    return v / np.where(n > 1e-12, n, 1.0)


def ang_deg(a, b):
    c = abs(float(np.dot(unit(a), unit(b))))
    return float(np.degrees(np.arccos(min(1.0, c))))


def pott_best(X, gt, rng, draws):
    n = X.shape[1]
    angs = []
    for _ in range(draws):
        idx = rng.choice(n, size=6, replace=False)
        try:
            d = compute_pottmann_axis(X[:, idx])
        except Exception:
            continue
        if d is None or not np.all(np.isfinite(d)):
            continue
        angs.append(ang_deg(np.asarray(d, dtype=float).reshape(-1)[0:3], gt))
    if not angs:
        return float("nan"), float("nan"), 0
    return min(angs), float(np.median(angs)), len(angs)


def main():
    os.makedirs(OUT, exist_ok=True)
    sd = os.path.join(CORPUS, "Surfaces")
    rows = []
    rng = np.random.default_rng(71)
    stems = sorted(fn.replace("_Surface_0.xyz", "") for fn in os.listdir(sd)
                   if fn.endswith("_Surface_0.xyz"))
    for stem in stems:
        pot = stem.split("_")[1]
        piece = stem.split("_")[-1]
        gpath = os.path.join(CORPUS, "Ground Truth Axes", stem + "_Axis.xyz")
        if not os.path.isfile(gpath):
            continue
        gt = np.loadtxt(gpath, ndmin=2)[0, 3:6]
        C0 = load(os.path.join(sd, stem + "_Surface_0.xyz"))
        C1 = load(os.path.join(sd, stem + "_Surface_1.xyz"))
        both = np.concatenate([C0, C1], axis=1)
        rel = np.loadtxt(os.path.join(CORPUS, "Axes", stem + "_Axis.xyz"), ndmin=2)[0, 3:6]
        b_best, b_med, n_d = pott_best(both, gt, rng, DRAWS)
        s0_best, s0_med, _ = pott_best(C0, gt, rng, DRAWS)
        nrm = unit(both[3:6])
        ndot = nrm.T @ unit(gt)
        rows.append(dict(pot=pot, piece=piece, n=both.shape[1],
                         rel_gt=ang_deg(rel, gt),
                         pott_both_best=b_best, pott_both_med=b_med,
                         pott_s0_best=s0_best, pott_s0_med=s0_med,
                         mean_abs_ndot=float(np.mean(np.abs(ndot))),
                         frac_inward=float(np.mean(ndot < 0.0)), valid=n_d))
        print("[B4] %s %s rel %.2f  both best %.2f med %.2f  s0 best %.2f  |n.a| %.3f inward %.3f"
              % (pot, stem, rows[-1]["rel_gt"], b_best, b_med, s0_best,
                 rows[-1]["mean_abs_ndot"], rows[-1]["frac_inward"]), flush=True)
    p = os.path.join(OUT, "b4_pottmann.tsv")
    with open(p, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), delimiter="\t")
        w.writeheader()
        w.writerows(rows)
    print("[B4] wrote", p, len(rows), "pieces")


if __name__ == "__main__":
    main()
