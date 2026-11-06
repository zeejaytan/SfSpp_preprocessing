#!/usr/bin/env python3
"""stage311cd.py -- Ticket 311 Stage C (all-candidates basin table & stationarity on Pot E)
and Stage D (blind-cap sweep over the 163-piece corpus).

Phase 1 (fast, ~20 s):
  1A. For all 34 Pot E pieces:
      - Evaluates every line in axes310/Pot_E_Piece_*_Axis.xyz on C0, C1, C (hub0, hub1, huball,
        worst_pt, cost ratio to rank 1, wall-alone optima angle a_c0_c1, wall thickness, roughness,
        patch_gap_deg, angles to released Axes/ and Ground Truth Axes/).
      - Evaluates the authors' released Axes/ line(s) on C0, C1, C (hub0, hub1, huball, worst_pt,
        ratio to our rank-1 worst_pt), refines the authors' line on C at 1e-9 (measuring drift_deg
        and angle to our nearest axes310 line), and refines the authors' line on C0 alone and C1
        alone at 1e-9 (measuring wall-to-wall disagreement on the piece).
  1B. For all 163 corpus pieces in axes310:
      - Evaluates worst_pt, huball, hub0, hub1, patch_gap_deg, and pairwise angles for all 750 lines.
      - Sweeps blind caps (cost-ratio r, angular separation sep_deg, K_max) without reading GT or
        released Axes/, then scores the kept sets against the 308/310 tier table (all 163, gt_close 81,
        gt_off 82) and per-pot line counts on A, B, D, E, G, I.

Phase 2 (full 10-seed pool basin analysis on 20 Pot E pieces, 20 workers):
  For pieces [1, 3, 5, 9, 12, 14, 17, 18, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]:
  - Runs the 10-seed (10,000-draw) MLESAC+stage1 pool on Cd.
  - Records how many raw/stage-1 draws land within 10 deg and 25 deg of the authors' line.
  - Clusters all 10,000 stage-1 draws into 10-deg basins and refines EVERY basin on ALL points C
    at 1e-9 (no BASIN_REFINE_MAX cut and no max_candidates cap).
  - Re-clusters at 10 deg and ranks all converged basins by worst_pt = max(hub0, hub1) and by huball.
  - Writes out/basins/Pot_E_Piece_<NN>_basins.tsv (every converged 10-deg basin with hub0, hub1,
    huball, worst_pt, ratio, draw count, wall-alone agreement, and angle to the authors' line)
    plus out/stagec_summary.tsv locating the authors' line among all converged basins.
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

from sfs_axes.cao import compute_biaxial_cao_error                    # noqa: E402
from sfs_axes.io_axes import direction_angle_deg, read_axes           # noqa: E402
from sfs_axes.potsac import (DEDUP_COS, _cluster_union,               # noqa: E402
                             compute_axis_of_symmetry, effective_step,
                             patch_gap_deg, refine_axis)
from sfs_axes.robust import apply_robustifier, robustifier_huber      # noqa: E402

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
RUNS = "/data/gpfs/projects/punim2657/SfSpp/runs"
AX310 = os.path.join(RUNS, "20261105-1215_1a6f16e_t310b3-timing", "out", "axes310")
AX308 = os.path.join(RUNS, "20261105-0532_d330469_t308a-axes", "out", "axes_paper")


def unit(v):
    v = np.asarray(v[0:3], dtype=float)
    n = np.linalg.norm(v)
    return v / n if n > 0 else v


def canonicalize(vt):
    vt = np.asarray(vt, dtype=float).copy()
    if vt[2] < 0:
        vt[0:3] = -vt[0:3]
    return vt


def load_surface(path):
    a = np.loadtxt(path, usecols=(0, 1, 2, 3, 4, 5), ndmin=2)
    return np.asarray(a, dtype=float).T


def hub_pt(vt, X):
    err = np.atleast_1d(compute_biaxial_cao_error(vt, X))
    return float(np.sum(apply_robustifier(robustifier_huber, err))) / max(X.shape[1], 1)


def cyl_profile(vt, C0, C1, nb=10):
    d = unit(vt)
    p0 = vt[3:6] - (vt[3:6] @ d) * d

    def _wall(X):
        rel = X[0:3, :] - p0[:, None]
        h = d @ rel
        rad = np.linalg.norm(rel - np.outer(d, h), axis=0)
        return h, rad

    h0, r0 = _wall(C0)
    h1, r1 = _wall(C1)
    lo = min(float(h0.min()), float(h1.min()))
    hi = max(float(h0.max()), float(h1.max()))
    if not (hi > lo):
        return float("nan"), float("nan"), float("nan"), float("nan")
    edges = np.linspace(lo, hi, nb + 1)
    cen = 0.5 * (edges[:-1] + edges[1:])

    def _rough(h, r):
        idx = np.clip(np.searchsorted(edges, h, side="right") - 1, 0, nb - 1)
        med = np.array([np.median(r[idx == b]) if np.any(idx == b) else np.nan for b in range(nb)])
        ok = ~np.isnan(med)
        if ok.sum() < 2:
            return float("nan"), med
        pred = np.interp(h, cen[ok], med[ok])
        return float(np.sqrt(np.mean((r - pred) ** 2))), med

    rg0, m0 = _rough(h0, r0)
    rg1, m1 = _rough(h1, r1)
    ok = ~(np.isnan(m0) | np.isnan(m1))
    if ok.sum() < 2:
        return float("nan"), float("nan"), rg0, rg1
    t = np.abs(m0[ok] - m1[ok])
    return float(np.median(t)), float(np.std(t)), rg0, rg1


def phase1_pot_e_piece(p):
    stem = "Pot_E_Piece_%02d" % p
    C0 = load_surface(os.path.join(CORPUS, "Surfaces", stem + "_Surface_0.xyz"))
    C1 = load_surface(os.path.join(CORPUS, "Surfaces", stem + "_Surface_1.xyz"))
    C = np.concatenate([C0, C1], axis=1)
    ref = read_axes(os.path.join(CORPUS, "Axes", stem + "_Axis.xyz"))
    v310 = read_axes(os.path.join(AX310, stem + "_Axis.xyz"))
    gpath = os.path.join(CORPUS, "Ground Truth Axes", stem + "_Axis.xyz")
    gt = read_axes(gpath) if os.path.isfile(gpath) else None

    # Evaluate v310 lines
    K = v310.shape[1]
    lines_info = []
    for k in range(K):
        vk = v310[:, k]
        h0 = hub_pt(vk, C0)
        h1 = hub_pt(vk, C1)
        hall = hub_pt(vk, C)
        w = max(h0, h1)
        ang_ref0 = float(direction_angle_deg(vk[0:3], ref[0:3, 0]))
        ang_ref_any = min(float(direction_angle_deg(vk[0:3], ref[0:3, r])) for r in range(ref.shape[1]))
        ang_gt = float(direction_angle_deg(vk[0:3], gt[0:3, 0])) if gt is not None else float("nan")
        pgap = patch_gap_deg(vk, C)
        tmed, tstd, rg0, rg1 = cyl_profile(vk, C0, C1)
        lines_info.append(dict(
            k=k + 1, h0=h0, h1=h1, hall=hall, worst=w,
            ang_ref0=ang_ref0, ang_ref_any=ang_ref_any, ang_gt=ang_gt,
            patch_gap=pgap, thick_med=tmed, thick_std=tstd, rough0=rg0, rough1=rg1
        ))
    w0 = lines_info[0]["worst"]
    for x in lines_info:
        x["ratio_worst"] = x["worst"] / max(w0, 1e-30)

    # Evaluate and refine authors' line 0 (and line 1 if present)
    ref_info = []
    for r in range(ref.shape[1]):
        vr = ref[:, r].copy()
        rh0 = hub_pt(vr, C0)
        rh1 = hub_pt(vr, C1)
        rhall = hub_pt(vr, C)
        rw = max(rh0, rh1)
        # Refine vr on C, C0, C1 at 1e-9
        vr_conv = refine_axis(vr.copy(), C, 2, 300, 1e-9)
        vr_c0 = refine_axis(vr.copy(), C0, 2, 300, 1e-9)
        vr_c1 = refine_axis(vr.copy(), C1, 2, 300, 1e-9)
        drift_c = float(direction_angle_deg(vr[0:3], vr_conv[0:3]))
        drift_c0 = float(direction_angle_deg(vr[0:3], vr_c0[0:3]))
        drift_c1 = float(direction_angle_deg(vr[0:3], vr_c1[0:3]))
        wall_disagree = float(direction_angle_deg(vr_c0[0:3], vr_c1[0:3]))
        ch0 = hub_pt(vr_conv, C0)
        ch1 = hub_pt(vr_conv, C1)
        chall = hub_pt(vr_conv, C)
        cw = max(ch0, ch1)
        angs_to_310 = [float(direction_angle_deg(vr_conv[0:3], v310[0:3, k])) for k in range(K)]
        nearest_k = int(np.argmin(angs_to_310)) + 1
        nearest_deg = angs_to_310[nearest_k - 1]
        tmed, tstd, rg0, rg1 = cyl_profile(vr, C0, C1)
        ref_info.append(dict(
            piece=p, stem=stem, ref_idx=r,
            n_s0=int(C0.shape[1]), n_s1=int(C1.shape[1]),
            ref_h0=rh0, ref_h1=rh1, ref_hall=rhall, ref_worst=rw,
            ref_vs_best310_ratio=rw / max(w0, 1e-30),
            best310_worst=w0, best310_h0=lines_info[0]["h0"], best310_h1=lines_info[0]["h1"],
            best310_ang_to_this_ref=min(float(direction_angle_deg(v310[0:3, k], vr[0:3])) for k in range(K)),
            line0_310_ang_to_this_ref=float(direction_angle_deg(v310[0:3, 0], vr[0:3])),
            drift_on_C_deg=drift_c,
            conv_h0=ch0, conv_h1=ch1, conv_hall=chall, conv_worst=cw,
            conv_vs_best310_ratio=cw / max(w0, 1e-30),
            conv_nearest_310_rank=nearest_k,
            conv_nearest_310_deg=nearest_deg,
            drift_on_C0_deg=drift_c0,
            drift_on_C1_deg=drift_c1,
            wall0_vs_wall1_deg=wall_disagree,
            thick_med_mm=tmed, thick_std_mm=tstd, rough0_mm=rg0, rough1_mm=rg1
        ))
    return dict(piece=p, stem=stem, lines=lines_info, refs=ref_info)


def phase1_corpus_piece(stem):
    C0 = load_surface(os.path.join(CORPUS, "Surfaces", stem + "_Surface_0.xyz"))
    C1 = load_surface(os.path.join(CORPUS, "Surfaces", stem + "_Surface_1.xyz"))
    C = np.concatenate([C0, C1], axis=1)
    v310 = read_axes(os.path.join(AX310, stem + "_Axis.xyz"))
    ref = read_axes(os.path.join(CORPUS, "Axes", stem + "_Axis.xyz"))
    gpath = os.path.join(CORPUS, "Ground Truth Axes", stem + "_Axis.xyz")
    gt_rel, tier = float("nan"), "no_gt"
    if os.path.isfile(gpath):
        gt = read_axes(gpath)
        gt_rel = float(direction_angle_deg(ref[0:3, 0], gt[0:3, 0]))
        tier = "gt_close" if gt_rel <= 5.0 else "gt_off"

    K = v310.shape[1]
    worsts = []
    halls = []
    pgaps = []
    angs_ref0 = []
    dirs = []
    for k in range(K):
        vk = v310[:, k]
        h0 = hub_pt(vk, C0)
        h1 = hub_pt(vk, C1)
        worsts.append(max(h0, h1))
        halls.append(hub_pt(vk, C))
        pgaps.append(patch_gap_deg(vk, C))
        angs_ref0.append(float(direction_angle_deg(vk[0:3], ref[0:3, 0])))
        dirs.append(unit(vk).tolist())
    return dict(
        stem=stem, pot=stem.split("_")[1], tier=tier, gt_rel=gt_rel,
        K_ref=int(ref.shape[1]), K_310=K,
        worsts=worsts, halls=halls, pgaps=pgaps,
        angs_ref0=angs_ref0, dirs=dirs
    )


def phase2_full_basins(job):
    p, outdir = job
    t0 = time.time()
    stem = "Pot_E_Piece_%02d" % p
    C0 = load_surface(os.path.join(CORPUS, "Surfaces", stem + "_Surface_0.xyz"))
    C1 = load_surface(os.path.join(CORPUS, "Surfaces", stem + "_Surface_1.xyz"))
    C = np.concatenate([C0, C1], axis=1)
    n = C.shape[1]
    step = effective_step(n, None)
    Cd = C[:, 0:n:step]

    ref = read_axes(os.path.join(CORPUS, "Axes", stem + "_Axis.xyz"))
    v310 = read_axes(os.path.join(AX310, stem + "_Axis.xyz"))
    gpath = os.path.join(CORPUS, "Ground Truth Axes", stem + "_Axis.xyz")
    gt = read_axes(gpath) if os.path.isfile(gpath) else None

    cand = []
    for seed in range(10):
        vt = compute_axis_of_symmetry(Cd, rng=np.random.default_rng(seed))[0]
        for k in range(vt.shape[1]):
            cand.append(refine_axis(vt[:, k], Cd, 2, 300, 1e-3))
    V_stage1 = np.column_stack(cand)
    n_draws = V_stage1.shape[1]

    # Count stage-1 draws near ref line 0 (and any ref line)
    d1_ref0 = np.array([direction_angle_deg(V_stage1[0:3, i], ref[0:3, 0]) for i in range(n_draws)])
    d1_ref_any = np.array([
        min(direction_angle_deg(V_stage1[0:3, i], ref[0:3, r]) for r in range(ref.shape[1]))
        for i in range(n_draws)
    ])
    draws_w5_ref0 = int(np.sum(d1_ref0 <= 5.0))
    draws_w10_ref0 = int(np.sum(d1_ref0 <= 10.0))
    draws_w25_ref0 = int(np.sum(d1_ref0 <= 25.0))
    draws_w10_any = int(np.sum(d1_ref_any <= 10.0))

    # Cluster into 10-deg stage-1 basins
    reps_pre, sizes_pre = _cluster_union(V_stage1, cos=DEDUP_COS)
    nb_pre = reps_pre.shape[1]
    pre_worst = np.array([max(hub_pt(reps_pre[:, j], C0), hub_pt(reps_pre[:, j], C1))
                          for j in range(nb_pre)])
    pre_rank = np.argsort( np.argsort(pre_worst, kind="stable") ) + 1

    # Refine ALL stage-1 basin representatives on ALL points C at 1e-9 (no 32-basin cut)
    V_ref = reps_pre.copy()
    for j in range(nb_pre):
        V_ref[:, j] = refine_axis(V_ref[:, j], C, 2, 300, 1e-9)

    # Re-cluster converged axes at 10 deg
    # Track which pre-basins merged into each post-basin
    d_post = V_ref[0:3, :] / np.linalg.norm(V_ref[0:3, :], axis=0)
    post_reps_idx = []
    dreps = np.empty((3, 0))
    post_draw_counts = []
    post_min_pre_rank = []
    for j in range(nb_pre):
        if dreps.shape[1]:
            sim = np.abs(dreps.T @ d_post[:, j])
            hit = np.flatnonzero(sim > DEDUP_COS)
        else:
            hit = np.empty(0, dtype=int)
        if hit.size:
            idx = int(hit[0])
            post_draw_counts[idx] += int(sizes_pre[j])
            post_min_pre_rank[idx] = min(post_min_pre_rank[idx], int(pre_rank[j]))
        else:
            post_reps_idx.append(j)
            dreps = np.column_stack([dreps, d_post[:, j]])
            post_draw_counts.append(int(sizes_pre[j]))
            post_min_pre_rank.append(int(pre_rank[j]))

    reps_post = V_ref[:, post_reps_idx]
    nb_post = reps_post.shape[1]

    basin_rows = []
    for b in range(nb_post):
        vb = reps_post[:, b]
        h0 = hub_pt(vb, C0)
        h1 = hub_pt(vb, C1)
        hall = hub_pt(vb, C)
        w = max(h0, h1)
        ang_ref0 = float(direction_angle_deg(vb[0:3], ref[0:3, 0]))
        ang_ref_any = min(float(direction_angle_deg(vb[0:3], ref[0:3, r])) for r in range(ref.shape[1]))
        ang_gt = float(direction_angle_deg(vb[0:3], gt[0:3, 0])) if gt is not None else float("nan")
        # Wall-alone refinement from vb
        va = refine_axis(vb.copy(), C0, 2, 300, 1e-9)
        vc = refine_axis(vb.copy(), C1, 2, 300, 1e-9)
        a_c0_c1 = float(direction_angle_deg(va[0:3], vc[0:3]))
        pgap = patch_gap_deg(vb, C)
        # Check if in axes310
        angs310 = [float(direction_angle_deg(vb[0:3], v310[0:3, k])) for k in range(v310.shape[1])]
        in310_rank = (int(np.argmin(angs310)) + 1) if min(angs310) < 0.5 else 0
        basin_rows.append(dict(
            piece=p, basin_id=b + 1,
            draws=post_draw_counts[b],
            min_pre_rank=post_min_pre_rank[b],
            kept_by_32=int(post_min_pre_rank[b] <= 32),
            in310_rank=in310_rank,
            hub0=h0, hub1=h1, huball=hall, worst_pt=w,
            ang_ref0=ang_ref0, ang_ref_any=ang_ref_any, ang_gt=ang_gt,
            a_c0_c1=a_c0_c1, patch_gap=pgap
        ))

    # Rank by worst_pt and by huball
    basin_rows.sort(key=lambda x: x["worst_pt"])
    w_best = basin_rows[0]["worst_pt"]
    hall_sorted = sorted(basin_rows, key=lambda x: x["huball"])
    hall_ranks = {id(x): i + 1 for i, x in enumerate(hall_sorted)}
    for i, x in enumerate(basin_rows):
        x["rank_worst"] = i + 1
        x["rank_huball"] = hall_ranks[id(x)]
        x["ratio_worst"] = x["worst_pt"] / max(w_best, 1e-30)

    os.makedirs(os.path.join(outdir, "basins"), exist_ok=True)
    bcols = [
        "piece", "rank_worst", "rank_huball", "in310_rank", "kept_by_32",
        "draws", "min_pre_rank", "hub0", "hub1", "huball", "worst_pt", "ratio_worst",
        "ang_ref0", "ang_ref_any", "ang_gt", "a_c0_c1", "patch_gap"
    ]
    with open(os.path.join(outdir, "basins", "%s_basins.tsv" % stem), "w") as fh:
        fh.write("\t".join(bcols) + "\n")
        for r in basin_rows:
            fh.write("\t".join(
                ("%.4f" % r[k] if isinstance(r[k], float) else str(r[k]))
                for k in bcols
            ) + "\n")

    best_ref0_basin = min(basin_rows, key=lambda x: x["ang_ref0"])
    best_any_basin = min(basin_rows, key=lambda x: x["ang_ref_any"])
    secs = round(time.time() - t0, 1)
    summary = dict(
        piece=p, stem=stem, n_pts=n, step=step,
        nb_pre=nb_pre, nb_post=nb_post,
        draws_w5_ref0=draws_w5_ref0, draws_w10_ref0=draws_w10_ref0,
        draws_w25_ref0=draws_w25_ref0, draws_w10_any=draws_w10_any,
        closest_ref0_deg=round(best_ref0_basin["ang_ref0"], 3),
        closest_ref0_rank_worst=best_ref0_basin["rank_worst"],
        closest_ref0_rank_huball=best_ref0_basin["rank_huball"],
        closest_ref0_ratio=round(best_ref0_basin["ratio_worst"], 4),
        closest_ref0_draws=best_ref0_basin["draws"],
        closest_any_deg=round(best_any_basin["ang_ref_any"], 3),
        closest_any_rank_worst=best_any_basin["rank_worst"],
        rank1_ang_ref0=round(basin_rows[0]["ang_ref0"], 3),
        rank1_worst_pt=round(basin_rows[0]["worst_pt"], 4),
        rank1_a_c0_c1=round(basin_rows[0]["a_c0_c1"], 3),
        secs=secs
    )
    print("[StageC] %s pre=%d post=%d draws_w10=%d closest_ref0=%.2fdeg(rank %d, ratio %.3f) rank1=%.2fdeg (%.1fs)" % (
        stem, nb_pre, nb_post, draws_w10_ref0,
        summary["closest_ref0_deg"], summary["closest_ref0_rank_worst"],
        summary["closest_ref0_ratio"], summary["rank1_ang_ref0"], secs
    ), flush=True)
    return summary


def filter_cap(c, r_max=None, sep_deg=10.0, k_max=6, min_pgap=None):
    K = c["K_310"]
    worsts = c["worsts"]
    dirs = [np.array(d) for d in c["dirs"]]
    pgaps = c["pgaps"]
    w0 = worsts[0]
    cos_thr = np.cos(np.radians(sep_deg))
    kept = []
    for k in range(K):
        if k > 0 and r_max is not None and worsts[k] > r_max * w0:
            continue
        if k > 0 and min_pgap is not None and pgaps[k] < min_pgap:
            continue
        if any(abs(float(dirs[k] @ dirs[j])) > cos_thr for j in kept):
            continue
        kept.append(k)
        if len(kept) >= k_max:
            break
    if not kept:
        kept = [0]
    return kept


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=20)
    ap.add_argument("--pieces", default="1,3,5,9,12,14,17,18,20,21,22,23,24,25,26,27,28,29,30,31")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    # --- Phase 1A: Fast Pot E stationarity & detailed axes310 table (all 34 pieces) ---
    print("[Phase 1A] Running Pot E stationarity & wall agreement across all 34 pieces...", flush=True)
    t0 = time.time()
    with Pool(a.jobs) as pool:
        p1a = list(pool.map(phase1_pot_e_piece, list(range(1, 35))))

    ref_cols = [
        "piece", "stem", "ref_idx", "n_s0", "n_s1",
        "ref_h0", "ref_h1", "ref_hall", "ref_worst", "ref_vs_best310_ratio",
        "best310_worst", "best310_ang_to_this_ref", "line0_310_ang_to_this_ref",
        "drift_on_C_deg", "conv_h0", "conv_h1", "conv_hall", "conv_worst",
        "conv_vs_best310_ratio", "conv_nearest_310_rank", "conv_nearest_310_deg",
        "drift_on_C0_deg", "drift_on_C1_deg", "wall0_vs_wall1_deg",
        "thick_med_mm", "thick_std_mm", "rough0_mm", "rough1_mm"
    ]
    with open(os.path.join(a.out, "pot_e_ref_stationarity.tsv"), "w") as fh:
        fh.write("\t".join(ref_cols) + "\n")
        for item in p1a:
            for r in item["refs"]:
                fh.write("\t".join(
                    ("%.4f" % r[k] if isinstance(r[k], float) else str(r[k]))
                    for k in ref_cols
                ) + "\n")

    with open(os.path.join(a.out, "pot_e_axes310_detailed.json"), "w") as fh:
        json.dump(p1a, fh, indent=2)
    print("[Phase 1A] Done in %.1fs -> pot_e_ref_stationarity.tsv" % (time.time() - t0), flush=True)

    # --- Phase 1B: 163-piece corpus blind-cap sweep ---
    print("[Phase 1B] Running 163-piece corpus evaluation for blind caps...", flush=True)
    t1 = time.time()
    stems = sorted(
        fn[:-len("_Surface_0.xyz")]
        for fn in os.listdir(os.path.join(CORPUS, "Surfaces"))
        if fn.endswith("_Surface_0.xyz")
    )
    with Pool(a.jobs) as pool:
        corp_data = list(pool.map(phase1_corpus_piece, stems))

    with open(os.path.join(a.out, "corpus_lines_750.json"), "w") as fh:
        json.dump(corp_data, fh, indent=1)

    # Sweep blind caps: cost-ratio r, separation sep_deg, K_max
    configs = [
        ("K6_uncapped(310)", None, 10.0, 6),
        ("K1_only", None, 10.0, 1),
        ("K2_only", None, 10.0, 2),
        ("K3_only", None, 10.0, 3),
        ("ratio_1.02", 1.02, 10.0, 6),
        ("ratio_1.05", 1.05, 10.0, 6),
        ("ratio_1.10", 1.10, 10.0, 6),
        ("ratio_1.15", 1.15, 10.0, 6),
        ("ratio_1.20", 1.20, 10.0, 6),
        ("ratio_1.25", 1.25, 10.0, 6),
        ("ratio_1.30", 1.30, 10.0, 6),
        ("ratio_1.50", 1.50, 10.0, 6),
        ("sep_15deg", None, 15.0, 6),
        ("sep_20deg", None, 20.0, 6),
        ("sep_25deg", None, 25.0, 6),
        ("sep_30deg", None, 30.0, 6),
        ("ratio_1.10_K2", 1.10, 10.0, 2),
        ("ratio_1.15_K2", 1.15, 10.0, 2),
        ("ratio_1.20_K2", 1.20, 10.0, 2),
        ("ratio_1.25_K3", 1.25, 10.0, 3),
        ("ratio_1.25_sep20", 1.25, 20.0, 6),
    ]
    sweep_rows = []
    for name, r_max, sep_deg, k_max in configs:
        tot_lines = 0
        best_angs = []
        gt_close_angs = []
        gt_off_angs = []
        pot_lines = {p: 0 for p in ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J")}
        pot_w5 = {p: 0 for p in ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J")}
        pA08_has_good = 0
        for c in corp_data:
            kept = filter_cap(c, r_max=r_max, sep_deg=sep_deg, k_max=k_max)
            tot_lines += len(kept)
            pot_lines[c["pot"]] = pot_lines.get(c["pot"], 0) + len(kept)
            b_ang = min(c["angs_ref0"][k] for k in kept)
            best_angs.append(b_ang)
            if b_ang <= 5.0:
                pot_w5[c["pot"]] = pot_w5.get(c["pot"], 0) + 1
            if c["tier"] == "gt_close":
                gt_close_angs.append(b_ang)
            elif c["tier"] == "gt_off":
                gt_off_angs.append(b_ang)
            if c["stem"] == "Pot_A_Piece_08":
                pA08_has_good = len(kept)
        ba = np.array(best_angs)
        gca = np.array(gt_close_angs)
        goa = np.array(gt_off_angs)
        row = dict(
            config=name, r_max=str(r_max), sep_deg=sep_deg, k_max=k_max,
            total_lines=tot_lines,
            med_best_deg=round(float(np.median(ba)), 3),
            w5_all="%d/163" % int(np.sum(ba <= 5.0)),
            w5_gt_close="%d/%d" % (int(np.sum(gca <= 5.0)), len(gca)),
            med_gt_close=round(float(np.median(gca)), 3),
            w5_gt_off="%d/%d" % (int(np.sum(goa <= 5.0)), len(goa)),
            med_gt_off=round(float(np.median(goa)), 3),
            lines_A=pot_lines["A"], lines_B=pot_lines["B"],
            lines_D=pot_lines["D"], lines_E=pot_lines["E"],
            lines_G=pot_lines["G"], lines_I=pot_lines["I"],
            w5_A=pot_w5["A"], w5_B=pot_w5["B"], w5_D=pot_w5["D"],
            w5_E=pot_w5["E"], w5_G=pot_w5["G"], w5_I=pot_w5["I"]
        )
        sweep_rows.append(row)

    scols = [
        "config", "r_max", "sep_deg", "k_max", "total_lines",
        "med_best_deg", "w5_all", "w5_gt_close", "med_gt_close", "w5_gt_off", "med_gt_off",
        "lines_A", "lines_B", "lines_D", "lines_E", "lines_G", "lines_I",
        "w5_A", "w5_B", "w5_D", "w5_E", "w5_G", "w5_I"
    ]
    with open(os.path.join(a.out, "d_corpus_sweep.tsv"), "w") as fh:
        fh.write("\t".join(scols) + "\n")
        for r in sweep_rows:
            fh.write("\t".join(str(r[k]) for k in scols) + "\n")
    print("[Phase 1B] Done in %.1fs -> d_corpus_sweep.tsv" % (time.time() - t1), flush=True)

    # --- Phase 2: Full 10-seed basin analysis on the selected Pot E pieces ---
    pieces = [int(x) for x in a.pieces.split(",") if x.strip()]
    print("[Phase 2] Running full 10-seed (10,000-draw) all-basins analysis on %d Pot E pieces..." % len(pieces), flush=True)
    jobs = [(p, a.out) for p in pieces]
    with Pool(a.jobs) as pool:
        summaries = list(pool.map(phase2_full_basins, jobs))

    summaries.sort(key=lambda x: x["piece"])
    sum_cols = [
        "piece", "stem", "n_pts", "step", "nb_pre", "nb_post",
        "draws_w5_ref0", "draws_w10_ref0", "draws_w25_ref0", "draws_w10_any",
        "closest_ref0_deg", "closest_ref0_rank_worst", "closest_ref0_rank_huball",
        "closest_ref0_ratio", "closest_ref0_draws",
        "closest_any_deg", "closest_any_rank_worst",
        "rank1_ang_ref0", "rank1_worst_pt", "rank1_a_c0_c1", "secs"
    ]
    with open(os.path.join(a.out, "stagec_summary.tsv"), "w") as fh:
        fh.write("\t".join(sum_cols) + "\n")
        for s in summaries:
            fh.write("\t".join(str(s[k]) for k in sum_cols) + "\n")
    print("[Phase 2] Complete -> stagec_summary.tsv", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
