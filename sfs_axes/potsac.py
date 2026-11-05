"""PotSAC candidate search + selection — port of compute_axis_of_symmetry.m
(MLESAC 1000x6-pt + Pottmann) and run_potsac.m (dedup + two-stage refine).

MATLAB fidelity notes:
  * randsample(n, 6) = uniform WITHOUT replacement -> rng.choice(n, 6, replace=False).
  * Per-sample mean/scale normalisation uses mean(abs(Cs)) over ALL 36 entries.
  * The biaxial cost is PER-POINT (MATLAB sum collapses only dim 1):
    the inlier count is sum(per-point GM-robustified cost < 1.0) and the
    ranking cost is the sum of those per-point costs.
  * Dedup threshold 0.9848 = cos(10deg).
  * run_potsac.m:61 and :78 additionally keep only axes with cost < cost(0)*1.1
    ("first survivor, not the minimum" — MATLAB quirk). The paper has no such
    prune; SFS_AXES_COST_PRUNE (default OFF since ticket 307) selects which of
    the two chains is used. See the block below.
"""

import os

import numpy as np

from .cao import compute_biaxial_cao_error
from .pottmann import compute_pottmann_axis
from .refine import refine_axis
from .robust import apply_robustifier, robustifier_gm, robustifier_huber

DEDUP_COS = 0.9848  # cos(10 deg), run_potsac.m:65,86
# Ticket 303 switch, default OFF (MATLAB-faithful stale cost).
#   ON: after the all-points refinement, recompute each surviving axis' Huber
#   cost on all points and re-dedup/re-order with it. run_potsac.m:82-84 sorts
#   by the stage-1 subsample cost even though stage-2 has moved the axes, so the
#   axis handed to the assembler as line 0 may not be the best refined one.
#   Paper (papers/text/sfspp-2502.13986v1.md:175) defines the cost as the axis'
#   robustified residual error; after refinement that is the refined axis' cost.
#   MEASURED (ticket 303, Pot A): 7/8 13/15 on 3 replays — the sort order is not
#   what loses Piece 08, so this is a fidelity option and NOT a fix.
POST_REFINE_COST = os.environ.get("SFS_AXES_POST_REFINE_COST", "") not in ("", "0")
# Ticket 303 switch, default OFF (MATLAB-faithful: order by residual cost).
#   ON: order the surviving axes by whether they make the piece ONE CONTIGUOUS
#   PATCH about the axis, then by cost (see patch_gap_deg, and _patch_order).
#   Why: the assembler z-aligns every piece on axis LINE 0
#   (main_pristine_batch.cpp, AxisAlignment with the default index), so whichever
#   candidate the estimator ranks first fixes the frame that piece is searched
#   in. Cost is not a reliable rank for that purpose: on Pot A Piece 08 all four
#   residual costs (stage-1 subsample, all-points Huber, per-face Huber,
#   worst-face) prefer the axis 35.9 deg from the released line over the 7.7-deg
#   one, because several distinct symmetries explain a small patch equally well.
#   What a wrong axis cannot do is make the patch contiguous: a sherd is one
#   connected piece cut out of a pot, so about the true axis its points fill one
#   arc of azimuth and leave one large empty gap, while Piece 08's two
#   cost-favoured axes wrap a full 3.3 deg and 4.4 deg around with no empty gap
#   at all (the good one leaves 287.6 deg empty). See also the paper's premise
#   that a fragment may have several Pottmann-valid axes
#   (papers/text/sfspp-2502.13986v1.md:175).
#   MEASURED (ticket 303, Pot A): 7/8 13/15 on 2 replays — Piece 08 is never
#   joined in any order, so this reorders correctly and still does not seat it.
#   Kept for the axis-ranking work; NOT a fix.
PATCH_GAP = os.environ.get("SFS_AXES_PATCH_GAP", "") not in ("", "0")
# An axis that leaves at least this much of the circle empty is treated as
# making the piece one patch. 90 deg is deliberately loose: real sherds wrap
# anything from a small fraction of the pot to most of it, and the two axes this
# rule has to demote leave 3-4 deg empty, so the exact value is not delicate.
PATCH_GAP_MIN_DEG = 90.0
# Ticket 304, default ON: use step = 1 on pieces under 5,000 points even when
#   the caller passes step=10 (as corpus302.py:79 and cli.py:19 do).
#   SFS_AXES_ADAPTIVE_UNDER_5K=0 turns it off (step=10 always).
#   PROVENANCE, corrected by ticket 307: this is a DEVIATION, not the authors'
#   rule. run_potsac.m:18 samples C(:,1:10:num_points) with no size exception;
#   the under-5,000 block lives only in the locally patched copy
#   (AxisExtraction/run_potsac.m:18-27, ff40fc9, Zeejay Tan) and is absent from
#   the vendored upstream tree (original_nurbs_preprocessing/AxisExtraction/).
#   Why it is kept anyway: Pot A Piece 08 has 3,337 surface points; step=10
#   decimates it to 334 and destroys the secondary Huber basin near released
#   line 1 (stationary point drifts 21.08 deg away). At step=1 all 3,337 points
#   are used, the basin is recovered (1.4-1.6 deg at stage-1, 5.23 deg at
#   stage-2) and Pot A seats 8/8 + 15/15 with our own axes (job 34350986).
#   44 of the 163 corpus pieces are under 5,000 points. MEASURED (ticket 307,
#   arm B5, step=10 always): Pot A NP=8 7/8 13/15, 6/8 10/15, 6/8 10/15 over
#   seeds 0/1/2 vs 6/8 10/15, 7/8 12/15, 6/8 10/15 with the rule on -- no seed
#   improves consistently, so the rule stays on its own 304 measurement.
ADAPTIVE_UNDER_5K = os.environ.get("SFS_AXES_ADAPTIVE_UNDER_5K", "1") not in ("", "0")
# Ticket 307: the paper's candidate set, DEFAULT since this ticket.
#   ON (SFS_AXES_COST_PRUNE=1): the authors' cost < cost(1)*1.1 prune, run twice
#   (run_potsac.m:61 after the stage-1 dedup, :78 again after the all-points
#   refinement, on the stale stage-1 cost).
#   OFF (default): the top 10 survivors of the dedup are all written, which is
#   what papers/text/sfspp-2502.13986v1.md:175 describes -- "selects the top 10
#   candidate axes ... those with an angle of 10 degrees or less are considered
#   duplicates, with the axis having the higher cost ... being removed through
#   pruning" -- with no cost cut. Paper and the authors' .m genuinely disagree,
#   so this is decided by measurement, not by preference.
#   MEASURED (ticket 307, Pot A, assembler NP=8, two internal repeats each,
#   our axes only): OFF 7/8 13/15, 8/8 15/15, 7/8 13/15 at seeds 0/1/2;
#   ON 6/8 10/15, 7/8 12/15, 6/8 10/15. Every seed improves by at least one
#   sherd and no seed regresses; seed 1 reaches the paper's own 8/8 + 15/15.
#   Corpus (163 pieces): 84/163 within 5 deg, median best 4.56 deg with OFF vs
#   83/163, 4.66 deg with ON -- no worse. Juglet F20 (floor 20, NP=9): 0/9
#   seated with our axes; the authors' own released Dataset axes also seat 0/9,
#   so that lane does not discriminate. The extra lines cost little at the
#   assembler: 120 of 163 pieces write the same count either way and matching is
#   quadratic in candidates per piece.
COST_PRUNE = os.environ.get("SFS_AXES_COST_PRUNE", "0") not in ("", "0")
MAX_ITERS = 1000
SAMPLE_SET = 6
INLIER_THRESHOLD = 1.0

