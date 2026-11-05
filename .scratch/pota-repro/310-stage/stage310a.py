#!/usr/bin/env python3
"""stage310a.py -- ticket 310 Stage A: what is different about the lines that seat?

Per (piece, seed) this writes, into <out>/p<piece>/s<seed>/:

  written.tsv   one row per line in the axis file the shipped chain writes
                (run_potsac, the production call: parity with the 308a files is
                exact, checked at seed 0), plus every cluster representative of
                the 1000-draw pool, so the good basin is measured even in the
                seeds where it is not written.
  basins.tsv    one row per 10-deg basin of the pool: size, best draw rank, costs.
  pool.tsv      the 1000 stage-1-refined draws.
  case.json     counts and timings.

Every statistic is computed from the piece's OWN two surfaces. The one exception
is the label column: ang_good is the angle to the axis that seated in ticket 308
(seeds 1/4/5, the three lines agree to 0.19 deg), used to LABEL good vs wrong for
the separation table and the prevalence count -- never as an input to a rule.
Released Axes/ are read for the printed angle columns only.
"""
import argparse
import json
import os
import sys
import time
import traceback
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from sfs_axes.cao import compute_biaxial_cao_error                    # noqa: E402
from sfs_axes.io_axes import direction_angle_deg, read_axes           # noqa: E402
from sfs_axes.io_surfaces import read_surfaces                        # noqa: E402
from sfs_axes.potsac import (DEDUP_COS, compute_axis_of_symmetry,     # noqa: E402
                             effective_step, refine_axis, run_potsac)
from sfs_axes.robust import (apply_robustifier, robustifier_gm,       # noqa: E402
                             robustifier_huber)

CORPUS = os.path.join("/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp")
GOOD = "/tmp/good310.xyz"
QUAL = 1.0          # the paper's inlier threshold, for both kernels


# ------------------------------------------------------------------ basics
def resid(vt, X):
    return np.atleast_1d(compute_biaxial_cao_error(vt, X))


def gm_cost_pt(vt, X):
    """GM-robustified cost per point (the draw-ranking cost, / n)."""
    return float(np.sum(apply_robustifier(robustifier_gm, resid(vt, X)))) / max(X.shape[1], 1)


def huber_pt(vt, X):
    return float(np.sum(apply_robustifier(robustifier_huber, resid(vt, X)))) / max(X.shape[1], 1)


def inl_gm(vt, X):
    rob = apply_robustifier(robustifier_gm, resid(vt, X))
    return float(np.mean(np.abs(rob) < QUAL))


def inl_huber(vt, X):
    r = resid(vt, X)
    return float(np.mean(np.abs(r) < QUAL))


def unit(v):
    return v[0:3] / np.linalg.norm(v[0:3])


def axis_point(v):
    d = unit(v)
    p = np.asarray(v[3:6], dtype=float)
    return p - (p @ d) * d


def line_dist(a, b):
    """Closest approach of two axis LINES (mm)."""
    da, db = unit(a), unit(b)
    c = np.cross(da, db)
    nc = np.linalg.norm(c)
    w = axis_point(b) - axis_point(a)
    if nc < 1e-9:
        return float(np.linalg.norm(w - (w @ da) * da))
    return float(abs(w @ c) / nc)


def pottmann_resid(vt, X):
    """RMS distance (mm) between the candidate axis and each point's normal line.

    The Pottmann condition for an axis of symmetry is that every surface normal
    meets the axis; the Plucker distance between the two 3-D lines is the
    residual of that condition, measured here per wall about the given axis.
    """
    d = unit(vt)
    p0 = axis_point(vt)
    N = X[3:6, :]
    P = X[0:3, :] - p0[:, None]
    c = np.cross(N.T, d)                       # (n, 3)
    nc = np.linalg.norm(c, axis=1)
    num = np.abs(np.sum(P.T * c, axis=1))
    with np.errstate(divide="ignore", invalid="ignore"):
        dist = np.where(nc > 1e-9, num / nc, 0.0)
    return float(np.sqrt(np.mean(dist ** 2)))


def cyl(vt, X):
    d = unit(vt)
    p0 = axis_point(vt)
    rel = X[0:3, :] - p0[:, None]
    h = d @ rel
    rad = rel - np.outer(d, h)
    return h, np.linalg.norm(rad, axis=0)


