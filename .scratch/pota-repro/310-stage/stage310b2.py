#!/usr/bin/env python3
"""stage310b2.py -- ticket 310 B2: does the basin rule write the seating axis?

Same pool, same seeds, two orders:
  ON  (ticket 310 default): cluster the pool -> refine every basin on ALL points
      -> re-cluster -> rank by the worse wall's cost -> cap.
  OFF (pre-310, the authors' order): rank the stage-1 basin reps -> cap ->
      refine only the survivors.
Each seed is one pool (SFS_AXES_UNION_SEEDS semantics: seeds=<that seed>), so the
comparison is like-for-like with the per-seed files of run 20261105-0532 (308a).

Blind: the clouds and the seeds only. The seating axis is used for SCORING.
"""
import argparse
import importlib
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import sfs_axes.potsac as ps                                    # noqa: E402
from sfs_axes.io_axes import direction_angle_deg, read_axes     # noqa: E402
from sfs_axes.io_surfaces import read_surfaces                  # noqa: E402

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"


def unit(v):
    return v[0:3] / np.linalg.norm(v[0:3])


def angled(vt, good):
    return min(direction_angle_deg(unit(vt), unit(g)) for g in good.T)


def run_one(job):
    """One (arm, piece, seed) case in its own process, so the env switch bites.

    PAPER  the shipped CLI default (run_potsac, one seed): top-10 draws by cost,
           10-degree dedup, stage-2 refine -- the chain ticket 308 wrote.
    UNION0 run_potsac_union with SFS_AXES_CONVERGE_BEFORE_RANK=0: every draw
           clustered first, basins ranked on the stage-1 cost, cap, then refine.
    BASIN  the same union with the rule on (SFS_AXES_CONVERGE_BEFORE_RANK=1,
           the ticket-310 default): cluster, converge every basin on all points,
           re-cluster, rank by the worse wall's cost, cap.
    """
    arm, pot, piece, seed, surfs, goodp, outdir, cap = job
    os.environ["SFS_AXES_CONVERGE_BEFORE_RANK"] = "0" if arm == "UNION0" else "1"
    importlib.reload(ps)
    t0 = time.time()
    C0, C1 = read_surfaces(surfs, pot, piece, truncate=False)
    good = read_axes(goodp) if goodp and os.path.isfile(goodp) else None
    if arm == "PAPER":
        vt = ps.run_potsac(C0, C1, rng=np.random.default_rng(int(seed)))
    else:
        vt = ps.run_potsac_union(C0, C1, seeds=[int(seed)], max_candidates=cap)
    angs = [angled(vt[:, j], good) for j in range(vt.shape[1])] if good is not None else []
    w = [ps._worst_surface_cost(vt[:, j], C0, C1) for j in range(vt.shape[1])]
    margin = (w[1] / w[0]) if (len(w) > 1 and w[0] > 0) else float("nan")
    row = dict(arm=arm, pot=pot, piece=int(piece), seed=int(seed),
               K=int(vt.shape[1]), secs=round(time.time() - t0, 2),
               best_ang=(min(angs) if angs else -1.0),
               line0_ang=(angs[0] if angs else -1.0),
               within5=int(min(angs) < 5.0) if angs else -1,
               margin=round(margin, 5) if margin == margin else -1.0,
               all_ang=";".join("%.2f" % a for a in angs))
    # keep the written file for the seating arm
    d = os.path.join(outdir, "arms", arm, "p%d" % int(piece))
    os.makedirs(d, exist_ok=True)
    # position-first, the axis-file convention (io_axes.write_axes); an earlier version
    # of this line wrote direction-first, which no seating run ever consumed.
    from sfs_axes.io_axes import write_axes
    write_axes(os.path.join(d, "s%d.xyz" % int(seed)), vt)
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--pot", default="A")
    ap.add_argument("--pieces", default="8")
    ap.add_argument("--seeds", default="0:12")
    ap.add_argument("--arms", default="ON,OFF")
    ap.add_argument("--cap", type=int, default=6)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--corpus", default=CORPUS)
    ap.add_argument("--good", default="/tmp/good310.xyz")
    a = ap.parse_args()
    surfs = os.path.join(a.corpus, "Surfaces")
    pieces = [int(x) for x in a.pieces.split(",") if x.strip()]
    if ":" in a.seeds:
        lo, hi = a.seeds.split(":")
        seeds = list(range(int(lo), int(hi)))
    else:
        seeds = [int(x) for x in a.seeds.split(",") if x.strip()]
    jobs = [(arm, a.pot, p, s, surfs, a.good, a.out, a.cap)
            for arm in a.arms.split(",") for p in pieces for s in seeds]
    print("[stage310b2] %d cases, jobs=%d, pieces=%s seeds=%d" %
          (len(jobs), a.jobs, pieces, len(seeds)), flush=True)
    rows = []
    if a.jobs > 1:
        with Pool(a.jobs) as pool:
            for r in pool.imap_unordered(run_one, jobs):
                rows.append(r)
                print("[b2] %s p%d s%d K=%d best=%6.2f line0=%6.2f w5=%d (%.1fs)"
                      % (r["arm"], r["piece"], r["seed"], r["K"], r["best_ang"],
                         r["line0_ang"], r["within5"], r["secs"]), flush=True)
    else:
        for j in jobs:
            r = run_one(j)
            rows.append(r)
            print("[b2] %s p%d s%d K=%d best=%6.2f w5=%d (%.1fs)"
                  % (r["arm"], r["piece"], r["seed"], r["K"], r["best_ang"],
                     r["within5"], r["secs"]), flush=True)
    keys = ["arm", "pot", "piece", "seed", "K", "secs", "best_ang", "line0_ang",
            "within5", "margin", "all_ang"]
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "b2.tsv"), "w") as fh:
        fh.write("\t".join(keys) + "\n")
        for r in sorted(rows, key=lambda x: (x["arm"], x["piece"], x["seed"])):
            fh.write("\t".join(str(r[k]) for k in keys) + "\n")
    for arm in sorted(set(r["arm"] for r in rows)):
        sel = [r for r in rows if r["arm"] == arm and r["within5"] >= 0]
        if sel:
            print("[B2] %s: %d of %d seeds write a line within 5 deg; "
                  "line0 within 5: %d; median K %.0f; median %.0fs/piece"
                  % (arm, sum(r["within5"] for r in sel), len(sel),
                     sum(1 for r in sel if r["line0_ang"] < 5.0),
                     np.median([r["K"] for r in sel]),
                     np.median([r["secs"] for r in sel])), flush=True)
    with open(os.path.join(a.out, "b2.json"), "w") as fh:
        json.dump(rows, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