# Ticket 306 (default ON for the corpus path): the number of deterministic seeds
# whose 1000 Pottmann draws are unioned, and the cap on lines written per piece.
# Why 10 seeds: the single-seed pool does contain every basin (Piece 07's second
# released axis is 228-252 of 1000 draws; Piece 08's released axis is a basin of
# 7-18 draws), but which draws survive the top-10 cut and the duplicate filter
# swings with the seed -- on Piece 08 the released basin is rank 1 of 20 at one
# seed and rank 38 at another. Ten seeds x 1000 draws lands in every basin of
# every piece measured, without best-of-N on the assembler.
# Why a cap of 6: the authors' own released axis files hold at most 6 lines
# (129 pieces 1 line, 19 with 2, 11 with 3, 1 with 4, 2 with 5, 1 with 6), so 6 is
# their practical candidate budget. The assembler's matching is quadratic in
# candidates per piece (feature_matching.cpp FeatureCompGraphBuilding loops
# axis_x x axis_y), so an uncapped basin list would also cost run time.
UNION_SEEDS = int(os.environ.get("SFS_AXES_UNION_SEEDS", "10"))
UNION_MAX = int(os.environ.get("SFS_AXES_UNION_MAX", "6"))

# Ticket 310, DEFAULT OFF: converge every basin before it is scored and ranked.
#   ON: cluster the whole draw pool into 10-deg basins, refine EVERY basin
#   representative on all points at 1e-9 (the tolerance the written file gets),
#   re-cluster the converged axes, then rank by the worse wall's Huber cost and
#   only then cap to the candidate budget.
#   OFF (pre-310 behaviour, also the authors' stage order): score the stage-1
#   basin representatives, cap, and refine only the survivors
#   (run_potsac_union's original body, kept below).
#   Why the step exists: at the stage-1 tolerance (1e-3 on the sampled cloud) a
#   candidate 5-25 deg off the seating axis measures CHEAPER than the seating
#   axis itself -- 6.26 deg at 87.05 against 87.66 per point (job 34393545) --
#   because it is not at a stationary point of the full-cloud cost; 83 of 1000
#   draws land in that band and every cost statistic reads it alike. Refining a
#   basin on all points collapses it onto its own stationary point (the seating
#   basin onto 0.00-0.19 deg of itself in 24 of 24 seeds).
#   Why it is NOT the default (measured, ticket 310): the collapse happens
#   whenever a basin is refined, and the union path refines the basins it writes
#   anyway; the step only chooses WHICH basins are refined before the cap. On
#   Pot A Piece 08 the written file is the same with the step on or off in 24 of
#   24 seeds at cap 6 and 12 of 12 at cap 2 (seating axis first in 24 of 24
#   either way, job 34398847); on the large pieces the whole pool refines into
#   ONE 10-deg basin (Pot D Pieces 01 and 03, K=1 in all 6 seeds, job 34399109),
#   so the arms cannot differ there either. ON costs 1.03x the time (63 against
#   61 s/seed) and writes more lines (K=6 against 4 at cap 6). The "axis every
#   time" gain belongs to the union path's whole-pool basins ranked by the worse
#   wall's cost, not to this step. Reading of
#   papers/text/sfspp-2502.13986v1.md:175: the cost it ranks by is "the
#   robustified residual error" of the axis, which is not yet that number while
#   the axis is unconverged; the "sample only 10% ... after pruning all surface
#   points are used" clause is an efficiency statement and is what OFF restores.
CONVERGE_BEFORE_RANK = os.environ.get(
    "SFS_AXES_CONVERGE_BEFORE_RANK", "0") not in ("", "0")
