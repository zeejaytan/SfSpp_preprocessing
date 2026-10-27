"""Gate-passage probe, pipeline-faithful variant (ticket 06 Test 1).

The pipeline reads ONLY Breakline_0 per piece -- this probe restricts to
_0 <-> _0 segment pairs at GT placements, counting nearest-neighbour
inliers the way MakeCorWOBuildTree + UnifiedPotteryValidation do.

Ticket 31 port (2026-10-27). The cluster's python3 (3.11, numpy 2.4.6) has no
scipy, and every re-score runs on a compute node. Four changes, listed so a
diff reader can stop looking:

  1. scipy.spatial.cKDTree(Bq).query(Aq) -> nn_query(Bq, Aq, ARGS.nn): a
     chunked brute-force nearest neighbour with bounded memory. Same distance,
     same index. The clouds here are a few hundred points, so the chunk loop
     runs once on this bundle; --selftest forces tiny chunks to prove the
     answer cannot depend on the chunk size.
  2. scipy is imported inside the ckdtree branch only. --nn ckdtree is the
     ORIGINAL search, kept solely to re-measure the same bytes on a machine
     that has scipy; the default, and the reported result, is bruteforce.
  3. One BUNDLES entry, "p31": the p07 spec with the roots supplied at run
     time (--bl, --gt). The two gates (2.0 mm / 0.85 and 20 deg / 0.7), the
     _0-only restriction, the max-inlier-count-over-segment-pairs reduction
     and the PASS rule (inliers at 2.0 mm / 0.85 > 0) are untouched, and every
     other BUNDLES entry is byte-identical to gate_probe_b0_p07.py.
  4. Argument parsing and --selftest, which run before any data is read. The
     measurement block below still runs at module level, exactly as it did, so
     the diff against gate_probe_b0_p07.py is a handful of hunks and not a
     rewrite.

Usage: python gate_probe_p31.py <bundle-key> [--bl DIR] [--gt DIR] [--nn MODE]
       python gate_probe_p31.py --selftest
"""
import argparse
import sys

import numpy as np

