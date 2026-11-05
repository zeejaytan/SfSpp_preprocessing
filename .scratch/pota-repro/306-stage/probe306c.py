#!/usr/bin/env python3
"""probe306c.py -- ticket 306 Stage A, second pass: the same candidate pool, with
what a piece-level SELECTION rule needs to see.

probe306.py answered "does the basin exist and which cut kills it".  It did not
record the axis POSITION, so a candidate could be scored only on the cloud the
search ran on.  This pass repeats exactly the same draws (same C, same step, same
rng seed -> identical pool) and adds:

  * the axis position, so any rule can be evaluated offline without re-running;
  * the cost of every candidate on EACH surface separately (per point, so the two
    surfaces are comparable) -- the physical basis for a rule that prefers an
    axis both faces agree on;
  * for each 10-deg cluster representative, a refine on Surface_0 alone and on
    Surface_1 alone, and the cost of each one-surface optimum measured on the
    OTHER surface.  A true symmetry axis of the pair is a mutual fixed point
    (both one-surface optima near the rep, and each optimum cheap on the other
    surface); a basin that wins only on the concatenation is not.

Same rules as the shipped chain for the pool itself (1000 Pottmann draws, stage-1
refine on the sampled cloud at 1e-3, greedy 10-deg clustering in GM order).  The
released axes are read to SCORE only (angle columns); nothing here selects.
"""
import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import probe306 as P  # noqa: E402  (module-level code guarded by __main__)

from sfs_axes.potsac import compute_axis_of_symmetry, effective_step, refine_axis  # noqa: E402
from sfs_axes.io_surfaces import read_surfaces  # noqa: E402
from sfs_axes.io_axes import direction_angle_deg  # noqa: E402

CORPUS = P.CORPUS


def cost_pt(vt, X):
    n = X.shape[1]
    return P.cost_huber(vt, X) / n if n else float("nan")


