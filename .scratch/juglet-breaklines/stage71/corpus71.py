#!/usr/bin/env python3
"""Ticket 71 stages A, B2 and B3 on the released corpus.

Stage A. run_potsac on each piece, seeds 0..19, step 10, no wall truncation.
The arm is the candidate generator: SFS_AXES_REFINE_NOOP=1, because the live
refiner (the port default) already scored 1/163 any-line at seed 0
(job 34277138) and walks a released axis about 40 deg. Pass --refine live to
run that default instead. A released line 1 matches when some line of that
seed is within 5 deg and 2 mm radial (the ticket 70 gate).

Stage B2. Perturb released line 1 by 2 deg and 1 mm, minimise each of the six
costs on the full two-wall cloud, and record the drift back to the released
axis, the final cost, and the angle to the GT axis when one exists.

Stage B3. On that same cloud, does the released axis score lower than this
run's seed-0 line 1?

The corpus is read only. Nothing under sfs_axes is imported for writing.

usage: corpus71.py CORPUS OUTDIR [--jobs 8] [--seeds 20] [--refine noop|live]
       corpus71.py --check
"""
import argparse
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.abspath(os.path.join(_HERE, "..", "..", "..")))

from costs71 import COSTS, canonicalize, cost_value, minimize_cost, perturb  # noqa: E402
from sfs_axes.io_axes import direction_angle_deg, radial_axial_errors, read_axes  # noqa: E402
from sfs_axes.potsac import run_potsac  # noqa: E402

ANG_TOL = 5.0
RAD_TOL = 2.0


def load_surface(path):
    a = np.loadtxt(path, usecols=(0, 1, 2, 3, 4, 5), ndmin=2)
    return np.asarray(a, dtype=float).T


def lines_of(vt):
    out = []
    for k in range(vt.shape[1]):
        d = vt[0:3, k] / np.linalg.norm(vt[0:3, k])
        out.append((d, vt[3:6, k].copy()))
    return out


def match(rel_line, ours):
    """Best counterpart of one released line. Empty `ours` -> no match."""
    if not ours:
        return float("nan"), float("nan"), False
    rd, rp = rel_line
    best = None
    for od, op in ours:
        ang = direction_angle_deg(od, rd)
        rad = radial_axial_errors(op, rd, rp)[0]
        ok = ang <= ANG_TOL and rad <= RAD_TOL
        key = (not ok, ang)
        if best is None or key < best[0]:
            best = (key, ang, rad, ok)
    return best[1], best[2], best[3]


def cloud_of(C0, C1):
    X = np.concatenate([C0, C1], axis=1)
    nrm = X[3:6]
    ln = np.linalg.norm(nrm, axis=0)
    ok = ln > 1e-12
    X = X.copy()
    X[3:6, ok] = nrm[:, ok] / ln[ok]
    X[3:6, ~ok] = 0.0
    return X


