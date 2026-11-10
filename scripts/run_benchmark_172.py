#!/usr/bin/env python3
import os, sys, time, argparse
from multiprocessing import Pool
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
# Check if sfs_axes is in HERE, or HERE/.., or cwd
for p in [HERE, os.path.join(HERE, ".."), os.getcwd(), os.path.join(os.getcwd(), "work")]:
    if os.path.isdir(os.path.join(p, "sfs_axes")):
        sys.path.insert(0, p)
        break

import sfs_axes.potsac as ps
from sfs_axes.io_axes import direction_angle_deg, read_axes

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
JUGLANES = "/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom"
JUGAXES = "/data/gpfs/projects/punim2657/Dataset/Axes/Juglet"
AX317 = "/data/gpfs/projects/punim2657/SfSpp/runs/20261108-0951_5044a41_t317a-axes/out/axes317"

def canonicalize(vt):
    vt = np.asarray(vt, dtype=float).copy()
    if vt[2] < 0:
        vt[0:3] = -vt[0:3]
    return vt

def load_wall(path):
    with open(path, "r") as fh:
        first = fh.readline()
    if first.startswith("ply"):
        n = None
        with open(path, "r") as fh:
            for line in fh:
                if line.startswith("element vertex"):
                    n = int(line.split()[-1])
                if line.strip() == "end_header":
                    break
            rows = []
            for _ in range(n):
                parts = fh.readline().split()
                rows.append([float(v) for v in parts[:6]])
        return np.asarray(rows, dtype=float).T
    a = np.loadtxt(path, usecols=(0, 1, 2, 3, 4, 5), ndmin=2)
    return np.asarray(a, dtype=float).T

def get_piece_info(stem):
    if stem.startswith("Juglet_"):
        idx = int(stem.split("_")[-1])
        c0_path = os.path.join(JUGLANES, f"Juglet_Piece_{idx}.S0")
        c1_path = os.path.join(JUGLANES, f"Juglet_Piece_{idx}.S1")
        rel_path = os.path.join(JUGAXES, f"Juglet_Piece_{idx}_Axis.xyz")
        gt_path = None
        pot = "JUG"
    else:
        parts = stem.split("_")
        pot = parts[1]
        c0_path = os.path.join(CORPUS, "Surfaces", f"{stem}_Surface_0.xyz")
        c1_path = os.path.join(CORPUS, "Surfaces", f"{stem}_Surface_1.xyz")
        rel_path = os.path.join(CORPUS, "Axes", f"{stem}_Axis.xyz")
        gt_path = os.path.join(CORPUS, "Ground Truth Axes", f"{stem}_Axis.xyz")
    return pot, c0_path, c1_path, rel_path, gt_path