# Cap on how many basins the all-points refinement above may run on, so a piece
# with a very scattered pool cannot blow up the run time. Basins are dropped by
# their stage-1 worst-wall cost, i.e. only after the cheap score has been used.
BASIN_REFINE_MAX = int(os.environ.get("SFS_AXES_BASIN_REFINE_MAX", "32"))


def compute_axis_of_symmetry(C, rng=None, max_iters=MAX_ITERS, verbose=False):
    """Port of compute_axis_of_symmetry.m.

    C: (6, n). Returns (vt (6, K) [dir; pos] sorted by ascending cost,
    inliers (K,) per-point counts, costs (K,) summed GM costs, samples list).
    """
    C = np.asarray(C, dtype=float)
    C = C.copy()
    C[3:6, :] = C[3:6, :] / np.sqrt(np.sum(C[3:6, :] ** 2, axis=0))
    n = C.shape[1]
    rng = np.random.default_rng() if rng is None else rng
    vts, inliers, costs, samples = [], [], [], []
    for _ in range(max_iters):
        kidx = np.sort(rng.choice(n, SAMPLE_SET, replace=False))
        Cs = C[:, kidx].copy()
        mCs = Cs[0:3, :].mean(axis=1)
        Cs[0:3, :] = Cs[0:3, :] - mCs[:, None]
        scale = float(np.mean(np.abs(Cs)))
        Cs[0:3, :] = Cs[0:3, :] / scale
        vt = compute_pottmann_axis(Cs)
        vt[3:6] = vt[3:6] * scale + mCs
        vt[3:6] = vt[3:6] - (vt[0:3] @ vt[3:6]) * vt[0:3]
        err = compute_biaxial_cao_error(vt, C)
        # compute_axis_of_symmetry.m:29-34: robustify the PER-POINT errors,
        # rank by their sum, count points whose robustified cost < 1.0.
        rob = apply_robustifier(robustifier_gm, np.atleast_1d(err))
        cost = float(np.sum(rob))
        inl = int(np.sum(np.abs(rob) < INLIER_THRESHOLD))
        vts.append(vt)
        inliers.append(inl)
        costs.append(cost)
        samples.append(kidx)
    vts = np.column_stack(vts)
    inliers = np.array(inliers)
    costs = np.array(costs)
    order = np.argsort(costs, kind="stable")
    return vts[:, order], inliers[order], costs[order], [samples[i] for i in order]