def one(job):
    corpus, pot, piece, seeds, refine, fit_step = job
    os.environ["SFS_AXES_REFINE_NOOP"] = "1" if refine == "noop" else "0"
    stem = "Pot_%s_Piece_%02d" % (pot, piece)
    C0 = load_surface(os.path.join(corpus, "Surfaces", stem + "_Surface_0.xyz"))
    C1 = load_surface(os.path.join(corpus, "Surfaces", stem + "_Surface_1.xyz"))
    rel = read_axes(os.path.join(corpus, "Axes", stem + "_Axis.xyz"))
    rel1 = canonicalize(rel[:, 0])
    gpath = os.path.join(corpus, "Ground Truth Axes", stem + "_Axis.xyz")
    if os.path.isfile(gpath):
        gt = read_axes(gpath)[0:3, 0]
        gt_rel = direction_angle_deg(rel1[0:3], gt)
    else:
        gt = None
        gt_rel = float("nan")
    reach = []
    ours0 = None
    for seed in range(seeds):
        t0 = time.time()
        vt = run_potsac(C0, C1, rng=np.random.default_rng(seed), step=10)
        secs = time.time() - t0
        O = lines_of(vt) if vt.size and vt.shape[1] else []
        if seed == 0:
            ours0 = O[0] if O else None
        ang, rad, ok = match((rel1[0:3], rel1[3:6]), O)
        if O:
            l1_ang = direction_angle_deg(O[0][0], rel1[0:3])
            l1_rad = radial_axial_errors(O[0][1], rel1[0:3], rel1[3:6])[0]
            l1_ok = int(l1_ang <= ANG_TOL and l1_rad <= RAD_TOL)
        else:
            l1_ang = l1_rad = float("nan")
            l1_ok = 0
        reach.append(dict(
            arm=refine, pot=pot, piece=piece, seed=seed, n=C0.shape[1] + C1.shape[1],
            secs=secs, K=len(O), best_ang=ang, best_rad=rad, match=int(ok),
            l1_ang=l1_ang, l1_rad=l1_rad, l1_match=l1_ok, gt_rel_deg=gt_rel))
    X = cloud_of(C0, C1)
    if fit_step > 1:
        X = X[:, ::fit_step]
    start = perturb(rel1, 2.0, 1.0)
    fixed, rank = [], []
    for name in COSTS:
        vt, final, iters, capped = minimize_cost(name, start, X, max_iters=50)
        vt = canonicalize(vt)
        c_rel = cost_value(name, rel1, X)
        if gt is None:
            c_gt = float("nan")
            gt_ang = float("nan")
            below = ""
        else:
            # GT files carry a direction; the position column is whatever the
            # file stores. Score the whole line the file gives.
            gtv = canonicalize(read_axes(gpath)[:, 0])
            c_gt = cost_value(name, gtv, X)
            gt_ang = direction_angle_deg(vt[0:3], gt)
            below = int(c_rel < c_gt)
        fixed.append(dict(
            arm=refine, pot=pot, piece=piece, cost=name, n=X.shape[1],
            drift_deg=direction_angle_deg(vt[0:3], rel1[0:3]),
            drift_mm=radial_axial_errors(vt[3:6], rel1[0:3], rel1[3:6])[0],
            final_cost=final, cost_released=c_rel, cost_gt=c_gt,
            gt_ang=gt_ang, gt_rel_deg=gt_rel, iters=iters, capped=capped,
            rel_below_gt=below,
            moved_deg=direction_angle_deg(vt[0:3], start[0:3]),
            moved_mm=radial_axial_errors(vt[3:6], start[0:3], start[3:6])[0]))
        if ours0 is None:
            c_ours, o_ang, o_rad, lower = float("nan"), float("nan"), float("nan"), 0
        else:
            ov = canonicalize(np.concatenate([ours0[0], ours0[1]]))
            c_ours = cost_value(name, ov, X)
            o_ang = direction_angle_deg(ours0[0], rel1[0:3])
            o_rad = radial_axial_errors(ours0[1], rel1[0:3], rel1[3:6])[0]
            lower = int(c_rel < c_ours)
        rank.append(dict(
            arm=refine, pot=pot, piece=piece, cost=name,
            cost_rel=c_rel, cost_ours=c_ours, rel_lower=lower,
            ours_ang=o_ang, ours_rad=o_rad))
    return reach, fixed, rank


def _fmt(v):
    if isinstance(v, float):
        return "%.6g" % v
    return str(v)


def _append(path, cols, rows, newfile):
    mode = "w" if newfile else "a"
    with open(path, mode) as fh:
        if newfile:
            fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join(_fmt(r[c]) for c in cols) + "\n")
        fh.flush()


REACH_COLS = ["arm", "pot", "piece", "seed", "n", "secs", "K", "best_ang", "best_rad",
              "match", "l1_ang", "l1_rad", "l1_match", "gt_rel_deg"]
FIXED_COLS = ["arm", "pot", "piece", "cost", "n", "drift_deg", "drift_mm", "final_cost",
              "cost_released", "cost_gt", "gt_ang", "gt_rel_deg", "iters", "capped",
              "rel_below_gt", "moved_deg", "moved_mm"]