ART = "C:/PR/structure-from-sherds-pp/artifacts"
BUNDLES = {
    "juglet": (ART + "/juglet_bl/Juglet_Piece_%d_Breakline_0.pcd",
               ART + "/juglet_input/Ground Truth/Juglet_Piece_%d_T.txt",
               ART + "/juglet_run1/Juglet_simple_graph.txt", 9),
    "pota": (ART + "/pot_a_nurbs_bl/Pot_A_Piece_%02d_Breakline_0.pcd",
             ART + "/pot_a_nurbs_gt/Pot_A_Piece_%d_T.txt",
             ART + "/pot_a_nurbs_gt/Pot_A_simple_graph.txt", 8),
    "pota_orig": (ART + "/pot_a_bl/Pot_A_Piece_%02d_Breakline_0.pcd",
                  ART + "/pot_a_gt/Pot_A_Piece_%d_T.txt",
                  ART + "/pot_a_gt/Pot_A_simple_graph.txt", 8),
    # Ticket 09. OUR preprocessing, re-run 2026-09-26, paired with the
    # AUTHORS' ground truth.
    #
    # This is the arm that should have existed all along. It is legitimate
    # precisely BECAUSE the fresh output is in the scan frame: its breakline
    # centroids sit 0.7-2.5 mm from the Pot_A mesh centroids on 6 of 8
    # pieces, the same frame the authors' breaklines occupy (within ~1 mm).
    # Same frame means the same ground truth applies, so this compares our
    # curves against the authors' ground truth directly -- which is the
    # comparison the "15/15 control" was believed to be.
    #
    # The older "pota" arm used pot_a_nurbs_bl, which is the Nov-2025
    # NURBS_Dataset_20251103 bundle. Its eight pieces are arranged 4.5x
    # further apart than Pot_A's real sherds (331 mm vs 73 mm mean pairwise
    # centroid distance), so its 0/15 measured a stale, dispersed artifact
    # rather than the pipeline. Do not read that number as a result.
    "pota_fresh": (ART + "/pot_a_fresh_bl/Pot_A_Piece_%02d_Breakline_0.pcd",
                   ART + "/pot_a_gt/Pot_A_Piece_%d_T.txt",
                   ART + "/pot_a_gt/Pot_A_simple_graph.txt", 8),
    # Ticket 10: the surface-swap ablation, applied to the WHOLE bundle.
    #
    # Taking each sherd's rim from Surface_1 instead of Surface_0 lands
    # within 0.53-0.80 mm of the authors' rim on pieces 3-8, with 99-100% of
    # points inside the 2 mm gate. Piece 1 was already correct on Surface_0
    # and gets worse when swapped; piece 2 is truncated and unaffected.
    # Baseline drift across all 8 was 0.00 mm, so the arms are comparable.
    #
    # This is deliberately a BLANKET swap, not a fixed selection rule. It is
    # an upper bound on what correct surface selection could buy, and a
    # blanket rule that scores well here would still be wrong on piece 1 --
    # which is exactly the inconsistency ticket 04 has to resolve properly
    # (the paper's interior/exterior test, not "always the other wall").
    "pota_swapped": (ART + "/Pot_A_Piece_%02d_Breakline_0_swapped.pcd",
                     ART + "/pot_a_gt/Pot_A_Piece_%d_T.txt",
                     ART + "/pot_a_gt/Pot_A_simple_graph.txt", 8),
    # Ticket 12 smoothness sweep (2026-09-28). Control must reproduce
    # pota_fresh's 7/15; s8.0 is the only non-default arm that completed.
    # s2.0/s15.0 crashed the edgeline on an empty unclustered file;
    # s25.0 failed in the mesh stage (1 cluster, no surfaces).
    "smooth_control": (ART + "/smooth_sweep_out/control/Pot_A_Piece_%02d_Breakline_0.pcd",
                       ART + "/pot_a_gt/Pot_A_Piece_%d_T.txt",
                       ART + "/pot_a_gt/Pot_A_simple_graph.txt", 8),
    "smooth_s8": (ART + "/smooth_sweep_out/s8.0/Pot_A_Piece_%02d_Breakline_0.pcd",
                  ART + "/pot_a_gt/Pot_A_Piece_%d_T.txt",
                  ART + "/pot_a_gt/Pot_A_simple_graph.txt", 8),
    # Per-sherd selection: piece 1+2 from baseline (Surface_0), pieces 3-8
    # from the swapped arm (Surface_1). Baseline piece 1 matches at 0.69mm
    # and the swap breaks it; pieces 3-8 match only when swapped. Neither
    # blanket choice is right -- this is what a per-sherd interior/exterior
    # test would produce.
    "mixed_select": (ART + "/mixed_bl/Pot_A_Piece_%02d_Breakline_0.pcd",
                     ART + "/pot_a_gt/Pot_A_Piece_%d_T.txt",
                     ART + "/pot_a_gt/Pot_A_simple_graph.txt", 8),
    # Ticket 12 round 2 (2026-09-28): smoothness 3.0/3.5 crashed like 2.0;
    # 5.0/6.0 completed. Control reproduced 7/15 again.
    "smooth_s5": (ART + "/smooth_sweep_out/s5.0/Pot_A_Piece_%02d_Breakline_0.pcd",
                  ART + "/pot_a_gt/Pot_A_Piece_%d_T.txt",
                  ART + "/pot_a_gt/Pot_A_simple_graph.txt", 8),
    "smooth_s6": (ART + "/smooth_sweep_out/s6.0/Pot_A_Piece_%02d_Breakline_0.pcd",
                  ART + "/pot_a_gt/Pot_A_Piece_%d_T.txt",
                  ART + "/pot_a_gt/Pot_A_simple_graph.txt", 8),
    # Ticket 04 (2026-09-28): pipeline-selected interior wall per sherd.
    # The vote kept piece 1 on Surface_0 and exchanged pieces 2-8.
    # Prediction from the mixed bundle: ~11/15, all remaining failures
    # containing piece 2.
    "t04_interior": (ART + "/pot_a_t04_bl/Pot_A_Piece_%02d_Breakline_0.pcd",
                     ART + "/pot_a_gt/Pot_A_Piece_%d_T.txt",
                     ART + "/pot_a_gt/Pot_A_simple_graph.txt", 8),
    # Ticket 07 (2026-09-30): Juglet with the interior/exterior vote live.
    # First run where per-sherd wall selection happens on this pot. Scored
    # against the honest denominator (10 touching of 18), not the key.
    "juglet_t04": (ART + "/juglet_t04_bl/Juglet_Piece_%d_Breakline_0.pcd",
                   ART + "/juglet_input/Ground Truth/Juglet_Piece_%d_T.txt",
                   ART + "/juglet_run1/Juglet_simple_graph.txt", 9),
    # Ticket 14 (2026-09-28): piece 2's decorative rim (110 pts from the
    # unclustered fracture zone, mesh normals, one segment) in place of its
    # wall rim; other 7 pieces from the t04 arm. The decorative rim reaches
    # 1-2 at 0.56mm with 43.6% normals agreement. Prediction: 12/15.
    "decor_piece2": (ART + "/decor_bundle/Pot_A_Piece_%02d_Breakline_0.pcd",
                     ART + "/pot_a_gt/Pot_A_Piece_%d_T.txt",
                     ART + "/pot_a_gt/Pot_A_simple_graph.txt", 8),
    # Ticket 14 implemented (2026-09-28): patch rims appended as segments.
    # Piece 2: 771 pts, piece 3: 538, piece 5: 345, piece 4: 273.
    "t14_patches": (ART + "/pot_a_t14_bl/Pot_A_Piece_%02d_Breakline_0.pcd",
                    ART + "/pot_a_gt/Pot_A_Piece_%d_T.txt",
                    ART + "/pot_a_gt/Pot_A_simple_graph.txt", 8),
    # Ticket 17 no-regression (2026-09-30): full pipeline with stale-temp
    # cleanup, unblocked retry loop, and skip-missing. Must match t14 by
    # pair: the ticket-17 paths are unexercised on Pot_A (min 2 clusters).
    "t17_noregress": (ART + "/pot_a_t17_bl/Pot_A_Piece_%02d_Breakline_0.pcd",
                      ART + "/pot_a_gt/Pot_A_Piece_%d_T.txt",
                      ART + "/pot_a_gt/Pot_A_simple_graph.txt", 8),
    # Preproc 03 (2026-09-30): mergeClusters iterates to convergence
    # (cap 10, per-pass log). Criteria unchanged. Must match t14 per pair.
    "merge_conv": (ART + "/pot_a_merge_bl/Pot_A_Piece_%02d_Breakline_0.pcd",
                  ART + "/pot_a_gt/Pot_A_Piece_%d_T.txt",
                  ART + "/pot_a_gt/Pot_A_simple_graph.txt", 8),
    # Ticket 05 (2026-09-30): noise filter output ordered (dead reload
    # deleted, shared seam, unit test green). Must match t14 per pair.
    "filter_live": (ART + "/pot_a_filter_bl/Pot_A_Piece_%02d_Breakline_0.pcd",
                   ART + "/pot_a_gt/Pot_A_Piece_%d_T.txt",
                   ART + "/pot_a_gt/Pot_A_simple_graph.txt", 8),
    # Ticket 06 (2026-09-30): true 1.9mm equidistant resampling, clamp
    # gone, traced lengths logged. Must hold t14 per pair.
    "resample19": (ART + "/pot_a_resample_bl/Pot_A_Piece_%02d_Breakline_0.pcd",
                  ART + "/pot_a_gt/Pot_A_Piece_%d_T.txt",
                  ART + "/pot_a_gt/Pot_A_simple_graph.txt", 8),
    # E2E baseline 2026-10-01: the exact bundle staged for the assembler
    # (fresh current-code extraction). Must read 15/15 or the assembly run
    # is scored against a bundle the probe rejects.
    "e2e_fresh": (ART + "/pot_a_e2e_bl/Pot_A_Piece_%02d_Breakline_0.pcd",
                 ART + "/pot_a_gt/Pot_A_Piece_%d_T.txt",
                 ART + "/pot_a_gt/Pot_A_simple_graph.txt", 8),
    # Ticket 07 stage 1 (2026-10-27): Pot A rebuilt in the same job as the
    # Juglet rebuild, from run 20261027-0055_d8af9d2_p07-juglet-stage1.
    # Breakline files renamed to the canonical names at fetch time; contents
    # untouched (md5s in that run's out/files.md5).
    "p07": (ART + "/p07_stage1/pota_bl/Pot_A_Piece_%02d_Breakline_0.pcd",
            ART + "/pot_a_gt/Pot_A_Piece_%d_T.txt",
            ART + "/pot_a_gt/Pot_A_simple_graph.txt", 8),
    # Ticket 31 (2026-10-27): the SAME spec as p07, re-rooted so the scoring
    # can run on a compute node. {bl} and {gt} are filled from --bl and --gt,
    # which default to the p07 laptop layout, so on the laptop this entry
    # reads the same files p07 does. No gate, counting rule or PASS rule
    # changes with the root: only where the bytes come from.
    "p31": ("{bl}/Pot_A_Piece_%02d_Breakline_0.pcd",
            "{gt}/Pot_A_Piece_%d_T.txt",
            "{gt}/Pot_A_simple_graph.txt", 8),
}

