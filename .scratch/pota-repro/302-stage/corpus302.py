#!/usr/bin/env python3
"""Ticket 302 gate 3: corrected corpus axes, written to NEW paths.

Every corpus piece, seeds 0..4, run_potsac with the per-point fix and the
LIVE refiner. Headline table = seed 0: error of our line 1 to the released
line 1 (both canonicalized), split by released-axis tier (GT-close / GT-off /
no-GT). Corrected axes (all K lines, canonicalized) are written under
out/axes302/, never into the corpus. The corpus is read only; md5s unchanged.
"""
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "sfs_axes")))

from sfs_axes.io_axes import (direction_angle_deg, radial_axial_errors,  # noqa: E402
                              read_axes)
from sfs_axes.potsac import run_potsac  # noqa: E402

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
ANG_TOL = 5.0
RAD_TOL = 2.0
SEEDS = 5


def canonicalize(vt):
    """Flip the DIRECTION's sign only, for a reproducible comparison.

    vt is [dir; pos] and pos is an anchor point ON the axis line, so negating
    the whole six-vector (as this did until 2026-11-04) moves the line to the
    other side of the piece frame - on Pot A it shifted Piece 07 by 2|pos| =
    712.6 mm, and it moves any piece whose line runs far from the origin.
    Direction-only comparisons are unchanged by the fix; position-based ones are
    corrected.
    """
    vt = np.asarray(vt, dtype=float).copy()
    if vt[2] < 0:
        vt[0:3] = -vt[0:3]
    return vt


def load_surface(path):
    a = np.loadtxt(path, usecols=(0, 1, 2, 3, 4, 5), ndmin=2)
    return np.asarray(a, dtype=float).T


def piece_list():
    out = []
    for fn in sorted(os.listdir(os.path.join(CORPUS, "Surfaces"))):
        if fn.endswith("_Surface_0.xyz"):
            out.append(fn[:-len("_Surface_0.xyz")])
    return out


def one(stem):
    try:
        C0 = load_surface(os.path.join(CORPUS, "Surfaces", stem + "_Surface_0.xyz"))
        C1 = load_surface(os.path.join(CORPUS, "Surfaces", stem + "_Surface_1.xyz"))
    except Exception as exc:
        return dict(stem=stem, error=str(exc))
    rel = read_axes(os.path.join(CORPUS, "Axes", stem + "_Axis.xyz"))
    r1 = canonicalize(rel[:, 0])
    gpath = os.path.join(CORPUS, "Ground Truth Axes", stem + "_Axis.xyz")
    if os.path.isfile(gpath):
        gt = read_axes(gpath)
        gt_rel = direction_angle_deg(r1[0:3], gt[0:3, 0])
        tier = "gt_close" if gt_rel <= 5.0 else "gt_off"
    else:
        gt_rel = float("nan")
        tier = "no_gt"
    rows = []
    best_vt = None
    for seed in range(SEEDS):
        t0 = time.time()
        vt = run_potsac(C0, C1, rng=np.random.default_rng(seed), step=10)
        secs = time.time() - t0
        K = vt.shape[1] if vt.size else 0
        if K and seed == 0:
            best_vt = vt
        o1 = canonicalize(vt[:, 0]) if K else None
        ang = direction_angle_deg(o1[0:3], r1[0:3]) if K else float("nan")
        rad = radial_axial_errors(o1[3:6], r1[0:3], r1[3:6])[0] if K else float("nan")
        rows.append(dict(stem=stem, seed=seed, K=K, ang=ang, rad=rad,
                         secs=secs, tier=tier, gt_rel=gt_rel))
        print("%s s%d K=%d ang=%.4f rad=%.4f (%.1fs)" % (stem, seed, K, ang, rad, secs),
              flush=True)
    return dict(stem=stem, rows=rows, vt=best_vt, tier=tier, gt_rel=gt_rel)


def main(outdir, jobs):
    os.makedirs(os.path.join(outdir, "axes302"), exist_ok=True)
    stems = piece_list()
    print("pieces:", len(stems))
    with Pool(jobs) as pool:
        results = pool.map(one, stems)
    per, axes_rows = [], []
    for res in results:
        if "error" in res:
            print("ERROR", res["stem"], res["error"])
            continue
        if res["vt"] is not None:
            path = os.path.join(outdir, "axes302", res["stem"] + "_Axis.xyz")
            with open(path, "w") as fh:
                for k in range(res["vt"].shape[1]):
                    v = canonicalize(res["vt"][:, k])
                    # position-first, the Axes/*.xyz convention (io_axes.write_axes)
                    fh.write(" ".join("%.17g" % x for x in
                             np.r_[v[3:6], v[0:3]]) + "\n")
            axes_rows.append((res["stem"], res["vt"].shape[1]))
        per.extend(res["rows"])
    with open(os.path.join(outdir, "corpus302.tsv"), "w") as fh:
        fh.write("stem\tseed\tK\tang_deg\trad_mm\tsecs\ttier\tgt_rel_deg\n")
        for r in per:
            fh.write("\t".join(("%.17g" % v if isinstance(v, float) else str(v))
                                for v in (r["stem"], r["seed"], r["K"], r["ang"],
                                          r["rad"], r["secs"], r["tier"],
                                          r["gt_rel"])) + "\n")
    s0 = [r for r in per if r["seed"] == 0 and r["K"] > 0]
    angs = np.array([r["ang"] for r in s0])
    print("--- seed-0 headline: n=%d median=%.3f deg  <=5deg: %d (%.1f%%)"
          % (len(s0), float(np.median(angs)), int((angs <= 5).sum()),
             100.0 * (angs <= 5).mean()))
    for tier in ("gt_close", "gt_off", "no_gt"):
        a = np.array([r["ang"] for r in s0 if r["tier"] == tier])
        if a.size:
            print("    %-8s n=%3d median=%7.3f  <=5deg %3d (%5.1f%%)"
                  % (tier, a.size, float(np.median(a)), int((a <= 5).sum()),
                     100.0 * (a <= 5).mean()))
    sp = np.array([r["ang"] for r in per if r["seed"] > 0])
    print("--- seeds 1-4 stability: median=%.3f, p90=%.3f, worst=%.3f over %d runs"
          % (float(np.median(sp)), float(np.percentile(sp, 90)), float(sp.max()),
             sp.size))
    with open(os.path.join(outdir, "summary302.txt"), "w") as fh:
        fh.write("pieces %d\naxes files %d\n" % (len(stems), len(axes_rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 8))