def run_case(pot, piece, C0, C1, rel, seed, limit, outdir, tag):
    t0 = time.time()
    C = np.concatenate([C0, C1], axis=1)
    n = C.shape[1]
    n0, n1 = C0.shape[1], C1.shape[1]
    step = effective_step(n, 10)
    Cd = C[:, 0:n:step]
    vt, _inl, _gm, _s = compute_axis_of_symmetry(Cd, rng=np.random.default_rng(seed))
    K = vt.shape[1]
    if limit:
        K = min(K, limit)
        vt = vt[:, 0:K]

    v1 = np.empty_like(vt)
    h1 = np.empty(K)
    g1 = np.empty(K)
    for i in range(K):
        v1[:, i] = refine_axis(vt[:, i], Cd, 2, 300, 1e-3)
        h1[i] = P.cost_huber(v1[:, i], Cd)
        g1[i] = P.cost_gm(v1[:, i], Cd)

    # per-surface and whole-cloud cost of the same axis, no extra refinement
    ha = np.empty(K)   # whole cloud
    c0 = np.empty(K)   # Surface_0 only, per point
    c1 = np.empty(K)   # Surface_1 only, per point
    inl = np.empty(K, dtype=int)
    for i in range(K):
        ha[i] = P.cost_huber(v1[:, i], C)
        c0[i] = cost_pt(v1[:, i], C0)
        c1[i] = cost_pt(v1[:, i], C1)
        inl[i] = P.n_inlier_gm(v1[:, i], C)
    mx = np.maximum(c0, c1)
    sm = c0 + c1

    assign, reps = P.greedy_clusters(v1, np.arange(K))

    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "candidates3.tsv"), "w") as fh:
        fh.write("rank_gm\tcluster\tis_cluster_rep\tgm_cd\thuber_cd\thuber_all\tinl_all"
                 "\tc0_pt\tc1_pt\tmax_pt\tsum_pt\tdx\tdy\tdz\tpx\tpy\tpz"
                 "\tang_rel_min\tang_rel_idx\tang_rel_all\n")
        for i in range(K):
            a, j, alls = P.angles_to_released(v1[:, i], rel)
            fh.write("%d\t%d\t%d\t%.10g\t%.10g\t%.10g\t%d\t%.10g\t%.10g\t%.10g\t%.10g"
                     "\t%.10f\t%.10f\t%.10f\t%.10f\t%.10f\t%.10f\t%.4f\t%d\t%s\n"
                     % (i, assign[i], int(i in set(reps.tolist())), g1[i], h1[i], ha[i],
                        inl[i], c0[i], c1[i], mx[i], sm[i],
                        v1[0, i], v1[1, i], v1[2, i], v1[3, i], v1[4, i], v1[5, i],
                        a, j, alls))

    # per-rep: the two one-surface optima and their cross-surface costs
    with open(os.path.join(outdir, "reps3.tsv"), "w") as fh:
        fh.write("cluster\tsize\trank_gm\thuber_cd_rep\thuber_all_rep\tc0_pt\tc1_pt"
                 "\tmax_pt\tsum_pt\tang_rep_s0opt\tang_rep_s1opt\tang_s0opt_s1opt"
                 "\tc1_pt_of_s0opt\tc0_pt_of_s1opt\tmax_cross_pt"
                 "\tang_rel_min\tang_rel_idx\tang_rel_all\n")
        for ci in range(reps.size):
            r = int(reps[ci])
            m = np.where(assign == ci)[0]
            va = refine_axis(v1[:, r], C0, 2, 300, 1e-9)
            vb = refine_axis(v1[:, r], C1, 2, 300, 1e-9)
            a0 = direction_angle_deg(va[0:3], v1[0:3, r])
            a1 = direction_angle_deg(vb[0:3], v1[0:3, r])
            a01 = direction_angle_deg(va[0:3], vb[0:3])
            c1_of_a = cost_pt(va, C1)
            c0_of_b = cost_pt(vb, C0)
            cross = max(cost_pt(va, C0), c1_of_a, cost_pt(vb, C1), c0_of_b)
            ang, j, alls = P.angles_to_released(v1[:, r], rel)
            fh.write("%d\t%d\t%d\t%.10g\t%.10g\t%.10g\t%.10g\t%.10g\t%.10g"
                     "\t%.4f\t%.4f\t%.4f\t%.10g\t%.10g\t%.10g\t%.4f\t%d\t%s\n"
                     % (ci, m.size, r, h1[r], ha[r], c0[r], c1[r], mx[r], sm[r],
                        a0, a1, a01, c1_of_a, c0_of_b, cross, ang, j, alls))

    hdr = dict(pot=pot, piece=piece, seed=seed, tag=tag, n=int(n), n0=int(n0),
               n1=int(n1), step=int(step), K=int(K), n_clusters=int(reps.size),
               secs=round(time.time() - t0, 1))
    with open(os.path.join(outdir, "case3.json"), "w") as fh:
        json.dump(hdr, fh, indent=1)
    print("[case3] %s K=%d clusters=%d (%.1fs)" % (tag, K, reps.size, time.time() - t0),
          flush=True)
    return hdr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--surfaces", default=os.path.join(CORPUS, "Surfaces"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--pot", default="A")
    ap.add_argument("--pieces", default="1,7,8")
    ap.add_argument("--seeds", default="0,1")
    ap.add_argument("--trunc", default="0,1")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    pieces = [int(x) for x in a.pieces.split(",") if x.strip()]
    seeds = [int(x) for x in a.seeds.split(",") if x.strip()]
    truncs = [int(x) for x in a.trunc.split(",") if x.strip()]
    for piece in pieces:
        rel = P.read_released(a.pot, piece)
        for tr in truncs:
            C0, C1 = read_surfaces(a.surfaces, a.pot, piece, truncate=bool(tr))
            tag = "P%s%02d_t%d" % (a.pot, piece, tr)
            for seed in seeds:
                od = os.path.join(a.out, "x", tag, "s%d" % seed)
                run_case(a.pot, piece, C0, C1, rel, seed, a.limit, od, tag + "_s%d" % seed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
