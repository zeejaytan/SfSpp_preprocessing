#!/usr/bin/env python3
"""Ticket 38 instrument: grow regions at one angle threshold, with no floor applied, on a cloud
of any density, and report the whole pre-floor distribution.

The growth is replica37.grow, imported unchanged (replica37.py sits beside this file, byte-identical
to the copy ticket 37 ran -- the md5 is recorded by the driver).  What is new here is only the
choice of normals and the bookkeeping ticket 38 asks for.

Arms, all at the same theta/kappa/neighbours so the only variable is the normal field:
  scan  the cloud's own normals, as shipped (real clouds only; this is the anchor that must
        reproduce ticket 37's recorded numbers)
  A     analytic face normals straight from the sampler, sign as the mesh winding gives it
  F     the same face normals flipped towards the viewpoint (0,0,0), which is what PCL's
        NormalEstimation does with the header's VIEWPOINT 0 0 0 1 0 0 0
  B     the pipeline's own re-estimation: PCA over k = max(5, min(20, n/1000)) neighbours
        (mesh_processing_headless.cpp:405-433, g_normalMinK=5 g_normalMaxK=20), then the same
        viewpoint flip

usage:
  grow38.py selftest
  grow38.py cell --cloud X.pcd --mesh M.obj --orig-cloud O.pcd --piece P --level 4 --arm A
                 --outdir O [--theta 3.4 --kappa 1.0 --nb 10 --floor 50]
  grow38.py aggregate --cells DIR --outdir DIR [--figures37 figs.json]
"""
import argparse
import json
import os
import sys
import time

import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import replica37 as R          # noqa: E402
import measure34 as M          # noqa: E402
import mesh38 as S             # noqa: E402

VIEWPOINT = np.zeros(3, dtype=np.float64)      # the PCD header's VIEWPOINT 0 0 0 1 0 0 0


