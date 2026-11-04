#!/usr/bin/env python3
"""axes305.py -- ticket 305 Stage 0/2: shipped-default axis extraction, all pots.

Every piece in <surfaces> (Pot_<P>_Piece_<NN>_Surface_0.xyz) is run through the
SHIPPED chain exactly as 'python -m sfs_axes.cli extract-pot-a' does it:
read_surfaces(truncate=True), run_potsac(step=10) -- which applies the authors'
under-5,000-point rule (step 1) unless SFS_AXES_ADAPTIVE_UNDER_5K=0.  No other
env override is set by this script; a caller that sets one is recorded.

Seeds: seed 0 writes the axis file used by the assembler; seeds 1..N-1 are
diagnostics only (policy: 3 seeds for every Pot A piece and for every piece
under 5,000 surface points, 1 elsewhere).

Outputs under <out>:
  axes305/<stem>_Axis.xyz   seed-0 axes, position-first (write_axes)
  axes305.tsv               one row per piece-seed
  axes305_summary.txt
"""
import argparse
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from sfs_axes.io_axes import (direction_angle_deg, radial_axial_errors,  # noqa: E402
                              read_axes, write_axes)
from sfs_axes.io_surfaces import read_surfaces, surface_path  # noqa: E402
from sfs_axes.potsac import effective_step, run_potsac  # noqa: E402

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
POTS = "ABCDEFGHIJ"


def canonicalize(vt):
    vt = np.asarray(vt, dtype=float).copy()
    if vt[2] < 0:
        vt[0:3] = -vt[0:3]
    return vt


def piece_stems(surfaces, pot):
    out = []
    pre = "Pot_%s_Piece_" % pot
    for fn in sorted(os.listdir(surfaces)):
        if fn.startswith(pre) and fn.endswith("_Surface_0.xyz"):
            out.append(fn[:-len("_Surface_0.xyz")])
    return out


def load_wall(path, truncate=True):
    """Read one wall as (6,n).  Plain xyz (one row per point: x y z nx ny nz) or
    an ASCII PLY whose body rows start with 6 numbers -- which is what the t66
    juglet lanes wrote for Surface_0/Surface_1."""
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
        a = np.asarray(rows, dtype=float).T
        return a
    a = np.loadtxt(path, dtype=float).T
    return a[:6]


def read_walls(surfaces, pot, frag, truncate):
    """read_surfaces for the normal corpus layout; explicit files for JUGLET."""
    if pot != "JUGLET":
        return read_surfaces(surfaces, pot, frag, truncate=truncate)
    pre = os.path.join(surfaces, "Pot_%s_Piece_%02d_Surface_%%d.xyz" % (pot, frag))
    C0 = load_wall(pre % 0)
    C1 = load_wall(pre % 1)
    if truncate:
        m = min(C0.shape[1], C1.shape[1])
        C0, C1 = C0[:, :m], C1[:, :m]
    return C0, C1


