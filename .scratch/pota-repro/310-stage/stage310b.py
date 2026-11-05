#!/usr/bin/env python3
"""stage310b.py -- ticket 310 A4(ii): what does the pool look like after the FULL refine?

Stage A (stage310a.py) measured the basins as the shipped chain sees them: candidates
refined on the sampled cloud Cd at tolerance 1e-3. On Piece 08 that leaves a shallow
valley of near-duplicate axes from 0 to about 24 deg off the seating axis, all at the
same cost -- which is why no cost statistic separates them.

This instrument takes the same 1000 draws, refines the basin representatives on ALL
points at 1e-9 (stage 2, the tolerance the written file gets), and re-clusters at
10 deg. Two questions:

  1. does an unconverged neighbour of the seating axis collapse ONTO it? (how many of
     the pre-refine reps land within 5 deg of the seating axis)
  2. after that collapse, how many distinct basins remain, does the file's shortlist
     contain the seating axis, and what rank does it get by each cost?

Blind in the sense that matters: everything here is a function of the piece's own two
surfaces and the seeds. The seating axis is used for SCORING only (ang_good, is_good).
"""
import argparse
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from sfs_axes.cao import compute_biaxial_cao_error                       # noqa: E402
from sfs_axes.io_axes import direction_angle_deg, read_axes             # noqa: E402
from sfs_axes.io_surfaces import read_surfaces                          # noqa: E402
from sfs_axes.potsac import (DEDUP_COS, compute_axis_of_symmetry,       # noqa: E402
                             effective_step, refine_axis)
from sfs_axes.robust import (apply_robustifier, robustifier_huber)      # noqa: E402

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"


def unit(v):
    return v[0:3] / np.linalg.norm(v[0:3])


def resid(vt, X):
    return np.atleast_1d(compute_biaxial_cao_error(vt, X))


def hub_pt(vt, X):
    return float(np.sum(apply_robustifier(robustifier_huber, resid(vt, X)))) / max(X.shape[1], 1)


def cluster(V, cos=DEDUP_COS):
    """Greedy clustering in the given column order; returns (rep idx, assign, sizes)."""
    assign = np.full(V.shape[1], -1, dtype=int)
    reps = []
    for i in range(V.shape[1]):
        hit = -1
        for ci, rj in enumerate(reps):
            if abs(float(unit(V[:, i]) @ unit(V[:, rj]))) > cos:
                hit = ci
                break
        if hit >= 0:
            assign[i] = hit
        else:
            assign[i] = len(reps)
            reps.append(i)
    sizes = np.array([int(np.sum(assign == c)) for c in range(len(reps))])
    return np.array(reps, dtype=int), assign, sizes


