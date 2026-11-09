#!/usr/bin/env python3
"""Ticket 322 probe: is the profile-thickness objective minimised at the true axis?

Profile thickness of axis v on one wall: map every point to (r, z) about v; a surface of
revolution maps to a curve. For each point take its k nearest neighbours in the (r, z) plane
and the smallest principal std of that neighbourhood = how far the local profile is from
being a curve. Cost = trimmed mean (best 80%) over the wall, in mm; a piece's cost = mean of
the two walls. No mm constant enters the ranking (it is within one piece).

Reports per piece: cost at truth, at the normal-cost local optimum from truth, rank of the
truth-nearest basin among all basins, and the drift of a Nelder-Mead refinement of this
cost started at the truth (does the minimum sit at the truth?).
"""

import argparse
import json
import os
import sys
from multiprocessing import Pool

import numpy as np
from scipy.optimize import minimize
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dump_basins import load_wall, piece_paths  # noqa: E402
from sfs_axes.io_axes import direction_angle_deg, read_axes  # noqa: E402


def stride(X, n):
    return X[:, 0:X.shape[1]:max(1, int(np.ceil(X.shape[1] / n)))]


def wall_thickness(v, X, k=24, keep=0.8):
    a = v[0:3] / np.linalg.norm(v[0:3])
    p0 = v[3:6] - (v[3:6] @ a) * a
    dp = X[0:3] - p0[:, None]
    z = a @ dp
    r = np.linalg.norm(dp - np.outer(a, z), axis=0)
    Q = np.c_[r, z]
    _, idx = cKDTree(Q).query(Q, k=k)
    nb = Q[idx] - Q[idx].mean(1, keepdims=True)
    cov = np.einsum("nki,nkj->nij", nb, nb) / k
    lam = np.linalg.eigvalsh(cov)[:, 0]
    t = np.sqrt(np.maximum(lam, 0))
    t.sort()
    return float(t[: max(1, int(keep * len(t)))].mean())


def cost(v, W):
    return float(np.mean([wall_thickness(v, X) for X in W]))


def to_params(v, c):
    a = v[0:3] / np.linalg.norm(v[0:3])
    e1 = np.cross(a, [1.0, 0, 0] if abs(a[0]) < 0.9 else [0, 1.0, 0])
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(a, e1)
    foot = v[3:6] + ((c - v[3:6]) @ a) * a
    return a, e1, e2, foot


def refine(v, W, c, scale):
    a, e1, e2, foot = to_params(v, c)

    def mk(x):
        d = a + x[0] * e1 + x[1] * e2
        d /= np.linalg.norm(d)
        p = foot + scale * (x[2] * e1 + x[3] * e2)
        return np.r_[d, p - (p @ d) * d]

    res = minimize(lambda x: cost(mk(x), W), np.zeros(4), method="Nelder-Mead",
                   options=dict(xatol=1e-4, fatol=1e-5, maxfev=400,
                                initial_simplex=np.vstack([np.zeros(4), 0.08 * np.eye(4)])))
    return mk(res.x), res.fun


def one(job):
    row, jugkey = job
    stem = row["stem"]
    pot, p0, p1, relp, gtp = piece_paths(stem, jugkey)
    C0, C1 = load_wall(p0), load_wall(p1)
    W = [stride(C0, 2500), stride(C1, 2500)]
    C = np.concatenate([C0, C1], axis=1)
    c = C[0:3].mean(1)
    rel = read_axes(relp[0])
    # truth line = the basin-free reference line used by dump_basins
    gt = read_axes(gtp)[:, 0] if gtp and os.path.isfile(gtp) else None
    cands = [rel[:, k] for k in range(rel.shape[1])] + ([gt] if gt is not None else [])
    bl = row["basins"]
    best = min(bl, key=lambda b: b["ref_e"]["err"])
    tdir = np.array(best["ref"][0:3])
    truth = min(cands, key=lambda t: direction_angle_deg(t[0:3], tdir))
    bc = []
    for b in bl:
        for kind in ("raw", "ref"):
            bc.append((cost(np.array(b[kind]), W), b[kind + "_e"]["err"], kind, b["size"]))
    bc.sort(key=lambda x: x[0])
    t_cost = cost(truth, W)
    rank_truthlike = next((i for i, x in enumerate(bc) if x[1] <= 10.0), None)
    tref, tref_cost = refine(truth, W, c, scale=0.1 * row["L"])
    out = dict(stem=stem, pot=pot, L=row["L"], truth_cost=t_cost,
               pool_top=[[round(x[0], 4), round(x[1], 1), x[2], x[3]] for x in bc[:8]],
               rank_first_within10=rank_truthlike, n_pool=len(bc),
               truth_refined_drift=direction_angle_deg(tref[0:3], truth[0:3]),
               truth_refined_cost=tref_cost)
    print("%-20s L=%5.0f truth=%.4f  pool0=%.4f(err %.1f)  first<=10 at rank %s/%d  NMdrift=%.1f"
          % (stem, row["L"], t_cost, bc[0][0], bc[0][1], rank_truthlike, len(bc),
             out["truth_refined_drift"]), flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--basins", required=True)
    ap.add_argument("--jugkey", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    rows = json.load(open(a.basins))
    if a.only:
        rows = [r for r in rows if any(r["stem"].startswith(k) for k in a.only.split(","))]
    with Pool(a.jobs) as p:
        res = p.map(one, [(r, a.jugkey) for r in rows], chunksize=1)
    json.dump(res, open(a.out, "w"), default=float)


if __name__ == "__main__":
    main()
