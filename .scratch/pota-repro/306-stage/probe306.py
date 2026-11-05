#!/usr/bin/env python3
"""probe306.py -- ticket 306 Stage A: the axis candidate pool BEFORE dedup and before
the cost prune, plus the provenance probe (A3).

Why a probe and not run_potsac: the shipped chain keeps the 10 lowest-GM Pottmann
draws (num_candidates=10), 10-deg-dedups them and prunes with cost < cost[0]*1.1.
Three different cuts therefore decide what reaches the axis file, and run_potsac
only ever shows the survivors. This dumps all 1,000 draws with the same stage-1
refinement the shipped code applies, so the cuts can be attributed one by one:
  cut 0  num_candidates=10        (rank_gm >= 10)
  cut 1  10-deg dedup             (drop_dedup)
  cut 2  cost < cost[0]*1.1       (drop_prune)
Nothing here is used by the shipped rule; released axes are read to SCORE only
(angle columns + the A3 probe), never to choose anything.

Modes
  pool      --pieces 1,7,8 --seeds 0,1 --trunc 0,1
            per (piece, truncate, seed): candidates.tsv (1000 rows), clusters.tsv,
            survivors.tsv (the pipeline's stage-2 output for every survivor),
            faithful.xyz (exact shipped replica, for the parity check)
  released  --piece 8 --trunc 0,1 --line 1
            A3: cost at the authors' released line on each cloud, 8-direction
            perturb-and-re-refine at 5 deg, and a 1-deg cost arc around it.

Every cost is reported raw and per point (cost/n): the two clouds have different
point counts, so only the per-point column is comparable between them.
"""
import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from sfs_axes.cao import compute_biaxial_cao_error           # noqa: E402
from sfs_axes.io_axes import direction_angle_deg, read_axes  # noqa: E402
from sfs_axes.io_surfaces import read_surfaces, surface_path  # noqa: E402
from sfs_axes.potsac import (DEDUP_COS, compute_axis_of_symmetry,  # noqa: E402
                             effective_step, refine_axis)
from sfs_axes.robust import (apply_robustifier, robustifier_gm,  # noqa: E402
                             robustifier_huber)

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"


# ---------------------------------------------------------------- costs
def resid(vt, X):
    return np.atleast_1d(compute_biaxial_cao_error(vt, X))


def cost_huber(vt, X):
    return float(np.sum(apply_robustifier(robustifier_huber, resid(vt, X))))


def cost_gm(vt, X):
    return float(np.sum(apply_robustifier(robustifier_gm, resid(vt, X))))


def n_inlier_gm(vt, X):
    rob = apply_robustifier(robustifier_gm, resid(vt, X))
    return int(np.sum(np.abs(rob) < 1.0))


# ---------------------------------------------------------------- helpers
def unit_dirs(vt):
    v = np.asarray(vt, dtype=float)[0:3, :]
    return v / np.linalg.norm(v, axis=0)


def read_released(pot, piece):
    p = os.path.join(CORPUS, "Axes", "Pot_%s_Piece_%02d_Axis.xyz" % (pot, piece))
    if not os.path.isfile(p):
        return None
    return read_axes(p)          # (6, K) [dir; pos]


def angles_to_released(vt, rel, k=None):
    """min / per-line unsigned direction angles (deg) of vt vs the released lines."""
    if rel is None:
        return float("nan"), -1, ""
    K = rel.shape[1]
    per = [direction_angle_deg(vt[0:3], rel[0:3, j]) for j in range(K)]
    j = int(np.argmin(per))
    return per[j], j, " ".join("%.3f" % a for a in per)


def dedup_and_prune(v1, h1):
    """Extended _dedup over every candidate, in the given (GM) order.

    Returns (drop_dedup, drop_prune) boolean masks. Same rules as potsac._dedup:
    sim > DEDUP_COS against ANY earlier survivor drops the candidate; the prune
    then keeps cost < cost[first survivor] * 1.1.
    """
    d = unit_dirs(v1)
    K = d.shape[1]
    sim = np.abs(d.T @ d)
    drop_dedup = np.zeros(K, dtype=bool)
    for j in range(1, K):
        if np.any(sim[:j, j] > DEDUP_COS):
            drop_dedup[j] = True
    kept = np.where(~drop_dedup)[0]
    drop_prune = np.zeros(K, dtype=bool)
    if kept.size:
        c0 = h1[kept[0]]
        for i in kept:
            if not (h1[i] < c0 * 1.1):
                drop_prune[i] = True
    return drop_dedup, drop_prune