# Peak working set of the brute-force search, in float64 elements; a query
# chunk never holds more than this many of them.
CHUNK_FLOATS = 4_000_000


def nn_query(points, query, mode="bruteforce", chunk_floats=CHUNK_FLOATS):
    """Nearest neighbour of every query point, by chunked brute force.

    Stands in for scipy.spatial.cKDTree(points).query(query): dist[i] is the
    Euclidean distance from query[i] to its nearest row of points, idx[i] that
    row. The query points are walked in chunks sized so that one chunk needs at
    most chunk_floats float64 elements -- peak memory does not grow with
    len(query) x len(points). Each chunk is an independent argmin, so the
    result cannot depend on the chunk size.

    mode="ckdtree" runs the original search instead. It needs scipy and exists
    only to re-measure the same bytes where scipy is available.
    """
    if mode == "ckdtree":
        from scipy.spatial import cKDTree
        return cKDTree(points).query(query)
    npts, nqry = len(points), len(query)
    if npts == 0 or nqry == 0:
        raise ValueError(f"nn_query: empty input ({npts} points, {nqry} queries)")
    rows = max(1, int(chunk_floats) // (3 * npts))
    dist = np.empty(nqry, dtype=np.float64)
    idx = np.empty(nqry, dtype=np.intp)
    for s in range(0, nqry, rows):
        e = min(s + rows, nqry)
        diff = query[s:e, None, :] - points[None, :, :]
        sq = (diff * diff).sum(axis=2)
        j = sq.argmin(axis=1)
        idx[s:e] = j
        dist[s:e] = np.sqrt(sq[np.arange(e - s), j])
    return dist, idx


def _direct(points, query):
    """The nearest-neighbour search written out point by point, for --selftest.

    No chunking, no broadcasting of a whole chunk, no argmin down a row: the
    thing nn_query() is supposed to be an exact stand-in for.
    """
    dist = np.empty(len(query), dtype=np.float64)
    idx = np.empty(len(query), dtype=np.intp)
    for k in range(len(query)):
        v = points - query[k]
        s = (v * v).sum(axis=1)
        idx[k] = int(s.argmin())
        dist[k] = np.sqrt(s[idx[k]])
    return dist, idx


def selftest(mode):
    """Show the brute-force search agrees with a direct computation."""
    rng = np.random.default_rng(31)
    failures = []

    def check(label, ok, detail=""):
        print(f"[selftest] {label}: {'PASS' if ok else 'FAIL'}"
              + (f" {detail}" if detail else ""))
        if not ok:
            failures.append(label)

    print(f"[selftest] python {sys.version.split()[0]}, numpy {np.__version__}, "
          f"nn mode asked for = '{mode}', CHUNK_FLOATS = {CHUNK_FLOATS}")

    # (a) chunked brute force vs the per-point direct computation, on a point
    # count near this bundle's (<= 208 points per piece) and on a tiny one,
    # each run once as a single chunk and once in chunks of a few points.
    for name, npts, nqry in (("dense", 120, 90), ("sparse", 7, 5), ("single", 1, 1)):
        pts = rng.normal(size=(npts, 3)) * 50.0
        qry = rng.normal(size=(nqry, 3)) * 50.0
        d0, i0 = _direct(pts, qry)
        for label, cf in (("one_chunk", CHUNK_FLOATS), ("tiny_chunks", 3 * npts * 2)):
            d1, i1 = nn_query(pts, qry, "bruteforce", chunk_floats=cf)
            check(f"a/{name}/{label}/dist", np.array_equal(d0, d1),
                  f"max_abs_delta={float(np.abs(d0 - d1).max()):.3e}")
            check(f"a/{name}/{label}/index", np.array_equal(i0, i1),
                  f"{int((i0 != i1).sum())} of {nqry} differ")

    # (b) exact ties (duplicated points, queries landing on them) must not make
    # the answer depend on the chunk size, and every tie must be found at 0 mm.
    pts = rng.normal(size=(40, 3)) * 10.0
    pts = np.vstack([pts, pts[:10]])
    qry = np.vstack([rng.normal(size=(50, 3)) * 10.0, pts[:5]])
    d1, i1 = nn_query(pts, qry, "bruteforce", chunk_floats=CHUNK_FLOATS)
    d2, i2 = nn_query(pts, qry, "bruteforce", chunk_floats=3 * len(pts))
    check("b/ties/dist", np.array_equal(d1, d2),
          f"max_abs_delta={float(np.abs(d1 - d2).max()):.3e}")
    check("b/ties/index", np.array_equal(i1, i2), f"{int((i1 != i2).sum())} differ")
    check("b/ties/zero_distance_found", bool((d1 <= 1e-9).sum() >= 5),
          f"{int((d1 <= 1e-9).sum())} of {len(qry)} queries at 0 mm")

    # (c) the original search, where scipy exists. On a node without scipy this
    # is the expected SKIP, not a failure: the port must not need scipy.
    try:
        import scipy
        from scipy.spatial import cKDTree
    except Exception as exc:
        print(f"[selftest] d/ckdtree: SKIPPED (scipy not importable: "
              f"{type(exc).__name__}) -- expected where the port has to run")
    else:
        pts = rng.normal(size=(300, 3)) * 20.0
        qry = rng.normal(size=(300, 3)) * 20.0
        d0, i0 = cKDTree(pts).query(qry)
        d1, i1 = nn_query(pts, qry, "bruteforce")
        check("d/ckdtree/index", np.array_equal(i0, i1),
              f"{int((i0 != i1).sum())} of {len(qry)} differ")
        check("d/ckdtree/dist", float(np.abs(d0 - d1).max()) <= 1e-12,
              f"max_abs_delta={float(np.abs(d0 - d1).max()):.3e}")
        print(f"[selftest] d/ckdtree: compared against scipy {scipy.__version__}")

    print(f"[selftest] {len(failures)} failure(s)"
          + (f": {failures}" if failures else ""))
    return 0 if not failures else 1


def _parse_args(argv):
    ap = argparse.ArgumentParser(
        description="Gate-passage probe (ticket 06), numpy-only port (ticket 31).")
    ap.add_argument("bundle", nargs="?",
                    help="bundle key, one of: " + ", ".join(BUNDLES))
    ap.add_argument("--bl", default=None, metavar="DIR",
                    help="root of the Breakline_0 .pcd files; fills {bl} in the p31 entry")
    ap.add_argument("--gt", default=None, metavar="DIR",
                    help="root of Pot_A_Piece_%%d_T.txt and Pot_A_simple_graph.txt; fills {gt}")
    ap.add_argument("--nn", choices=("bruteforce", "ckdtree"), default="bruteforce",
                    help="nearest-neighbour search: bruteforce is the port (default); "
                         "ckdtree is the original and needs scipy")
    ap.add_argument("--selftest", action="store_true",
                    help="check the nearest-neighbour search against a direct "
                         "computation and exit")
    args = ap.parse_args(argv)
    if not args.selftest:
        if not args.bundle:
            ap.error("give a bundle key, or --selftest")
        if args.bundle not in BUNDLES:
            ap.error(f"unknown bundle '{args.bundle}'; choose from "
                     + ", ".join(BUNDLES))
    return args


def resolve(key, bl, gt):
    """(Breakline_0 fmt, T fmt, graph, N) for a bundle key.

    Only the p31 entry carries the {bl} / {gt} placeholders; every other entry
    comes back exactly as it is written in BUNDLES above.
    """
    bl_fmt, gt_t_fmt, gra_fmt, n = BUNDLES[key]
    if bl is None:
        bl = ART + "/p07_stage1/pota_bl"
    if gt is None:
        gt = ART + "/p07_stage1/pota_gt"
    return (bl_fmt.replace("{bl}", bl), gt_t_fmt.replace("{gt}", gt),
            gra_fmt.replace("{gt}", gt), n)


ARGS = _parse_args(sys.argv[1:])
if ARGS.selftest:
    sys.exit(selftest(ARGS.nn))
BL, GTP, GRA, N = resolve(ARGS.bundle, ARGS.bl, ARGS.gt)


def load_pcd_seg(path):
    lines = open(path).read().splitlines()
    segs = []
    for ln in lines[2:]:
        if ln.startswith("#"):
            a = list(map(int, ln[1:].split()))
            if len(a) >= 3:
                segs.append((a[0] - 1, a[1] - 1))
        else:
            break
    rows = []
    for ln in lines:
        s = ln.split()
        if len(s) >= 6 and not ln.startswith(
                ("#", "VERSION", "FIELDS", "SIZE", "TYPE", "COUNT",
                 "WIDTH", "HEIGHT", "VIEWPOINT", "POINTS", "DATA")):
            try:
                rows.append([float(x) for x in s[:6]])
            except ValueError:
                pass
    return segs, np.array(rows)


def T(p):
    return np.loadtxt(GTP % p).reshape(4, 4)


def place(pts6, M):
    q = pts6[:, :3] @ M[:3, :3].T + M[:3, 3]
    n = pts6[:, 3:6] @ M[:3, :3].T
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    return q, n


gt = [list(map(int, ln.split())) for ln in open(GRA) if ln.strip()]
mates = [(a + 1, b + 1) for a in range(N) for b in range(a + 1, N) if gt[a][b]]
print(f"{ARGS.bundle} mates: {len(mates)} (_0-only)")

GATES = [(2.0, 0.85), (20.0, 0.7)]
npass = 0
for a, b in mates:
    MA, MB = T(a), T(b)
    sa, da = load_pcd_seg(BL % a)
    sb, db = load_pcd_seg(BL % b)
    best = {}
    for s0, s1 in sa:
        Aq, nA = place(da[s0:s1 + 1], MA)
        for t0, t1 in sb:
            Bq, nB = place(db[t0:t1 + 1], MB)
            d, idx = nn_query(Bq, Aq, ARGS.nn)
            ag = (nA * nB[idx]).sum(1)
            for g in GATES:
                inl = int(((d < g[0]) & (ag > g[1])).sum())
                ab = int(((d < g[0]) & (np.abs(ag) > g[1])).sum())
                dd = float(d.min())
                if g not in best:
                    best[g] = [inl, ab, dd]
                else:
                    best[g][0] = max(best[g][0], inl)
                    best[g][1] = max(best[g][1], ab)
                    best[g][2] = min(best[g][2], dd)
    if best[(2.0, 0.85)][0] > 0:
        npass += 1
    print(f"  {a}-{b}: " + "; ".join(
        f"d<{g[0]}/n>{g[1]} raw={v[0]} abs={v[1]} min_d={v[2]:.2f}"
        for g, v in sorted(best.items())))
print(f"STRICT pass rate at GT (_0-only): {npass}/{len(mates)}")