def one(args):
    surfaces, outdir, pot, stem, truncate, nseeds, wseeds = args
    frag = int(stem.split("_")[-1])
    try:
        C0, C1 = read_walls(surfaces, pot, frag, truncate)
    except Exception as exc:
        return dict(stem=stem, pot=pot, piece=frag, error=str(exc))
    n = C0.shape[1] + C1.shape[1]
    step = effective_step(n, 10)
    under5k = n < 5000
    seeds = list(range(nseeds))
    rel = None
    relp = os.path.join(CORPUS, "Axes", stem + "_Axis.xyz")
    if os.path.isfile(relp):
        try:
            rel = canonicalize(read_axes(relp)[:, 0])
        except Exception:
            rel = None
    rows = []
    for seed in seeds:
        t0 = time.time()
        vt = run_potsac(C0, C1, rng=np.random.default_rng(seed), step=10)
        secs = time.time() - t0
        K = int(vt.shape[1]) if vt.size else 0
        if seed == 0:
            os.makedirs(os.path.join(outdir, "axes305"), exist_ok=True)
            if K:
                write_axes(os.path.join(outdir, "axes305", stem + "_Axis.xyz"), vt)
            else:
                open(os.path.join(outdir, "axes305", stem + "_Axis.xyz"), "w").close()
        if wseeds:
            sd = os.path.join(outdir, "axes_seed%d" % seed)
            os.makedirs(sd, exist_ok=True)
            fp = os.path.join(sd, stem + "_Axis.xyz")
            if K:
                write_axes(fp, vt)
            else:
                open(fp, "w").close()
        ang = rad = angmin = float("nan")
        if K:
            o1 = canonicalize(vt[:, 0])
            if rel is not None:
                ang = direction_angle_deg(o1[0:3], rel[0:3])
                rad = radial_axial_errors(o1[3:6], rel[0:3], rel[3:6])[0]
                angmin = min(direction_angle_deg(canonicalize(vt[:, k])[0:3], rel[0:3])
                             for k in range(K))
        rows.append(dict(stem=stem, pot=pot, piece=frag, seed=seed, K=K, ang=ang,
                         angmin=angmin, rad=rad, secs=secs, n=n,
                         n0=C0.shape[1], n1=C1.shape[1],
                         step=step, trunc=int(bool(truncate)), under5k=int(under5k)))
        print("%s s%d K=%d n=%d step=%d ang=%.4f rad=%.4f (%.1fs)"
              % (stem, seed, K, n, step, ang, rad, secs), flush=True)
    return dict(stem=stem, pot=pot, piece=frag, rows=rows, error=None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--surfaces", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--pot", default="ALL")
    ap.add_argument("--seeds", type=int, default=0,
                    help="0 = ticket policy (3 seeds Pot A and under-5k pieces, 1 else)")
    ap.add_argument("--truncate", type=int, default=1)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--write-seeds", type=int, default=0,
                    help="1 = also write axes_seed<k>/ for every seed")
    a = ap.parse_args()
    pots = list(POTS) if a.pot == "ALL" else ([a.pot] if len(a.pot) > 1 else list(a.pot))
    tasks = []
    for pot in pots:
        stems = piece_stems(a.surfaces, pot)
        print("pot %s: %d pieces" % (pot, len(stems)), flush=True)
        for stem in stems:
            frag = int(stem.split("_")[-1])
            try:
                C0, C1 = read_surfaces(a.surfaces, pot, frag, truncate=bool(a.truncate))
                n = C0.shape[1] + C1.shape[1]
            except Exception:
                n = 999999
            ns = a.seeds if a.seeds else (3 if (pot == "A" or n < 5000) else 1)
            tasks.append((a.surfaces, a.out, pot, stem, bool(a.truncate), ns,
                          bool(a.write_seeds)))
    print("tasks:", len(tasks), "piece-seeds:", sum(t[5] for t in tasks), flush=True)
    with Pool(a.jobs) as pool:
        res = pool.map(one, tasks)
    rows, files, errs = [], 0, 0
    for r in res:
        if r["error"]:
            errs += 1
            print("ERROR", r["stem"], r["error"])
            continue
        rows.extend(r["rows"])
        files += 1
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "axes305.tsv"), "w") as fh:
        fh.write("stem\tpot\tpiece\tseed\tK\tang_vs_released_deg\tangmin_vs_released_deg"
                 "\trad_mm\tsecs\tn_pts"
                 "\tn_wall0\tn_wall1\tstep\ttruncate\tunder5k\n")
        for r in rows:
            fh.write("\t".join("%.17g" % v if isinstance(v, float) else str(v)
                               for v in (r["stem"], r["pot"], r["piece"], r["seed"],
                                         r["K"], r["ang"], r["angmin"], r["rad"], r["secs"],
                                         r["n"], r["n0"], r["n1"], r["step"],
                                         r["trunc"], r["under5k"])) + "\n")
    s0 = [r for r in rows if r["seed"] == 0]
    k0 = [r for r in s0 if r["K"] > 0]
    angs = np.array([r["ang"] for r in s0 if not np.isnan(r["ang"])])
    u5 = [r for r in s0 if r["under5k"]]
    tot = sum(r["secs"] for r in rows)
    lines = ["pieces %d  axis files %d  errors %d" % (len(s0), files, errs),
             "seed-0 candidate-0 vs best-candidate angle to released: median %.3f / %.3f deg"
             % (float(np.median(angs)) if angs.size else float("nan"),
                float(np.median([r["angmin"] for r in s0 if not np.isnan(r["angmin"])]))
                if any(not np.isnan(r["angmin"]) for r in s0) else float("nan")),
             "piece-seeds %d  under-5k pieces %d (rule fired step=1 on %d)"
             % (len(rows), len(u5), sum(1 for r in u5 if r["step"] == 1)),
             "K==0 pieces %d" % (len(s0) - len(k0)),
             "seed-0 angle to released axis: n=%d median=%.3f p90=%.3f  <=5deg %d"
             % (angs.size, float(np.median(angs)) if angs.size else float("nan"),
                float(np.percentile(angs, 90)) if angs.size else float("nan"),
                int((angs <= 5).sum())),
             "cpu-seconds total %.0f" % tot]
    with open(os.path.join(a.out, "axes305_summary.txt"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
