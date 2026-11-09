#!/usr/bin/env python3
"""Ticket 322 fast loop, step 1: every refined basin of every piece, with its features.

Pool = exactly run_potsac_union's normalised pool (10 seeds x 1000 Pottmann 6-point draws on
the step-strided cloud, 10-deg greedy clustering). Then, unlike the shipped ranker, EVERY basin
representative (up to --max-basins, largest first) is refined with refine_axis_normalized on a
<= --nref point stride of both walls, and described by scale-free features. Each basin also
carries its error against the piece's reference, so ranking rules can be scored offline
(rank_rules.py) without re-running any geometry.

Reference: pots = min(direction error to any released Axes line, to Ground Truth Axes line 0)
(the 318/319 benchmark definition) and the released-only error separately; Juglet = the
mesh-derived key from juglet_key.py. Offsets are measured at the piece centroid.

Also scores an existing axis set (--before DIR) with the same reference, for the before column.
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
import sfs_axes.potsac as ps  # noqa: E402
from sfs_axes.io_axes import direction_angle_deg, read_axes  # noqa: E402
from sfs_axes.normalized import (centroid_distance, compute_normalized_residual,  # noqa: E402
                                 refine_axis_normalized)
from sfs_axes.pottmann import compute_pottmann_axis  # noqa: E402
from sfs_axes.robust import apply_robustifier, robustifier_huber  # noqa: E402

CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
JUGLANES = ("/data/gpfs/projects/punim2657/SfSpp/runs/"
            "20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom")


def load_wall(path):
    with open(path) as fh:
        first = fh.readline()
    if first.startswith("ply"):
        n = None
        with open(path) as fh:
            for line in fh:
                if line.startswith("element vertex"):
                    n = int(line.split()[-1])
                if line.strip() == "end_header":
                    break
            rows = [[float(v) for v in fh.readline().split()[:6]] for _ in range(n)]
        return np.asarray(rows).T
    return np.loadtxt(path, usecols=range(6), ndmin=2).T


def piece_paths(stem, jugkey):
    if stem.startswith("Juglet_"):
        i = int(stem.split("_")[-1])
        return ("JUG", os.path.join(JUGLANES, "Juglet_Piece_%d.S0" % i),
                os.path.join(JUGLANES, "Juglet_Piece_%d.S1" % i),
                [os.path.join(jugkey, "key", "Juglet_Piece_%d_Axis.xyz" % i)], None)
    pot = stem.split("_")[1]
    return (pot, os.path.join(CORPUS, "Surfaces", stem + "_Surface_0.xyz"),
            os.path.join(CORPUS, "Surfaces", stem + "_Surface_1.xyz"),
            [os.path.join(CORPUS, "Axes", stem + "_Axis.xyz")],
            os.path.join(CORPUS, "Ground Truth Axes", stem + "_Axis.xyz"))


def offset_at(va, vb, c):
    out = []
    for vt in (va, vb):
        d = vt[0:3] / np.linalg.norm(vt[0:3])
        out.append(vt[3:6] + ((c - vt[3:6]) @ d) * d)
    return float(np.linalg.norm(out[0] - out[1]))


def ref_errors(v, rel, gt, c):
    er = [(direction_angle_deg(v[0:3], rel[:, k][0:3]), offset_at(v, rel[:, k], c))
          for k in range(rel.shape[1])]
    e_rel = min(er, key=lambda x: x[0])
    e_gt = (direction_angle_deg(v[0:3], gt[0:3]), offset_at(v, gt, c)) if gt is not None else (np.nan, np.nan)
    e = e_rel if not (e_gt[0] < e_rel[0]) else e_gt
    return dict(err=e[0], off=e[1], err_rel=e_rel[0], off_rel=e_rel[1], err_gt=e_gt[0])


def huber_mean(e):
    return float(np.mean(apply_robustifier(robustifier_huber, e, None)))


def features(v, C0, C1, L):
    """Scale-free description of axis v on the two walls; L = piece size (bbox diagonal)."""
    a = v[0:3] / np.linalg.norm(v[0:3])
    p0 = v[3:6] - (v[3:6] @ a) * a
    out = {}
    for name, X in (("0", C0), ("1", C1)):
        e = compute_normalized_residual(v, X)[0]
        out["c" + name] = huber_mean(e)
        out["med_abs_e" + name] = float(np.median(np.abs(e)))
        dp = X[0:3] - p0[:, None]
        z = a @ dp
        r = np.linalg.norm(dp - np.outer(a, z), axis=0)
        nax = np.abs(a @ X[3:6])
        out["r_min" + name] = float(r.min())
        out["r_med" + name] = float(np.median(r))
        out["r_max" + name] = float(r.max())
        out["z_ext" + name] = float(np.ptp(z))
        out["nax" + name] = float(np.mean(nax))
        near = r < 0.05 * L
        out["n_near" + name] = int(near.sum())
        out["nax_near" + name] = float(np.mean(nax[near])) if near.any() else np.nan
        # azimuth coverage of the wall about the axis
        e1 = np.cross(a, [1.0, 0, 0] if abs(a[0]) < 0.9 else [0, 1.0, 0])
        e1 /= np.linalg.norm(e1)
        e2 = np.cross(a, e1)
        th = np.sort(np.degrees(np.arctan2(e2 @ dp, e1 @ dp)) % 360)
        out["az_span" + name] = float(360.0 - np.max(np.diff(np.r_[th, th[0] + 360])))
    X = np.concatenate([C0, C1], axis=1)
    out["d_c"] = centroid_distance(v, X)
    out["cw"] = max(out["c0"], out["c1"])
    out["cm"] = 0.5 * (out["c0"] + out["c1"])
    return out


def pottmann_spectrum(X, rng, n=4000):
    """Singular values of Pottmann's reduced 3x3 system on a normalised subsample."""
    idx = rng.choice(X.shape[1], size=min(n, X.shape[1]), replace=False)
    Cs = X[:, idx].copy()
    m = Cs[0:3].mean(1)
    Cs[0:3] -= m[:, None]
    Cs[0:3] /= float(np.mean(np.abs(Cs)))
    from sfs_axes.plucker import euc2plucker
    J = euc2plucker(Cs[np.r_[3:6, 0:3], :])
    J = J[np.r_[3:6, 0:3], :].T
    JTJ = J.T @ J
    M = JTJ[0:3, 0:3] - JTJ[0:3, 3:6] @ np.linalg.lstsq(JTJ[3:6, 3:6], JTJ[0:3, 3:6].T, rcond=None)[0]
    return np.linalg.svd(M, compute_uv=False).tolist()


