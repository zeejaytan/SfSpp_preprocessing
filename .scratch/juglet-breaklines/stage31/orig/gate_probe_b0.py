"""Gate-passage probe, pipeline-faithful variant (ticket 06 Test 1).

The pipeline reads ONLY Breakline_0 per piece -- this probe restricts to
_0 <-> _0 segment pairs at GT placements, counting nearest-neighbour
inliers the way MakeCorWOBuildTree + UnifiedPotteryValidation do.

Usage: python gate_probe_b0.py juglet | pota
"""
import sys
import numpy as np
from scipy.spatial import cKDTree

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
}
BL, GTP, GRA, N = BUNDLES[sys.argv[1]]


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
print(f"{sys.argv[1]} mates: {len(mates)} (_0-only)")

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
            d, idx = cKDTree(Bq).query(Aq)
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
