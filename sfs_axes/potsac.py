"""PotSAC candidate search + selection — port of compute_axis_of_symmetry.m
(MLESAC 1000x6-pt + Pottmann) and run_potsac.m (dedup + two-stage refine).

MATLAB fidelity notes:
  * randsample(n, 6) = uniform WITHOUT replacement -> rng.choice(n, 6, replace=False).
  * Per-sample mean/scale normalisation uses mean(abs(Cs)) over ALL 36 entries.
  * The biaxial cost is PER-POINT (MATLAB sum collapses only dim 1):
    the inlier count is sum(per-point GM-robustified cost < 1.0) and the
    ranking cost is the sum of those per-point costs.
  * Dedup threshold 0.9848 = cos(10deg); cost prune keeps cost < cost[0]*1.1
    (first survivor, not the minimum — MATLAB quirk, kept).
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
MAX_ITERS = 1000
SAMPLE_SET = 6
INLIER_THRESHOLD = 1.0


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
    if vt.shape[1] == 0:
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
    if step is None:
        step = adaptive_step(n)
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