def curvature_k(n):
    """replica37's rule, the same one the pipeline's floor-scaling path uses."""
    return int(min(max(n // 300, 10), 50))


def pipeline_k(n):
    """mesh_processing_headless.cpp:405-433: g_normalMinK=5, g_normalMaxK=20, n/1000."""
    return int(max(5, min(20, n // 1000)))


def orient(nrm, pts, vp=VIEWPOINT):
    """Flip each normal towards the viewpoint, as PCL does.  Not a per-point free choice: it is
    the pipeline's own rule, so it is reproducible."""
    v = vp[None, :] - pts
    d = np.einsum("ij,ij->i", nrm, v)
    out = nrm.copy()
    out[d < 0] *= -1.0
    return out


def normals_for(arm, xyz, nrm_file, n_pca_log=None):
    n = len(xyz)
    if arm in ("scan", "scan37"):
        if nrm_file is None:
            raise ValueError("arm scan needs normals in the cloud")
        src = "cloud" if arm == "scan" else "cloud(t37prefloor)"
        return np.asarray(nrm_file, dtype=np.float64), src, 0
    if arm == "A":
        return np.asarray(nrm_file, dtype=np.float64), "analytic", 0
    if arm == "F":
        return orient(np.asarray(nrm_file, dtype=np.float64), xyz), "analytic+viewpoint", 0
    if arm == "B":
        k = pipeline_k(n)
        pn, _c = M.pca_normals(xyz, k)
        return orient(pn, xyz), "pca%d+viewpoint" % k, k
    raise ValueError("unknown arm %r" % (arm,))


def ranked(labels, sizes):
    """Region ids -> rank by size, 0 = largest.  replica37.write_prefloor_ply writes the label
    straight into cluster_id, so this is the relabelling a figure needs to say 'region 0'."""
    order = np.argsort(-np.asarray(sizes, dtype=np.int64), kind="stable")
    rank = np.empty(len(sizes), dtype=np.int64)
    rank[order] = np.arange(len(sizes), dtype=np.int64)
    return rank[labels], order


def cmd_cell(a):
    t0 = time.time()
    xyz, nrm_file = S.read_pcd_xyz(a.cloud)
    verts, vnorm = M.read_obj(a.mesh)
    orig_xyz, _orig_n = S.read_pcd_xyz(a.orig_cloud)
    nrm, src, kp = normals_for(a.arm, xyz, nrm_file)
    kc = curvature_k(len(xyz))
    curv = R.pcl_curvature(xyz, kc)
    t1 = time.time()
    regions, nu, label, is_seed = R.grow(xyz, nrm, curv, a.nb, a.theta, a.kappa)
    t2 = time.time()
    sizes = [int(r["size"]) for r in regions]
    dist = R.distribution(regions, len(xyz), a.floor)
    rank, order = ranked(label, sizes)
    os.makedirs(a.outdir, exist_ok=True)
    tag = "%s_%s_x%d" % (a.piece, a.arm, a.level)
    ply_all = os.path.join(a.outdir, tag + "_prefloor_regions.ply")
    R.write_prefloor_ply(ply_all, xyz, nu, rank, is_seed)
    # the largest region alone, in the property layout measure34.surface_row already reads
    big = int(np.count_nonzero(rank == 0))
    bigmask = rank == 0
    ply_big = os.path.join(a.outdir, tag + "_largest.ply")
    R.write_prefloor_ply(ply_big, xyz[bigmask], nu[bigmask], np.zeros(bigmask.sum(), dtype=np.int64),
                         is_seed[bigmask])
    largest = M.surface_row(ply_big, orig_xyz, verts, vnorm)
    pair = None
    if len(sizes) >= 2 and sizes[order[1]] >= a.floor and sizes[order[0]] >= a.floor:
        m0 = rank == 0
        m1 = rank == 1
        p = M.pair_stats(xyz[m0], nu[m0], xyz[m1], nu[m1])
        p["region0_size"] = int(m0.sum())
        p["region1_size"] = int(m1.sum())
        pair = p
    row = {"piece": a.piece, "level": int(a.level), "arm": a.arm,
           "cloud": a.cloud, "mesh": a.mesh, "orig_cloud": a.orig_cloud,
           "points": int(len(xyz)), "normal_src": src, "k_pca": int(kp), "k_curv": int(kc),
           "theta_deg": a.theta, "kappa": a.kappa, "nb": a.nb, "floor": a.floor,
           "requested_spacing_mm": a.requested, "achieved_spacing_mm": a.achieved,
           "regions": dist["regions_before"], "largest": dist["largest"],
           "largest_share": float(dist["largest"]) / float(len(xyz)),
           "sizes": dist["sizes"][:20], "buckets": dist["buckets"],
           "ge10": dist["ge10"], "ge20": dist["ge20"], "ge30": dist["ge30"], "ge50": dist["ge50"],
           "ge_pct1": dist["ge_pct1"], "ge_pct5": dist["ge_pct5"], "ge_pct10": dist["ge_pct10"],
           "fail_angle_total": dist["fail_angle_total"], "fail_curv_total": dist["fail_curv_total"],
           "fail_angle_per_point": dist["fail_angle_per_point"],
           "tests_per_point": dist["tests_per_point"],
           "largest_depth": dist["largest_depth"], "largest_pops": dist["largest_pops"],
           "largest_seed": dist["largest_seed"],
           "largest_fail_angle": dist["largest_fail_angle"],
           "survivors": dist["survivor_count"],
           "largest_region": largest, "pair": pair,
           "secs_grow": round(t2 - t1, 2), "secs_total": round(time.time() - t0, 2),
           "prefloor_ply": os.path.basename(ply_all)}
    with open(os.path.join(a.outdir, tag + "_cell.json"), "w") as f:
        json.dump(row, f, indent=1, sort_keys=True)
    print("[CELL] %s arm=%s normals=%s points=%d spacing req=%.5f ach=%.5f -> regions=%d largest=%d "
          "(%.2f%%) ge50=%d ge_pct5=%d fail_angle/pt=%.3f depth=%d cov2mm=%.4f fold=%.3f deg pair=%s"
          % (tag, a.arm, src, len(xyz), a.requested, a.achieved, dist["regions_before"],
             dist["largest"], 100.0 * dist["largest"] / len(xyz), dist["ge50"], dist["ge_pct5"],
             dist["fail_angle_per_point"], dist["largest_depth"], largest["cov_2mm"],
             largest["fold_deg"], "yes" if pair else "no"))
    return 0


COLS_REG = ["piece", "level", "arm", "points", "requested_spacing_mm", "achieved_spacing_mm",
            "regions", "largest", "largest_share", "ge10", "ge20", "ge30", "ge50",
            "ge_pct1", "ge_pct5", "ge_pct10", "fail_angle_total", "fail_curv_total",
            "fail_angle_per_point", "tests_per_point", "largest_depth", "survivors",
            "normal_src", "k_pca", "k_curv", "theta_deg", "kappa", "nb", "floor"]
COLS_BIG = ["piece", "level", "arm", "points", "largest", "largest_share", "ext_x", "ext_y",
            "ext_z", "diag", "cov_2mm", "fold_deg", "normal_src_meas"]
COLS_PAIR = ["piece", "level", "arm", "region0_size", "region1_size", "med_nn", "med_along",
             "p90_along", "med_across", "p90_across", "coin"]


def _fmt(v):
    if isinstance(v, float):
        return "%.6f" % v
    return str(v)


def _write_tsv(path, rows, cols):
    with open(path, "w") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(_fmt(r[c]) for c in cols) + "\n")
    return len(rows)


def cmd_fromply(a):
    """Turn ticket 37's pre-floor PLY (its own resampled cloud + normals) into the PCD this
    instrument grows on, so the ticket-37 anchor is re-grown from ticket 37's own bytes."""
    d = M.read_ply(a.ply)
    xyz = M.ply_xyz(d)
    nrm = M.ply_normals(d)
    if nrm is None:
        raise SystemExit("[FROMPLY] no normals in %s" % a.ply)
    sp = S.nn_spacing(xyz)
    S.write_pcd(a.out, xyz, nrm)
    row = {"src_ply": a.ply, "out_pcd": a.out, "points": int(len(xyz)),
           "median_mm": sp["median"], "p10_mm": sp["p10"], "p90_mm": sp["p90"]}
    with open(a.out + ".json", "w") as f:
        json.dump(row, f, indent=1, sort_keys=True)
    print("[FROMPLY] %s -> %s points=%d median_nn=%.5f p10=%.5f p90=%.5f mm"
          % (os.path.basename(a.ply), os.path.basename(a.out), len(xyz), sp["median"],
             sp["p10"], sp["p90"]))
    return 0


def cmd_aggregate(a):
    cells = []
    for root, _d, files in os.walk(a.cells):
        for fn in sorted(files):
            if fn.endswith("_cell.json"):
                with open(os.path.join(root, fn)) as f:
                    cells.append(json.load(f))
    cells.sort(key=lambda c: (c["piece"], c["level"], c["arm"]))
    os.makedirs(a.outdir, exist_ok=True)
    reg = []
    big = []
    pr = []
    for c in cells:
        r = dict(c)
        lr = c["largest_region"]
        r.update({"ext_x": lr["ext_x"], "ext_y": lr["ext_y"], "ext_z": lr["ext_z"],
                  "diag": lr["diag"], "cov_2mm": lr["cov_2mm"], "fold_deg": lr["fold_deg"],
                  "normal_src_meas": lr["normal_src"]})
        reg.append(r)
        big.append(r)
        if c.get("pair"):
            pr.append(dict(list(c.items()) + list(c["pair"].items())))
    n1 = _write_tsv(os.path.join(a.outdir, "regions38.tsv"), reg, COLS_REG)
    n2 = _write_tsv(os.path.join(a.outdir, "largest38.tsv"), big, COLS_BIG)
    n3 = _write_tsv(os.path.join(a.outdir, "pair38.tsv"), pr, COLS_PAIR) if pr else 0
    if not pr:
        with open(os.path.join(a.outdir, "pair38.tsv"), "w") as f:
            f.write("\t".join(COLS_PAIR) + "\n")
    print("[AGG] %d cells -> regions38.tsv %d rows, largest38.tsv %d rows, pair38.tsv %d rows"
          % (len(cells), n1, n2, n3))
    for c in cells:
        print("[AGG] %-28s arm=%s n=%-7d regions=%-6d largest=%-6d ge50=%-5d cov2mm=%.4f fold=%.3f"
              % ("%s_x%d" % (c["piece"], c["level"]), c["arm"], c["points"], c["regions"],
                 c["largest"], c["ge50"], c["largest_region"]["cov_2mm"],
                 c["largest_region"]["fold_deg"]))
    if a.figures37 and os.path.exists(a.figures37):
        with open(a.figures37) as f:
            t37 = json.load(f)
        if isinstance(t37, dict):
            t37 = [t37]
        rec = {d["piece"]: d for d in t37}
        out = []
        for c in cells:
            if c["piece"] in rec and c["arm"] in ("scan",) and c["level"] == 1:
                d = rec[c["piece"]]
                out.append({"piece": c["piece"], "t37_points": d.get("points"),
                            "my_points": c["points"], "t37_regions": d.get("regions"),
                            "my_regions": c["regions"], "t37_largest": d.get("largest_region"),
                            "my_largest": c["largest"]})
        with open(os.path.join(a.outdir, "ticket37_compare.json"), "w") as f:
            json.dump(out, f, indent=1, sort_keys=True)
        for o in out:
            print("[AGG] ticket37 anchor %s: points %s/%s regions %s/%s largest %s/%s (t37/mine)"
                  % (o["piece"], o["t37_points"], o["my_points"], o["t37_regions"],
                     o["my_regions"], o["t37_largest"], o["my_largest"]))
    return 0


def cmd_selftest(a):
    bad = 0
    # a flat plane grows to exactly one region whatever the normals are
    rng = np.random.default_rng(7)
    n = 900
    pts = np.stack([rng.random(n) * 20.0, rng.random(n) * 20.0, np.zeros(n)], axis=1)
    nrm = np.tile(np.array([0.0, 0.0, 1.0]), (n, 1))
    curv = R.pcl_curvature(pts, curvature_k(n))
    reg, nu, lab, seed = R.grow(pts, nrm, curv, 10, 3.4, 1.0)
    print("[SELFTEST] plane n=%d regions=%d (want 1)" % (n, len(reg)))
    if len(reg) != 1:
        bad += 1
        print("[SELFTEST] FAIL plane split")
    # a 60 deg hinge at 3.4 deg must split, and the refusal must be recorded as an angle refusal
    left = pts[pts[:, 0] < 10.0].copy()
    right = pts[pts[:, 0] >= 10.0].copy()
    c60, s60 = np.cos(np.radians(60.0)), np.sin(np.radians(60.0))
    right = np.stack([10.0 + (right[:, 0] - 10.0) * c60, right[:, 1],
                      (right[:, 0] - 10.0) * s60], axis=1)
    pts2 = np.vstack([left, right])
    nrm2 = np.vstack([np.tile(np.array([0.0, 0, 1.0]), (len(left), 1)),
                      np.tile(np.array([-s60, 0, c60]), (len(right), 1))])
    curv2 = R.pcl_curvature(pts2, curvature_k(len(pts2)))
    reg2, _nu2, _l2, _s2 = R.grow(pts2, nrm2, curv2, 10, 3.4, 1.0)
    d2 = R.distribution(reg2, len(pts2), 50)
    print("[SELFTEST] 60deg hinge regions=%d fail_angle/pt=%.3f fail_curv/pt=%.3f"
          % (d2["regions_before"], d2["fail_angle_per_point"],
             d2["fail_curv_total"] / float(len(pts2))))
    if d2["regions_before"] < 2 or d2["fail_angle_total"] == 0:
        bad += 1
        print("[SELFTEST] FAIL hinge did not split on angle")
    if d2["fail_curv_total"] != 0:
        bad += 1
        print("[SELFTEST] FAIL hinge refused on curvature too")
    # the distribution's partition must cover every point exactly once
    ok = sum(d2["sizes"]) == len(pts2)
    print("[SELFTEST] distribution partition sum=%d n=%d" % (sum(d2["sizes"]), len(pts2)))
    if not ok:
        bad += 1
    # ranked() must put the largest region at rank 0
    lab3 = np.array([0, 0, 1, 1, 1, 2])
    rk, order = ranked(lab3, [2, 3, 1])
    print("[SELFTEST] ranked: labels %s sizes (2,3,1) -> ranks %s order %s"
          % (lab3.tolist(), rk.tolist(), order.tolist()))
    if rk[2] != 0 or rk[0] != 1 or rk[5] != 2:
        bad += 1
        print("[SELFTEST] FAIL ranked")
    print("[SELFTEST] %s (%d failures)" % ("PASS" if bad == 0 else "FAIL", bad))
    return 0 if bad == 0 else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    s = sub.add_parser("selftest"); s.set_defaults(fn=cmd_selftest)
    s = sub.add_parser("cell")
    for k in ("--cloud", "--mesh", "--orig-cloud", "--piece", "--arm", "--outdir"):
        s.add_argument(k, required=True)
    s.add_argument("--level", type=int, required=True)
    s.add_argument("--requested", type=float, default=float("nan"))
    s.add_argument("--achieved", type=float, default=float("nan"))
    s.add_argument("--theta", type=float, default=3.4)
    s.add_argument("--kappa", type=float, default=1.0)
    s.add_argument("--nb", type=int, default=10)
    s.add_argument("--floor", type=int, default=50)
    s.set_defaults(fn=cmd_cell)
    s = sub.add_parser("fromply")
    s.add_argument("--ply", required=True); s.add_argument("--out", required=True)
    s.set_defaults(fn=cmd_fromply)
    s = sub.add_parser("aggregate")
    s.add_argument("--cells", required=True); s.add_argument("--outdir", required=True)
    s.add_argument("--figures37", default="")
    s.set_defaults(fn=cmd_aggregate)
    a = ap.parse_args(argv)
    if not getattr(a, "fn", None):
        ap.print_help()
        return 2
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
