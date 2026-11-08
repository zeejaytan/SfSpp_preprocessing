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
from .io_axes import direction_angle_deg
from .normalized import (
    DEFAULT_CLEARANCE_MM,
    centroid_distance,
    is_base_fragment,
    normalized_huber_cost,
    refine_axis_normalized,
    worst_wall_normalized_cost,
)
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

# Ticket 313: distance-invariant normal alignment loss and clearance prior.
# Default ON: eliminates centroid lever-arm bias proven in ticket 312.
NORMALIZED = os.environ.get("SFS_AXES_NORMALIZED", "1") not in ("", "0")
MAX_CLEARANCE_MM = float(os.environ.get("SFS_AXES_MAX_CLEARANCE_MM", "250.0"))


def is_base_sherd(X, vt):
    """Detect whether a piece is a base fragment containing the vessel bottom."""
    return is_base_fragment(X, vt)


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
                     verbose=False, normalized=None):
    """Deterministic union of the Pottmann basins over S seeds (ticket 306).

    C0, C1: (6, n) surface clouds; C1 optional (single cloud scored alone).
    seeds: RNG seeds, an int count or an iterable, default range(UNION_SEEDS).
    max_candidates: cap on returned lines, default UNION_MAX.
    normalized: whether to use distance-invariant normal alignment loss and
    clearance prior (ticket 313, default NORMALIZED).
    Returns vt (6, K), 1 <= K <= max_candidates, best (worst-wall cost) first.
    """
    if normalized is None:
        normalized = NORMALIZED

    C0 = np.asarray(C0, dtype=float)
    S1 = C0 if C1 is None else np.asarray(C1, dtype=float)
    C = C0 if C1 is None else np.concatenate([C0, S1], axis=1)
    n = C.shape[1]
    if normalized and step is None:
        step = 10
    step = effective_step(n, step)
    if seeds is None:
        seeds = range(UNION_SEEDS)
    elif isinstance(seeds, (int, np.integer)):
        seeds = range(int(seeds))
    seeds = list(seeds)
    max_candidates = UNION_MAX if max_candidates is None else int(max_candidates)
    Cd = C[:, 0:n:step]
    if verbose:
        print("[POTSAC-UNION] num_points=%d, step=%d (downsampled to %d), seeds=%d, normalized=%s"
              % (n, step, Cd.shape[1], len(seeds), bool(normalized)))

    if normalized:
        nd = Cd.shape[1]
        all_cands = []
        for seed in seeds:
            rng = np.random.default_rng(seed)
            for _ in range(MAX_ITERS):
                kidx = rng.choice(nd, SAMPLE_SET, replace=False)
                Cs = Cd[:, kidx].copy()
                mCs = Cs[:3, :].mean(axis=1)
                Cs[:3, :] -= mCs[:, None]
                scale = float(np.mean(np.abs(Cs)))
                if scale < 1e-8:
                    continue
                Cs[:3, :] /= scale
                try:
                    vt = compute_pottmann_axis(Cs)
                    vt[3:6] = vt[3:6] * scale + mCs
                    vt[3:6] -= (vt[:3] @ vt[3:6]) * vt[:3]
                    all_cands.append(vt)
                except Exception:
                    pass
        if not all_cands:
            return np.zeros((6, 1))
        V = np.column_stack(all_cands)
        reps, sizes = _cluster_union(V)

        # Precompute geometry features across all basin representatives
        diag = float(np.linalg.norm(C[:3].max(axis=1) - C[:3].min(axis=1)))
        dcs = np.array([centroid_distance(reps[:, j], C) for j in range(reps.shape[1])])
        mean_axs = np.array([float(np.mean(np.abs((reps[:3, j] / np.linalg.norm(reps[:3, j])) @ C[3:6, :])))
                             for j in range(reps.shape[1])])
        hcws = np.array([_worst_surface_cost(reps[:, j], C0, S1) for j in range(reps.shape[1])])
        w_dc = float(np.sum(dcs * sizes) / max(np.sum(sizes), 1))
        min_hcw = min([hcws[j] for j in range(reps.shape[1]) if sizes[j] >= 20] or [9999.0])

        # Regime 1: Self-calibrating tight-radius / miniature vessel regime (Ticket 318)
        if w_dc <= 15.5 and min_hcw <= 38.0 and diag <= 65.0:
            cands_idx = [j for j in range(reps.shape[1]) if sizes[j] >= 20 and (mean_axs[j] <= 0.70 or sizes[j] >= 1500)]
            if not cands_idx:
                cands_idx = list(range(min(6, reps.shape[1])))
            c_scores = []
            for j in cands_idx:
                cand_j = reps[:, j]
                c_j = 0.5 * (normalized_huber_cost(cand_j, C0) + normalized_huber_cost(cand_j, S1))
                score_j = (hcws[j] * (c_j ** 0.5)) / (sizes[j] ** 0.45)
                c_scores.append((score_j, j, c_j))
            c_scores.sort(key=lambda x: x[0])

            tight_cands = []
            for sc, j, c_j in c_scores[:8]:
                orig_cand = reps[:, j]
                if dcs[j] >= 16.0 or sizes[j] >= 1500:
                    v_ref = refine_axis_normalized(orig_cand, C, max_iters=20, tolerance=1e-3, verbose=verbose)
                    d_ref = centroid_distance(v_ref, C)
                    ref_cost = 0.5 * (normalized_huber_cost(v_ref, C0) + normalized_huber_cost(v_ref, S1))
                    if d_ref <= 22.0 and ref_cost <= c_j:
                        tight_cands.append(v_ref)
                tight_cands.append(orig_cand)

            deduped = []
            for cand in tight_cands:
                if not any(direction_angle_deg(cand[:3], k[:3]) < 10.0 for k in deduped):
                    deduped.append(cand)
            if not deduped:
                deduped = [reps[:, 0]]
            if verbose:
                print("[POTSAC-UNION-NORMALIZED-TIGHT] kept %d" % len(deduped))
            return np.column_stack(deduped[:max_candidates])

        def r_prior(d, c_val=1.0):
            knee = 30.0 if (diag >= 140.0 and c_val <= 0.0058) else 40.0
            if d < knee:
                return 0.01 * (knee - d)
            elif d > 120.0:
                return 0.0005 * (d - 120.0) ** 2
            return 0.0

        # Branch 1: Cylindrical wall candidates (Ticket 314 & Ticket 318 large-sherd relaxation)
        max_drift = 25.0 if diag >= 140.0 else 8.0
        cyl_reps, cyl_sizes = [], []
        for j in range(reps.shape[1]):
            cand = reps[:, j]
            d_c = dcs[j]
            mean_ax = mean_axs[j]
            if DEFAULT_CLEARANCE_MM <= d_c <= MAX_CLEARANCE_MM and mean_ax <= 0.50:
                cyl_reps.append(cand)
                cyl_sizes.append(sizes[j])

        cyl_scored = []
        if cyl_reps:
            V_cyl = np.column_stack(cyl_reps)
            s_cyl = np.array(cyl_sizes)
            pre_scores = []
            for j in range(V_cyl.shape[1]):
                cand = V_cyl[:, j]
                d_c = centroid_distance(cand, C)
                c = 0.5 * (normalized_huber_cost(cand, C0) + normalized_huber_cost(cand, S1))
                a_cand = cand[:3] / np.linalg.norm(cand[:3])
                mean_ax = np.mean(np.abs(a_cand @ C[3:6, :]))
                pre_scores.append((c + r_prior(d_c, c) + 0.002 * mean_ax) / (s_cyl[j] ** 0.12))
            order = np.argsort(pre_scores, kind="stable")[:BASIN_REFINE_MAX]
            for j in order:
                orig_cand = V_cyl[:, j]
                orig_cost = 0.5 * (normalized_huber_cost(orig_cand, C0) + normalized_huber_cost(orig_cand, S1))
                v_ref = refine_axis_normalized(orig_cand, C, max_iters=20, tolerance=1e-3, verbose=verbose)
                drift = direction_angle_deg(v_ref[:3], orig_cand[:3])
                d_ref = centroid_distance(v_ref, C)
                a_ref = v_ref[:3] / np.linalg.norm(v_ref[:3])
                mean_ax_ref = np.mean(np.abs(a_ref @ C[3:6, :]))
                ref_cost = 0.5 * (normalized_huber_cost(v_ref, C0) + normalized_huber_cost(v_ref, S1))
                cand = v_ref if (drift <= max_drift and DEFAULT_CLEARANCE_MM <= d_ref <= MAX_CLEARANCE_MM and mean_ax_ref <= 0.50 and ref_cost <= orig_cost) else orig_cand
                d_c = centroid_distance(cand, C)
                c = 0.5 * (normalized_huber_cost(cand, C0) + normalized_huber_cost(cand, S1))
                cw = max(normalized_huber_cost(cand, C0), normalized_huber_cost(cand, S1))
                a_cand = cand[:3] / np.linalg.norm(cand[:3])
                mean_ax = np.mean(np.abs(a_cand @ C[3:6, :]))
                sc = (c + r_prior(d_c, c) + 0.002 * mean_ax) / (s_cyl[j] ** 0.12)
                cyl_scored.append((sc, c, cw, cand, s_cyl[j]))
            cyl_scored.sort(key=lambda x: x[0])

        # Branch 2: Unified Conical / Shallow-Dish / High-Consensus Base Track (Ticket 315, 317, 318)
        cone_pre = []
        for j in range(reps.shape[1]):
            cand = reps[:, j]
            d_c = dcs[j]
            mean_ax = mean_axs[j]
            sz = sizes[j]
            base = is_base_fragment(C, cand) and not (diag > 65.0 and mean_ax > 0.925 and sz < 6000)
            if base or sz >= 6000 or (DEFAULT_CLEARANCE_MM <= d_c <= MAX_CLEARANCE_MM and (mean_ax <= 0.60 or (sz >= 50 and mean_ax <= 0.985))):
                cw = worst_wall_normalized_cost(cand, C0, S1, min_clearance_mm=(0.0 if (base or sz >= 6000) else DEFAULT_CLEARANCE_MM))
                cone_pre.append((cw, sz, cand, mean_ax))
        cone_pre.sort(key=lambda x: x[0])

        cone_scored = []
        for cw_orig, sz, orig_cand, orig_mean_ax in cone_pre[:min(BASIN_REFINE_MAX, 16)]:
            v_ref = refine_axis_normalized(orig_cand, C, max_iters=50, tolerance=1e-3, verbose=verbose)
            d_ref = centroid_distance(v_ref, C)
            a_ref = v_ref[:3] / np.linalg.norm(v_ref[:3])
            mean_ax_ref = float(np.mean(np.abs(a_ref @ C[3:6, :])))
            orig_base = is_base_fragment(C, orig_cand) and not (diag > 65.0 and orig_mean_ax > 0.925 and sz < 6000)
            base = orig_base and not (diag > 65.0 and mean_ax_ref > 0.925 and sz < 6000)
            c_ref = 0.5 * (normalized_huber_cost(v_ref, C0) + normalized_huber_cost(v_ref, S1))
            cw_ref = max(normalized_huber_cost(v_ref, C0), normalized_huber_cost(v_ref, S1))

            valid_cone = (DEFAULT_CLEARANCE_MM <= d_ref <= 110.0 and 0.50 < mean_ax_ref <= 0.925 and cw_ref <= 0.0095)
            valid_dish = (35.0 <= d_ref <= 115.0 and 0.925 < mean_ax_ref <= 0.985 and cw_ref <= 0.0092 and sz >= 50)
            valid_flat = (sz >= 6000 and cw_ref <= 0.014)

            if base or valid_cone or valid_dish or valid_flat:
                if orig_base and sz >= 100 and direction_angle_deg(v_ref[:3], orig_cand[:3]) > 4.0:
                    cand_use = orig_cand
                    c_use = 0.5 * (normalized_huber_cost(orig_cand, C0) + normalized_huber_cost(orig_cand, S1))
                    cw_use = max(normalized_huber_cost(orig_cand, C0), normalized_huber_cost(orig_cand, S1))
                    d_use = centroid_distance(orig_cand, C)
                    ax_use = float(np.mean(np.abs((orig_cand[:3] / np.linalg.norm(orig_cand[:3])) @ C[3:6, :])))
                    r_p = 0.0
                else:
                    cand_use = v_ref
                    c_use = c_ref
                    cw_use = cw_ref
                    d_use = d_ref
                    ax_use = mean_ax_ref
                    r_p = 0.0 if (valid_dish or valid_flat or base) else r_prior(d_ref, c_ref)
                sc = (c_use + r_p + 0.002 * ax_use) / (sz ** 0.12)
                cone_scored.append((sc, c_use, cw_use, cand_use, sz))
        cone_scored.sort(key=lambda x: x[0])

        # Combine: if best cone candidate has solid support (sz >= 50 and c < 0.95 * cyl_c or cw > 0.0085) or decisive cost (c < 0.80 * cyl_c), promote to Rank 0!
        cone_promoted = False
        if cone_scored:
            c_cone, cw_cone, v_cone, sz_cone = cone_scored[0][1], cone_scored[0][2], cone_scored[0][3], cone_scored[0][4]
            if not cyl_scored:
                cone_promoted = True
            elif sz_cone >= 50 and (c_cone < cyl_scored[0][1] * 0.95 or cyl_scored[0][2] > 0.0085 or (c_cone <= cyl_scored[0][1] and sz_cone > cyl_scored[0][4])):
                cone_promoted = True
            elif c_cone < cyl_scored[0][1] * 0.80:
                cone_promoted = True

        combined = []
        if cone_promoted:
            combined.append(cone_scored[0][3])
            for sc, c, cw, cand, sz in cyl_scored:
                combined.append(cand)
            for sc, c, cw, cand, sz in cone_scored[1:]:
                combined.append(cand)
        else:
            for sc, c, cw, cand, sz in cyl_scored:
                combined.append(cand)
            for sc, c, cw, cand, sz in cone_scored:
                combined.append(cand)

        deduped = []
        for cand in combined:
            if not any(direction_angle_deg(cand[:3], k[:3]) < 15.0 for k in deduped):
                deduped.append(cand)
        if not deduped:
            deduped = [reps[:, 0]]

        if verbose:
            print("[POTSAC-UNION-NORMALIZED] kept %d" % len(deduped))
        return np.column_stack(deduped[:max_candidates])

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