def greedy_clusters(v1, order):
    """Greedy 10-deg clustering in GM order: first cluster within 10 deg wins,
    otherwise a new cluster. The representative is the cluster's first member --
    exactly the candidate the shipped dedup would keep."""
    d = unit_dirs(v1)
    K = d.shape[1]
    assign = np.full(K, -1, dtype=int)
    reps = []
    for i in order:
        for ci, rj in enumerate(reps):
            if abs(float(d[:, i] @ d[:, rj])) > DEDUP_COS:
                assign[i] = ci
                break
        else:
            assign[i] = len(reps)
            reps.append(int(i))
    return assign, np.array(reps, dtype=int)


def stage2(vt, C):
    """The pipeline's stage-2 refinement (all points, tol 1e-9)."""
    return refine_axis(vt, C, 2, 300, 1e-9)


# ---------------------------------------------------------------- pool mode
def run_case(pot, piece, C, rel, seed, limit, outdir, tag):
    t0 = time.time()
    n = C.shape[1]
    step = effective_step(n, 10)
    Cd = C[:, 0:n:step]
    vt, _inl_gm, gm_c, _samples = compute_axis_of_symmetry(
        Cd, rng=np.random.default_rng(seed))
    K = vt.shape[1]
    if limit:
        K = min(K, limit)
        vt = vt[:, 0:K]

    # stage 1: refine every draw exactly as the pipeline refines its survivors
    v1 = np.empty_like(vt)
    h1 = np.empty(K)
    g1 = np.empty(K)
    for i in range(K):
        v1[:, i] = refine_axis(vt[:, i], Cd, 2, 300, 1e-3)
        h1[i] = cost_huber(v1[:, i], Cd)
        g1[i] = cost_gm(v1[:, i], Cd)

    # all-points cost of the same axis (no extra refinement -- this is the
    # candidate's cost on the whole cloud, which is what A1 asks for)
    h2 = np.empty(K)
    g2 = np.empty(K)
    in2 = np.empty(K, dtype=int)
    for i in range(K):
        h2[i] = cost_huber(v1[:, i], C)
        g2[i] = cost_gm(v1[:, i], C)
        in2[i] = n_inlier_gm(v1[:, i], C)

    drop_dedup, drop_prune = dedup_and_prune(v1, h1)
    keep = ~(drop_dedup | drop_prune)
    assign, reps = greedy_clusters(v1, np.arange(K))

    # the shipped pipeline, replicated from the same draws: top-10 by GM, dedup,
    # prune, then stage-2 on all points.
    head = min(10, K)
    dd10, dp10 = dedup_and_prune(v1[:, :head], h1[:head])
    surv = np.where(~(dd10 | dp10))[0]
    v2 = np.empty((6, surv.size))
    cost2 = np.empty(surv.size)
    for k, i in enumerate(surv):
        v2[:, k] = stage2(v1[:, i], C)
        cost2[k] = cost_huber(v2[:, k], C)
    order2 = np.argsort(cost2, kind="stable")
    v2, cost2 = v2[:, order2], cost2[order2]

    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "candidates.tsv"), "w") as fh:
        fh.write("rank_gm\tcluster\tis_cluster_rep\tgm_cd\thuber_cd\thuber_all"
                 "\tgm_all\tinl_all\tdx\tdy\tdz\tang_rel_min\tang_rel_idx"
                 "\tang_rel_all\tdrop_dedup\tdrop_prune\tin_top10\tkept\n")
        for i in range(K):
            a, j, alls = angles_to_released(v1[:, i], rel)
            fh.write("%d\t%d\t%d\t%.10g\t%.10g\t%.10g\t%.10g\t%d\t%.10f\t%.10f\t%.10f"
                     "\t%.4f\t%d\t%s\t%d\t%d\t%d\t%d\n"
                     % (i, assign[i], int(i in set(reps.tolist())), g1[i], h1[i], h2[i],
                        g2[i], in2[i], v1[0, i], v1[1, i], v1[2, i], a, j, alls,
                        int(drop_dedup[i]), int(drop_prune[i]), int(i < 10),
                        int(keep[i])))

    # cluster table
    first_surv = int(np.where(~drop_dedup)[0][0]) if np.any(~drop_dedup) else -1
    c0 = h1[first_surv] if first_surv >= 0 else float("nan")
    with open(os.path.join(outdir, "clusters.tsv"), "w") as fh:
        fh.write("cluster\tsize\tfirst_rank_gm\tgm_cd_of_rep\thuber_cd_rep"
                 "\thuber_cd_min\thuber_all_min\tinl_all_of_best\tang_rel_min"
                 "\tang_rel_idx\tdrop_prune\tin_top10\tkept\n")
        for ci in range(reps.size):
            m = np.where(assign == ci)[0]
            r = int(reps[ci])
            best = m[int(np.argmin(h2[m]))]
            a, j, _ = angles_to_released(v1[:, best], rel)
            fh.write("%d\t%d\t%d\t%.10g\t%.10g\t%.10g\t%.10g\t%d\t%.4f\t%d\t%d\t%d\t%d\n"
                     % (ci, m.size, r, g1[r], h1[r], float(h1[m].min()),
                        float(h2[m].min()), in2[best], a, j,
                        int(h1[r] >= c0 * 1.1), int(m.min() < 10), int(keep[r])))

    # survivors after the FULL dedup+prune, with their stage-2 refinement
    with open(os.path.join(outdir, "survivors.tsv"), "w") as fh:
        fh.write("rank_gm\tcluster\thuber_cd\thuber_all_stage2\tang_rel_min"
                 "\tang_rel_idx\tdx\tdy\tdz\n")
        for i in np.where(keep)[0]:
            vv = stage2(v1[:, i], C)
            a, j, _ = angles_to_released(vv, rel)
            fh.write("%d\t%d\t%.10g\t%.10g\t%.4f\t%d\t%.10f\t%.10f\t%.10f\n"
                     % (i, assign[i], h1[i], cost_huber(vv, C), a, j,
                        vv[0], vv[1], vv[2]))

    # exact shipped replica
    with open(os.path.join(outdir, "faithful.xyz"), "w") as fh:
        for k in range(v2.shape[1]):
            row = np.r_[v2[3:6, k], v2[0:3, k]]
            fh.write("%.12f %.12f %.12f %.12f %.12f %.12f\n" % tuple(row))

    # the draws themselves, for A3-style reuse: GM-sorted candidate 0
    hdr = dict(pot=pot, piece=piece, seed=seed, tag=tag, n=int(n),
               n0=int(C.shape[1]), step=int(step), K=int(K),
               n_clusters=int(reps.size), n_kept=int(keep.sum()),
               faithful_K=int(v2.shape[1]), secs=round(time.time() - t0, 1))
    with open(os.path.join(outdir, "case.json"), "w") as fh:
        json.dump(hdr, fh, indent=1)
    print("[case] %s %s K=%d clusters=%d kept=%d faithful=%d (%.1fs)"
          % (tag, "seed%d" % seed, K, reps.size, int(keep.sum()),
             int(v2.shape[1]), time.time() - t0), flush=True)
    return hdr, v2


