#!/usr/bin/env python3
"""Ticket 32 part B -- curvature radius and neighbour-normal angle over FIXED PHYSICAL
WINDOWS (1, 2, 3, 5 mm) instead of a fixed neighbour count.

The quadric fit is ticket 30's (analyse30.quadric_radii, copied arithmetic for
arithmetic; the selftest proves it reproduces the k-NN version on identical neighbour
sets).  The angle is ticket 29's (replica29.pair_angles, imported, not rewritten).
The mesh noise floor is ticket 30's (analyse30.mesh_floor, imported).

Only the neighbourhood rule changes: every neighbour inside the window is used instead
of the k nearest.
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy.spatial import cKDTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import io32
import partA32 as PA
import replica29 as R
import analyse30 as A30

RHO_CAP_MM = A30.RHO_CAP_MM
WINDOWS = (1.0, 2.0, 3.0, 5.0)
N_CENTRES = 8000
K_NB = 40000
ANG_STEP = 0.005
ANG_NB = int(round(180.0 / ANG_STEP)) + 1
MIN_FIT_NB = 6


def quadric_radii_from_lists(pts, sub, lists):
    """analyse30.quadric_radii arithmetic over an explicit list of neighbour index arrays."""
    m = sub.size
    rad = np.full(m, np.nan)
    groups = {}
    for i, idx in enumerate(lists):
        groups.setdefault(int(idx.size), []).append(i)
    for k in sorted(groups):
        if k < MIN_FIT_NB:
            continue
        ii = np.asarray(groups[k], dtype=np.int64)
        block = max(1, min(192, int(1.5e6 // max(k, 1))))
        for s in range(0, ii.size, block):
            jj = ii[s:s + block]
            nb = np.stack([lists[i] for i in jj])
            Q = pts[nb]
            P = pts[sub[jj]]
            C = Q - Q.mean(axis=1, keepdims=True)
            cov = np.einsum("mki,mkj->mij", C, C)
            _w, V = np.linalg.eigh(cov)
            e = V[:, :, 0]
            a = np.tile(np.array([1.0, 0.0, 0.0]), (e.shape[0], 1))
            a[np.abs(e[:, 0]) > 0.9] = np.array([0.0, 1.0, 0.0])
            u = np.cross(e, a)
            u /= np.linalg.norm(u, axis=1, keepdims=True)
            v = np.cross(e, u)
            rel = Q - P[:, None, :]
            x = np.einsum("mki,mi->mk", rel, u)
            y = np.einsum("mki,mi->mk", rel, v)
            z = np.einsum("mki,mi->mk", rel, e)
            one = np.ones_like(x)
            A = np.stack([x, y, 0.5 * x * x, x * y, 0.5 * y * y, one], axis=2)
            M = np.einsum("mki,mkj->mij", A, A)
            b = np.einsum("mki,mk->mi", A, z)
            ridge = 1e-12 * np.trace(M, axis1=1, axis2=2)
            M[:, np.arange(6), np.arange(6)] += ridge[:, None]
            coef = np.linalg.solve(M, b[:, :, None])[:, :, 0]
            L, Mm, N = coef[:, 2], coef[:, 3], coef[:, 4]
            tr = L + N
            det = L * N - Mm * Mm
            disc = np.sqrt(np.maximum(0.25 * tr * tr - det, 0.0))
            k1 = 0.5 * tr + disc
            k2 = 0.5 * tr - disc
            kmax = np.maximum(np.abs(k1), np.abs(k2))
            rr = np.full(kmax.shape, np.inf)
            good = np.isfinite(kmax) & (kmax > 1.0 / RHO_CAP_MM)
            rr[good] = 1.0 / kmax[good]
            rr[~np.isfinite(rr)] = RHO_CAP_MM
            rad[jj] = np.clip(rr, 0.0, RHO_CAP_MM)
    return rad


def hist_pct(counts, q):
    tot = int(counts.sum())
    if tot <= 0:
        return None
    c = np.cumsum(counts)
    i = int(np.searchsorted(c, q / 100.0 * tot))
    if i >= counts.size:
        i = counts.size - 1
    return (i + 0.5) * ANG_STEP


def load_cell(arm, piece, dataset, corpus, outdir):
    cells = os.path.join(outdir, "cells")
    if arm == "J":
        n = int(piece)
        p = PA.jug_paths(dataset, n)
        cl = io32.read_pcd(p["pcd"])
        acell = os.path.join(cells, "A_J_%d.json" % n)
        mesh = p["objs"][0]
        if os.path.isfile(acell):
            with open(acell) as f:
                a = json.load(f)
            if a.get("obj_chosen"):
                mesh = a["obj_chosen"]
        return {"xyz": cl["xyz"], "nrm": cl["nrm"], "md5": cl["md5"],
                "src": p["pcd"], "mesh": mesh, "n_points": cl["n_points"]}
    if arm == "PA_native":
        p = PA.pa_paths(corpus, int(piece))
        cl = io32.read_pcd(p["pcd"])
        return {"xyz": cl["xyz"], "nrm": cl["nrm"], "md5": cl["md5"],
                "src": p["pcd"], "mesh": p["obj"], "n_points": cl["n_points"]}
    if arm == "PA_025":
        p = PA.pa_paths(corpus, int(piece))
        gp = os.path.join(outdir, "geom", "pa025", "Pot_A_Piece_%02d_025.npz" % int(piece))
        if not os.path.isfile(gp):
            raise SystemExit("[B32] missing subsampled cloud %s" % gp)
        z = np.load(gp, allow_pickle=False)
        return {"xyz": np.asarray(z["xyz"], dtype=np.float64),
                "nrm": np.asarray(z["nrm"], dtype=np.float64),
                "md5": str(z["src_md5"]), "src": str(z["src"]) + " -> " + gp,
                "mesh": p["obj"], "n_points": int(z["xyz"].shape[0])}
    raise SystemExit("[B32] unknown arm %r" % arm)


def cell(arm, piece, dataset, corpus, outdir, seed):
    rng = np.random.default_rng(seed)
    c = load_cell(arm, piece, dataset, corpus, outdir)
    pts = np.ascontiguousarray(c["xyz"], dtype=np.float64)
    if c["nrm"] is None or c["nrm"].size == 0:
        raise SystemExit("[B32] no normals in %s" % c["src"])
    nu = R.normalised_f32(np.ascontiguousarray(c["nrm"], dtype=np.float32))
    n = pts.shape[0]
    tree = cKDTree(pts)
    centres = np.arange(n)
    if n > N_CENTRES:
        centres = np.sort(rng.choice(n, size=N_CENTRES, replace=False))
    smp = centres if centres.size <= 20000 else np.sort(
        rng.choice(centres, size=20000, replace=False))
    d, _ = tree.query(pts[smp], k=2, workers=-1)
    spacing = float(np.median(d[:, 1]))
    verts, vnorm, _nf = A30.read_obj_normals(c["mesh"])
    floor, floor_n = A30.mesh_floor(pts, c["nrm"], verts, vnorm, rng)
    rec = {"cell": "B_%s_%s" % (arm, piece), "arm": arm,
           "piece": piece if arm == "J" else "Pot_A_Piece_%02d" % int(piece),
           "src": c["src"], "md5": c["md5"], "mesh": c["mesh"],
           "mesh_md5": io32.md5_file(c["mesh"]), "n_points": int(n),
           "n_centres": int(centres.size), "spacing_median_mm": spacing,
           "noise_floor_deg": floor, "noise_floor_n": floor_n,
           "noise_floor_note": "one value per (piece, arm): the mesh normal is not a "
                               "function of the window; repeated on every window row",
           "n_zero_normals": int(np.count_nonzero(np.isnan(nu[:, 0]))),
           "k_nb_cap": K_NB, "ang_step_deg": ANG_STEP,
           "windows": {}}
    for w in WINDOWS:
        r = float(w)
        cnt = tree.query_ball_point(pts[centres], r, return_length=True, workers=-1)
        nb_true = np.asarray(cnt, dtype=np.int64) - 1
        hist = np.zeros(ANG_NB, dtype=np.int64)
        rad_all = np.full(centres.size, np.nan)
        n_pairs = 0
        n_gt90 = 0
        n_nan = 0
        n_capped = 0
        chunk0 = max(1, min(100, int(4.0e6 // max(int(np.percentile(nb_true, 90)), 1))))
        for c0 in range(0, centres.size, chunk0):
            idxc = centres[c0:c0 + chunk0]
            lists = tree.query_ball_point(pts[idxc], r, workers=-1)
            fit = []
            rows = []
            cols = []
            for li, nb in enumerate(lists):
                nb = np.asarray(nb, dtype=np.int64)
                nb = nb[nb != idxc[li]]
                if nb.size == 0:
                    fit.append(np.zeros(0, dtype=np.int64))
                    continue
                if nb.size > K_NB:
                    n_capped += 1
                    nb = np.sort(rng.choice(nb, size=K_NB, replace=False))
                fit.append(nb)
                rows.append(np.full(nb.size, int(idxc[li]), dtype=np.int64))
                cols.append(nb)
            if not fit:
                continue
            rad_all[c0:c0 + idxc.size] = quadric_radii_from_lists(pts, idxc, fit)
            if rows:
                rows_a = np.concatenate(rows)
                cols_a = np.concatenate(cols)
                ang = R.pair_angles(nu, rows_a, cols_a)
                good = ang[np.isfinite(ang)]
                n_nan += int(ang.size - good.size)
                n_pairs += int(good.size)
                n_gt90 += int(np.count_nonzero(good > 90.0))
                b = np.minimum((good / ANG_STEP).astype(np.int64), ANG_NB - 1)
                hist += np.bincount(b, minlength=ANG_NB)
        ok = rad_all[np.isfinite(rad_all)]
        q = np.percentile(ok, [25, 50, 75]) if ok.size else [None, None, None]
        rec["windows"]["%.1f" % w] = {
            "window_mm": w,
            "n_nb_median": float(np.median(nb_true)),
            "n_nb_p25": float(np.percentile(nb_true, 25)),
            "n_nb_p90": float(np.percentile(nb_true, 90)),
            "n_nb_min": int(nb_true.min()) if nb_true.size else None,
            "n_nb_max": int(nb_true.max()) if nb_true.size else None,
            "n_centres": int(centres.size),
            "n_centres_capped": int(n_capped),
            "n_fit": int(ok.size),
            "n_fit_skipped": int(rad_all.size - ok.size),
            "rho_p25_mm": None if q[0] is None else float(q[0]),
            "rho_median_mm": None if q[1] is None else float(q[1]),
            "rho_p75_mm": None if q[2] is None else float(q[2]),
            "share_at_cap": None if not ok.size else float(
                np.mean(ok >= RHO_CAP_MM - 1e-9)),
            "n_pairs": n_pairs, "n_nan_angle": n_nan,
            "share_gt90": None if not n_pairs else float(n_gt90) / float(n_pairs),
            "angle_p10_deg": hist_pct(hist, 10.0),
            "angle_p50_deg": hist_pct(hist, 50.0),
            "angle_p90_deg": hist_pct(hist, 90.0)}
        print("[B32] %s %s w=%.1f nb_med=%.0f rho=%.3f ang50=%s pairs=%d"
              % (arm, rec["piece"], w, rec["windows"]["%.1f" % w]["n_nb_median"],
                 rec["windows"]["%.1f" % w]["rho_median_mm"] or float("nan"),
                 rec["windows"]["%.1f" % w]["angle_p50_deg"], n_pairs))
        sys.stdout.flush()
    d = os.path.join(outdir, "cells")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "B_%s_%s.json" % (arm, piece))
    with open(p, "w") as f:
        json.dump(rec, f, indent=1, sort_keys=True)
    print("[B32] wrote %s  floor=%.4f deg (n=%d) spacing=%.4f mm n=%d"
          % (p, floor, floor_n, spacing, n))
    sys.stdout.flush()
    return rec


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True)
    ap.add_argument("--piece", required=True)
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--seed", type=int, default=32)
    a = ap.parse_args(argv)
    cell(a.arm, a.piece, a.dataset, a.corpus, a.outdir, a.seed)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
