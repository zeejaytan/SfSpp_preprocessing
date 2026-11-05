"""Ticket 310 B4: does SFS_AXES_CONVERGE_BEFORE_RANK=0 restore the pre-310 behaviour exactly?

The switch is only honest if OFF is the code that was there before.  This driver runs the
SAME pool through two copies of the package -- one taken from git HEAD (the commit this
ticket started on) and one from the worktree (this ticket's edit) -- and writes both axis
arrays so they can be compared to the last bit.

Usage: stage310p.py --out DIR --pkg DIR --tag NAME --pot A --pieces 8 --seeds 0:2 --cap 6
   (--pkg is prepended to sys.path, so DIR must contain sfs_axes/)
"""
import argparse
import json
import os
import sys
import time

import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--pkg", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--pot", default="A")
    ap.add_argument("--pieces", default="8")
    ap.add_argument("--seeds", default="0:2")
    ap.add_argument("--cap", type=int, default=6)
    ap.add_argument("--corpus", default="/data/gpfs/projects/punim2657/sfs_main/"
                                        "original_samples/SfS_pp")
    a = ap.parse_args()
    sys.path.insert(0, a.pkg)

    from sfs_axes.io_surfaces import read_surfaces
    from sfs_axes.potsac import run_potsac_union
    import sfs_axes.potsac as ps

    def rng(spec):
        lo, hi = (spec.split(":") + [None])[:2]
        return range(int(lo), int(hi)) if hi is not None else [int(lo)]

    os.makedirs(a.out, exist_ok=True)
    rows = []
    for piece in [int(x) for x in a.pieces.split(",")]:
        C0, C1 = read_surfaces(a.corpus, a.pot, piece, truncate=False)
        for seed in rng(a.seeds):
            t0 = time.time()
            vt = run_potsac_union(C0, C1, seeds=[seed], max_candidates=a.cap)
            secs = time.time() - t0
            d = os.path.join(a.out, a.tag, "p%d" % piece)
            os.makedirs(d, exist_ok=True)
            np.save(os.path.join(d, "s%d.npy" % seed), np.asarray(vt, float))
            # canonical position-first text, same formatter as the shipped writer
            with open(os.path.join(d, "s%d.xyz" % seed), "w") as f:
                for k in range(vt.shape[1]):
                    f.write("%.12f %.12f %.12f %.12f %.12f %.12f\n" % (
                        vt[2, k], vt[3, k], vt[4, k], vt[0, k], vt[1, k], vt[5, k]))
            rows.append({"piece": piece, "seed": seed, "K": int(vt.shape[1]),
                         "secs": round(secs, 1),
                         "potsac": ps.__file__,
                         "switch": os.environ.get(
                             "SFS_AXES_CONVERGE_BEFORE_RANK", "(unset)")})
            print("[p] %s p%d s%d K=%d %.1fs" % (a.tag, piece, seed, vt.shape[1], secs),
                  flush=True)
    with open(os.path.join(a.out, a.tag, "index.json"), "w") as f:
        json.dump(rows, f, indent=1)


if __name__ == "__main__":
    main()