def _dedup(vt, cost):
    """Drop axes within 10deg of an earlier survivor. Port of run_potsac.m:59-75."""
    dirs = vt[0:3, :] / np.linalg.norm(vt[0:3, :], axis=0)
    sim = np.abs(dirs.T @ dirs)
    sim = np.triu(sim, k=1)
    jj = np.unique(np.where(sim > DEDUP_COS)[1])
    keep = np.ones(vt.shape[1], dtype=bool)
    keep[jj] = False
    vt, cost = vt[:, keep], cost[keep]
    if vt.shape[1] == 0 or not COST_PRUNE:
        return vt, cost
    keep = cost < cost[0] * 1.1
    return vt[:, keep], cost[keep]


def patch_gap_deg(vt, X):
    """Largest empty arc of azimuth (deg) left by X about the axis vt.

    A surface of revolution about vt, sampled over one connected patch of an
    object, fills one arc of azimuth: the rest of the circle is missing. A line
    that is not a symmetry of the piece does not carve it into one arc, so its
    azimuths cover the whole circle and the largest empty gap collapses to a few
    degrees. Blind: uses the piece's own surface points only.
    """
    d = vt[0:3] / np.linalg.norm(vt[0:3])
    p = vt[3:6] - vt[3:6].dot(d) * d
    a = np.array([1.0, 0.0, 0.0])
    if abs(a.dot(d)) > 0.9:
        a = np.array([0.0, 1.0, 0.0])
    e1 = a - a.dot(d) * d
    e1 = e1 / np.linalg.norm(e1)
    e2 = np.cross(d, e1)
    rel = X[0:3, :] - p[:, None]
    axial = d @ rel
    rad = rel - np.outer(d, axial)
    th = np.sort(np.degrees(np.arctan2(e2 @ rad, e1 @ rad)) % 360.0)
    gaps = np.diff(np.r_[th, th[0] + 360.0])
    return float(gaps.max())


