#!/usr/bin/env python3
# ticket 37 -- the python replica of the paper-234 region growth, extended to report what the
# pipeline cannot see: the regions BEFORE any floor.
#
# The pipeline passes the floor INTO growPaper234 (mesh_processing_headless.cpp:3647), so by
# construction it can only ever print the regions that survived it.  This instrument re-grows the
# same regions from the pipeline's own rung-2 dump (the cloud and normals exactly as clustering saw
# them), using the same curvature (k = clamp(npts//300, 10, 50)), the same 10-neighbour angle test,
# the same theta and kappa the pipeline printed, and then reports the whole region-size population.
#
# It is only admissible as evidence once it reproduces the pipeline's own cluster sizes on the same
# dump, so every run compares its survivors >= floor against the rung-2 sidecar's "clusters" list and
# records MATCH or MISMATCH.  A MISMATCH means the numbers are unvalidated and must be reported so.
#
# Nothing here writes outside --outdir.
import argparse
import json
import math
import os
import sys

import numpy as np
from scipy.spatial import cKDTree

WANT_PROPS = ["x", "y", "z", "nx", "ny", "nz", "cluster_id", "reason"]
# ticket-25 reason codes, as the pipeline numbers them
DR25 = {0: "NONE", 1: "CLAIMED", 2: "MERGED", 3: "ADMIT_OWN", 4: "ADMIT_OTHER",
        5: "REJECT_DIST", 6: "REJECT_NORMAL", 7: "WRITTEN", 8: "NOT_WRITTEN"}


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
    if props[:8] != WANT_PROPS:
        raise SystemExit("unexpected vertex properties %r in %s" % (props, path))
    body = raw[end + len(b"end_header"):].decode("ascii", "replace")
    arr = np.loadtxt(body.splitlines(), dtype=np.float64, ndmin=2)
    if arr.shape[0] != n or arr.shape[1] != 8:
        raise SystemExit("body %r does not match header %d x 8 in %s" % (arr.shape, n, path))
    return (arr[:, 0:3].astype(np.float32), arr[:, 3:6].astype(np.float32),
            arr[:, 6].astype(np.int64), arr[:, 7].astype(np.int64), props)


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
    """Faithful port of growPaper234.  Additionally returns the per-point label and whether the
    point was a region seed (so a dump can carry a cluster id and a reason per point)."""
    n = xyz.shape[0]
    pts = xyz.astype(np.float64)
    tree = cKDTree(pts)
    nu = normalised_f32(nrm)
    kq = min(int(nb) + 1, n)
    claimed = np.zeros(n, dtype=bool)
    label = np.full(n, -1, dtype=np.int64)
    is_seed = np.zeros(n, dtype=bool)
    regions = []
    for sd in np.argsort(curv, kind="stable"):
        sd = int(sd)
        if claimed[sd]:
            continue
        claimed[sd] = True
        is_seed[sd] = True
        label[sd] = len(regions)
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
                label[cand] = len(regions)
                reg.append(cand)
                front.append(cand)
                lv = level[cf] + 1
                level[cand] = lv
                if lv > depth:
                    depth = lv
        st.update({"size": len(reg), "seed": sd,
                   "seed_curv": float(curv[sd]), "max_depth": depth})
        regions.append(st)
    return regions, nu, label, is_seed


def buckets(sizes, npts):
    edges = [1, 2, 3, 5, 10, 20, 30, 50, 100]
    out = {}
    for i, lo in enumerate(edges):
        hi = edges[i + 1] if i + 1 < len(edges) else None
        key = "ge%d" % lo if hi is None else ("%d_%d" % (lo, hi - 1) if hi > lo + 1 else str(lo))
        if hi is None:
            out[key] = int(sum(1 for s in sizes if s >= lo))
        else:
            out[key] = int(sum(1 for s in sizes if lo <= s < hi))
    return out


