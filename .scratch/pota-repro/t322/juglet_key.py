#!/usr/bin/env python3
"""Ticket 322 Q4: derive the Juglet's answer key from the meshes, then judge the two files.

Three witnesses for where each piece sits on the assembled juglet:
  W1  Dataset/Juglet_GT/Juglet_Piece_N_T.txt        (4x4, the file under suspicion)
  W2  TORA/dataset/juglet_gt.hdf5 pieces/N/vertices  (assembled pieces, normalised units)
  W3  contact: assembled neighbours (Juglet_simple_graph) must touch along their break.
W2 shares the scan-pose meshes' vertex order, so a similarity Procrustes on
corresponding vertices gives each piece's true pose with no fitting choice.

Then one axis is fitted to the whole assembled vessel (all nine pieces at once,
distance-invariant normal residual, Huber), checked by slicing across it, and mapped
back into every piece's own scan frame: that is the per-piece key. The released
Dataset/Axes/Juglet lines and any candidate set are scored against it.

Writes key/Juglet_Piece_N_Axis.xyz (position-first, one line) and key_report.json.
"""

import argparse
import json
import os
import sys

import h5py
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
for p in (HERE, os.path.join(HERE, ".."), os.getcwd()):
    if os.path.isdir(os.path.join(p, "sfs_axes")):
        sys.path.insert(0, p)
        break
from sfs_axes.io_axes import direction_angle_deg, read_axes, write_axes  # noqa: E402
from sfs_axes.normalized import normalized_huber_cost, refine_axis_normalized  # noqa: E402

DS = "/data/gpfs/projects/punim2657/sfs_preprocessing/Dataset"
H5 = "/data/gpfs/projects/punim2657/TORA/dataset/juglet_gt.hdf5"
NP = 9


def load_obj(path):
    V, F = [], []
    with open(path) as fh:
        for line in fh:
            if line.startswith("v "):
                V.append([float(x) for x in line.split()[1:4]])
            elif line.startswith("f "):
                F.append([int(t.split("/")[0]) - 1 for t in line.split()[1:4]])
    return np.asarray(V), np.asarray(F, dtype=int)


def face_samples(V, F):
    a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    n = np.cross(b - a, c - a)
    area = 0.5 * np.linalg.norm(n, axis=1)
    ok = area > 1e-12
    n = n[ok] / (2 * area[ok, None])
    return ((a + b + c) / 3.0)[ok], n, area[ok]


def similarity(A, B):
    """s, R, t minimising |s R A + t - B| (Umeyama). A, B (n, 3)."""
    ma, mb = A.mean(0), B.mean(0)
    A0, B0 = A - ma, B - mb
    U, S, Vt = np.linalg.svd(B0.T @ A0)
    D = np.eye(3)
    D[2, 2] = np.sign(np.linalg.det(U @ Vt))
    R = U @ D @ Vt
    s = float(np.sum(S * np.diag(D)) / np.sum(A0 ** 2))
    t = mb - s * R @ ma
    return s, R, t


def line_to_world(R, t, vt):
    d = R @ vt[0:3]
    p = R @ vt[3:6] + t
    d = d / np.linalg.norm(d)
    return np.r_[d, p - (p @ d) * d]


def line_to_local(R, t, vt):
    d = R.T @ vt[0:3]
    p = R.T @ (vt[3:6] - t)
    d = d / np.linalg.norm(d)
    return np.r_[d, p - (p @ d) * d]


def offset_at(vt_a, vt_b, c):
    """Distance between two lines measured at point c: |foot_a(c) - foot_b(c)| (mm)."""
    out = []
    for vt in (vt_a, vt_b):
        d = vt[0:3] / np.linalg.norm(vt[0:3])
        out.append(vt[3:6] + ((c - vt[3:6]) @ d) * d)
    return float(np.linalg.norm(out[0] - out[1]))


def spread(dirs):
    """Angle of each unit direction to their sign-aligned mean (deg)."""
    D = np.array(dirs)
    ref = D[0]
    D = D * np.sign(D @ ref)[:, None]
    m = D.mean(0)
    m /= np.linalg.norm(m)
    return [direction_angle_deg(d, m) for d in D]


