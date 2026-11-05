#!/usr/bin/env python3
"""stage310h.py -- ticket 310 A4(iii): does a 10x bigger draw pool help?

For each seed: draw --draws Pottmann axes from the working cloud (the same
compute_axis_of_symmetry the chain uses, max_iters raised), then ask
  (a) how many raw draws are within 5 deg of the seating axis (cheap, exact),
  (b) how many of those are in the first 10 / 30 / 100 by GM cost on the
      sampled cloud (the shipped shortlist is the first 10),
  (c) after stage-1 refining the first 100 by cost plus every good raw draw,
      is a good candidate still in the first 10 by the stage-1 cost?

Blind: the clouds only. The seating axis is used for SCORING (--good).
"""
import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from sfs_axes.cao import compute_biaxial_cao_error                  # noqa: E402
from sfs_axes.io_axes import direction_angle_deg, read_axes         # noqa: E402
from sfs_axes.io_surfaces import read_surfaces                      # noqa: E402
from sfs_axes import potsac as ps                                   # noqa: E402
from sfs_axes.refine import refine_axis                             # noqa: E402
from sfs_axes.robust import apply_robustifier, robustifier_huber    # noqa: E402

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"


def unit(v):
    return v[0:3] / np.linalg.norm(v[0:3])


def ang(vt, good):
    return min(direction_angle_deg(unit(vt), unit(g)) for g in good.T)


def stage1_cost(vt, Cd):
    e = compute_biaxial_cao_error(vt, Cd)
    return float(np.sum(apply_robustifier(robustifier_huber, np.atleast_1d(e))))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--pot", default="A")
    ap.add_argument("--piece", type=int, default=8)
    ap.add_argument("--seeds", default="0,1,2")
    ap.add_argument("--draws", type=int, default=10000)
    ap.add_argument("--good", required=True)
    a = ap.parse_args(argv)
    C0, C1 = read_surfaces(os.path.join(CORPUS, "Surfaces"), a.pot, a.piece,
                           truncate=False)
    C = np.concatenate([C0, C1], axis=1)
    n = C.shape[1]
    step = ps.effective_step(n, None)
    Cd = C[:, 0:n:step]
    good = read_axes(a.good)
    rows = []
    for seed in [int(x) for x in a.seeds.split(",")]:
        t0 = time.time()
        vt = ps.compute_axis_of_symmetry(Cd, rng=np.random.default_rng(seed),
                                        max_iters=a.draws)[0]
        dirs = vt[0:3, :] / np.linalg.norm(vt[0:3, :], axis=0)
        gd = unit(good[0:3, 0])
        angs = np.degrees(np.arccos(np.clip(np.abs(gd @ dirs), -1.0, 1.0)))
        raw_good = np.flatnonzero(angs < 5.0)
        first = {"top10": 0, "top30": 0, "top100": 0}
        for k, lim in (("top10", 10), ("top30", 30), ("top100", 100)):
            first[k] = int(np.sum(raw_good < lim))
        # (c) refine the first 100 by cost plus every good raw draw
        idx = sorted(set(list(range(min(100, vt.shape[1]))) + list(raw_good)))
        ref = []
        for j in idx:
            v = refine_axis(vt[:, j], Cd, 2, 300, 1e-3)
            ref.append((stage1_cost(v, Cd), ang(v, good)))
        ref.sort(key=lambda t: t[0])
        good_in_refined_top10 = int(sum(1 for c, g in ref[:10] if g < 5.0))
        best_rank = next((i for i, (c, g) in enumerate(ref) if g < 5.0), -1)
        rows.append(dict(seed=seed, draws=int(vt.shape[1]), step=step,
                         cd=int(Cd.shape[1]),
                         raw_good=int(raw_good.size),
                         best_raw_ang=round(float(angs.min()), 3),
                         top10=first["top10"], top30=first["top30"],
                         top100=first["top100"],
                         refined=len(idx),
                         good_in_refined10=good_in_refined_top10,
                         best_good_rank=best_rank,
                         secs=round(time.time() - t0, 1)))
        print("[A4iii] seed=%d draws=%d raw_good=%d top10=%d top30=%d top100=%d "
              "good_in_refined_top10=%d (%.0fs)"
              % (seed, vt.shape[1], raw_good.size, first["top10"], first["top30"],
                 first["top100"], good_in_refined_top10, time.time() - t0),
              flush=True)
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "a4iii.tsv"), "w") as fh:
        keys = list(rows[0].keys())
        fh.write("\t".join(keys) + "\n")
        for r in rows:
            fh.write("\t".join(str(r[k]) for k in keys) + "\n")
    with open(os.path.join(a.out, "a4iii.json"), "w") as fh:
        json.dump(rows, fh, indent=1)
    print("[A4iii] seeds with a good draw in the shipped top-10 shortlist: %d of %d"
          % (sum(1 for r in rows if r["top10"] > 0), len(rows)))
    print("[A4iii] seeds where a refined good candidate ranks first-10: %d of %d"
          % (sum(1 for r in rows if r["good_in_refined10"] > 0), len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
