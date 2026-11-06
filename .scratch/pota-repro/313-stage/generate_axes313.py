#!/usr/bin/env python3
"""generate_axes313.py -- generate axes313 using normalized loss and clearance prior."""

import argparse
import os
import sys
import time
from multiprocessing import Pool
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "sfs_axes"))

import sfs_axes.potsac as ps
from sfs_axes.io_axes import direction_angle_deg, read_axes

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"


def canonicalize(vt):
    vt = np.asarray(vt, dtype=float).copy()
    if vt[2] < 0:
        vt[0:3] = -vt[0:3]
    return vt


def load_surface(path):
    a = np.loadtxt(path, usecols=(0, 1, 2, 3, 4, 5), ndmin=2)
    return np.asarray(a, dtype=float).T


def piece_list(corpus, pots=None):
    out = []
    for fn in sorted(os.listdir(os.path.join(corpus, "Surfaces"))):
        if fn.endswith("_Surface_0.xyz"):
            stem = fn[:-len("_Surface_0.xyz")]
            # stem format: Pot_E_Piece_01
            parts = stem.split("_")
            pot = parts[1]
            if pots is None or pot in pots:
                out.append(stem)
    return out


def one(job):
    stem, corpus, outdir, cap, seeds, step = job
    try:
        C0 = load_surface(os.path.join(corpus, "Surfaces", stem + "_Surface_0.xyz"))
        C1 = load_surface(os.path.join(corpus, "Surfaces", stem + "_Surface_1.xyz"))
    except Exception as exc:
        return dict(stem=stem, error=str(exc))
    t0 = time.time()
    vt = ps.run_potsac_union(C0, C1, seeds=list(range(seeds)), step=step, max_candidates=cap, normalized=True)
    secs = time.time() - t0
    K = int(vt.shape[1]) if vt.size else 0
    angs0, angs1 = [], []
    relpath = os.path.join(corpus, "Axes", stem + "_Axis.xyz")
    try:
        rel = read_axes(relpath)
        for k in range(K):
            v = canonicalize(vt[:, k])
            angs0.append(direction_angle_deg(v[0:3], rel[0:3, 0]))
            if rel.shape[1] > 1:
                angs1.append(direction_angle_deg(v[0:3], rel[0:3, 1]))
    except Exception:
        pass
    gpath = os.path.join(corpus, "Ground Truth Axes", stem + "_Axis.xyz")
    gt_rel, tier = float("nan"), "no_gt"
    if os.path.isfile(gpath):
        gt = read_axes(gpath)
        r1 = canonicalize(read_axes(relpath)[:, 0])
        gt_rel = direction_angle_deg(r1[0:3], gt[0:3, 0])
        tier = "gt_close" if gt_rel <= 5.0 else "gt_off"
    os.makedirs(outdir, exist_ok=True)
    outpath = os.path.join(outdir, stem + "_Axis.xyz")
    with open(outpath, "w") as fh:
        for k in range(K):
            v = canonicalize(vt[:, k])
            fh.write(" ".join("%.17g" % x for x in np.r_[v[3:6], v[0:3]]) + "\n")
    row = dict(stem=stem, K=K, secs=round(secs, 2), tier=tier, gt_rel=gt_rel,
               line0_deg=(angs0[0] if angs0 else float("nan")),
               best0_deg=(min(angs0) if angs0 else float("nan")),
               best1_deg=(min(angs1) if angs1 else float("nan")),
               n_released_1=(2 if angs1 else 1))
    print("[axes313] %s K=%d best0=%.2f line0=%.2f (%.1fs)"
          % (stem, K, row["best0_deg"], row["line0_deg"], secs), flush=True)
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--corpus", default=CORPUS)
    ap.add_argument("--jobs", type=int, default=16)
    ap.add_argument("--cap", type=int, default=6)
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--step", type=int, default=10)
    ap.add_argument("--pots", default="")
    a = ap.parse_args()

    pots = set(a.pots.split(",")) if a.pots else None
    outdir = os.path.join(a.out, "axes313")
    os.makedirs(outdir, exist_ok=True)
    stems = piece_list(a.corpus, pots)
    print(f"[axes313] Found {len(stems)} pieces for pots {pots or 'ALL'}, output to {outdir}", flush=True)

    jobs = [(s, a.corpus, outdir, a.cap, a.seeds, a.step) for s in stems]
    t0 = time.time()
    if a.jobs > 1:
        with Pool(a.jobs) as p:
            rows = p.map(one, jobs)
    else:
        rows = [one(j) for j in jobs]
    dt = time.time() - t0

    success = [r for r in rows if "error" not in r]
    print(f"[axes313] Processed {len(success)}/{len(stems)} pieces in {dt:.1f}s", flush=True)
    bests = [r["best0_deg"] for r in success if not np.isnan(r["best0_deg"])]
    if bests:
        under5 = sum(1 for b in bests if b <= 5.0)
        under10 = sum(1 for b in bests if b <= 10.0)
        print(f"[axes313] Best candidate vs released line 0: <=5 deg: {under5}/{len(bests)} ({under5/len(bests)*100:.1f}%), <=10 deg: {under10}/{len(bests)} ({under10/len(bests)*100:.1f}%), median {np.median(bests):.2f} deg", flush=True)


if __name__ == "__main__":
    main()