def one(job):
    stem, outdir, cap, seeds, step, line_rule = job
    pot, c0_path, c1_path, rel_path, gt_path = get_piece_info(stem)
    try:
        C0 = load_wall(c0_path)
        C1 = load_wall(c1_path)
    except Exception as exc:
        return dict(stem=stem, pot=pot, error=str(exc))

    t0 = time.time()
    vt = ps.run_potsac_union(C0, C1, seeds=list(range(seeds)), step=step, max_candidates=cap, normalized=True,
                             line_rule=line_rule)
    secs = time.time() - t0
    K = int(vt.shape[1]) if vt.size else 0

    gt_ax = None
    if gt_path and os.path.isfile(gt_path):
        try:
            gt_ax = canonicalize(read_axes(gt_path)[:, 0])
        except Exception:
            gt_ax = None

    rel_axes = []
    if rel_path and os.path.isfile(rel_path):
        try:
            rel = read_axes(rel_path)
            for r in range(rel.shape[1]):
                rel_axes.append(canonicalize(rel[:, r]))
        except Exception:
            pass

    cand_best_ref_errs = []
    for k in range(K):
        v = canonicalize(vt[:, k])
        gt_err = direction_angle_deg(v[:3], gt_ax[:3]) if gt_ax is not None else float("nan")
        rel_errs = [direction_angle_deg(v[:3], r[:3]) for r in rel_axes] if rel_axes else [float("nan")]
        min_rel_err = min(rel_errs)
        ref_err = min(gt_err, min_rel_err) if not np.isnan(gt_err) else min_rel_err
        cand_best_ref_errs.append(ref_err)

    os.makedirs(outdir, exist_ok=True)
    outpath = os.path.join(outdir, stem + "_Axis.xyz")
    with open(outpath, "w") as fh:
        for k in range(K):
            v = canonicalize(vt[:, k])
            fh.write(" ".join("%.17g" % x for x in np.r_[v[3:6], v[0:3]]) + "\n")

    if stem.startswith("Juglet_"):
        idx = int(stem.split("_")[-1])
        alt_path = os.path.join(outdir, f"Pot_JUGLET_Piece_{idx:02d}_Axis.xyz")
        with open(alt_path, "w") as fh:
            for k in range(K):
                v = canonicalize(vt[:, k])
                fh.write(" ".join("%.17g" % x for x in np.r_[v[3:6], v[0:3]]) + "\n")

    # Check 317 top-3 comparison if available
    p317 = os.path.join(AX317, stem + "_Axis.xyz")
    same_top3 = None
    e317_top3 = []
    if os.path.exists(p317):
        try:
            vt317 = read_axes(p317)
            e317_cands = []
            for k in range(vt317.shape[1]):
                v7 = canonicalize(vt317[:, k])
                g7 = direction_angle_deg(v7[:3], gt_ax[:3]) if gt_ax is not None else float("nan")
                r7 = min([direction_angle_deg(v7[:3], r[:3]) for r in rel_axes]) if rel_axes else float("nan")
                e7 = min(g7, r7) if not np.isnan(g7) else r7
                e317_cands.append(round(e7, 2))
            e317_top3 = e317_cands[:3]
            same_top3 = (e317_top3 == [round(x, 2) for x in cand_best_ref_errs[:3]])
        except Exception:
            pass

    row = dict(
        stem=stem,
        pot=pot,
        K=K,
        secs=round(secs, 2),
        rank0_err=(cand_best_ref_errs[0] if cand_best_ref_errs else float("nan")),
        best3_err=(min(cand_best_ref_errs[:3]) if cand_best_ref_errs else float("nan")),
        best6_err=(min(cand_best_ref_errs[:6]) if cand_best_ref_errs else float("nan")),
        cand_best_ref_errs=[round(x, 2) for x in cand_best_ref_errs],
        e317_top3=e317_top3,
        same_top3=same_top3
    )
    print(f"[axes318] {stem:25s} K={K} rank0={row['rank0_err']:5.2f} deg, top3={row['best3_err']:5.2f} deg, top6={row['best6_err']:5.2f} deg ({secs:.1f}s)", flush=True)
    return row

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--cap", type=int, default=6)
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--step", type=int, default=10)
    ap.add_argument("--pots", default="ALL")
    ap.add_argument("--no-line-rule", action="store_true",
                    help="write every profile-ranked line up to --cap (the axes322 set) "
                         "instead of the ticket 324 keep rule; same as SFS_AXES_LINE_RULE=0")
    a = ap.parse_args()

    selected_pots = None if a.pots == "ALL" else set(a.pots.split(","))

    stems = []
    # Collect Pots A..J
    for fn in sorted(os.listdir(os.path.join(CORPUS, "Surfaces"))):
        if fn.endswith("_Surface_0.xyz"):
            stem = fn[:-len("_Surface_0.xyz")]
            p = stem.split("_")[1]
            if selected_pots is None or p in selected_pots:
                stems.append(stem)

    # Collect Juglet
    if selected_pots is None or "JUG" in selected_pots or "JUGLET" in selected_pots:
        for i in range(1, 10):
            stems.append(f"Juglet_Piece_{i}")

    print(f"[axes318] Total {len(stems)} pieces to process, output to {a.out}", flush=True)
    line_rule = False if a.no_line_rule else None
    jobs = [(s, a.out, a.cap, a.seeds, a.step, line_rule) for s in stems]

    t0 = time.time()
    if a.jobs > 1:
        with Pool(a.jobs) as p:
            rows = p.map(one, jobs)
    else:
        rows = [one(j) for j in jobs]
    total_time = time.time() - t0

    success = [r for r in rows if "error" not in r]
    errors = [r for r in rows if "error" in r]
    if errors:
        print(f"[axes318] WARNING: {len(errors)} errors occurred:")
        for e in errors:
            print(f"  {e['stem']}: {e['error']}")

    print(f"\n================ 172-PIECE BENCHMARK SUMMARY (axes318) ================")
    print(f"Processed {len(success)} pieces in {total_time:.1f}s ({total_time/len(success):.2f}s/piece)")
    print(f"{'Pot':5s} | {'Pieces':6s} | {'K=1 (<=10°)':12s} | {'K<=3 (<=10°)':12s} | {'K<=6 (<=10°)':12s} | {'Notes'}")
    print("-" * 75)

    all_pots = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "JUG"]
    tot_pieces = 0
    tot_k1 = 0
    tot_k3 = 0
    tot_k6 = 0

    for pot in all_pots:
        p_rows = [r for r in success if r["pot"] == pot]
        if not p_rows:
            continue
        n_p = len(p_rows)
        k1 = sum(1 for r in p_rows if r["rank0_err"] <= 10.0)
        k3 = sum(1 for r in p_rows if r["best3_err"] <= 10.0)
        k6 = sum(1 for r in p_rows if r["best6_err"] <= 10.0)
        tot_pieces += n_p
        tot_k1 += k1
        tot_k3 += k3
        tot_k6 += k6

        notes = []
        if pot == "E":
            scored = [r for r in p_rows if r["stem"] not in ("Pot_E_Piece_32", "Pot_E_Piece_33", "Pot_E_Piece_34")]
            scored_k3 = sum(1 for r in scored if r["best3_err"] <= 10.0)
            notes.append(f"{scored_k3}/{len(scored)} scored")
            changed = [r for r in p_rows if r["same_top3"] is False]
            notes.append(f"changed top3 vs 317: {len(changed)}")
        elif pot == "G":
            g07 = [r for r in p_rows if r["stem"].endswith("_07")]
            if g07:
                notes.append(f"G_07 err={g07[0]['rank0_err']:.2f}°")
        elif pot == "H":
            notes.append(f"dish recovery")
        elif pot == "C":
            notes.append(f"large sherd relaxation")
        elif pot == "JUG":
            notes.append(f"tight radius miniature")

        note_str = ", ".join(notes)
        print(f"{pot:5s} | {n_p:6d} | {k1:2d}/{n_p:2d} ({k1/n_p*100:4.1f}%) | {k3:2d}/{n_p:2d} ({k3/n_p*100:4.1f}%) | {k6:2d}/{n_p:2d} ({k6/n_p*100:4.1f}%) | {note_str}")

    print("-" * 75)
    print(f"{'Total':5s} | {tot_pieces:6d} | {tot_k1:2d}/{tot_pieces:2d} ({tot_k1/tot_pieces*100:4.1f}%) | {tot_k3:2d}/{tot_pieces:2d} ({tot_k3/tot_pieces*100:4.1f}%) | {tot_k6:2d}/{tot_pieces:2d} ({tot_k6/tot_pieces*100:4.1f}%) |")

if __name__ == "__main__":
    main()