def profile(vt, X, nb=10):
    """Radius profile r(h) of one wall about vt: (roughness mm, r at bin centres)."""
    h, r = cyl(vt, X)
    lo, hi = float(h.min()), float(h.max())
    if not (hi > lo):
        return float("nan"), np.zeros(nb)
    edges = np.linspace(lo, hi, nb + 1)
    idx = np.clip(np.searchsorted(edges, h, side="right") - 1, 0, nb - 1)
    cen = 0.5 * (edges[:-1] + edges[1:])
    med = np.array([np.median(r[idx == b]) if np.any(idx == b) else np.nan
                    for b in range(nb)])
    ok = ~np.isnan(med)
    if ok.sum() < 2:
        return float("nan"), med
    pred = np.interp(h, cen[ok], med[ok])
    return float(np.sqrt(np.mean((r - pred) ** 2))), med


def thickness(med0, med1):
    """Spread of (outer - inner) radius over the matched axial bins, mm."""
    ok = ~(np.isnan(med0) | np.isnan(med1))
    if ok.sum() < 2:
        return float("nan"), float("nan")
    t = np.maximum(med0[ok], med1[ok]) - np.minimum(med0[ok], med1[ok])
    return float(np.std(t)), float(np.percentile(t, 90) - np.percentile(t, 10))


def point_line_dist(vt, q):
    d = unit(vt)
    w = np.asarray(q, dtype=float) - axis_point(vt)
    return float(np.linalg.norm(w - (w @ d) * d))


# ------------------------------------------------------------------ one seed
COLS = ("piece seed cand kind rank_in_file ang_good cluster basin_size"
        " hub0 hub1 huball worst_pt maxovermin"
        " gm0 gm1 gmall gminl0 gminl1 gminlall hinl0 hinl1"
        " pott0 pott1"
        " a_c0 a_c1 a_c0_c1 ld_c0 ld_c1 ld_c0_c1"
        " c1_of_opt0 c0_of_opt1 opt0_c0_pt opt1_c1_pt"
        " rough0 rough1 thick_std thick_range"
        " d_centroid d_bbox frac_in_r90 n10 n25 basin_rank_hub rank_written_hub"
        " written").split()


def cand_stats(vt, ctx):
    C0, C1, C = ctx["C0"], ctx["C1"], ctx["C"]
    good = ctx["good"]
    ang_good = min(direction_angle_deg(unit(vt), unit(g)) for g in good.T)
    h0, h1 = huber_pt(vt, C0), huber_pt(vt, C1)
    gall = huber_pt(vt, C)
    va = refine_axis(vt.copy(), C0, 2, 300, 1e-9)
    vb = refine_axis(vt.copy(), C1, 2, 300, 1e-9)
    r0, r1 = 0.0, 0.0
    with np.errstate(all="ignore"):
        rough0, m0 = profile(vt, C0)
        rough1, m1 = profile(vt, C1)
        tstd, trange = thickness(m0, m1)
    return dict(ang_good=ang_good, hub0=h0, hub1=h1, huball=gall,
                worst_pt=max(h0, h1), maxovermin=max(h0, h1) / max(min(h0, h1), 1e-30),
                gm0=gm_cost_pt(vt, C0), gm1=gm_cost_pt(vt, C1), gmall=gm_cost_pt(vt, C),
                gminl0=inl_gm(vt, C0), gminl1=inl_gm(vt, C1), gminlall=inl_gm(vt, C),
                hinl0=inl_huber(vt, C0), hinl1=inl_huber(vt, C1),
                pott0=pottmann_resid(vt, C0), pott1=pottmann_resid(vt, C1),
                a_c0=direction_angle_deg(unit(vt), unit(va)),
                a_c1=direction_angle_deg(unit(vt), unit(vb)),
                a_c0_c1=direction_angle_deg(unit(va), unit(vb)),
                ld_c0=line_dist(vt, va), ld_c1=line_dist(vt, vb),
                ld_c0_c1=line_dist(va, vb),
                c1_of_opt0=huber_pt(va, C1), c0_of_opt1=huber_pt(vb, C0),
                opt0_c0_pt=huber_pt(va, C0), opt1_c1_pt=huber_pt(vb, C1),
                rough0=rough0, rough1=rough1, thick_std=tstd, thick_range=trange,
                d_centroid=point_line_dist(vt, ctx["cent"]),
                d_bbox=point_line_dist(vt, ctx["bboxc"]),
                frac_in_r90=float(np.mean(cyl(vt, C)[1] <= ctx["r90good"])))


