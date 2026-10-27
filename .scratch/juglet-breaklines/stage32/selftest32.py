#!/usr/bin/env python3
"""Ticket 32 -- the in-job gate.  Proves that the reused instruments still agree with
the modules they were copied from, before any measurement runs.

Exit 0 = all checks passed.  Anything else stops the job.
"""
import argparse
import os
import shutil
import sys
import tempfile

import numpy as np
from scipy.spatial import cKDTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import io32
import partA32 as PA
import partB32 as PB
import partD32 as PD
import replica234 as R234
import analyse30 as A30

FAILS = []


def check(name, ok, detail):
    print("[ST32] %-34s %s  %s" % (name, "PASS" if ok else "FAIL", detail))
    sys.stdout.flush()
    if not ok:
        FAILS.append(name)


def synthetic_pcds(tmp):
    """Both reader branches on files whose answer is known, padding field included."""
    xyz = np.array([[1.5, -2.25, 3.0], [4.0, 5.5, -6.75]])
    head = ("VERSION 0.7\nFIELDS x y z normal_x normal_y normal_z _\nSIZE 4 4 4 4 4 4 4\n"
            "TYPE F F F F F F F\nCOUNT 1 1 1 1 1 1 4\nWIDTH 2\nHEIGHT 1\n"
            "VIEWPOINT 0 0 0 1 0 0 0\n")
    ok = []
    det = []
    p = os.path.join(tmp, "syn_ascii.pcd")
    with open(p, "w") as fh:
        fh.write(head + "POINTS 2\nDATA ascii\n")
        for i in range(2):
            fh.write("%.3f %.3f %.3f 0 0 1 0 0 0 0\n" % tuple(xyz[i]))
    r = io32.read_pcd(p)
    ok.append(r["data"] == "ascii" and r["n_points"] == 2 and r["nrm"] is not None
              and float(np.max(np.abs(r["xyz"] - xyz))) < 1e-6
              and float(np.max(np.abs(r["nrm"][:, 2] - 1.0))) < 1e-9)
    det.append("ascii n=%d nrm=%s" % (r["n_points"], r["nrm"] is not None))
    q = os.path.join(tmp, "syn_bin.pcd")
    rec = np.zeros(2, dtype=[("x", "<f4"), ("y", "<f4"), ("z", "<f4"),
                             ("normal_x", "<f4"), ("normal_y", "<f4"),
                             ("normal_z", "<f4"), ("_", "<f4", (4,))])
    rec["x"] = xyz[:, 0]
    rec["y"] = xyz[:, 1]
    rec["z"] = xyz[:, 2]
    rec["normal_z"] = 1.0
    with open(q, "wb") as fh:
        fh.write((head + "POINTS 5\nDATA binary\n").encode("ascii"))
        fh.write(rec.tobytes())
    r2 = io32.read_pcd(q)
    ok.append(r2["data"] == "binary" and r2["n_points"] == 2 and r2["header_points"] == 5
              and float(np.max(np.abs(r2["xyz"] - xyz))) < 1e-6)
    det.append("binary body=%d header=%d itemsize=%d"
               % (r2["n_points"], r2["header_points"], rec.dtype.itemsize))
    return all(ok), "; ".join(det)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--dump", required=True)
    a = ap.parse_args(argv)
    tmp = tempfile.mkdtemp(prefix="st32_")
    try:
        ok, det = synthetic_pcds(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    check("pcd_synthetic_parse", ok, det)
    jp = PA.jug_paths(a.dataset, 7)
    cl = io32.read_pcd(jp["pcd"])
    check("pcd_ascii_count", cl["n_points"] == PA.RECORDED_N[7],
          "piece 7 n=%d header=%d" % (cl["n_points"], cl["header_points"]))
    m = io32.read_obj(jp["objs"][0])
    v2, n2, nf2 = A30.read_obj_normals(jp["objs"][0])
    dv = float(np.max(np.abs(m["vnorm"] - n2))) if v2.shape == m["verts"].shape else 1e9
    check("obj_normals_match_analyse30", dv < 1e-12,
          "max |dvnorm| = %.3e, faces %d/%d" % (dv, m["faces"], nf2))
    pts = np.ascontiguousarray(cl["xyz"], dtype=np.float64)
    tree = cKDTree(pts)
    rng = np.random.default_rng(3)
    sub = np.sort(rng.choice(pts.shape[0], size=40, replace=False))
    # analyse30's k-NN query returns the centre point itself as the nearest of its k, so
    # exact parity needs the same 31 points here.  The window measurement drops the centre
    # (a point is not its own neighbour); that convention difference is recorded in the table.
    _d, nb = tree.query(pts[sub], k=31, workers=-1)
    ref = A30.quadric_radii(pts, sub, tree, 31)
    got = PB.quadric_radii_from_lists(pts, sub, [nb[i, :31] for i in range(sub.size)])
    both = np.isfinite(ref) & np.isfinite(got)
    rel = float(np.max(np.abs(ref[both] - got[both]) / np.maximum(ref[both], 1e-9)))
    check("quadric_matches_analyse30", rel < 1e-9,
          "max relative diff = %.3e over %d points" % (rel, both.sum()))
    floor, fn = A30.mesh_floor(pts, cl["nrm"], m["verts"], m["vnorm"], rng)
    ang = PD.mesh_angles_all(pts, cl["nrm"], m["verts"], m["vnorm"],
                             cKDTree(m["verts"]))
    check("mesh_angles_match_analyse30", abs(float(np.median(ang)) - floor) < 1e-12,
          "median %.6f vs %.6f" % (float(np.median(ang)), floor))
    hist = np.zeros(PB.ANG_NB, dtype=np.int64)
    u = np.linspace(0.0, 180.0, 200001)
    hist += np.bincount(np.minimum((u / PB.ANG_STEP).astype(np.int64),
                                   PB.ANG_NB - 1), minlength=PB.ANG_NB)
    p50 = PB.hist_pct(hist, 50.0)
    check("hist_percentile", abs(p50 - 90.0) < 0.02, "p50 of uniform 0..180 = %.4f" % p50)
    key = os.path.join(a.dump, "B", "Juglet_Piece_2", "r2_clusters_premerge.ply")
    xyz, nrm, _c, _r, _p = R234.read_rung2_ply(key)
    xyz = xyz.astype(np.float64)
    nrm = nrm.astype(np.float64)
    n = xyz.shape[0]
    curv = R234.pcl_curvature(xyz, max(10, min(50, n // 300)))
    reg_a, _nu = R234.grow(xyz, nrm, curv, 10, 3.4, 1.0)
    reg_b, _nu = PD.grow_members(xyz, nrm, curv, 10, 3.4, 1.0)
    sa = sorted(r["size"] for r in reg_a)
    sb = sorted(r["size"] for r in reg_b)
    check("grow_members_matches_replica234", sa == sb,
          "n=%d regions %d/%d sizes head %s" % (n, len(sa), len(sb), sb[-5:]))
    check("grow_anchor_piece2_B", (len(reg_b) == 661 and max(sb) == 36
                                   and sum(r["fail_angle"] for r in reg_b) == 4703),
          "regions=%d largest=%d fail_angle=%d" % (
              len(reg_b), max(sb), sum(r["fail_angle"] for r in reg_b)))
    g = np.stack(np.meshgrid(np.arange(6), np.arange(6), np.arange(2)), -1).reshape(-1, 3)
    g = g * 0.1 + rng.normal(scale=0.001, size=(g.shape[0], 3))
    i1 = io32.voxel_subsample(g, 0.25)
    i2 = io32.voxel_subsample(g, 0.25)
    ijk = np.floor(g / 0.25).astype(np.int64)
    uniq = np.unique(ijk, axis=0).shape[0]
    check("voxel_subsample", np.array_equal(i1, i2) and i1.size == uniq,
          "%d of %d points kept, %d cells, deterministic" % (i1.size, g.shape[0], uniq))
    pa_pcd = PA.pa_paths(a.corpus, 3)["pcd"]
    cb = io32.read_pcd(pa_pcd)
    check("pcd_binary_count", cb["data"] == "binary" and cb["header_points"] == 1000000,
          "header %d, body %d, fields %s" % (cb["header_points"], cb["n_points"],
                                             ",".join(cb["fields"])))
    print("[ST32] result=%s (%d failures)" % ("PASS" if not FAILS else "FAIL",
                                              len(FAILS)))
    return 0 if not FAILS else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
