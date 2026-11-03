#!/usr/bin/env python3
"""t71 stage B5 (lead): the deployable question. Generate a Pottmann pool, rank it by each cost,
pick the argmin, and compare with GT. No GT is used in the choice.

B4 proved the answer is IN the pool (best-of-400 Pottmann = 0.95 deg median, better than the
released axes at 2.78 deg). B5 asks whether any of the six residuals can FIND it without an oracle.
"""
import os, sys, csv
import numpy as np

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
OUT = sys.argv[1] if len(sys.argv) > 1 else "."
DRAWS = 400
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))

from sfs_axes.pottmann import compute_pottmann_axis
from costs71 import COSTS, canonicalize, cost_value


def load(path):
    a = np.loadtxt(path, usecols=(0, 1, 2, 3, 4, 5), ndmin=2)
    return np.asarray(a, dtype=float).T


def unit(v):
    n = np.linalg.norm(v, axis=0)
    return v / np.where(n > 1e-12, n, 1.0)


def ang_deg(a, b):
    c = abs(float(np.dot(unit(np.asarray(a).reshape(3)), unit(np.asarray(b).reshape(3)))))
    return float(np.degrees(np.arccos(min(1.0, c))))


def main():
    os.makedirs(OUT, exist_ok=True)
    sd = os.path.join(CORPUS, "Surfaces")
    stems = sorted(fn.replace("_Surface_0.xyz", "") for fn in os.listdir(sd)
                   if fn.endswith("_Surface_0.xyz"))
    rng = np.random.default_rng(71)
    rows = []
    for stem in stems:
        gpath = os.path.join(CORPUS, "Ground Truth Axes", stem + "_Axis.xyz")
        if not os.path.isfile(gpath):
            continue
        gt = np.loadtxt(gpath, ndmin=2)[0, 3:6]
        C0 = load(os.path.join(sd, stem + "_Surface_0.xyz"))
        C1 = load(os.path.join(sd, stem + "_Surface_1.xyz"))
        both = np.concatenate([C0, C1], axis=1)
        n = both.shape[1]
        pool = []
        for _ in range(DRAWS):
            idx = rng.choice(n, size=6, replace=False)
            try:
                d = compute_pottmann_axis(both[:, idx])
            except Exception:
                continue
            if d is None or not np.all(np.isfinite(d)):
                continue
            pool.append(np.asarray(d, dtype=float).reshape(-1)[0:6])
        if not pool:
            continue
        P = np.column_stack(pool)
        # normalise: direction unit, position orthogonal to direction
        for k in range(P.shape[1]):
            P[:, k] = canonicalize(P[:, k])
        best_true = min(ang_deg(P[0:3, k], gt) for k in range(P.shape[1]))
        row = dict(pot=stem.split("_")[1], piece=stem.split("_")[-1], n=n,
                   n_pool=P.shape[1], pool_best=best_true)
        for cost in COSTS:
            vals = np.array([cost_value(cost, P[:, k], both) for k in range(P.shape[1])])
            if not np.any(np.isfinite(vals)):
                row["pick_" + cost] = float("nan")
                continue
            k = int(np.nanargmin(vals))
            row["pick_" + cost] = ang_deg(P[0:3, k], gt)
        rows.append(row)
        print("[B5] %s %s pool_best %.2f  %s" % (row["pot"], stem, best_true,
              "  ".join("%s %.1f" % (c, row["pick_" + c]) for c in COSTS)), flush=True)
    p = os.path.join(OUT, "b5_rank.tsv")
    with open(p, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), delimiter="\t")
        w.writeheader()
        w.writerows(rows)
    print("[B5] wrote", p, len(rows))


if __name__ == "__main__":
    main()
