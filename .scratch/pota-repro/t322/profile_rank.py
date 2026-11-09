#!/usr/bin/env python3
"""Ticket 322 fast loop: the proposed ranking, end to end on the dumped pool.

For every piece: every basin (raw representative and its normal-cost refinement) is scored
by profile thickness per wall (profile_probe.wall_thickness); per-wall costs are stored so the
wall combination can be chosen offline. Then the proposed rule is run in full:
  score = mean of the two walls' thickness -> 15-deg dedup -> Nelder-Mead refine the top
  --refine-k on the same cost -> re-score -> 15-deg dedup -> ranked list.
Output keeps, per entry: walls' costs, direction, error vs the reference.
"""

import argparse
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dump_basins import load_wall, piece_paths, ref_errors  # noqa: E402
from profile_probe import refine, stride, wall_thickness  # noqa: E402
from sfs_axes.io_axes import direction_angle_deg, read_axes  # noqa: E402


def dedup(items, tol=15.0):
    out = []
    for it in items:
        if all(direction_angle_deg(it["v"][0:3], o["v"][0:3]) >= tol for o in out):
            out.append(it)
    return out


def one(job):
    row, a = job
    stem = row["stem"]
    pot, p0, p1, relp, gtp = piece_paths(stem, a.jugkey)
    C0, C1 = load_wall(p0), load_wall(p1)
    W = [stride(C0, 2500), stride(C1, 2500)]
    C = np.concatenate([C0, C1], axis=1)
    c = C[0:3].mean(1)
    rel = read_axes(relp[0])
    gt = read_axes(gtp)[:, 0] if gtp and os.path.isfile(gtp) else None
    pool = []
    for bi, b in enumerate(row["basins"]):
        for kind in ("raw", "ref"):
            v = np.array(b[kind])
            w = [wall_thickness(v, X) for X in W]
            pool.append(dict(v=v, w=w, s=float(np.mean(w)), basin=bi, kind=kind, size=b["size"],
                             err=b[kind + "_e"]["err"]))
    pool.sort(key=lambda x: x["s"])
    top = dedup(pool, a.dedup)[: a.refine_k]
    fin = []
    for it in top:
        v, s = refine(it["v"], W, c, scale=0.1 * row["L"])
        w = [wall_thickness(v, X) for X in W]
        e = ref_errors(v, rel, gt, c)
        fin.append(dict(v=v, w=w, s=float(np.mean(w)), basin=it["basin"], size=it["size"],
                        err=e["err"], off=e["off"], start_err=it["err"]))
    fin.sort(key=lambda x: x["s"])
    fin = dedup(fin, a.dedup)
    out = dict(stem=stem, pot=pot, L=row["L"],
               pool=[dict(w=p["w"], basin=p["basin"], kind=p["kind"], err=p["err"]) for p in pool],
               ranked=[dict(v=f["v"].tolist(), w=f["w"], s=f["s"], err=f["err"], off=f["off"],
                            start_err=f["start_err"], size=f["size"]) for f in fin])
    print("%-20s rank-errs %s" % (stem, " ".join("%.1f" % f["err"] for f in fin)), flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--basins", required=True)
    ap.add_argument("--jugkey", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--refine-k", type=int, default=8)
    ap.add_argument("--dedup", type=float, default=15.0)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    rows = json.load(open(a.basins))
    if a.only:
        rows = [r for r in rows if any(r["stem"].startswith(k) for k in a.only.split(","))]
    with Pool(a.jobs) as p:
        res = p.map(one, [(r, a) for r in rows], chunksize=1)
    json.dump(res, open(a.out, "w"), default=float)
    print("wrote", a.out, len(res))


if __name__ == "__main__":
    main()