def _patch_order(vt, cost, X):
    """Candidates that make the piece one patch first, then by cost (stable)."""
    if vt.shape[1] < 2:
        return np.arange(vt.shape[1])
    gap = np.array([patch_gap_deg(vt[:, i], X) for i in range(vt.shape[1])])
    contiguous = gap >= PATCH_GAP_MIN_DEG
    # sort key: contiguous group first (False < True), then ascending cost
    return np.lexsort((cost, np.logical_not(contiguous)))


def adaptive_step(n):
    """Working-tree sampling rule, run_potsac.m:18-30."""
    if n < 5000:
        return 1
    if n > 50000:
        return int(np.ceil(n / 10000))
    return max(1, int(round(n / 10000)))


def effective_step(n, step):
    """The stride actually used for candidacy and stage-1.

    step=None asks for the working-tree rule. An explicit step is honoured
    except on the small sherds the authors run whole (run_potsac.m:19-20),
    where ADAPTIVE_UNDER_5K forces 1 (ticket 304: step=10 erased Piece 08's
    second axis line and lost the piece from Pot A).
    """
    if step is None:
        return adaptive_step(n)
    if ADAPTIVE_UNDER_5K and n < 5000:
        return 1
    return step


def run_potsac(C1, C2=None, rng=None, step=None, num_candidates=10, verbose=False):
    """Port of run_potsac.m.

    C1, C2: (6, n) surface clouds (C2 optional; single-arg half-split kept).
    step: downsampling stride for candidacy/stage-1 (None = adaptive working-tree
    rule; pass 10 for the paper-letter 10% sampling). Stage-2 always uses all
    points. Returns vt (6, K), K >= 0, ordered by residual cost unless
    SFS_AXES_PATCH_GAP is set, in which case by patch contiguity first.
    """
    C1 = np.asarray(C1, dtype=float)
    if C2 is None:
        n = C1.shape[1]
        half = n // 2  # floor(0.5*n), run_potsac.m:10-12
        C = C1
    else:
        C = np.concatenate([C1, np.asarray(C2, dtype=float)], axis=1)
        n = C.shape[1]
    step = effective_step(n, step)
    if verbose:
        print("[POTSAC] num_points=%d, step=%d (downsampled to %d points)"
              % (n, step, n // step))
    Cd = C[:, 0:n:step]
    vt, _inl, _costs, _samples = compute_axis_of_symmetry(Cd, rng=rng)
    vt = vt[:, 0:num_candidates]
    for i in range(vt.shape[1]):
        vt[:, i] = refine_axis(vt[:, i], Cd, 2, 300, 1e-3, verbose=verbose)
    cost = np.empty(vt.shape[1])
    for i in range(vt.shape[1]):
        resid = compute_biaxial_cao_error(vt[:, i], Cd)
        cost[i] = float(np.sum(apply_robustifier(
            robustifier_huber, np.atleast_1d(resid))))
    vt, cost = _dedup(vt, cost)
    for i in range(vt.shape[1]):
        vt[:, i] = refine_axis(vt[:, i], C, 2, 300, 1e-9, verbose=verbose)
    if POST_REFINE_COST:
        for i in range(vt.shape[1]):
            resid = compute_biaxial_cao_error(vt[:, i], C)
            cost[i] = float(np.sum(apply_robustifier(
                robustifier_huber, np.atleast_1d(resid))))
    vt, cost = _dedup(vt, cost)
    if PATCH_GAP:
        order = _patch_order(vt, cost, C)
    else:
        order = np.argsort(cost, kind="stable")
    return vt[:, order]

# --------------------------------------------------------------- union path
# Ticket 306: hand the assembler every distinct symmetry basin, not one ranked
# guess. Measured on Pot A (see the ticket for the full tables): the shipped
# chain's cost < cost[0]*1.1 prune drops Piece 07's second released axis (a
# basin of 228-252 of 1000 draws at 3.5x the best cluster's cost) and the
# 10-deg dedup prunes Piece 08's released axis at one seed of four. Cost is not
# a rank the universal quantifier can rely on here: on Piece 08 the global cost
# minimum belongs to an axis 30.2 deg from released line 0 and 57.8 deg from
# line 1, and the released axis is the 13th cheapest of 20 basins.


def _huber_per_point(vt, X):
    """Huber cost per point of axis vt on cloud X (the run_potsac cost, / n)."""
    err = compute_biaxial_cao_error(vt, X)
    return float(np.sum(apply_robustifier(
        robustifier_huber, np.atleast_1d(err)))) / max(X.shape[1], 1)


def _worst_surface_cost(vt, C0, C1):
    """Cost per point on the worse of the two walls.

    The only statistic measured to rank Piece 08's released axis first of 20
    basins; the concatenated cost ranks it 13th, because Surface_0's residual
    dominates the sum.
    """
    return max(_huber_per_point(vt, C0), _huber_per_point(vt, C1))


def _cluster_union(V, cos=DEDUP_COS):
    """Greedy 10-deg basin clustering of candidate axes; first candidate wins.

    V: (6, K) in preference order. Returns (reps (6, R), sizes (R,)), reps[r]
    being the first candidate of basin r and sizes[r] how many fell in it.
    Deterministic: the order of V fixes the outcome.
    """
    d = V[0:3, :] / np.linalg.norm(V[0:3, :], axis=0)
    reps = []
    dreps = np.empty((3, 0))
    sizes = []
    for i in range(d.shape[1]):
        if dreps.shape[1]:
            sim = np.abs(dreps.T @ d[:, i])
            hit = np.flatnonzero(sim > cos)
        else:
            hit = np.empty(0, dtype=int)
        if hit.size:
            sizes[int(hit[0])] += 1
        else:
            reps.append(i)
            dreps = np.column_stack([dreps, d[:, i]])
            sizes.append(1)
    return V[:, reps], np.array(sizes, dtype=int)


# The union rule, one warrant per term (ticket 310 B1).  The paper's clause is
# papers/text/sfspp-2502.13986v1.md:175 unless a measurement is named.
#   1. every draw of every seed, not one draw        -- the paper's MLESAC returns one
#      axis per run; a single run carried the seating axis in 3 of 8 (ticket 308,
#      Pot A Piece 08) and 13 of 24 (ticket 310 A3, job 34393365), so the hypothesis
#      is in the pool but not reliably first.
#   2. cluster draws into 10-deg basins              -- paper:175, duplicates are axes
#      within 10 deg, the dearer one pruned.  Kept as given.
#   3. rank by the WORSE wall's Huber cost per point -- paper:175 names the cost the
#      "robustified residual error"; the worse wall because a single wall alone cannot
#      place the cylinder on a small sherd (ticket 310 A1: the two wall-alone optima
#      differ by 1.3-8.7 deg on Piece 08).  Measurement: this ranking put the seating
#      axis first in 24 of 24 seeds (ticket 310 B2, job 34398847).
#   4. cap at max_candidates (6)                     -- the most lines the authors ever
#      release for one piece (Axes/, 220 lines over 163 pieces).
#   5. refine the survivors on ALL points at 1e-9    -- paper:175, "after pruning, all
#      surface points are used"; 1e-9 is the tolerance at which the written file is
#      produced.  Measurement: this is the step that moves a basin onto its own
#      stationary point, 0.00-0.19 deg in 24 of 24 seeds (job 34393545).
# Blind: nothing here reads the released Axes/ files, the GT poses, or any per-piece
# constant; the only inputs are the piece's own two surfaces and the draws' own optima.
# SFS_AXES_CONVERGE_BEFORE_RANK (default off) reorders 2 and 5; see the switch above.
def run_potsac_union(C0, C1=None, seeds=None, step=None, max_candidates=None,
                     verbose=False):
    """Deterministic union of the Pottmann basins over S seeds (ticket 306).

    C0, C1: (6, n) surface clouds; C1 optional (single cloud scored alone).
    seeds: RNG seeds, an int count or an iterable, default range(UNION_SEEDS).
    max_candidates: cap on returned lines, default UNION_MAX.
    Returns vt (6, K), 1 <= K <= max_candidates, best (worst-wall cost) first.

    Rule: every draw of every seed is refined on the sampled cloud and the whole
    set is clustered at 10 deg in ascending GM-cost order, so each real basin
    contributes its GM-best representative and no basin is lost to the top-10
    cut or to the cost prune. Survivors are ranked by the worst wall's Huber
    cost per point, capped, then stage-2 refined on all points and re-clustered
    and re-ranked. Pure function of the clouds and the seeds.
    """
    C0 = np.asarray(C0, dtype=float)
    S1 = C0 if C1 is None else np.asarray(C1, dtype=float)
    C = C0 if C1 is None else np.concatenate([C0, S1], axis=1)
    n = C.shape[1]
    step = effective_step(n, step)
    if seeds is None:
        seeds = range(UNION_SEEDS)
    elif isinstance(seeds, (int, np.integer)):
        seeds = range(int(seeds))
    seeds = list(seeds)
    max_candidates = UNION_MAX if max_candidates is None else int(max_candidates)
    Cd = C[:, 0:n:step]
    if verbose:
        print("[POTSAC-UNION] num_points=%d, step=%d (downsampled to %d), seeds=%d"
              % (n, step, Cd.shape[1], len(seeds)))
    cand = []
    for seed in seeds:
        vt = compute_axis_of_symmetry(Cd, rng=np.random.default_rng(seed))[0]
        for k in range(vt.shape[1]):
            cand.append(refine_axis(vt[:, k], Cd, 2, 300, 1e-3))
    V = np.column_stack(cand)
    reps, sizes = _cluster_union(V)
    if CONVERGE_BEFORE_RANK:
        # ticket 310: converge first, then score. See the switch above.
        if reps.shape[1] > BASIN_REFINE_MAX:
            pre = np.array([_worst_surface_cost(reps[:, j], C0, S1)
                            for j in range(reps.shape[1])])
            reps = reps[:, np.argsort(pre, kind="stable")[:BASIN_REFINE_MAX]]
        V = reps.copy()
        for j in range(V.shape[1]):
            V[:, j] = refine_axis(V[:, j], C, 2, 300, 1e-9, verbose=verbose)
        reps, sizes2 = _cluster_union(V)
        score = np.array([_worst_surface_cost(reps[:, j], C0, S1)
                          for j in range(reps.shape[1])])
        order = np.argsort(score, kind="stable")
        if verbose:
            print("[POTSAC-UNION] %d draws -> %d basins (sizes %s), refined %d "
                  "-> %d converged, kept %d, costs %s"
                  % (len(cand), len(sizes), sizes.tolist(), V.shape[1],
                     reps.shape[1], min(reps.shape[1], max_candidates),
                     np.round(score[order], 1).tolist()))
        return reps[:, order[:max_candidates]]
    score = np.array([_worst_surface_cost(reps[:, j], C0, S1)
                      for j in range(reps.shape[1])])
    order = np.argsort(score, kind="stable")
    V = reps[:, order[:max_candidates]]
    for j in range(V.shape[1]):
        V[:, j] = refine_axis(V[:, j], C, 2, 300, 1e-9, verbose=verbose)
    reps, sizes2 = _cluster_union(V)
    score = np.array([_worst_surface_cost(reps[:, j], C0, S1)
                      for j in range(reps.shape[1])])
    order = np.argsort(score, kind="stable")
    if verbose:
        print("[POTSAC-UNION] %d draws -> %d basins (sizes %s), kept %d, "
              "costs %s" % (len(cand), len(sizes), sizes.tolist(),
                            reps.shape[1],
                            np.round(score[order], 1).tolist()))
    return reps[:, order]