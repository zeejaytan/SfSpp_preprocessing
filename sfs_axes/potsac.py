"""PotSAC candidate search + selection — port of compute_axis_of_symmetry.m
(MLESAC 1000x6-pt + Pottmann) and run_potsac.m (dedup + two-stage refine).

MATLAB fidelity notes:
  * randsample(n, 6) = uniform WITHOUT replacement -> rng.choice(n, 6, replace=False).
  * Per-sample mean/scale normalisation uses mean(abs(Cs)) over ALL 36 entries.
  * The biaxial cost is a whole-cloud scalar, so the "inlier count" is a
    degenerate 0/1 scalar; ranking is effectively by GM-robustified cost.
    Ported literally (sort ascending, no behavioural "fix").
  * Dedup threshold 0.9848 = cos(10deg); cost prune keeps cost < cost[0]*1.1
    (first survivor, not the minimum — MATLAB quirk, kept).
"""

import numpy as np

from .cao import compute_biaxial_cao_error
from .pottmann import compute_pottmann_axis
from .refine import refine_axis
from .robust import apply_robustifier, robustifier_gm, robustifier_huber

DEDUP_COS = 0.9848  # cos(10 deg), run_potsac.m:65,86
MAX_ITERS = 1000
SAMPLE_SET = 6
INLIER_THRESHOLD = 1.0


def compute_axis_of_symmetry(C, rng=None, max_iters=MAX_ITERS, verbose=False):
    """Port of compute_axis_of_symmetry.m.

    C: (6, n). Returns (vt (6, K) [dir; pos] sorted by ascending cost,
    inliers (K,) degenerate 0/1 counts, costs (K,), samples list).
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
        cost = float(apply_robustifier(robustifier_gm, np.atleast_1d(err)))
        inl = int(abs(err) < INLIER_THRESHOLD)
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
    points. Returns vt (6, K) cost-ordered, K >= 0.
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
    vt, cost = _dedup(vt, cost)
    order = np.argsort(cost, kind="stable")
    return vt[:, order]
