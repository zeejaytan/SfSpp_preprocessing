#!/usr/bin/env python3
"""Ticket 28 -- a Python replica (numpy + scipy) of growPaper234.

The C++ is mesh_processing_headless.cpp:2940-2998, called at :3438.  The semantics
below are copied from that source, not from the paper:

  * one pass over the whole cloud; the seed order is every point sorted by
    pnormals.curvature ascending (std::sort at :2950 -- here numpy's stable sort);
  * a seed already claimed is skipped, so a discarded region still burns the points
    it claimed during its BFS;
  * BFS over a front queue.  For each front point cf the reference normal is
    normal[cf] -- the front point's, NOT the seed's -- and the nb+1 nearest
    neighbours of cf are tested in distance order (self is skipped by cand == cf);
  * a candidate joins iff curvature[cand] < kappa AND
    getAngle3D(normal[cf], normal[cand]) <= theta in degrees (a candidate exactly
    at theta joins: the C++ rejects only on '> thetaDeg', :2985);
  * the floor minClusterSize is applied to the finished regions only, so the
    growth itself is identical whatever the floor is.

Curvature is not written to the rung-2 dump, so it is recomputed here the way the
C++ recomputed it (getNormalsOnSurface :726-745):
pcl::NormalEstimation with setKSearch(max(10, min(50, npts/300))) over the k
nearest neighbours including self, and curvature = |lambda_min| / trace(cov)
(pcl/features/impl/feature.hpp:61-88, solvePlaneParameters), which for a
covariance matrix is lambda0/(lambda0+lambda1+lambda2) <= 1/3.

The angle is pcl::getAngle3D (pcl/common/impl/common.hpp:46-64): each vector is
normalised in float, dotted in float, the result clamped to [-1,1] by two
comparisons, then acos in double and scaled to degrees.  A zero-length normal
gives 0/0 = NaN, the two clamps leave NaN alone, acos(NaN) = NaN and 'NaN >
theta' is false, so a dropped normal would be admitted; the count of such points
is reported as n_zero_normals.
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from scipy.spatial import cKDTree



def read_rung2_ply(path):
    with open(path, "rb") as f:
        raw = f.read()
    end = raw.find(b"end_header")
    if end < 0:
        raise SystemExit("no end_header: %s" % path)
    header = raw[:end].decode("ascii", "replace").splitlines()
    n = None
    props = []
    for line in header:
        p = line.split()
        if len(p) >= 3 and p[0] == "element" and p[1] == "vertex":
            n = int(p[2])
        elif p and p[0] == "property":
            props.append(p[-1])
    if n is None:
        raise SystemExit("no vertex element: %s" % path)
    want = ["x", "y", "z", "nx", "ny", "nz", "cluster_id", "reason"]
    if props[:8] != want:
        raise SystemExit("unexpected vertex properties %r in %s" % (props, path))
    body = raw[end + len(b"end_header"):].decode("ascii", "replace")
    arr = np.loadtxt(body.splitlines(), dtype=np.float64, ndmin=2)
    if arr.shape[0] != n or arr.shape[1] != 8:
        raise SystemExit("body %r does not match header %d x 8 in %s"
                         % (arr.shape, n, path))
    xyz = arr[:, 0:3].astype(np.float32)
    nrm = arr[:, 3:6].astype(np.float32)
    cid = arr[:, 6].astype(np.int64)
    rsn = arr[:, 7].astype(np.int64)
    return xyz, nrm, cid, rsn, props


def pcl_curvature(xyz, k):
    pts = xyz.astype(np.float64)
    n = pts.shape[0]
    kk = int(min(max(int(k), 2), n))
    tree = cKDTree(pts)
    _, idx = tree.query(pts, k=kk, workers=-1)
    x = pts[idx] - pts[idx].mean(axis=1, keepdims=True)
    cov = np.einsum("nki,nkj->nij", x, x) / float(kk)
    w = np.linalg.eigvalsh(cov)
    s = w.sum(axis=1)
    curv = np.zeros(n, dtype=np.float64)
    nz = s > 0.0
    curv[nz] = np.abs(w[nz, 0] / s[nz])
    return curv.astype(np.float32)


def normalised_f32(nrm):
    a = nrm.astype(np.float32)
    with np.errstate(invalid="ignore", divide="ignore"):
        ln = np.sqrt((a[:, 0] * a[:, 0] + a[:, 1] * a[:, 1]
                      + a[:, 2] * a[:, 2]).astype(np.float32)).astype(np.float32)
        return (a / ln[:, None]).astype(np.float32)


def angle_deg(n1, n2):
    rad = float(np.dot(n1, n2))
    if rad < -1.0:
        rad = -1.0
    elif rad > 1.0:
        rad = 1.0
    try:
        return math.degrees(math.acos(rad))
    except ValueError:
        return float("nan")


def grow(xyz, nrm, curv, nb, theta_deg, kappa):
    n = xyz.shape[0]
    pts = xyz.astype(np.float64)
    tree = cKDTree(pts)
    nu = normalised_f32(nrm)
    kq = min(int(nb) + 1, n)
    claimed = np.zeros(n, dtype=bool)
    regions = []
    for sd in np.argsort(curv, kind="stable"):
        sd = int(sd)
        if claimed[sd]:
            continue
        claimed[sd] = True
        reg = [sd]
        front = [sd]
        level = {sd: 0}
        fh = 0
        st = {"pops": 0, "tests": 0, "fail_curv": 0, "fail_angle": 0,
              "skip_self": 0, "skip_claimed": 0, "joined": 0}
        depth = 0
        while fh < len(front):
            cf = front[fh]
            fh += 1
            st["pops"] += 1
            _, nbrs = tree.query(pts[cf], k=kq)
            cur_n = nu[cf]
            for cand in np.atleast_1d(nbrs):
                cand = int(cand)
                if cand == cf:
                    st["skip_self"] += 1
                    continue
                if claimed[cand]:
                    st["skip_claimed"] += 1
                    continue
                st["tests"] += 1
                if curv[cand] >= kappa:
                    st["fail_curv"] += 1
                    continue
                if angle_deg(cur_n, nu[cand]) > theta_deg:
                    st["fail_angle"] += 1
                    continue
                claimed[cand] = True
                st["joined"] += 1
                reg.append(cand)
                front.append(cand)
                lv = level[cf] + 1
                level[cand] = lv
                if lv > depth:
                    depth = lv
        st.update({"size": len(reg), "seed": sd,
                   "seed_curv": float(curv[sd]), "max_depth": depth})
        regions.append(st)
    return regions, nu


def summarise(regions, floor):
    sizes = sorted((r["size"] for r in regions), reverse=True)
    if floor is None:
        return sizes, sizes
    return sizes, [s for s in sizes if s >= floor]


def floor_label(floor):
    return "none" if floor is None else str(int(floor))


EXPECT = {"Juglet_Piece_3": [169, 99], "Juglet_Piece_5": [679],
          "Juglet_Piece_7": [326, 263, 77, 68, 65]}


def calibrate(dump_root, tag, theta, kappa, nb, floor, outdir):
    ok = True
    print("[CAL] theta=%.2f nb=%d kappa=%.3f floor=%d arm=%s root=%s"
          % (theta, nb, kappa, floor, tag, dump_root))
    if os.path.isdir(outdir):
        pass
    else:
        os.makedirs(outdir, exist_ok=True)
    for piece in ("Juglet_Piece_2", "Juglet_Piece_3", "Juglet_Piece_5",
                  "Juglet_Piece_7"):
        ply = os.path.join(dump_root, tag, piece, "r2_clusters_premerge.ply")
        if not os.path.exists(ply):
            raise SystemExit("missing rung-2 dump: %s" % ply)
        xyz, nrm, cid, rsn, props = read_rung2_ply(ply)
        n = xyz.shape[0]
        curv_k = max(10, min(50, n // 300))
        curv = pcl_curvature(xyz, curv_k)
        regions, nu = grow(xyz, nrm, curv, nb, theta, kappa)
        before = sorted((r["size"] for r in regions), reverse=True)
        sizes, surv = summarise(regions, floor)
        # the floor must not change the growth itself
        regions0, _ = grow(xyz, nrm, curv, nb, theta, kappa)
        same = sorted((r["size"] for r in regions0), reverse=True) == before
        dump_cids = sorted(set(int(c) for c in cid if c >= 0))
        dump_sizes = []
        for c in dump_cids:
            dump_sizes.append(int(np.count_nonzero(cid == c)))
        dump_sizes.sort(reverse=True)
        exp = EXPECT.get(piece)
        verdict = "n/a"
        if exp is not None:
            verdict = "MATCH" if surv == exp else "MISMATCH"
            if verdict == "MISMATCH":
                ok = False
        print("[CAL] %-16s npts=%-6d curv_k=%-3d sizes_before=%-60s "
              "surv_ge_%d=%-40s expected=%-40s dump_clusters=%-40s %s "
              "growth_floor_independent=%s n_zero_normals=%d curv_max=%.6f"
              % (piece, n, curv_k, before, floor, surv,
                 exp if exp is not None else "-", dump_sizes, verdict, same,
                 int(np.count_nonzero(np.isnan(nu[:, 0]))), float(curv.max())))
        sys.stdout.flush()
        dl = os.path.join(outdir, "calib")
        os.makedirs(dl, exist_ok=True)
        with open(os.path.join(dl, "%s__%s.json" % (tag, piece)), "w") as f:
            json.dump({"piece": piece, "cloud": tag, "ply": ply, "npts": n,
                       "curv_k": curv_k, "theta_deg": theta, "kappa": kappa,
                       "nb": nb, "floor": floor, "sizes_before": before,
                       "survivors": surv, "expected": exp,
                       "verdict": verdict, "dump_cluster_sizes": dump_sizes,
                       "growth_floor_independent": same,
                       "regions": regions}, f, indent=1, sort_keys=True)
    print("[CAL] result=%s" % ("MATCH" if ok else "MISMATCH"))
    return 0 if ok else 4


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("calibrate")
    c.add_argument("--dump-root", required=True)
    c.add_argument("--tag", default="B")
    c.add_argument("--theta", type=float, default=3.4)
    c.add_argument("--kappa", type=float, default=1.0)
    c.add_argument("--nb", type=int, default=10)
    c.add_argument("--floor", type=int, default=50)
    c.add_argument("--outdir", required=True)
    s = sub.add_parser("sweep")
    s.add_argument("--ply", required=True)
    s.add_argument("--piece", required=True)
    s.add_argument("--tag", required=True)
    s.add_argument("--label", default=None)
    s.add_argument("--thetas", type=float, nargs="+", default=[3.4, 4.0])
    s.add_argument("--kappa", type=float, default=1.0)
    s.add_argument("--nb", type=int, default=10)
    s.add_argument("--floors", nargs="+", default=["50", "none"])
    s.add_argument("--outdir", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "calibrate":
        return calibrate(a.dump_root, a.tag, a.theta, a.kappa, a.nb, a.floor,
                         a.outdir)
    floors = []
    for f in a.floors:
        floors.append(None if str(f).lower() in ("none", "all", "0") else int(f))
    floors = sorted(set(floors), key=lambda x: (x is None, x))
    label = a.label or a.tag
    xyz, nrm, cid, rsn, props = read_rung2_ply(a.ply)
    n = xyz.shape[0]
    curv_k = max(10, min(50, n // 300))
    curv = pcl_curvature(xyz, curv_k)
    nu = normalised_f32(nrm)
    zero_normals = int(np.count_nonzero(np.isnan(nu[:, 0])))
    print("[SWEEP] piece=%s cloud=%s npts=%d curv_k=%d curv_max=%.6f "
          "n_zero_normals=%d dump_clusters=%s"
          % (a.piece, label, n, curv_k, float(curv.max()), zero_normals,
             sorted(set(int(x) for x in cid if x >= 0))))
    if not os.path.isdir(a.outdir):
        os.makedirs(a.outdir, exist_ok=True)
    tsv = os.path.join(a.outdir, "cells28.tsv")
    if not os.path.exists(tsv):
        with open(tsv, "w") as f:
            f.write("piece\tcloud\ttheta\tkappa\tnb\tfloor\tnpts\tcurv_k\t"
                    "regions_before\tsizes_before\tsurvivors\tsurviving_count\t"
                    "total_claimed\tlargest_size\tlargest_depth\tlargest_pops\t"
                    "fail_angle\tfail_curv\tn_zero_normals\tmax_curv\n")
    for theta in sorted(set(a.thetas)):
        regions, _ = grow(xyz, nrm, curv, a.nb, theta, a.kappa)
        before = sorted((r["size"] for r in regions), reverse=True)
        biggest = max(regions, key=lambda r: r["size"]) if regions else None
        for floor in floors:
            surv = before if floor is None else [x for x in before if x >= floor]
            out = {"piece": a.piece, "cloud": label, "ply": a.ply,
                   "theta_deg": theta, "kappa": a.kappa, "nb": a.nb,
                   "floor": floor, "npts": n, "curv_k": curv_k,
                   "curv_max": float(curv.max()), "n_zero_normals": zero_normals,
                   "cluster_ids_in_dump": sorted(set(int(x) for x in cid if x >= 0)),
                   "regions_before_floor": before, "regions": regions,
                   "survivors": surv, "total_claimed": int(sum(before)),
                   "fail_angle_total": int(sum(r["fail_angle"] for r in regions)),
                   "fail_curv_total": int(sum(r["fail_curv"] for r in regions)),
                   "largest": biggest}
            name = "%s__%s__%s__t%.2f__f%s.json" % (label, a.piece, label, theta,
                                                    floor_label(floor))
            with open(os.path.join(a.outdir, name), "w") as f:
                json.dump(out, f, indent=1, sort_keys=True)
            row = [a.piece, label, "%.2f" % theta, "%.3f" % a.kappa, str(a.nb),
                   floor_label(floor), str(n), str(curv_k), str(len(before)),
                   ",".join(str(x) for x in before) if before else "-",
                   ",".join(str(x) for x in surv) if surv else "-",
                   str(len(surv)), str(sum(before)),
                   str(biggest["size"]) if biggest else "0",
                   str(biggest["max_depth"]) if biggest else "-",
                   str(biggest["pops"]) if biggest else "-",
                   str(out["fail_angle_total"]), str(out["fail_curv_total"]),
                   str(zero_normals), "%.6f" % out["curv_max"]]
            with open(tsv, "a") as f:
                f.write("\t".join(row) + "\n")
            print("[CELL28] piece=%s cloud=%s theta=%.2f kappa=%.3f nb=%d "
                  "floor=%s npts=%d curv_k=%d regions=%d sizes=%s surviving=%d "
                  "largest=%s depth=%s pops=%s fail_angle=%s fail_curv=%s"
                  % (a.piece, label, theta, a.kappa, a.nb, floor_label(floor), n,
                     curv_k, len(before), row[9], len(surv), row[13], row[14],
                     row[15], row[16], row[17]))
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))