def slice_check(P, axis, nbins=24):
    """Circle fit per slice across the axis; centre offset from the axis (mm)."""
    d = axis[0:3] / np.linalg.norm(axis[0:3])
    p0 = axis[3:6]
    e1 = np.cross(d, [1.0, 0, 0] if abs(d[0]) < 0.9 else [0, 1.0, 0])
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(d, e1)
    rel = P - p0
    z = rel @ d
    x, y = rel @ e1, rel @ e2
    edges = np.linspace(np.percentile(z, 1), np.percentile(z, 99), nbins + 1)
    rows = []
    for k in range(nbins):
        m = (z >= edges[k]) & (z < edges[k + 1])
        if m.sum() < 200:
            continue
        xs, ys = x[m], y[m]
        # angular coverage about the axis
        th = np.sort(np.degrees(np.arctan2(ys, xs)) % 360)
        cover = 360.0 - float(np.max(np.diff(np.r_[th, th[0] + 360])))
        A = np.c_[2 * xs, 2 * ys, np.ones_like(xs)]
        sol, *_ = np.linalg.lstsq(A, xs ** 2 + ys ** 2, rcond=None)
        cx, cy = sol[0], sol[1]
        r = np.sqrt(sol[2] + cx ** 2 + cy ** 2)
        res = np.abs(np.hypot(xs - cx, ys - cy) - r)
        rows.append(dict(z=float(0.5 * (edges[k] + edges[k + 1])), n=int(m.sum()),
                         cover_deg=round(cover, 1), radius=float(r),
                         centre_offset=float(np.hypot(cx, cy)),
                         circ_resid_med=float(np.median(res))))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--cands", default="", help="dir of candidate axis files to score")
    ap.add_argument("--cand-pattern", default="Juglet_Piece_{i}_Axis.xyz")
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "key"), exist_ok=True)
    rep = dict(pieces={})

    h = h5py.File(H5, "r")
    g = h["juglet_gt/Juglet-000"]
    names = [x.decode() for x in g["pieces_names"][:]]

    scan, gtv, T = {}, {}, {}
    for i in range(1, NP + 1):
        V, F = load_obj(os.path.join(DS, "Mesh/Juglet/Juglet_Piece_%02d_Mesh.obj" % i))
        scan[i] = (V, F)
        k = names.index("Piece%02d" % i)
        gtv[i] = g["pieces/%d/vertices" % k][:]
        T[i] = np.loadtxt(os.path.join(DS, "Juglet_GT/Juglet_Piece_%d_T.txt" % i))

    # ---- W2: similarity pose of every piece from vertex correspondence
    pose = {}
    scales = []
    for i in range(1, NP + 1):
        V = scan[i][0]
        G = gtv[i]
        if V.shape != G.shape:
            raise SystemExit("piece %d: scan %s vs gt %s vertex count differs" % (i, V.shape, G.shape))
        s, R, t = similarity(V, G)
        res = np.linalg.norm(s * (R @ V.T).T + t - G, axis=1)
        scales.append(s)
        pose[i] = (s, R, t)
        rep["pieces"][i] = dict(n_vertices=int(V.shape[0]), procrustes_scale=s,
                                procrustes_rms_mm=float(np.sqrt(np.mean(res ** 2)) / s),
                                procrustes_max_mm=float(res.max() / s))
    s_med = float(np.median(scales))
    rep["procrustes_scale_spread"] = [float(min(scales)), float(max(scales))]
    rep["mm_per_unit"] = 1.0 / s_med
    # Assembled frame in mm: X = R V + t/s
    Pw = {i: (pose[i][1], pose[i][2] / pose[i][0]) for i in pose}

    # ---- W1 against W2: does T reproduce the same assembly up to ONE global motion?
    for conv in ("T", "Tinv"):
        rel = []
        for i in range(1, NP + 1):
            M = T[i] if conv == "T" else np.linalg.inv(T[i])
            R_true, t_true = Pw[i]
            # global G with  true = G * M  ->  G = true * M^-1
            Mt = np.eye(4)
            Mt[:3, :3], Mt[:3, 3] = R_true, t_true
            rel.append(Mt @ np.linalg.inv(M))
        Rs = [r[:3, :3] for r in rel]
        ang = [np.degrees(np.arccos(np.clip((np.trace(Rs[0].T @ r) - 1) / 2, -1, 1))) for r in Rs]
        rep["T_vs_mesh_" + conv] = dict(rot_deg_vs_piece1=[round(x, 3) for x in ang],
                                        det=[round(float(np.linalg.det(T[i][:3, :3])), 6) for i in T])

    # ---- W3: contact between graph neighbours, in the W2 frame and in the T frame
    A = np.loadtxt(os.path.join(DS, "Juglet_GT/Juglet_simple_graph.txt"))
    edges = [(i + 1, j + 1) for i in range(NP) for j in range(i + 1, NP) if A[i, j] > 0]
    rep["graph_edges"] = edges

    def contact(frames):
        trees = {i: cKDTree(frames[i]) for i in frames}
        rows = []
        for i, j in edges:
            d, _ = trees[j].query(frames[i], k=1)
            rows.append(dict(pair=[i, j], min_mm=round(float(d.min()), 3),
                             n_within_0p5mm=int(np.sum(d < 0.5))))
        return rows

    fr_w2 = {i: (Pw[i][0] @ scan[i][0].T).T + Pw[i][1] for i in scan}
    fr_t = {i: (T[i][:3, :3] @ scan[i][0].T).T + T[i][:3, 3] for i in scan}
    rep["contact_mesh_pose"] = contact(fr_w2)
    rep["contact_T_pose"] = contact(fr_t)

    # ---- one axis for the whole assembled vessel
    Pall, Nall, Aall, owner = [], [], [], []
    for i in range(1, NP + 1):
        c, n, ar = face_samples(*scan[i])
        R, t = Pw[i]
        Pall.append((R @ c.T).T + t)
        Nall.append((R @ n.T).T)
        Aall.append(ar)
        owner.append(np.full(len(ar), i))
    Pall, Nall, Aall, owner = map(np.concatenate, (Pall, Nall, Aall, owner))
    rng = np.random.default_rng(0)
    pick = rng.choice(len(Aall), size=min(60000, len(Aall)), replace=False, p=Aall / Aall.sum())
    X = np.vstack([Pall[pick].T, Nall[pick].T])
    ctr = Pall.mean(0)
    evals, evecs = np.linalg.eigh(np.cov((Pall - ctr).T, aweights=Aall))
    best = None
    for k in range(3):
        d0 = evecs[:, k]
        v0 = np.r_[d0, ctr - (ctr @ d0) * d0]
        v = refine_axis_normalized(v0, X, max_iters=200, tolerance=1e-10)
        c = normalized_huber_cost(v, X)
        if best is None or c < best[0]:
            best = (c, v, k)
    cost, axis_w, k0 = best
    rep["world_axis"] = dict(dir=axis_w[0:3].tolist(), pos=axis_w[3:6].tolist(),
                             huber_cost=cost, init_pca_component=k0,
                             pca_eigvals=evals.tolist())
    # leave-one-piece-out stability: refit without each piece
    loo = []
    for i in range(1, NP + 1):
        m = owner[pick] != i
        v = refine_axis_normalized(axis_w, X[:, m], max_iters=200, tolerance=1e-10)
        loo.append(dict(piece=i, angle_deg=direction_angle_deg(v[0:3], axis_w[0:3]),
                        offset_mm=offset_at(v, axis_w, ctr)))
    rep["world_axis_leave_one_out"] = loo
    rep["slices"] = slice_check(Pall, axis_w)

    # ---- per-piece key in scan frame; released lines scored against it
    rel_dir = os.path.join(DS, "Axes/Juglet")
    released_world = []
    for i in range(1, NP + 1):
        R, t = Pw[i]
        key = line_to_local(R, t, axis_w)
        write_axes(os.path.join(a.out, "key", "Juglet_Piece_%d_Axis.xyz" % i), key[:, None])
        V = scan[i][0]
        c = V.mean(0)
        dvec = key[0:3]
        rel = V - key[3:6]
        rr = np.linalg.norm(rel - np.outer(rel @ dvec, dvec), axis=1)
        cs, ns, ar = face_samples(*scan[i])
        nax = np.abs(ns @ dvec)
        pr = rep["pieces"][i]
        pr.update(diag_mm=float(np.linalg.norm(V.max(0) - V.min(0))),
                  r_min_mm=float(rr.min()), r_med_mm=float(np.median(rr)), r_max_mm=float(rr.max()),
                  z_extent_mm=float(np.ptp(rel @ dvec)),
                  mean_abs_n_dot_a=float(np.average(nax, weights=ar)),
                  n_dot_a_p10_p50_p90=[float(x) for x in np.percentile(nax, [10, 50, 90])],
                  key=key.tolist())
        rl = read_axes(os.path.join(rel_dir, "Juglet_Piece_%d_Axis.xyz" % i))
        errs = [(direction_angle_deg(rl[0:3, k], key[0:3]), offset_at(rl[:, k], key, c))
                for k in range(rl.shape[1])]
        pr["released_vs_key"] = [[round(e[0], 2), round(e[1], 1)] for e in errs]
        released_world.append(line_to_world(R, t, rl[:, 0])[0:3])
        # the 321 arithmetic for the record: released line pushed through T
        if a.cands:
            path = os.path.join(a.cands, a.cand_pattern.format(i=i, i02="%02d" % i))
            if os.path.isfile(path):
                cv = read_axes(path)
                pr["cand_vs_key"] = [[round(direction_angle_deg(cv[0:3, k], key[0:3]), 2),
                                      round(offset_at(cv[:, k], key, c), 1)] for k in range(cv.shape[1])]
    rep["released_world_spread_deg_meshpose"] = [round(x, 2) for x in spread(released_world)]
    for conv in ("a", "Ra", "RTa"):
        dirs = []
        for i in range(1, NP + 1):
            rl = read_axes(os.path.join(rel_dir, "Juglet_Piece_%d_Axis.xyz" % i))[0:3, 0]
            R = T[i][:3, :3]
            dirs.append(rl if conv == "a" else (R @ rl if conv == "Ra" else R.T @ rl))
        rep["released_world_spread_deg_T_" + conv] = [round(x, 2) for x in spread(dirs)]
    # the key pushed through T: does T at least carry the TRUE axis consistently?
    for conv in ("Ra", "RTa"):
        dirs = []
        for i in range(1, NP + 1):
            kd = np.array(rep["pieces"][i]["key"][0:3])
            R = T[i][:3, :3]
            dirs.append(R @ kd if conv == "Ra" else R.T @ kd)
        rep["key_world_spread_deg_T_" + conv] = [round(x, 2) for x in spread(dirs)]

    np.savez_compressed(os.path.join(a.out, "assembled_samples.npz"), P=Pall[pick], N=Nall[pick],
                        owner=owner[pick], axis=axis_w)
    with open(os.path.join(a.out, "key_report.json"), "w") as fh:
        json.dump(rep, fh, indent=1, default=float)
    print(json.dumps({k: v for k, v in rep.items() if k != "pieces"}, indent=1, default=float))
    for i in range(1, NP + 1):
        p = rep["pieces"][i]
        print("p%d n=%d procr_rms=%.4fmm diag=%.1f r=[%.1f %.1f %.1f] z=%.1f |n.a|=%.2f rel=%s cand=%s"
              % (i, p["n_vertices"], p["procrustes_rms_mm"], p["diag_mm"], p["r_min_mm"],
                 p["r_med_mm"], p["r_max_mm"], p["z_extent_mm"], p["mean_abs_n_dot_a"],
                 p["released_vs_key"], p.get("cand_vs_key")))


if __name__ == "__main__":
    main()