def run_seed(job):
    piece, seed, outdir, pot, surfs, goodp = job
    t0 = time.time()
    C0, C1 = read_surfaces(surfs, pot, piece, truncate=False)
    C = np.concatenate([C0, C1], axis=1)
    n = C.shape[1]
    good = read_axes(goodp)
    step = effective_step(n, None)
    Cd = C[:, 0:n:step]
    vt_all, _i, _c, _s = compute_axis_of_symmetry(Cd, rng=np.random.default_rng(seed))
    K = vt_all.shape[1]
    V1 = np.empty_like(vt_all)
    for i in range(K):
        V1[:, i] = refine_axis(vt_all[:, i], Cd, 2, 300, 1e-3)

    # pre-refine basins (what the shipped chain's shortlist and dedup work on)
    reps0, assign0, sizes0 = cluster(V1)
    # stage 2 on ALL points, for every pre-refine basin representative
    V2 = np.empty((6, reps0.size))
    for j, r in enumerate(reps0):
        V2[:, j] = refine_axis(V1[:, r].copy(), C, 2, 300, 1e-9)
    ang_conv = np.array([min(direction_angle_deg(unit(V2[:, j]), unit(g)) for g in good.T)
                         for j in range(V2.shape[1])])
    hp = np.array([hub_pt(V2[:, j], C) for j in range(V2.shape[1])])

    # re-cluster the converged axes, cheap ones first (the shipped order)
    order = np.argsort(hp, kind="stable")
    reps1, assign1, sizes1 = cluster(V2[:, order])
    rows = []
    for c, j in enumerate(reps1):
        v = V2[:, order[j]]
        ag = min(direction_angle_deg(unit(v), unit(g)) for g in good.T)
        rows.append(dict(
            seed=seed, basin=c, ang_good=ag, size=int(sizes1[c]),
            hub0=hub_pt(v, C0), hub1=hub_pt(v, C1), huball=hp[order[j]],
            worst_pt=max(hub_pt(v, C0), hub_pt(v, C1)),
            n_conv=int(np.sum(ang_conv < 5.0))))
    # write
    os.makedirs(outdir, exist_ok=True)
    cols = ["seed", "basin", "ang_good", "size", "hub0", "hub1", "huball",
            "worst_pt", "n_conv"]
    with open(os.path.join(outdir, "refined.tsv"), "w") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join(str(r[k]) for k in cols) + "\n")
    # the pre-refine reps' own fate: how many land within 5 deg, where they came from
    with open(os.path.join(outdir, "convergence.tsv"), "w") as fh:
        fh.write("pre_rep\tang0_to_good\tang1_to_good\thuball1\n")
        for j in range(reps0.size):
            a0 = min(direction_angle_deg(unit(V1[:, reps0[j]]), unit(g)) for g in good.T)
            fh.write("%d\t%.4f\t%.4f\t%.6f\n" % (j, a0, ang_conv[j], hp[j]))
    nconv = int(np.sum(ang_conv < 5.0))
    anygood = nconv > 0
    rank_worst = rank_hub = -1
    if anygood:
        ws = sorted([r["worst_pt"] for r in rows])
        hs = sorted([r["huball"] for r in rows])
        gw = min([r["worst_pt"] for r in rows if r["ang_good"] < 5.0])
        gh = min([r["huball"] for r in rows if r["ang_good"] < 5.0])
        rank_worst = int(sum(1 for x in ws if x < gw - 1e-12))
        rank_hub = int(sum(1 for x in hs if x < gh - 1e-12))
    hdr = dict(piece=piece, seed=seed, n=int(n), K=int(K), step=int(step),
               pre_basins=int(reps0.size), post_basins=int(len(rows)),
               conv_within5=nconv, has_good=int(anygood),
               rank_worst=rank_worst, rank_huball=rank_hub,
               best_ang=float(min(r["ang_good"] for r in rows)),
               secs=round(time.time() - t0, 1))
    with open(os.path.join(outdir, "case.json"), "w") as fh:
        json.dump(hdr, fh, indent=1)
    return hdr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--pot", default="A")
    ap.add_argument("--pieces", default="8")
    ap.add_argument("--seeds", default="0:24")
    ap.add_argument("--corpus", default=CORPUS)
    ap.add_argument("--good", default="/tmp/good310.xyz")
    ap.add_argument("--jobs", type=int, default=1)
    a = ap.parse_args()
    surfs = os.path.join(a.corpus, "Surfaces")
    pieces = [int(x) for x in a.pieces.split(",") if x.strip()]
    if ":" in a.seeds:
        lo, hi = a.seeds.split(":")
        seeds = list(range(int(lo), int(hi)))
    else:
        seeds = [int(x) for x in a.seeds.split(",") if x.strip()]
    jobs = []
    for piece in pieces:
        for seed in seeds:
            od = os.path.join(a.out, "p%d" % piece, "s%d" % seed)
            if os.path.isfile(os.path.join(od, "case.json")):
                continue
            jobs.append((piece, seed, od, a.pot, surfs, a.good))
    print("[stage310b] %d seed-jobs, jobs=%d" % (len(jobs), a.jobs), flush=True)
    hdrs = []
    if a.jobs > 1:
        with Pool(a.jobs) as pool:
            for h in pool.imap_unordered(run_seed, jobs):
                hdrs.append(h)
                print("[case] p%d s%d pre=%d post=%d conv5=%d rank_worst=%d rank_hub=%d "
                      "best=%.2f (%.1fs)" % (h["piece"], h["seed"], h["pre_basins"],
                                             h["post_basins"], h["conv_within5"],
                                             h["rank_worst"], h["rank_huball"],
                                             h["best_ang"], h["secs"]), flush=True)
    else:
        for j in jobs:
            h = run_seed(j)
            hdrs.append(h)
            print("[case] p%d s%d conv5=%d post=%d (%.1fs)" %
                  (h["piece"], h["seed"], h["conv_within5"], h["post_basins"], h["secs"]),
                  flush=True)
    keys = ["piece", "seed", "n", "K", "step", "pre_basins", "post_basins",
            "conv_within5", "has_good", "rank_worst", "rank_huball", "best_ang", "secs"]
    with open(os.path.join(a.out, "summary.tsv"), "w") as fh:
        fh.write("\t".join(keys) + "\n")
        for h in sorted(hdrs, key=lambda r: (r["piece"], r["seed"])):
            fh.write("\t".join(str(h[k]) for k in keys) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