def distribution(regions, npts, floor):
    sizes = sorted((r["size"] for r in regions), reverse=True)
    lg = max(regions, key=lambda r: r["size"]) if regions else None
    fa = int(sum(r["fail_angle"] for r in regions))
    fc = int(sum(r["fail_curv"] for r in regions))
    tests = int(sum(r["tests"] for r in regions))
    surv = [s for s in sizes if s >= floor]
    d = {
        "npts": npts, "regions_before": len(sizes), "largest": (sizes[0] if sizes else 0),
        "sizes": sizes,
        "ge10": int(sum(1 for s in sizes if s >= 10)),
        "ge20": int(sum(1 for s in sizes if s >= 20)),
        "ge30": int(sum(1 for s in sizes if s >= 30)),
        "ge50": int(sum(1 for s in sizes if s >= 50)),
        "ge_pct1": int(sum(1 for s in sizes if s >= 0.01 * npts)),
        "ge_pct5": int(sum(1 for s in sizes if s >= 0.05 * npts)),
        "ge_pct10": int(sum(1 for s in sizes if s >= 0.10 * npts)),
        "buckets": buckets(sizes, npts),
        "fail_angle_total": fa, "fail_curv_total": fc, "tests_total": tests,
        "fail_angle_per_point": (fa / float(npts)) if npts else 0.0,
        "tests_per_point": (tests / float(npts)) if npts else 0.0,
        "largest_depth": (lg["max_depth"] if lg else 0),
        "largest_pops": (lg["pops"] if lg else 0),
        "largest_seed": (lg["seed"] if lg else -1),
        "largest_fail_angle": (lg["fail_angle"] if lg else 0),
        "floor": floor, "survivors": surv, "survivor_count": len(surv),
        "sum_sizes": int(sum(sizes)),
    }
    return d


def write_prefloor_ply(path, xyz, nu, label, is_seed):
    """The pipeline's rung-2 layout, so an openviking-less reader of either dump sees the same file.
    cluster_id is the region id ordered by size (0 = largest).  reason keeps the ticket-25 numbers:
    1 CLAIMED for a region seed, 3 ADMIT_OWN for a point the growth admitted.  The growth partitions
    the cloud, so no point is unclaimed and codes 5/6 never appear in this file; the refusal counts
    live in the sidecar."""
    n = xyz.shape[0]
    with open(path, "w", newline="\n") as f:
        f.write("ply\n")
        f.write("format ascii 1.0\n")
        f.write("element vertex %d\n" % n)
        f.write("property float x\nproperty float y\nproperty float z\n")
        f.write("property float nx\nproperty float ny\nproperty float nz\n")
        f.write("property int cluster_id\n")
        f.write("property uchar reason\n")
        f.write("end_header\n")
        for i in range(n):
            f.write("%.6f %.6f %.6f %.6f %.6f %.6f %d %d\n"
                    % (xyz[i, 0], xyz[i, 1], xyz[i, 2], nu[i, 0], nu[i, 1], nu[i, 2],
                       label[i], 1 if is_seed[i] else 3))