# ---------------------------------------------------------------- A3 probe
def perturbed_axis(d0, p0, basin, deg):
    """[dir; pos] with dir rotated 'deg' from d0 in azimuth k*45 deg of the
    plane perpendicular to d0; the position moment is re-projected so the axis
    still passes as close to the released line as the rotation allows."""
    d0 = d0 / np.linalg.norm(d0)
    a = np.array([1.0, 0.0, 0.0])
    if abs(a @ d0) > 0.9:
        a = np.array([0.0, 1.0, 0.0])
    e1 = a - (a @ d0) * d0
    e1 = e1 / np.linalg.norm(e1)
    e2 = np.cross(d0, e1)
    th = np.radians(deg)
    d = np.cos(th) * d0 + np.sin(th) * (np.cos(np.radians(45 * basin)) * e1
                                        + np.sin(np.radians(45 * basin)) * e2)
    d = d / np.linalg.norm(d)
    p = p0 - (p0 @ d) * d
    return np.r_[d, p]


def run_released(pot, piece, C, rel, line, outdir, tag):
    os.makedirs(outdir, exist_ok=True)
    n = C.shape[1]
    step = effective_step(n, 10)
    Cd = C[:, 0:n:step]
    ref = rel[:, line].copy()
    rows = []
    with open(os.path.join(outdir, "basin.tsv"), "w") as fh:
        fh.write("cloud\tdeg\tbasin\thuber_all\tgm_all\tinl_all\thuber_cd\n")
        for basin in range(8):
            for deg in range(0, 13):
                vt = perturbed_axis(ref[0:3], ref[3:6], basin, float(deg))
                fh.write("%s\t%d\t%d\t%.10g\t%.10g\t%d\t%.10g\n"
                         % (tag, deg, basin, cost_huber(vt, C), cost_gm(vt, C),
                            n_inlier_gm(vt, C), cost_huber(vt, Cd)))
    for basin in range(8):
        for deg in (5.0, 10.0):
            vt0 = perturbed_axis(ref[0:3], ref[3:6], basin, deg)
            c_before = cost_huber(vt0, C)
            vt1 = refine_axis(vt0, C, 2, 300, 1e-9)
            ang = direction_angle_deg(vt1[0:3], ref[0:3])
            rows.append(dict(cloud=tag, basin=basin, start_deg=deg,
                             ang_to_released=ang, returned=int(ang < 2.0),
                             huber_before=c_before, huber_after=cost_huber(vt1, C),
                             huber_after_pt=cost_huber(vt1, C) / n))
    # cost at the released line itself, and after refining from it
    vt_ref = refine_axis(ref.copy(), C, 2, 300, 1e-9)
    with open(os.path.join(outdir, "released.tsv"), "w") as fh:
        fh.write("cloud\tn\tstep\thuber_all\thuber_per_pt\tgm_all\tinl_all"
                 "\thuber_cd\thuber_cd_per_pt\trefined_deg\trefined_huber_pt\n")
        fh.write("%s\t%d\t%d\t%.10g\t%.10g\t%.10g\t%d\t%.10g\t%.10g\t%.4f\t%.10g\n"
                 % (tag, n, step, cost_huber(ref, C), cost_huber(ref, C) / n,
                    cost_gm(ref, C), n_inlier_gm(ref, C),
                    cost_huber(ref, Cd), cost_huber(ref, Cd) / Cd.shape[1],
                    direction_angle_deg(vt_ref[0:3], ref[0:3]),
                    cost_huber(vt_ref, C) / n))
    with open(os.path.join(outdir, "perturb.tsv"), "w") as fh:
        fh.write("cloud\tbasin\tstart_deg\tang_to_released\treturned"
                 "\thuber_before\thuber_after\thuber_after_per_pt\n")
        for r in rows:
            fh.write("%s\t%d\t%.1f\t%.4f\t%d\t%.10g\t%.10g\t%.10g\n"
                     % (r["cloud"], r["basin"], r["start_deg"], r["ang_to_released"],
                        r["returned"], r["huber_before"], r["huber_after"],
                        r["huber_after_pt"]))
    print("[released] %s n=%d step=%d cost_pt=%.6e 8x5deg returned=%d/8"
          % (tag, n, step, cost_huber(ref, C) / n, sum(r["returned"] for r in rows
             if r["start_deg"] == 5.0)), flush=True)
    return rows


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["pool", "released"], default="pool")
    ap.add_argument("--surfaces", default=os.path.join(CORPUS, "Surfaces"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--pot", default="A")
    ap.add_argument("--pieces", default="1,7,8")
    ap.add_argument("--seeds", default="0,1")
    ap.add_argument("--trunc", default="0,1")
    ap.add_argument("--line", type=int, default=1)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    pieces = [int(x) for x in a.pieces.split(",") if x.strip()]
    seeds = [int(x) for x in a.seeds.split(",") if x.strip()]
    truncs = [int(x) for x in a.trunc.split(",") if x.strip()]
    summary = []
    for piece in pieces:
        rel = read_released(a.pot, piece)
        for tr in truncs:
            C0, C1 = read_surfaces(a.surfaces, a.pot, piece, truncate=bool(tr))
            C = np.concatenate([C0, C1], axis=1)
            tag = "P%s%02d_t%d" % (a.pot, piece, tr)
            if a.mode == "pool":
                for seed in seeds:
                    od = os.path.join(a.out, "pool", tag, "s%d" % seed)
                    hdr, _ = run_case(a.pot, piece, C, rel, seed, a.limit, od,
                                      tag + "_s%d" % seed)
                    hdr["trunc"] = tr
                    summary.append(hdr)
            else:
                od = os.path.join(a.out, "released", tag)
                run_released(a.pot, piece, C, rel, a.line, od, tag)
    if a.mode == "pool" and not os.environ.get("PROBE_NO_SUMMARY"):
        with open(os.path.join(a.out, "pool_summary.tsv"), "w") as fh:
            fh.write("tag\tpiece\ttrunc\tseed\tn\tn0\tstep\tK\tn_clusters"
                     "\tn_kept\tfaithful_K\tsecs\n")
            for r in summary:
                fh.write("%s\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%.1f\n"
                         % (r["tag"].rsplit("_s", 1)[0], r["piece"], r["trunc"],
                            r["seed"], r["n"], r["n0"], r["step"], r["K"],
                            r["n_clusters"], r["n_kept"], r["faithful_K"], r["secs"]))
        print("\n".join("%s t=%d s=%d K=%d clusters=%d kept=%d"
                        % (r["tag"], r["trunc"], r["seed"], r["K"],
                           r["n_clusters"], r["n_kept"]) for r in summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())
