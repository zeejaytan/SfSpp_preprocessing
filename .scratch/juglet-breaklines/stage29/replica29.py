#!/usr/bin/env python3
"""Ticket 29 -- what angle does each vessel's wall actually need?

Extends the ticket-28 replica (.scratch/juglet-breaklines/stage28/replica234.py
at commit 5227f8f) with the three measurements this ticket asks for and keeps
its growth semantics otherwise unchanged:

  A  the neighbour-normal angle distribution of each cloud, at the growth's own
     nb (k = 10 nearest neighbours of each point, self skipped, i.e. exactly the
     candidate set the BFS tests);
  B  the theta ladder over 2.0 .. 12.0 degrees, kappa 1.0 nb 10 floor 50;
  C  the ticket-28 calibration gate, run FIRST over every cloud whose rung-2
     sidecar was produced by growPaper234, and the run stops if it fails.

Where the numbers come from (unchanged from stage 28, copied deliberately):

  * growPaper234 is mesh_processing_headless.cpp:2972-3030, called at :3470 when
    paperChain is on.  paperChain is SFS_PAPER_CHAIN, read at :4359; when it is
    off, :3477-3487 runs pcl::RegionGrowing instead, which is a DIFFERENT
    segmentation.  Every rung-2 sidecar records the branch in "paper_chain", so
    a sidecar with "paper_chain": false is not a gate this replica can pass or
    fail -- it never ran this function.
  * one pass over the whole cloud; seed order is every point sorted by
    pnormals.curvature ascending (std::sort at :2950 -- numpy's stable sort
    here);
  * a seed already claimed is skipped, so a discarded region still burns the
    points it claimed during its BFS;
  * BFS over a front queue; for each front point cf the reference normal is
    normal[cf] -- the front point's, NOT the seed's -- and the nb+1 nearest
    neighbours of cf are tested in distance order (self is skipped by cand==cf);
  * a candidate joins iff curvature[cand] < kappa AND
    getAngle3D(normal[cf], normal[cand]) <= theta in degrees (a candidate
    exactly at theta joins: the C++ rejects only on '> thetaDeg', :2985);
  * the floor minClusterSize is applied to the finished regions only, so the
    growth itself is identical whatever the floor is.

Curvature is not written to the rung-2 dump, so it is recomputed here the way
the C++ recomputed it (getNormalsOnSurface :726-745): pcl::NormalEstimation with
setKSearch(max(10, min(50, npts/300))) over the k nearest neighbours including
self, and curvature = |lambda_min| / trace(cov)
(pcl/features/impl/feature.hpp:61-88, solvePlaneParameters), which for a
covariance matrix is lambda0/(lambda0+lambda1+lambda2) <= 1/3.

The angle is pcl::getAngle3D (pcl/common/impl/common.hpp:46-64): each vector is
normalised in float, dotted in float, the result clamped to [-1,1] by two
comparisons, then acos in double and scaled to degrees.  A zero-length normal
gives 0/0 = NaN, the two clamps leave NaN alone, acos(NaN) = NaN and
'NaN > theta' is false, so a dropped normal would be admitted; the count of such
points is reported as n_zero_normals.

Part A uses the same float-32 normalise/dot/clamp then double acos, but pools
every neighbour pair of every point at once (n*k directed pairs).  A directed
pair appears twice, once from each end, with the same angle either way, so the
percentiles are the same percentile of the undirected pair set.
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from scipy.spatial import cKDTree

THETAS = (2.0, 3.4, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0)
PCTS = ((10, "p10"), (25, "p25"), (50, "p50"), (75, "p75"), (90, "p90"),
        (99, "p99"))
FRACS = (2.0, 3.4, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0)
GRID_ARMS = ("B", "D", "E")
GRID_PIECES = ("Juglet_Piece_2", "Juglet_Piece_3", "Juglet_Piece_5",
               "Juglet_Piece_7")
POTA = "Pot_A_Piece_07"
ARM_LABEL = {"B": "arm B (chain on, 0.6 mm)", "D": "arm D (chain off, 0.6 mm)",
             "E": "arm E (chain off, native)", "PA": "Pot A 07 (defaults)"}
ARM_COLOUR = {"B": "#1f77b4", "D": "#2ca02c", "E": "#d62728", "PA": "#000000"}
GATE_TOL = 10          # points; stage 28's Pot A 07 delta was 10 (144 vs 134)
# Pot A 07's two big regions as the pipeline itself wrote them (r2 sidecar);
# a theta leaves them intact when the replica still returns regions at least
# this size.
POTA_BIG = (3093, 2850)
POTA_MIN_SURV = 8
JUG_MIN_SURV = 2
JUG_KGATE = 0.5
HIST_BINW = 0.25
HIST_NBIN = 240        # 0 .. 60 degrees


# ---------------------------------------------------------------- copied part
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


# ------------------------------------------------------- part A: the angles
def neighbour_pairs(n, nbr, nb):
    """(rows, cols) of every point's nb nearest neighbours, self skipped.

    nbr is the growth's own candidate table: tree.query(pts, k=nb+1) including
    self.  A row where self is absent (a tie at the k-th distance) contributes
    nb non-self candidates and the surplus is dropped here, so part A never
    counts more than nb pairs per point.
    """
    rows = np.repeat(np.arange(n), nbr.shape[1])
    cols = nbr.reshape(-1)
    keep = rows != cols
    rows, cols = rows[keep], cols[keep]
    if rows.size == 0:
        return rows, cols
    order = np.argsort(rows, kind="stable")
    rows, cols = rows[order], cols[order]
    counts = np.bincount(rows, minlength=n)
    starts = np.searchsorted(rows, np.arange(n), side="left")
    rank = np.arange(rows.size) - np.repeat(starts, counts)
    keep = rank < nb
    return rows[keep], cols[keep]


def pair_angles(nu, rows, cols):
    a = nu[rows]
    b = nu[cols]
    with np.errstate(invalid="ignore"):
        dot = (a[:, 0] * b[:, 0] + a[:, 1] * b[:, 1]
               + a[:, 2] * b[:, 2]).astype(np.float32)
        dot = np.where(dot < -1.0, np.float32(-1.0), dot).astype(np.float32)
        dot = np.where(dot > 1.0, np.float32(1.0), dot).astype(np.float32)
        ang = np.degrees(np.arccos(dot.astype(np.float64)))
    return ang


def angles_stats(ang):
    good = ang[np.isfinite(ang)]
    d = {"n_pairs": int(ang.size), "n_nan": int(ang.size - good.size)}
    if good.size == 0:
        return d
    q = np.percentile(good, [p for p, _ in PCTS])
    for (p, name), v in zip(PCTS, q):
        d[name] = float(v)
    d["mean"] = float(good.mean())
    d["max"] = float(good.max())
    for t in FRACS:
        d["le_%.1f" % t] = float(np.count_nonzero(good <= t)) / float(good.size)
    cnt, _edges = np.histogram(good, bins=HIST_NBIN,
                              range=(0.0, HIST_BINW * HIST_NBIN))
    d["hist_counts"] = [int(x) for x in cnt]
    d["n_good"] = int(good.size)
    return d


# ------------------------------------------------ copied part: the growth
def grow(xyz, nu, curv, nbr, theta_deg, kappa):
    """growPaper234 over a cloud, with the candidate table precomputed.

    nbr == tree.query(pts, k=min(nb+1, n))[1] is the same call the BFS made per
    front point; the job checks a sample of rows against single-point queries
    and writes the result to out/preflight.tsv.
    """
    n = xyz.shape[0]
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
            cur_n = nu[cf]
            for cand in nbr[cf]:
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
    return regions


def ladder_row(regions, npts, floor):
    sizes = sorted((r["size"] for r in regions), reverse=True)
    surv = [s for s in sizes if s >= floor]
    big = max(regions, key=lambda r: r["size"]) if regions else None
    return {
        "regions": len(sizes),
        "largest": sizes[0] if sizes else 0,
        "second_largest": sizes[1] if len(sizes) > 1 else 0,
        "surviving": len(surv),
        "sizes_ge_floor": surv,
        "kgate": (float(sum(surv)) / float(npts)) if npts else 0.0,
        "angle_rejections": int(sum(r["fail_angle"] for r in regions)),
        "fail_curv": int(sum(r["fail_curv"] for r in regions)),
        "largest_depth": big["max_depth"] if big else -1,
        "largest_pops": big["pops"] if big else -1,
        "total_claimed": int(sum(sizes)),
        "sizes_top10": sizes[:10],
    }


# ------------------------------------------------------------------- clouds
def cloud_list(grid_root, pota_root):
    out = []
    for arm in GRID_ARMS:
        for piece in GRID_PIECES:
            out.append({"cloud": "%s/%s" % (arm, piece), "arm": arm,
                        "piece": piece,
                        "dir": os.path.join(grid_root, arm, piece)})
    out.append({"cloud": "PA/%s" % POTA, "arm": "PA", "piece": POTA,
                "dir": os.path.join(pota_root, POTA)})
    return out


def load_cloud(cd, nb, pre):
    r2 = os.path.join(cd["dir"], "r2_clusters_premerge.ply")
    r1 = os.path.join(cd["dir"], "r1_downsampled.ply")
    sj = os.path.join(cd["dir"], "r2_clusters_premerge.json")
    for f in (r2, r1, sj):
        if not os.path.exists(f):
            raise SystemExit("missing input: %s" % f)
    xyz, nrm, cid, rsn, props = read_rung2_ply(r2)
    with open(sj) as f:
        side = json.load(f)
    n = int(xyz.shape[0])
    curv_k = max(10, min(50, n // 300))
    curv = pcl_curvature(xyz, curv_k)
    nu = normalised_f32(nrm)
    zero_normals = int(np.count_nonzero(np.isnan(nu[:, 0])))
    pts = xyz.astype(np.float64)
    tree = cKDTree(pts)
    kq = min(int(nb) + 1, n)
    _d, nbr = tree.query(pts, k=kq, workers=-1)
    nbr = np.atleast_2d(np.asarray(nbr))
    if nbr.shape[0] != n:
        nbr = nbr.reshape(n, kq)
    # the rung-2 dump must carry the same cloud the growth saw at rung 1
    try:
        x1, n1, _c1, _r1, _p1 = read_rung2_ply(r1)
        same_r1 = bool(x1.shape == xyz.shape and np.array_equal(x1, xyz)
                       and np.array_equal(n1, nrm))
    except SystemExit as e:
        same_r1 = "error: %s" % e
    # the precomputed candidate table must equal the per-point queries
    rng = np.random.default_rng(29)
    samp = rng.choice(n, size=min(25, n), replace=False)
    bad = 0
    for i in samp:
        _dd, query = tree.query(pts[int(i)], k=kq)
        if not np.array_equal(np.atleast_1d(query).astype(np.int64),
                              np.asarray(nbr[int(i)]).astype(np.int64)):
            bad += 1
    pre.append({"cloud": cd["cloud"], "r1_r2_xyz_normals_identical": same_r1,
                "nbr_sample_rows": int(samp.size), "nbr_sample_mismatch": bad})
    dump_sizes = []
    ids = sorted(set(int(c) for c in cid if c >= 0))
    for c in ids:
        dump_sizes.append(int(np.count_nonzero(cid == c)))
    dump_sizes.sort(reverse=True)
    return {"cd": cd, "xyz": xyz, "nrm": nrm, "nu": nu, "curv": curv,
            "curv_k": curv_k, "n": n, "nbr": nbr, "nb": int(nb),
            "side": side, "zero_normals": zero_normals,
            "dump_sizes": dump_sizes, "cid": cid}


# --------------------------------------------------------------------- main
def write_tsv(path, header, rows):
    with open(path, "w") as f:
        f.write("\t".join(header) + "\n")
        for r in rows:
            f.write("\t".join("" if v is None else str(v) for v in r) + "\n")


def joinlist(xs):
    return ",".join(str(x) for x in xs) if xs else "-"


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--grid-root", required=True)
    ap.add_argument("--pota-root", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--figure", default=None)
    ap.add_argument("--kappa", type=float, default=1.0)
    ap.add_argument("--nb", type=int, default=10)
    ap.add_argument("--floor", type=int, default=50)
    ap.add_argument("--thetas", type=float, nargs="+", default=list(THETAS))
    ap.add_argument("--gate-tol", type=int, default=GATE_TOL)
    ap.add_argument("--commit", default="")
    ap.add_argument("--runid", default="")
    ap.add_argument("--jobid", default="")
    a = ap.parse_args(argv)
    thetas = sorted(set(a.thetas))
    if 3.4 not in thetas:
        raise SystemExit("theta 3.4 must be in the ladder: it is the gate")
    for d in (a.outdir, os.path.join(a.outdir, "cells")):
        os.makedirs(d, exist_ok=True)
    out = a.outdir

    def say(*xs):
        print(*xs)
        sys.stdout.flush()

    clouds = cloud_list(a.grid_root, a.pota_root)
    say("[SURVEY] clouds=%d thetas=%s kappa=%.3f nb=%d floor=%d"
        % (len(clouds), ",".join("%.2f" % t for t in thetas), a.kappa, a.nb,
           a.floor))
    say("[SURVEY] grid=%s pota=%s" % (a.grid_root, a.pota_root))

    pre = []
    loaded = {}
    for cd in clouds:
        c = load_cloud(cd, a.nb, pre)
        loaded[cd["cloud"]] = c
        say("[LOAD] %-22s npts=%-6d curv_k=%-3d zero_normals=%d paper_chain=%s "
            "sidecar_theta=%.2f sidecar_nb=%d sidecar_floor=%d dump_clusters=%s"
            % (cd["cloud"], c["n"], c["curv_k"], c["zero_normals"],
               c["side"].get("paper_chain"), float(c["side"].get("theta", -1)),
               int(c["side"].get("nb", -1)),
               int(c["side"].get("min_cluster", -1)), joinlist(c["dump_sizes"])))
    write_tsv(os.path.join(out, "preflight.tsv"),
              ["cloud", "r1_r2_xyz_normals_identical", "nbr_sample_rows",
               "nbr_sample_mismatch"],
              [[p["cloud"], p["r1_r2_xyz_normals_identical"], p["nbr_sample_rows"],
                p["nbr_sample_mismatch"]] for p in pre])

    # ---------------------------------------------------------------- part C
    cache = {}

    def growth(cloud_key, theta):
        key = (cloud_key, round(float(theta), 4))
        if key not in cache:
            c = loaded[cloud_key]
            regs = grow(c["xyz"], c["nu"], c["curv"], c["nbr"], theta, a.kappa)
            cache[key] = ladder_row(regs, c["n"], a.floor)
        return cache[key]

    cal_rows = []
    gate_ok = True
    for cd in clouds:
        c = loaded[cd["cloud"]]
        paper = bool(c["side"].get("paper_chain"))
        row = growth(cd["cloud"], 3.4)
        rep = row["sizes_ge_floor"]
        dump = c["dump_sizes"]
        if not paper:
            verdict = "NOT-GATED-sidecar-is-pcl-region-growing"
            delta = ""
            note = ('rung-2 sidecar has "paper_chain": false, so its clusters '
                    'come from pcl::RegionGrowing (mesh_processing_headless.cpp:'
                    '3477-3487), not growPaper234; the replica sizes beside it '
                    'are evidence of the difference, not a gate')
        else:
            if len(rep) != len(dump):
                verdict = "FAIL"
                gate_ok = False
                delta = "count %d vs %d" % (len(rep), len(dump))
            else:
                d = [abs(x - y) for x, y in zip(rep, dump)]
                delta = max(d) if d else 0
                verdict = "MATCH" if delta <= a.gate_tol else "FAIL"
                if verdict == "FAIL":
                    gate_ok = False
            note = ("identical or within %d points per region, same region count"
                    % a.gate_tol)
        cal_rows.append([cd["cloud"], cd["arm"], cd["piece"], c["n"], paper,
                         c["side"].get("theta"), c["side"].get("kappa"),
                         c["side"].get("nb"), c["side"].get("min_cluster"),
                         joinlist(dump), joinlist(rep), len(dump), len(rep),
                         delta, verdict, note])
        say("[CAL] %-22s npts=%-6d paper_chain=%-5s pipeline=%-46s replica=%-46s "
            "delta=%-8s %s" % (cd["cloud"], c["n"], paper, joinlist(dump),
                               joinlist(rep), delta, verdict))
    write_tsv(os.path.join(out, "calibration.tsv"),
              ["cloud", "arm", "piece", "npts", "sidecar_paper_chain",
               "pipeline_theta", "pipeline_kappa", "pipeline_nb",
               "pipeline_floor", "pipeline_rung2_sizes", "replica_sizes_ge_floor",
               "n_pipeline", "n_replica", "max_abs_delta", "verdict", "note"],
              cal_rows)
    say("[CAL] result=%s (gated clouds only, tolerance %d points)"
        % ("MATCH" if gate_ok else "FAIL", a.gate_tol))
    if not gate_ok:
        with open(os.path.join(out, "GATE_FAILED.txt"), "w") as f:
            f.write("# ticket 29 part C -- the calibration gate failed on at "
                    "least one growPaper234 cloud.\n")
            f.write("# No angles, no ladder, no figure were computed: the "
                    "replica is not calibrated.\n")
            f.write("cloud\tnpts\tpipeline_sizes\treplica_sizes\tverdict\n")
            for r in cal_rows:
                f.write("%s\t%s\t%s\t%s\t%s\n" % (r[0], r[3], r[9], r[10], r[14]))
        say("[STOP] gate failed -- stopping before parts A, B, D and the figure")
        return 5

    # ---------------------------------------------------------------- part A
    ang_rows = []
    astats = {}
    for cd in clouds:
        c = loaded[cd["cloud"]]
        rows, cols = neighbour_pairs(c["n"], c["nbr"], a.nb)
        ang = pair_angles(c["nu"], rows, cols)
        st = angles_stats(ang)
        astats[cd["cloud"]] = st
        base = [cd["cloud"], cd["arm"], cd["piece"], c["n"], a.nb,
                st["n_pairs"], st["n_nan"]]
        for p, name in PCTS:
            if name in st:
                ang_rows.append(base + ["percentile", name, "%.6f" % st[name]])
        if "mean" in st:
            ang_rows.append(base + ["mean", "mean", "%.6f" % st["mean"]])
            ang_rows.append(base + ["max", "max", "%.6f" % st["max"]])
        for t in FRACS:
            k = "le_%.1f" % t
            if k in st:
                ang_rows.append(base + ["fraction_le_deg", "%.1f" % t,
                                        "%.6f" % st[k]])
        say("[ANGLES] %-22s npts=%-6d pairs=%-7d p10=%.3f p25=%.3f p50=%.3f "
            "p75=%.3f p90=%.3f p99=%.3f mean=%.3f le3.4=%.4f le4.0=%.4f nan=%d"
            % (cd["cloud"], c["n"], st["n_pairs"], st["p10"], st["p25"],
               st["p50"], st["p75"], st["p90"], st["p99"], st["mean"],
               st["le_3.4"], st["le_4.0"], st["n_nan"]))
    write_tsv(os.path.join(out, "angles.tsv"),
              ["cloud", "arm", "piece", "npts", "k", "n_pairs", "n_nan",
               "kind", "name", "value_deg"], ang_rows)
    with open(os.path.join(out, "angles_hist.json"), "w") as f:
        json.dump({"bin_width_deg": HIST_BINW,
                   "range_deg": [0.0, HIST_BINW * HIST_NBIN],
                   "note": "per-cloud binned pair-angle counts; bin i covers "
                           "[i*%.2f, (i+1)*%.2f) degrees" % (HIST_BINW, HIST_BINW),
                   "counts": {k: v["hist_counts"] for k, v in astats.items()},
                   "n_pairs_good": {k: v["n_good"] for k, v in astats.items()}},
                  f)

    # ---------------------------------------------------------------- part B
    lad_rows = []
    for cd in clouds:
        c = loaded[cd["cloud"]]
        for theta in thetas:
            r = growth(cd["cloud"], theta)
            lad_rows.append([cd["cloud"], cd["arm"], cd["piece"],
                             "%.2f" % theta, "%.3f" % a.kappa, a.nb, a.floor,
                             c["n"], c["curv_k"], r["regions"], r["largest"],
                             r["second_largest"], "%.6f" % r["kgate"],
                             r["surviving"], r["angle_rejections"],
                             r["fail_curv"], r["largest_depth"],
                             r["largest_pops"], r["total_claimed"],
                             c["zero_normals"], joinlist(r["sizes_ge_floor"])])
            with open(os.path.join(out, "cells", "%s__%s__t%.2f.json"
                                  % (cd["arm"], cd["piece"], theta)), "w") as f:
                json.dump({"cloud": cd["cloud"], "arm": cd["arm"],
                           "piece": cd["piece"], "theta_deg": theta,
                           "kappa": a.kappa, "nb": a.nb, "floor": a.floor,
                           "npts": c["n"], "curv_k": c["curv_k"],
                           "zero_normals": c["zero_normals"],
                           "sidecar": c["side"], "row": r}, f, indent=1,
                          sort_keys=True)
            say("[LADDER] %-22s t=%-5.2f regions=%-6d largest=%-6d second=%-6d "
                "kgate=%.4f surv=%-3d angle_rej=%-7d depth=%d"
                % (cd["cloud"], theta, r["regions"], r["largest"],
                   r["second_largest"], r["kgate"], r["surviving"],
                   r["angle_rejections"], r["largest_depth"]))
    write_tsv(os.path.join(out, "theta_ladder.tsv"),
              ["cloud", "arm", "piece", "theta_deg", "kappa", "nb", "floor",
               "npts", "curv_k", "regions", "largest", "second_largest",
               "kgate", "regions_ge_floor", "angle_rejections", "fail_curv",
               "largest_depth", "largest_pops", "total_claimed",
               "zero_normals", "sizes_ge_floor"], lad_rows)

    # ---------------------------------------------------------------- part D
    juglets = {}
    for arm in GRID_ARMS:
        juglets[arm] = [cd for cd in clouds if cd["arm"] == arm]
    d_rows = []
    for theta in thetas:
        row = ["%.2f" % theta]
        for arm in GRID_ARMS:
            ok, fail, kmin, smax = 0, [], None, 0
            for cd in juglets[arm]:
                r = growth(cd["cloud"], theta)
                pass_ = (r["surviving"] >= JUG_MIN_SURV
                         and r["kgate"] >= JUG_KGATE)
                if pass_:
                    ok += 1
                else:
                    fail.append(cd["piece"].replace("Juglet_Piece_", "p"))
                kmin = r["kgate"] if kmin is None else min(kmin, r["kgate"])
                smax = max(smax, r["surviving"])
            row += [ok, "/4", joinlist(fail), "%.4f" % (kmin or 0.0), smax,
                    "ALL4" if ok == len(juglets[arm]) else "not-all"]
        rp = growth("PA/%s" % POTA, theta)
        intact = (rp["largest"] >= POTA_BIG[0]
                  and rp["second_largest"] >= POTA_BIG[1])
        pota_pass = (rp["surviving"] >= POTA_MIN_SURV) and intact
        row += [rp["surviving"], rp["largest"], rp["second_largest"], intact,
                "%.6f" % rp["kgate"], pota_pass]
        row += ["both-B" if (pota_pass and row[6] == "ALL4") else "not-both",
                "both-D" if (pota_pass and row[12] == "ALL4") else "not-both",
                "both-E" if (pota_pass and row[18] == "ALL4") else "not-both"]
        d_rows.append(row)
    write_tsv(os.path.join(out, "partD.tsv"),
              ["theta_deg",
               "B_juglet_clouds_pass", "B_of", "B_fail", "B_kgate_min",
               "B_max_surv", "B_all4",
               "D_juglet_clouds_pass", "D_of", "D_fail", "D_kgate_min",
               "D_max_surv", "D_all4",
               "E_juglet_clouds_pass", "E_of", "E_fail", "E_kgate_min",
               "E_max_surv", "E_all4",
               "potA_regions_ge_floor", "potA_largest", "potA_second_largest",
               "potA_two_big_intact", "potA_kgate", "potA_pass",
               "both_B", "both_D", "both_E"], d_rows)
    for r in d_rows:
        say("[PARTD] theta=%s B=%s/4 D=%s/4 E=%s/4 potA_surv=%s largest=%s "
            "second=%s intact=%s pass=%s both(B,D,E)=%s/%s/%s"
            % (r[0], r[1], r[7], r[13], r[19], r[20], r[21], r[22], r[24],
               r[25], r[26], r[27]))

    # -------------------------------------------------------------- figure
    fig_info = {}
    if a.figure:
        fig_info = draw_figure(a, thetas, clouds, loaded, astats, growth, path=a.figure)
        with open(os.path.join(out, "figure.txt"), "w") as f:
            for k in sorted(fig_info):
                f.write("%s\t%s\n" % (k, fig_info[k]))

    # ------------------------------------------------------------- summary
    write_summary(a, out, thetas, cal_rows, fig_info)
    return 0


def draw_figure(a, thetas, clouds, loaded, astats, growth, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.gridspec import GridSpec
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    fig_w, fig_h, dpi = 18.0, 11.0, 160
    binw = HIST_BINW
    p99max = max([astats[cd["cloud"]].get("p99", 0.0) for cd in clouds] + [0.0])
    xmax = max(12.0, float(math.ceil(p99max)))
    edges = np.arange(0.0, HIST_BINW * HIST_NBIN + binw, binw)
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi)
    gs = GridSpec(3, 5, figure=fig, hspace=0.46, wspace=0.26,
                  left=0.055, right=0.985, top=0.895, bottom=0.07)
    axes = {}
    for r, arm in enumerate(GRID_ARMS):
        for k, piece in enumerate(GRID_PIECES):
            axes[(arm, piece)] = fig.add_subplot(gs[r, k])
    axes[("PA", POTA)] = fig.add_subplot(gs[0, 4])
    ax_kg = fig.add_subplot(gs[1, 4])
    ax_ct = fig.add_subplot(gs[2, 4])
    first = True
    for cd in clouds:
        c = loaded[cd["cloud"]]
        st = astats[cd["cloud"]]
        ax = axes[(cd["arm"], cd["piece"])]
        cnt = np.asarray(st["hist_counts"], dtype=np.float64)
        nbin_show = int(round(xmax / binw))
        tot = float(st["n_good"]) if st["n_good"] else 1.0
        seen = float(cnt[:nbin_show].sum())
        ax.stairs(100.0 * cnt[:nbin_show] / tot, edges[:nbin_show + 1],
                  color=ARM_COLOUR[cd["arm"]], linewidth=1.2, fill=True,
                  alpha=0.35)
        ax.set_yscale("log")
        ax.set_xlim(0.0, xmax)
        ax.grid(alpha=0.25, linewidth=0.5)
        ax.axvline(3.4, color="#555555", linestyle="--", linewidth=1.0)
        ax.axvline(4.0, color="#555555", linestyle=":", linewidth=1.0)
        ax.text(0.985, 0.94, "above %.0f deg: %.2f %%"
                % (xmax, 100.0 * (tot - seen) / tot),
                transform=ax.transAxes, ha="right", va="top", fontsize=6.5,
                color="#444444")
        ax.text(0.985, 0.80, "p50 %.2f  p90 %.2f deg"
                % (st.get("p50", float("nan")), st.get("p90", float("nan"))),
                transform=ax.transAxes, ha="right", va="top", fontsize=6.5,
                color="#222222")
        ax.set_title("%s  -  %s\nn=%d k=%d pairs=%d"
                     % (cd["piece"].replace("Juglet_Piece_", "Juglet p"),
                        cd["arm"], c["n"], a.nb, st["n_pairs"]), fontsize=7.5)
        ax.tick_params(labelsize=6)
        if first:
            ax.set_ylabel("%% of pairs per %.2f deg bin (log)" % binw, fontsize=6.5)
            y0 = 0.06
            ax.plot([0.60, 0.60 + 10.0 / xmax], [y0, y0],
                    transform=ax.transAxes, color="black", linewidth=2.5,
                    clip_on=False)
            ax.text(0.60 + 5.0 / xmax, y0 + 0.035, "10 deg",
                    transform=ax.transAxes, ha="center", fontsize=6.5)
            first = False
    for cd in clouds:
        ks = [growth(cd["cloud"], t)["kgate"] for t in thetas]
        ax_kg.plot(thetas, ks, "-o", ms=3.0, linewidth=1.2,
                   color=ARM_COLOUR[cd["arm"]], alpha=0.85)
    ax_kg.axhline(JUG_KGATE, color="#555555", linestyle="--", linewidth=1.0)
    ax_kg.set_xlabel("theta (degrees)", fontsize=7)
    ax_kg.set_ylabel("kgate: share of the cloud in\nregions >= floor (%d pts)"
                     % a.floor, fontsize=6.5)
    ax_kg.set_title("kgate against theta", fontsize=8)
    ax_kg.set_ylim(0.0, 1.08)
    ax_kg.set_xlim(min(thetas), max(thetas))
    ax_kg.grid(alpha=0.25, linewidth=0.5)
    ax_kg.tick_params(labelsize=6)
    ax_kg.plot([0.05, 0.05 + 0.25 / 1.08], [0.06, 0.06],
               transform=ax_kg.transAxes, color="black", linewidth=2.5,
               clip_on=False)
    ax_kg.text(0.05 + 0.125 / 1.08, 0.095, "0.25 kgate",
               transform=ax_kg.transAxes, ha="center", fontsize=6.5)
    for cd in clouds:
        ns = [growth(cd["cloud"], t)["surviving"] for t in thetas]
        ax_ct.plot(thetas, ns, "-o", ms=3.0, linewidth=1.2,
                   color=ARM_COLOUR[cd["arm"]], alpha=0.85)
    ax_ct.axhline(POTA_MIN_SURV, color="#555555", linestyle="--", linewidth=1.0)
    ax_ct.set_xlabel("theta (degrees)", fontsize=7)
    ax_ct.set_ylabel("regions at or above\nthe floor", fontsize=6.5)
    ax_ct.set_title("regions >= floor against theta", fontsize=8)
    ax_ct.set_xlim(min(thetas), max(thetas))
    ax_ct.grid(alpha=0.25, linewidth=0.5)
    ax_ct.tick_params(labelsize=6)
    ymax_ct = max(1.0, float(POTA_MIN_SURV),
                  max(max(growth(cd["cloud"], t)["surviving"]
                          for t in thetas) for cd in clouds))
    ax_ct.set_ylim(0.0, ymax_ct * 1.06)
    ax_ct.plot([0.05, 0.35], [0.06, 0.06], transform=ax_ct.transAxes,
               color="black", linewidth=2.5, clip_on=False)
    ax_ct.text(0.20, 0.012, "8 regions", transform=ax_ct.transAxes,
               ha="center", fontsize=6.5)
    handles = [Patch(facecolor=ARM_COLOUR[k], alpha=0.45,
                     edgecolor=ARM_COLOUR[k], label=ARM_LABEL[k])
               for k in ("B", "D", "E", "PA")]
    handles += [
        Line2D([], [], color="#555555", linestyle="--",
               label="shipped theta 3.4 / juglet kgate 0.5 / pot A 8 regions"),
        Line2D([], [], color="#555555", linestyle=":",
               label="paper theta 4.0")]
    fig.legend(handles=handles, loc="upper center", ncol=6, fontsize=7.5,
               frameon=False, bbox_to_anchor=(0.5, 0.998),
               title="ticket 29 - neighbour-normal angle distribution and theta "
                     "ladder; k=10, kappa=1.0, floor=50 points",
               title_fontsize=8.5)
    fig.savefig(path, dpi=dpi)
    plt.close(fig)
    from PIL import Image
    with Image.open(path) as im:
        wpx, hpx = im.size
    mm_w = fig_w * 25.4
    mm_h = fig_h * 25.4
    return {"path": os.path.abspath(path),
            "figsize_in": "%.1f x %.1f" % (fig_w, fig_h),
            "figsize_mm": "%.1f x %.1f" % (mm_w, mm_h), "dpi": dpi,
            "pixels": "%d x %d" % (wpx, hpx),
            "mm_per_pixel_x": "%.5f" % (mm_w / wpx),
            "mm_per_pixel_y": "%.5f" % (mm_h / hpx),
            "hist_x_range_deg": "0..%.2f, bin %.2f deg" % (xmax, binw),
            "scale_bar_hist": "10 deg bar in the first histogram panel; every "
                              "histogram panel uses the same 0..%.0f deg x axis"
                              % xmax,
            "scale_bar_kgate": "0.25 kgate bar in the kgate panel",
            "scale_bar_counts": "8 regions bar in the count panel",
            "colours": "B %s  D %s  E %s  PotA %s"
                       % (ARM_COLOUR["B"], ARM_COLOUR["D"], ARM_COLOUR["E"],
                          ARM_COLOUR["PA"])}


def write_summary(a, out, thetas, cal_rows, fig_info):
    L = []
    L.append("# ticket 29 - what angle does each vessel's wall need?")
    L.append("")
    L.append("Run %s, job %s, commit %s." % (a.runid, a.jobid, a.commit))
    L.append("")
    L.append("## What the replica is, and what it is not")
    L.append("")
    L.append("instruments/replica29.py is the ticket-28 replica of growPaper234")
    L.append("(mesh_processing_headless.cpp:2972-3030, called at :3470) with the "
             "theta ladder and")
    L.append("the angle measurement added. It reproduces the region growing "
             "only: it knows nothing")
    L.append("about the merge step, nothing about the 3 mm reassignment, and "
             "nothing about the")
    L.append("curvature-driven normal estimation that runs before the growth. A "
             "theta that looks")
    L.append("right here is a candidate for a pipeline run on the same pieces, "
             "not a result.")
    L.append("")
    L.append("Part A is not the replica: it reads the rung-2 cloud and normals "
             "the pipeline itself")
    L.append("wrote, so those angles are the angles the growth saw.")
    L.append("")
    L.append('A cloud whose rung-2 sidecar says "paper_chain": false was '
             "segmented by")
    L.append("pcl::RegionGrowing (:3477-3487), not by growPaper234, so the "
             "replica sizes beside it")
    L.append("cannot be a gate. Those rows are marked "
             "NOT-GATED-sidecar-is-pcl-region-growing.")
    L.append("")
    L.append("## Parameters")
    L.append("")
    L.append("- kappa %.3f, nb %d, floor %d points, thetas %s."
             % (a.kappa, a.nb, a.floor, ", ".join("%.2f" % t for t in thetas)))
    L.append("- curvature recomputed as mesh_processing_headless.cpp:745-747 does: k = max(10, min(50, npts/300)),")
    L.append("  curvature = lambda_min / trace(cov) <= 1/3, so the curvature gate "
             "cannot refuse while kappa = 1.")
    L.append("- part A pair set: each point's nb nearest neighbours, self "
             "skipped, i.e. the BFS")
    L.append("  candidate set; angles in the getAngle3D arithmetic (float "
             "normalise, float dot,")
    L.append("  clamp, double acos). Percentiles are over all n*k directed pairs.")
    L.append("- part D criterion, as applied: a Juglet cloud passes at a theta "
             "when it has at least")
    L.append("  %d regions at or above the floor and kgate >= %.1f; Pot A 07 "
             "passes when it has at" % (JUG_MIN_SURV, JUG_KGATE))
    L.append("  least %d regions at or above the floor and its two largest are "
             "still at least %d" % (POTA_MIN_SURV, POTA_BIG[0]))
    L.append("  and %d points (the pipeline's own rung-2 sizes, so a larger "
             "region counts as intact" % POTA_BIG[1])
    L.append("  and a split one does not).")
    L.append("")
    L.append("## Part C - the calibration gate (run first; the run stops if it "
             "fails)")
    L.append("")
    L.append("| cloud | npts | paper_chain | pipeline rung-2 sizes | replica >= "
             "floor | max delta | verdict |")
    L.append("|---|---|---|---|---|---|---|")
    for r in cal_rows:
        L.append("| %s | %s | %s | %s | %s | %s | %s |"
                 % (r[0], r[3], r[4], r[9], r[10], r[13], r[14]))
    L.append("")
    L.append("## Files")
    L.append("")
    for f in ("calibration.tsv", "preflight.tsv", "angles.tsv",
              "angles_hist.json", "theta_ladder.tsv", "partD.tsv",
              "figure.txt", "cells/", "GEOMETRY_DELETED.txt",
              "dump_inventory_before.tsv", "dump_inventory_after.tsv"):
        L.append("- out/%s" % f)
    if fig_info:
        L.append("")
        L.append("Figure: %s, %s in, %s px at dpi %s, %s mm/px."
                 % (fig_info.get("path"), fig_info.get("figsize_in"),
                    fig_info.get("pixels"), fig_info.get("dpi"),
                    fig_info.get("mm_per_pixel_x")))
    L.append("")
    with open(os.path.join(out, "summary.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    with open(os.path.join(out, "params29.json"), "w") as f:
        json.dump({"runid": a.runid, "jobid": a.jobid, "commit": a.commit,
                   "kappa": a.kappa, "nb": a.nb, "floor": a.floor,
                   "thetas": thetas, "grid_root": a.grid_root,
                   "pota_root": a.pota_root, "gate_tol": a.gate_tol,
                   "pota_big": list(POTA_BIG), "figure": fig_info}, f, indent=1,
                  sort_keys=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