RANK_COLS = ["arm", "pot", "piece", "cost", "cost_rel", "cost_ours", "rel_lower",
             "ours_ang", "ours_rad"]


def _done_pieces(path, seeds):
    if not os.path.isfile(path):
        return set()
    counts = {}
    with open(path) as fh:
        next(fh, None)
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) < 4:
                continue
            key = (p[0], p[1], int(p[2]))
            counts[key] = counts.get(key, 0) + 1
    return {k for k, n in counts.items() if n >= seeds}


def _pct(a, q):
    a = np.asarray(list(a), dtype=float)
    a = a[np.isfinite(a)]
    if a.size == 0:
        return float("nan")
    return float(np.percentile(a, q))


def summarise(reach_path, fixed_path, rank_path, outdir, seeds):
    reach, fixed, rank = [], [], []

    def load(path):
        rows = []
        with open(path) as fh:
            header = fh.readline().rstrip("\n").split("\t")
            for line in fh:
                p = line.rstrip("\n").split("\t")
                if len(p) != len(header):
                    continue
                row = {}
                for k, v in zip(header, p):
                    try:
                        row[k] = int(v) if v.isdigit() or (v.startswith("-") and v[1:].isdigit()) else float(v)
                    except ValueError:
                        row[k] = v
                rows.append(row)
        return rows

    reach, fixed, rank = load(reach_path), load(fixed_path), load(rank_path)
    lines = []

    def say(s):
        print(s, flush=True)
        lines.append(s)

    pieces = sorted({(r["pot"], int(r["piece"])) for r in reach})
    say("[71] pieces %d  seeds %d  (per-piece rows: reach71.tsv, fixed71.tsv, rank71.tsv)"
        % (len(pieces), seeds))
    by_seed = {s: [] for s in range(seeds)}
    matched = {s: set() for s in range(seeds)}
    per_piece = {}
    for r in reach:
        key = (r["pot"], int(r["piece"]))
        s = int(r["seed"])
        by_seed[s].append(float(r["best_ang"]))
        per_piece.setdefault(key, []).append(r)
        if int(r["match"]) == 1:
            matched[s].add(key)
    say("[A] per seed: n_match  best_ang min / p10 / median / p90 / max")
    for s in range(seeds):
        a = by_seed[s]
        say("[A] seed %2d  match %3d/%d  ang %.3f / %.3f / %.3f / %.3f / %.3f"
            % (s, len(matched[s]), len(pieces), _pct(a, 0), _pct(a, 10),
               _pct(a, 50), _pct(a, 90), _pct(a, 100)))
    covered = set()
    need = {}
    for s in range(seeds):
        covered |= matched[s]
        frac = len(covered) / float(len(pieces) or 1)
        for mark in (0.5, 0.9):
            if mark not in need and frac + 1e-12 >= mark:
                need[mark] = s + 1
        say("[A] cumulative seeds 0..%d cover %d/%d (%.1f%%)"
            % (s, len(covered), len(pieces), 100.0 * frac))
    any_reach = len(covered)
    say("[A] reachable at some seed: %d/%d" % (any_reach, len(pieces)))
    say("[A] seeds to cover 50%%: %s   90%%: %s"
        % (need.get(0.5, ">seeds"), need.get(0.9, ">seeds")))
    # one row per piece: the best seed
    pcols = ["pot", "piece", "n_matched", "first_seed", "best_seed", "best_ang",
             "best_rad", "worst_ang", "spread_ang", "gt_rel_deg"]
    with open(os.path.join(outdir, "piece71.tsv"), "w") as fh:
        fh.write("\t".join(pcols) + "\n")
        for key in pieces:
            rows = per_piece[key]
            hits = [r for r in rows if int(r["match"]) == 1]
            first = min((int(r["seed"]) for r in hits), default=-1)
            winner = min(rows, key=lambda r: (int(r["match"]) == 0, float(r["best_ang"])))
            angs = [float(r["best_ang"]) for r in rows]
            rec = dict(pot=key[0], piece=key[1], n_matched=len(hits), first_seed=first,
                       best_seed=int(winner["seed"]), best_ang=float(winner["best_ang"]),
                       best_rad=float(winner["best_rad"]), worst_ang=max(angs),
                       spread_ang=max(angs) - min(angs), gt_rel_deg=rows[0]["gt_rel_deg"])
            fh.write("\t".join(_fmt(rec[c]) for c in pcols) + "\n")
    say("[A] piece71.tsv: one row per piece, best seed against released line 1")
    say("[B2] drift of the minimiser from the released axis (every piece is in fixed71.tsv)")
    for name in COSTS:
        sub = [r for r in fixed if r["cost"] == name]
        d = [float(r["drift_deg"]) for r in sub]
        m = [float(r["drift_mm"]) for r in sub]
        g = [float(r["gt_ang"]) for r in sub if np.isfinite(float(r["gt_ang"]))]
        n = len(sub)
        med = _pct(d, 50)
        bar = "yes" if np.isfinite(med) and med <= 2.0 else "no"
        below = [r for r in sub if str(r["rel_below_gt"]) == "1"]
        with_gt = [r for r in sub if str(r["rel_below_gt"]) in ("0", "1")]
        say("[B2] %-12s n=%d  drift_deg med %.3f p90 %.3f  drift_mm med %.3f  "
            "<=0.5deg %d  <=2deg %d  <=3deg %d  gt_ang med %.3f (n_gt %d)  "
            "rel<gt %d/%d  stageC_median<=2 %s"
            % (name, n, med, _pct(d, 90), _pct(m, 50),
               sum(x <= 0.5 for x in d), sum(x <= 2.0 for x in d), sum(x <= 3.0 for x in d),
               _pct(g, 50), len(g), len(below), len(with_gt), bar))
        worst = sorted(sub, key=lambda r: -float(r["drift_deg"]))[:5]
        say("[B2] %-12s five largest drifts: %s"
            % (name, ", ".join("%s%d %.2fdeg/%.2fmm" % (r["pot"], int(r["piece"]),
                                                        float(r["drift_deg"]), float(r["drift_mm"]))
                               for r in worst)))
    say("[B3] released line 1 lower than seed-0 line 1 (rank71.tsv)")
    for name in COSTS:
        sub = [r for r in rank if r["cost"] == name]
        say("[B3] %-12s rel_lower %d/%d"
            % (name, sum(int(r["rel_lower"]) == 1 for r in sub), len(sub)))
    say("[C] not wired by this script. Stage C needs B1 pass and B2 median drift <= 2 deg.")
    text = "\n".join(lines) + "\n"
    with open(os.path.join(outdir, "summary71.txt"), "w") as fh:
        fh.write(text)