def cmd_run(a):
    xyz, nrm, _cid, _rsn, props = read_rung2_ply(a.dump)
    side = {}
    if a.sidecar and os.path.isfile(a.sidecar):
        with open(a.sidecar) as f:
            side = json.load(f)
    theta = float(side.get("theta", a.theta))
    kappa = float(side.get("kappa", a.kappa))
    nb = int(side.get("nb", a.nb))
    floor = int(side.get("floor_applied", a.floor))
    npts = int(xyz.shape[0])
    k = int(min(max(npts // 300, 10), 50))
    curv = pcl_curvature(xyz, k)
    regions, nu, label, is_seed = grow(xyz, nrm, curv, nb, theta, kappa)
    dist = distribution(regions, npts, floor)
    pipe = sorted((int(x) for x in side.get("clusters", [])), reverse=True)
    mine = dist["survivors"]
    ok = (pipe == mine)
    outc = {
        "piece": a.piece, "config": a.config, "source_dump": os.path.abspath(a.dump),
        "retry": side.get("retry"), "theta": theta, "kappa": kappa, "nb": nb,
        "curv_k": k, "floor_applied": floor,
        "floor_from": side.get("floor_from"), "count_scale": side.get("count_scale"),
        "spacing_mm": side.get("spacing_mm"), "paper_chain": side.get("paper_chain"),
        "dist": dist,
        "pipeline_clusters": pipe,
        "validation": {"verdict": "MATCH" if ok else "MISMATCH",
                       "pipeline_count": len(pipe), "replica_count": len(mine),
                       "pipeline_sizes": pipe, "replica_sizes": mine,
                       "note": "replica survivors >= floor vs the rung-2 sidecar clusters"},
    }
    if not ok:
        only_p = [s for s in pipe]
        for s in mine:
            if s in only_p:
                only_p.remove(s)
        only_r = list(mine)
        for s in pipe:
            if s in only_r:
                only_r.remove(s)
        outc["validation"]["pipeline_only"] = only_p
        outc["validation"]["replica_only"] = only_r
    regions_detail = []
    if a.partd:
        order = sorted(range(len(regions)), key=lambda i: (-regions[i]["size"], i))
        remap = np.full(len(regions), -1, dtype=np.int64)
        for new, old in enumerate(order):
            remap[old] = new
        lab2 = np.where(label >= 0, remap[np.clip(label, 0, None)], -1)
        ply = os.path.join(a.outdir, "%s_prefloor_regions.ply" % a.piece)
        write_prefloor_ply(ply, xyz, nu, lab2, is_seed)
        for new, old in enumerate(order):
            r = regions[old]
            regions_detail.append({"id": int(new), "size": int(r["size"]), "seed": int(r["seed"]),
                                   "seed_curv": r["seed_curv"], "max_depth": int(r["max_depth"]),
                                   "pops": int(r["pops"]), "tests": int(r["tests"]),
                                   "fail_curv": int(r["fail_curv"]),
                                   "fail_angle": int(r["fail_angle"])})
        outc["partd"] = {"ply": ply, "ply_bytes": os.path.getsize(ply),
                         "cluster_id_order": "region size, 0 = largest",
                         "reason_codes": {"1": "CLAIMED (region seed)", "3": "ADMIT_OWN (grown onto)"},
                         "regions": regions_detail}
        sj = os.path.join(a.outdir, "%s_prefloor_regions.json" % a.piece)
        with open(sj, "w", newline="\n") as f:
            json.dump(outc, f, indent=1, sort_keys=True)
        outc["partd"]["sidecar"] = sj
    oj = os.path.join(a.outdir, "replica_%s.json" % a.config)
    with open(oj, "w", newline="\n") as f:
        json.dump(outc, f, indent=1, sort_keys=True)
    row = [a.config, a.piece, str(npts), str(dist["regions_before"]), str(dist["largest"]),
           str(dist["ge10"]), str(dist["ge20"]), str(dist["ge30"]), str(dist["ge50"]),
           str(dist["ge_pct1"]), str(dist["ge_pct5"]), str(dist["ge_pct10"]),
           str(dist["largest_depth"]), str(dist["fail_angle_total"]),
           "%0.3f" % dist["fail_angle_per_point"], str(dist["largest_pops"]),
           str(floor), str(dist["survivor_count"]), ",".join(str(s) for s in dist["survivors"])[:400],
           outc["validation"]["verdict"], str(len(pipe))]
    with open(os.path.join(a.outdir, "replica.tsv"), "w", newline="\n") as f:
        f.write("#config\tpiece\tnpts\tregions_before\tlargest\tge10\tge20\tge30\tge50"
                "\tge_pct1\tge_pct5\tge_pct10\tlargest_depth\tfail_angle\taf_per_point"
                "\tlargest_pops\tfloor\tsurvivors\tsizes_ge_floor\tvalidation\tpipeline_clusters\n")
        f.write("\t".join(row) + "\n")
    print("[REPLICA] %s %s npts=%d regions=%d largest=%d ge10=%d ge50=%d floor=%d surv=%d %s"
          % (a.config, a.piece, npts, dist["regions_before"], dist["largest"], dist["ge10"],
             dist["ge50"], floor, dist["survivor_count"], outc["validation"]["verdict"]))
    return 0


def cmd_selftest(_a):
    """Two synthetic checks: a plane must grow as ONE region (normals agree, curvature ~0), and a
    ridge folded at 60 degrees must break at theta=3.4 (the angle gate refuses the crossing)."""
    rng = np.random.RandomState(7)
    n = 40
    xs, ys = np.meshgrid(np.linspace(0, 10, n), np.linspace(0, 10, n))
    z = np.zeros_like(xs)
    pts = np.stack([xs.ravel(), ys.ravel(), z.ravel()], axis=1)
    nrm = np.tile(np.array([0.0, 0.0, 1.0]), (pts.shape[0], 1))
    curv = np.full(pts.shape[0], 0.01)
    reg, _nu, lab, seed = grow(pts, nrm, curv, 10, 3.4, 1.0)
    assert len(reg) == 1 and reg[0]["size"] == pts.shape[0], "plane did not grow to one region"
    assert lab.min() >= 0 and lab.max() == 0, "plane label wrong"
    # a real hinge: the y > 5 half is tilted 60 degrees about the line y = 5, and the two halves
    # share that boundary, so the crossing is a genuine neighbour pair the angle gate must refuse.
    c60, s60 = math.cos(math.radians(60)), math.sin(math.radians(60))
    pts2 = pts.copy()
    upper = pts2[:, 1] > 5.0
    dy = pts2[upper, 1] - 5.0
    pts2[upper, 1] = 5.0 + dy * c60
    pts2[upper, 2] = dy * s60
    nrm2 = np.tile(np.array([0.0, 0.0, 1.0]), (pts2.shape[0], 1))
    nrm2[upper] = np.array([0.0, -s60, c60])
    curv2 = np.full(pts2.shape[0], 0.01)
    reg2, _nu2, _lab2, _s2 = grow(pts2, nrm2, curv2, 10, 3.4, 1.0)
    assert len(reg2) >= 2, "folded plane did not split"
    assert any(r["fail_angle"] > 0 for r in reg2), "no angle refusal on the fold"
    d = distribution(reg2, pts2.shape[0], 50)
    assert d["ge10"] >= 1 and d["sum_sizes"] == pts2.shape[0], "distribution book-keeping wrong"
    print("[SELFTEST] plane -> 1 region, fold -> %d regions with %d angle refusals, "
          "distribution partition ok (%d points)"
          % (len(reg2), d["fail_angle_total"], d["sum_sizes"]))
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description="ticket 37 replica: pre-floor region distribution")
    sub = ap.add_subparsers(dest="cmd")
    r = sub.add_parser("run")
    r.add_argument("--dump", required=True)
    r.add_argument("--sidecar", default="")
    r.add_argument("--piece", required=True)
    r.add_argument("--config", required=True)
    r.add_argument("--outdir", required=True)
    r.add_argument("--partd", action="store_true")
    r.add_argument("--theta", default=3.4, type=float)
    r.add_argument("--kappa", default=1.0, type=float)
    r.add_argument("--nb", default=10, type=int)
    r.add_argument("--floor", default=50, type=int)
    sub.add_parser("selftest")
    a = ap.parse_args(argv)
    if a.cmd == "run":
        os.makedirs(a.outdir, exist_ok=True)
        return cmd_run(a)
    if a.cmd == "selftest":
        return cmd_selftest(a)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
