#!/usr/bin/env python3
"""corpus310.py -- ticket 310 B3: every corpus piece through the basin rule.

One job per piece: run_potsac_union with the ticket-310 default
(SFS_AXES_CONVERGE_BEFORE_RANK=1: cluster the whole pool, refine every basin on
all points, re-cluster, rank by the worse wall's cost, cap). Axes are written to
NEW paths under the run directory; the corpus is read only.

Reports, per piece: K (lines written), wall seconds, and -- for SCORING only --
the angle of each written line to the released line 0 and line 1, so the tier
table of ticket 308 can be recomputed on the same footing.

The rule is blind: the clouds and the seeds are its only inputs. The released
Axes/ files are read after the axes are written, to score them.
"""
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import sfs_axes.potsac as ps                                       # noqa: E402
from sfs_axes.io_axes import direction_angle_deg, read_axes         # noqa: E402

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"


def canonicalize(vt):
    vt = np.asarray(vt, dtype=float).copy()
    if vt[2] < 0:
        vt[0:3] = -vt[0:3]
    return vt


def load_surface(path):
    a = np.loadtxt(path, usecols=(0, 1, 2, 3, 4, 5), ndmin=2)
    return np.asarray(a, dtype=float).T


def piece_list(corpus):
    out = []
    for fn in sorted(os.listdir(os.path.join(corpus, "Surfaces"))):
        if fn.endswith("_Surface_0.xyz"):
            out.append(fn[:-len("_Surface_0.xyz")])
    return out


def one(job):
    stem, corpus, outdir, cap, seeds = job
    try:
        C0 = load_surface(os.path.join(corpus, "Surfaces", stem + "_Surface_0.xyz"))
        C1 = load_surface(os.path.join(corpus, "Surfaces", stem + "_Surface_1.xyz"))
    except Exception as exc:                                    # noqa: BLE001
        return dict(stem=stem, error=str(exc))
    t0 = time.time()
    vt = ps.run_potsac_union(C0, C1, seeds=list(range(seeds)), max_candidates=cap)
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
    except Exception:                                           # noqa: BLE001
        pass
    gpath = os.path.join(corpus, "Ground Truth Axes", stem + "_Axis.xyz")
    gt_rel, tier = float("nan"), "no_gt"
    if os.path.isfile(gpath):
        gt = read_axes(gpath)
        r1 = canonicalize(read_axes(relpath)[:, 0])
        gt_rel = direction_angle_deg(r1[0:3], gt[0:3, 0])
        tier = "gt_close" if gt_rel <= 5.0 else "gt_off"
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, stem + "_Axis.xyz"), "w") as fh:
        for k in range(K):
            v = canonicalize(vt[:, k])
            fh.write(" ".join("%.17g" % x for x in np.r_[v[3:6], v[0:3]]) + "\n")
    row = dict(stem=stem, K=K, secs=round(secs, 2), tier=tier, gt_rel=gt_rel,
               line0_deg=(angs0[0] if angs0 else float("nan")),
               best0_deg=(min(angs0) if angs0 else float("nan")),
               best1_deg=(min(angs1) if angs1 else float("nan")),
               n_released_1=(2 if angs1 else 1))
    print("[corpus310] %s K=%d best0=%.2f line0=%.2f (%.1fs)"
          % (stem, K, row["best0_deg"], row["line0_deg"], secs), flush=True)
    return row


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--corpus", default=CORPUS)
    ap.add_argument("--jobs", type=int, default=16)
    ap.add_argument("--cap", type=int, default=6)
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    outdir = os.path.join(a.out, "axes310")
    os.makedirs(outdir, exist_ok=True)
    stems = piece_list(a.corpus)
    if a.only:
        want = set(a.only.split(","))
        stems = [s for s in stems if s in want]
    print("[corpus310] pieces=%d jobs=%d cap=%d seeds=%d rule=%s"
          % (len(stems), a.jobs, a.cap, a.seeds, ps.CONVERGE_BEFORE_RANK),
          flush=True)
    jobs = [(s, a.corpus, outdir, a.cap, a.seeds) for s in stems]
    rows = []
    t0 = time.time()
    with Pool(a.jobs) as pool:
        for r in pool.imap_unordered(one, jobs):
            rows.append(r)
    wall = time.time() - t0
    keys = ["stem", "K", "secs", "tier", "gt_rel", "line0_deg", "best0_deg",
            "best1_deg", "n_released_1"]
    with open(os.path.join(a.out, "corpus310.tsv"), "w") as fh:
        fh.write("\t".join(keys) + "\n")
        for r in sorted(rows, key=lambda x: x["stem"]):
            if "error" in r:
                fh.write("%s\tERROR\t%s\n" % (r["stem"], r["error"]))
                continue
            fh.write("\t".join(("%.17g" % r[k] if isinstance(r[k], float) else str(r[k]))
                               for k in keys) + "\n")
    ok = [r for r in rows if "error" not in r]
    angs = np.array([r["best0_deg"] for r in ok])
    print("[corpus310] files=%d lines=%d (median K %.1f) wall=%.0fs"
          % (len(ok), sum(r["K"] for r in ok), float(np.median([r["K"] for r in ok])), wall))
    print("[corpus310] best-line vs released line 0: within 5 deg %d of %d, median %.2f"
          % (int((angs <= 5).sum()), angs.size, float(np.median(angs))))
    for tier in ("gt_close", "gt_off", "no_gt"):
        sel = [r for r in ok if r["tier"] == tier]
        if sel:
            aa = np.array([r["best0_deg"] for r in sel])
            print("[corpus310]   %-8s n=%3d median=%7.2f  <=5deg %3d"
                  % (tier, len(sel), float(np.median(aa)), int((aa <= 5).sum())))
    per = np.array([r["secs"] for r in ok])
    print("[corpus310] seconds/piece median %.1f max %.1f" % (float(np.median(per)), per.max()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