def pieces_of(corpus):
    found = []
    for fn in sorted(os.listdir(os.path.join(corpus, "Axes"))):
        if not fn.endswith("_Axis.xyz"):
            continue
        t = fn.split("_")
        pot, piece = t[1], int(t[3])
        stem = "Pot_%s_Piece_%02d" % (pot, piece)
        if all(os.path.isfile(os.path.join(corpus, "Surfaces", stem + "_Surface_%d.xyz" % k))
               for k in (0, 1)):
            found.append((pot, piece))
    return found


def selftest(corpus, pieces):
    ok = 0
    for pot, piece in pieces:
        stem = "Pot_%s_Piece_%02d" % (pot, piece)
        rel = lines_of(read_axes(os.path.join(corpus, "Axes", stem + "_Axis.xyz")))
        if all(match(rl, rel)[2] for rl in rel):
            ok += 1
    print("[71] selftest: released file matched itself on %d/%d" % (ok, len(pieces)), flush=True)
    if ok != len(pieces):
        raise SystemExit("selftest failed: the match rule rejects a file against itself")


def check():
    """Exact cylinder, seed 0.

    The raw 6-point generator is scored separately from the line run_potsac
    keeps. On this shell the shipped cost ranks a wrong axis first and the
    1.1x prune drops the true one, so line 1 is not the axis even though
    almost every candidate is. proj_signed from 2 deg / 1 mm must return.
    """
    os.environ["SFS_AXES_REFINE_NOOP"] = "1"
    from b1_synthetic import TRUE, revolution
    from sfs_axes.potsac import compute_axis_of_symmetry
    X = revolution(0.0, 50.0, 4.0, -40.0, 40.0, 24, 8)
    half = X.shape[1] // 2
    vts, _inl, _costs, _samples = compute_axis_of_symmetry(
        X[:, ::10], rng=np.random.default_rng(0))
    angs = [direction_angle_deg(vts[0:3, k], TRUE[0:3]) for k in range(vts.shape[1])]
    order = int(np.argmin(angs))
    vt = run_potsac(X[:, :half], X[:, half:], rng=np.random.default_rng(0), step=10)
    ang = direction_angle_deg(vt[0:3, 0], TRUE[0:3])
    rad = radial_axial_errors(vt[3:6, 0], TRUE[0:3], TRUE[3:6])[0]
    got, _c, iters, _cap = minimize_cost("proj_signed", perturb(TRUE, 2.0, 1.0), X, max_iters=40)
    ang2 = direction_angle_deg(got[0:3], TRUE[0:3])
    rad2 = radial_axial_errors(got[3:6], TRUE[0:3], TRUE[3:6])[0]
    n_close = sum(a <= 0.5 for a in angs)
    text = (
        "candidates %d  within_0.5deg %d  best_ang %.4f at cost-rank %d\n"
        "run_potsac line1 %.4f deg %.4f mm  K %d\n"
        "proj_signed from 2deg/1mm: %.4f deg %.4f mm (%d iters)\n"
        % (len(angs), n_close, min(angs), order, ang, rad, vt.shape[1], ang2, rad2, iters))
    path = os.path.join(_HERE, "check71.txt")
    with open(path, "w") as fh:
        fh.write(text)
    print(text, end="", flush=True)
    if n_close < 1 or ang2 > 0.5 or rad2 > 0.5:
        raise SystemExit("check failed")
    print("[check] PASS", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus", nargs="?")
    ap.add_argument("outdir", nargs="?")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--seeds", type=int, default=20)
    ap.add_argument("--refine", choices=("noop", "live"), default="noop")
    ap.add_argument("--fit-step", type=int, default=1)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.check:
        check()
        return
    if not a.corpus or not a.outdir:
        ap.error("CORPUS and OUTDIR are required")
    os.makedirs(a.outdir, exist_ok=True)
    pieces = pieces_of(a.corpus)
    print("[71] pieces %d  refine %s  seeds %d  fit_step %d"
          % (len(pieces), a.refine, a.seeds, a.fit_step), flush=True)
    selftest(a.corpus, pieces)
    reach_path = os.path.join(a.outdir, "reach71.tsv")
    fixed_path = os.path.join(a.outdir, "fixed71.tsv")
    rank_path = os.path.join(a.outdir, "rank71.tsv")
    done = _done_pieces(reach_path, a.seeds)
    jobs = [(a.corpus, p, k, a.seeds, a.refine, a.fit_step)
            for (p, k) in pieces if (a.refine, p, k) not in done]
    print("[71] to run %d  already done %d" % (len(jobs), len(done)), flush=True)
    newfile = not os.path.isfile(reach_path)
    if jobs:
        with Pool(a.jobs) as pool:
            for i, (reach, fixed, rank) in enumerate(pool.imap_unordered(one, jobs)):
                _append(reach_path, REACH_COLS, reach, newfile)
                _append(fixed_path, FIXED_COLS, fixed, newfile)
                _append(rank_path, RANK_COLS, rank, newfile)
                newfile = False
                r0 = reach[0]
                print("[71] %d/%d %s %02d seeds %d (%.1fs on seed 0)"
                      % (i + 1, len(jobs), r0["pot"], r0["piece"], a.seeds, reach[0]["secs"]),
                      flush=True)
    summarise(reach_path, fixed_path, rank_path, a.outdir, a.seeds)


if __name__ == "__main__":
    main()