def run_seed(job):
    piece, seed, outroot, pot, surfs, goodp = job
    t0 = time.time()
    C0, C1 = read_surfaces(surfs, pot, piece, truncate=False)
    C = np.concatenate([C0, C1], axis=1)
    n = C.shape[1]
    good = read_axes(goodp) if os.path.isfile(goodp) else np.zeros((6, 0))
    ctx = dict(C0=C0, C1=C1, C=C, good=good, cent=C[0:3, :].mean(axis=1))
    bmin, bmax = C[0:3, :].min(axis=1), C[0:3, :].max(axis=1)
    ctx["bboxc"] = 0.5 * (bmin + bmax)
    if good.shape[1]:
        ctx["r90good"] = float(np.percentile(cyl(good[:, 0], C)[1], 90))
    else:
        ctx["r90good"] = float(np.percentile(cyl(np.r_[0, 0, 1, 0, 0, 0.], C)[1], 90))

    # --- the written file: the production call, no replication
    W = run_potsac(C0, C1, rng=np.random.default_rng(seed))
    nw = W.shape[1]

    # --- the pool: the same 1000 draws, stage-1 refined, as the pipeline sees them
    step = effective_step(n, None)
    Cd = C[:, 0:n:step]
    vt_all, _inl, gm_cd, _s = compute_axis_of_symmetry(Cd, rng=np.random.default_rng(seed))
    K = vt_all.shape[1]
    V1 = np.empty_like(vt_all)
    hcd = np.empty(K)
    for i in range(K):
        V1[:, i] = refine_axis(vt_all[:, i], Cd, 2, 300, 1e-3)
        hcd[i] = float(np.sum(apply_robustifier(robustifier_huber, resid(V1[:, i], Cd))))
    hpool = np.array([huber_pt(V1[:, i], C) for i in range(K)])

    # --- 10-deg basins of the pool, in draw-GM order (the shipped order)
    dreps, assign = [], np.full(K, -1, dtype=int)
    for i in range(K):
        hit = -1
        for ci, rj in enumerate(dreps):
            if abs(float(unit(V1[:, i]) @ unit(V1[:, rj]))) > DEDUP_COS:
                hit = ci
                break
        if hit >= 0:
            assign[i] = hit
        else:
            assign[i] = len(dreps)
            dreps.append(i)
    dreps = np.array(dreps, dtype=int)
    nb = dreps.size
    bmin_hub = np.array([hpool[assign == c].min() for c in range(nb)])
    bsize = np.array([int(np.sum(assign == c)) for c in range(nb)])
    brank = np.empty(nb, dtype=int)
    brank[np.argsort(bmin_hub, kind="stable")] = np.arange(nb)

    # --- written lines: label, occupancy, rank
    wang = [min(direction_angle_deg(unit(W[:, k]), unit(g)) for g in good.T)
            for k in range(nw)] if good.shape[1] else [float("nan")] * nw
    wbas = []
    for k in range(nw):
        hit = -1
        for ci, rj in enumerate(dreps):
            if abs(float(unit(W[:, k]) @ unit(V1[:, rj]))) > DEDUP_COS:
                hit = ci
                break
        wbas.append(hit)
    whub = np.array([huber_pt(W[:, k], C) for k in range(nw)])

    os.makedirs(outroot, exist_ok=True)
    rows = []
    with open(os.path.join(outroot, "written.tsv"), "w") as fh:
        fh.write("\t".join(COLS) + "\n")
        for k in range(nw):
            st = cand_stats(W[:, k], ctx)
            n10 = int(np.sum([direction_angle_deg(unit(W[:, k]), unit(V1[:, i])) < 10
                              for i in range(K)]))
            n25 = int(np.sum([direction_angle_deg(unit(W[:, k]), unit(V1[:, i])) < 25
                              for i in range(K)]))
            row = dict(piece=piece, seed=seed, cand="W%d" % k,
                       kind="good" if wang[k] < 5.0 else "wrong",
                       rank_in_file=k, ang_good=wang[k], cluster=wbas[k],
                       basin_size=int(bsize[wbas[k]]) if wbas[k] >= 0 else -1)
            row.update(st)
            row.update(n10=n10, n25=n25,
                       basin_rank_hub=int(brank[wbas[k]]) if wbas[k] >= 0 else -1,
                       rank_written_hub=int(np.sum(whub < whub[k])), written=1)
            rows.append(row)
        # cluster representatives (the pool's own basins), good ones included
        for ci in range(nb):
            r = int(dreps[ci])
            st = cand_stats(V1[:, r], ctx)
            row = dict(piece=piece, seed=seed, cand="R%d" % ci, kind="cand",
                       rank_in_file=-1, ang_good=st["ang_good"], cluster=ci,
                       basin_size=int(bsize[ci]))
            row.update(st)
            row.update(n10=int(bsize[ci]), n25=int(bsize[ci]),
                       basin_rank_hub=int(brank[ci]),
                       rank_written_hub=-1, written=0)
            rows.append(row)
    with open(os.path.join(outroot, "written.tsv"), "w") as fh:
        fh.write("\t".join(COLS) + "\n")
        for row in rows:
            fh.write("\t".join(str(row[c]) for c in COLS) + "\n")

    with open(os.path.join(outroot, "basins.tsv"), "w") as fh:
        fh.write("cluster\tsize\tmin_draw_rank\tmin_hub_all\trank_hub\tang_good"
                 "\twritten\tworst_pt\ta_c0\ta_c1\ta_c0_c1\n")
        for ci in range(nb):
            m = np.where(assign == ci)[0]
            r = int(dreps[ci])
            ag = min(direction_angle_deg(unit(V1[:, r]), unit(g)) for g in good.T) \
                if good.shape[1] else float("nan")
            wrote = int(any(wbas[k] == ci for k in range(nw)))
            st = cand_stats(V1[:, r], ctx)
            fh.write("%d\t%d\t%d\t%.6e\t%d\t%.3f\t%d\t%.6e\t%.3f\t%.3f\t%.3f\n" %
                     (ci, int(bsize[ci]), int(m.min()), float(bmin_hub[ci]),
                      int(brank[ci]), ag, wrote, st["worst_pt"], st["a_c0"],
                      st["a_c1"], st["a_c0_c1"]))

    with open(os.path.join(outroot, "pool.tsv"), "w") as fh:
        fh.write("rank\tgm_cd\thuber_cd\thub_pt_all\tang_good\tcluster\tis_rep\n")
        repset = set(dreps.tolist())
        for i in range(K):
            ag = min(direction_angle_deg(unit(V1[:, i]), unit(g)) for g in good.T) \
                if good.shape[1] else float("nan")
            fh.write("%d\t%.8e\t%.8e\t%.8e\t%.3f\t%d\t%d\n" %
                     (i, gm_cd[i], hcd[i], hpool[i], ag, assign[i],
                      int(i in repset)))

    hdr = dict(pot=pot, piece=piece, seed=seed, n=int(n), n0=int(C0.shape[1]),
               n1=int(C1.shape[1]), step=int(step), written=int(nw), K=int(K),
               basins=int(nb),
               written_good=int(sum(1 for a in wang if a < 5.0)),
               best_written_ang=float(min(wang)) if wang else float("nan"),
               good_in_pool=int(np.sum([min(direction_angle_deg(unit(V1[:, i]), unit(g))
                                            for g in good.T) < 5.0 for i in range(K)]))
               if good.shape[1] else -1,
               secs=round(time.time() - t0, 1))
    with open(os.path.join(outroot, "case.json"), "w") as fh:
        json.dump(hdr, fh, indent=1)
    return hdr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--pot", default="A")
    ap.add_argument("--pieces", default="8")
    ap.add_argument("--seeds", default="0:24")
    ap.add_argument("--corpus", default=CORPUS)
    ap.add_argument("--good", default=GOOD)
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
    print("[stage310a] %d seed-jobs, jobs=%d" % (len(jobs), a.jobs), flush=True)
    hdrs = []
    if a.jobs > 1:
        with Pool(a.jobs) as pool:
            for h in pool.imap_unordered(run_seed, jobs):
                hdrs.append(h)
                print("[case] p%d s%d n=%d written=%d good_written=%d best=%.2f "
                      "basins=%d (%.1fs)" % (h["piece"], h["seed"], h["n"],
                                             h["written"], h["written_good"],
                                             h["best_written_ang"], h["basins"],
                                             h["secs"]), flush=True)
    else:
        for j in jobs:
            h = run_seed(j)
            hdrs.append(h)
            print("[case] p%d s%d n=%d written=%d good_written=%d best=%.2f (%.1fs)" %
                  (h["piece"], h["seed"], h["n"], h["written"], h["written_good"],
                   h["best_written_ang"], h["secs"]), flush=True)
    with open(os.path.join(a.out, "summary.tsv"), "w") as fh:
        keys = ["piece", "seed", "n", "n0", "n1", "step", "written", "basins", "K",
                "written_good", "best_written_ang", "good_in_pool", "secs"]
        fh.write("\t".join(keys) + "\n")
        for h in sorted(hdrs, key=lambda r: (r["piece"], r["seed"])):
            fh.write("\t".join(str(h[k]) for k in keys) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