def one(job):
    stem, a = job
    pot, p0, p1, relp, gtp = piece_paths(stem, a.jugkey)
    try:
        C0, C1 = load_wall(p0), load_wall(p1)
    except Exception as exc:  # noqa: BLE001
        return dict(stem=stem, error=str(exc))
    t0 = time.time()
    C = np.concatenate([C0, C1], axis=1)
    n = C.shape[1]
    c = C[0:3].mean(1)
    L = float(np.linalg.norm(C[0:3].max(1) - C[0:3].min(1)))
    rel = read_axes(relp[0])
    gt = None
    if gtp and os.path.isfile(gtp):
        gt = read_axes(gtp)[:, 0]
    step = ps.effective_step(n, 10)
    Cd = C[:, 0:n:step]
    nd = Cd.shape[1]
    cands = []
    for seed in range(ps.UNION_SEEDS):
        rng = np.random.default_rng(seed)
        for _ in range(ps.MAX_ITERS):
            kidx = rng.choice(nd, ps.SAMPLE_SET, replace=False)
            Cs = Cd[:, kidx].copy()
            mCs = Cs[:3, :].mean(axis=1)
            Cs[:3, :] -= mCs[:, None]
            scale = float(np.mean(np.abs(Cs)))
            if scale < 1e-8:
                continue
            Cs[:3, :] /= scale
            try:
                vt = compute_pottmann_axis(Cs)
                vt[3:6] = vt[3:6] * scale + mCs
                vt[3:6] -= (vt[:3] @ vt[3:6]) * vt[:3]
                cands.append(vt)
            except Exception:  # noqa: BLE001
                pass
    V = np.column_stack(cands)
    reps, sizes = ps._cluster_union(V)
    order = np.argsort(-sizes, kind="stable")[: a.max_basins]
    rstep = max(1, int(np.ceil(n / a.nref)))
    Cr = C[:, 0:n:rstep]
    C0r = C0[:, 0:C0.shape[1]:max(1, int(np.ceil(C0.shape[1] / (a.nref // 2))))]
    C1r = C1[:, 0:C1.shape[1]:max(1, int(np.ceil(C1.shape[1] / (a.nref // 2))))]
    basins = []
    for j in order:
        raw = reps[:, j]
        ref = refine_axis_normalized(raw, Cr, max_iters=a.iters, tolerance=1e-6)
        b = dict(size=int(sizes[j]), drift=direction_angle_deg(raw[0:3], ref[0:3]),
                 raw=raw.tolist(), ref=ref.tolist())
        b["raw_f"] = features(raw, C0r, C1r, L)
        b["ref_f"] = features(ref, C0r, C1r, L)
        b["raw_e"] = ref_errors(raw, rel, gt, c)
        b["ref_e"] = ref_errors(ref, rel, gt, c)
        basins.append(b)
    # the reference itself, described the same way (what does the truth look like?)
    truth = rel[:, 0] if pot == "JUG" else rel[:, int(np.argmin(
        [ref_errors(rel[:, k], rel, gt, c)["err"] for k in range(rel.shape[1])]))]
    tf = features(truth, C0r, C1r, L)
    tloc = refine_axis_normalized(truth, Cr, max_iters=a.iters, tolerance=1e-6)
    before = None
    if a.before:
        bp = os.path.join(a.before, stem + "_Axis.xyz")
        if os.path.isfile(bp):
            bv = read_axes(bp)
            before = [ref_errors(bv[:, k], rel, gt, c) for k in range(bv.shape[1])]
    row = dict(stem=stem, pot=pot, n=n, n0=int(C0.shape[1]), n1=int(C1.shape[1]), L=L, step=step,
               n_draws=int(V.shape[1]), n_basins=int(reps.shape[1]), basins=basins,
               truth_f=tf, truth_local_deg=direction_angle_deg(tloc[0:3], truth[0:3]),
               truth_local_f=features(tloc, C0r, C1r, L),
               spectrum=pottmann_spectrum(C, np.random.default_rng(0)),
               before=before, secs=time.time() - t0)
    best = min(b["ref_e"]["err"] for b in basins)
    print("%-22s n=%7d L=%6.1f basins=%3d/%3d best_refined=%6.2f truth_local=%6.2f %5.1fs"
          % (stem, n, L, len(basins), reps.shape[1], best, row["truth_local_deg"], row["secs"]), flush=True)
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--jugkey", required=True)
    ap.add_argument("--before", default="")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--max-basins", type=int, default=40)
    ap.add_argument("--nref", type=int, default=12000)
    ap.add_argument("--iters", type=int, default=40)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    stems = sorted(fn[:-len("_Surface_0.xyz")] for fn in os.listdir(os.path.join(CORPUS, "Surfaces"))
                   if fn.endswith("_Surface_0.xyz"))
    stems += ["Juglet_Piece_%d" % i for i in range(1, 10)]
    if a.only:
        keep = a.only.split(",")
        stems = [s for s in stems if any(s.startswith(k) for k in keep)]
    # largest pieces first so the pool drains evenly
    with Pool(a.jobs) as p:
        rows = p.map(one, [(s, a) for s in stems], chunksize=1)
    with open(a.out, "w") as fh:
        json.dump(rows, fh, default=float)
    print("wrote", a.out, len(rows))


if __name__ == "__main__":
    main()
