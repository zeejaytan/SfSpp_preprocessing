"""Joint axis selection: the three independent hypotheses, merged (ticket 03).

Two parallel arms (calibrated normal residual, Hermite normal-consistent
thickness) recover most reference-consistent lines but leave the ten-pot
end-to-end run short on Pot J: the shipped profile selector ("axes335",
select_union_lines) sometimes ranks a line the two arms both miss
(Pot_J_Piece_05: shipped 2.8 deg, calibrated normal 20.6, thickness 26.7), and a
15-deg dedup can drop a good thickness line behind a mediocre normal one
(Pot_J_Piece_11: thickness 3.4 deg behind normal 11.0 deg).

So the three hypotheses are computed independently on the same cached pool and
only their candidates are merged:

  normal rank-0      always first when that arm returned anything
  thickness rank-0   appended when it disagrees with every kept line
  shipped rank-0     select_union_lines' own rank-0 (the axes335 path)
  shipped rest       appended in rank order under the same test (default ON)

"Disagrees" is one angle, JOINT_DEDUP_DEG, a parameter of the selector and not of
the object, and JOINT_KMAX is the existing three-candidate cap.  No arm is retuned
and no per-pot, per-piece or object-size constant enters.  orient_base_axis is
applied once, to the merged list, exactly as the shipped path does.

Ticket 06 measured the chosen variant (10-deg merge with the shipped
secondaries, "tri_psec_d10" in the ticket's table) as the winner of five:
Authors' surfaces 110/141 rank-0 and 128/141 best-of-3 within 10 deg, median
2.7054 deg, d_gt_to_est 4.3383 mm; own surfaces 116/141 and 127/141; Pot G 7/7 at
K=1 on both.  SFS_AXES_TRI_SELECT=0 (or --no-tri-select) restores the shipped
selector byte-for-byte; select.py owns that switch.
"""

import numpy as np

from .io_axes import direction_angle_deg
from .meridian import (
    NORMAL_WIDTH,
    finish_line,
    line_shift,
    normal_cost,
    profile_thickness_cost,
    refine_axis_normal,
    refine_axis_profile_thickness,
)
from .profile import stride
from .select import (
    LINE_RULE_KMAX,
    LINE_RULE_TAU,
    PROFILE_DEDUP_DEG,
    PROFILE_REFINE_K,
    keep_lines,
    orient_base_axis,
    select_union_lines,
)

# Angle at which two kept hypotheses count as the same line.  10 deg is the
# paper's own duplicate angle (sfspp-2502.13986v1.md:175).
JOINT_DEDUP_DEG = 10.0
# Cap on lines written per piece -- the shipped three-candidate cap.
JOINT_KMAX = LINE_RULE_KMAX
# The most lines the authors ever release for one piece (Axes/, 220 over 163).
JOINT_MAX_CANDIDATES = 6
# The arms keep the shipped selection skeleton unchanged: 15-deg dedup, refine the
# best 8, keep within 1.2x the cheapest, cap at JOINT_MAX_CANDIDATES.
ARM_DEDUP_DEG = PROFILE_DEDUP_DEG
ARM_REFINE_K = PROFILE_REFINE_K
ARM_TAU = LINE_RULE_TAU
ARM_MAX_LINES = JOINT_MAX_CANDIDATES


def _dedup(lines, costs, deg=ARM_DEDUP_DEG):
    """Keep the cheapest line of every group within deg, preserving cost order."""
    order = np.argsort(np.asarray(costs, dtype=float))
    keep = []
    for i in order:
        v = lines[:, i]
        if all(direction_angle_deg(v[0:3], lines[0:3, j]) > deg for j in keep):
            keep.append(int(i))
    return keep


def _bounded(seed, refined, size, C):
    """Accept a refinement only if it moved the line < one piece-size at the piece.

    Without the bound the azimuthal objective diverges on a near-planar base
    sherd: on the native-3x Juglet base it reported a line 251-323 mm from the
    truth on a 33 mm object.
    """
    if not np.all(np.isfinite(refined)):
        return seed
    if line_shift(seed, refined, C) > size:
        return seed
    return refined


def _candidates(reps, sizes):
    """The most-drawn basins (the shipped PROFILE_BASINS habit), cost-blind."""
    if reps.shape[1] > 60:
        return reps[:, np.argsort(-np.asarray(sizes, dtype=float))[:60]]
    return reps


def _select(reps, cost_fn, refine_fn, walls, C, size, cap=ARM_MAX_LINES):
    """Rank -> dedup -> refine best k -> dedup -> keep_lines -> cap -> orient."""
    if reps.shape[1] == 0:
        return None
    costs = np.array([cost_fn(reps[:, i]) for i in range(reps.shape[1])])
    short = _dedup(reps, costs)[:ARM_REFINE_K]
    refined, rcost = [], []
    for i in short:
        v = _bounded(reps[:, i], refine_fn(reps[:, i]), size, C)
        if not np.all(np.isfinite(v)):
            continue
        refined.append(v)
        rcost.append(cost_fn(v))
    if not refined:
        return None
    lines = np.column_stack(refined)
    keep = _dedup(lines, rcost)
    lines = lines[:, keep]
    costs = np.asarray(rcost)[keep]
    sel = keep_lines(costs, tau=ARM_TAU, kmax=LINE_RULE_KMAX)[:cap]
    return orient_base_axis(lines[:, sel], C), costs[sel]


def normal_arm(reps, sizes, walls, C, size, width=NORMAL_WIDTH):
    """Hypothesis 1: e_hat, Huber width calibrated in the residual's own units."""
    cs = _candidates(reps, sizes)
    cost = lambda v: _mean([normal_cost(v, W, width) for W in walls])  # noqa: E731
    return _select(cs, cost, lambda v: refine_axis_normal(v, C, width=width),
                   walls, C, size)


def thickness_arm(reps, sizes, walls, C, size):
    """Hypothesis 2: Hermite thickness, neighbours charged for normal disagreement."""
    cs = _candidates(reps, sizes)

    def cost(v):
        return _mean([profile_thickness_cost(v, [W], normal_consistent=True)
                      for W in walls])

    def refine(v):
        return refine_axis_profile_thickness(v, walls, _centre(C), size,
                                             normal_consistent=True)[0]

    return _select(cs, cost, refine, walls, C, size)


def _mean(vals):
    return float(np.mean(vals))


def _centre(C):
    return np.asarray(C, dtype=float)[0:3].mean(axis=1)


def _split(res):
    """(lines (6, K), costs (K,)) from a selector result, or (None, None)."""
    if res is None:
        return None, None
    lines, costs = res
    lines = np.asarray(lines, dtype=float)
    if lines.ndim == 1:
        lines = lines.reshape(6, 1)
    if lines.size == 0 or lines.shape[1] == 0:
        return None, None
    costs = np.asarray(costs, dtype=float).ravel()
    if costs.size != lines.shape[1]:
        # An arm whose costs do not line up is still usable for its lines; the
        # merge only needs the ordering, and the costs are report-only.
        costs = (np.resize(costs, lines.shape[1]) if costs.size
                 else np.zeros(lines.shape[1]))
    return lines, costs


def merge_lines(res_normal, res_thickness, res_shipped, dedup_deg=JOINT_DEDUP_DEG,
                kmax=JOINT_KMAX, include_shipped_secondaries=True):
    """Merge three already-computed selector results; (lines, costs) or None.

    Order: normal rank-0, then thickness rank-0, then shipped rank-0, each
    appended only when it is at least dedup_deg from every kept line, until kmax
    lines are kept.  With include_shipped_secondaries the shipped candidate's
    remaining lines are scanned in rank order afterwards under the same test.
    Nothing is reoriented here.
    """
    a, ca = _split(res_normal)
    b, cb = _split(res_thickness)
    p, cp = _split(res_shipped)
    lines, costs = [], []

    def far_enough(v):
        return all(direction_angle_deg(v[0:3], u[0:3]) >= dedup_deg for u in lines)

    def add(v, c):
        lines.append(np.asarray(v, dtype=float).reshape(6))
        costs.append(float(c))

    if a is not None:
        add(a[:, 0], ca[0])
    for group, group_costs in ((b, cb), (p, cp)):
        if group is None or len(lines) >= kmax:
            continue
        if far_enough(group[:, 0]):
            add(group[:, 0], group_costs[0])
    if include_shipped_secondaries and p is not None:
        for k in range(1, p.shape[1]):
            if len(lines) >= kmax:
                break
            if far_enough(p[:, k]):
                add(p[:, k], cp[k])
    if not lines:
        return None
    return np.column_stack(lines), np.asarray(costs, dtype=float)


def orient_merged(merged, C, base_orient=True):
    """Point the merged set base -> rim once (the single final sign step)."""
    if merged is None:
        return None
    lines, costs = merged
    if not base_orient:
        return lines, costs
    C = np.asarray(C, dtype=float)
    if C.ndim == 1:
        C = C.reshape(3, 1)
    if C.size == 0 or C.shape[1] == 0:
        return lines, costs
    return orient_base_axis(lines, C), costs


def select_joint_lines(reps, sizes, C0, C1, C, max_candidates=None,
                       line_rule=True, base_orient=True):
    """Run the three hypotheses once and merge them (the union path's default).

    reps, sizes: basin representatives and their draw counts (_cluster_union);
    C0, C1: the two walls; C: both together, as select_union_lines expects.
    The shipped hypothesis is select_union_lines itself with the switch off, so
    the merge never re-enters this function.
    """
    walls = [stride(C0), stride(C1)]
    n = C.shape[1]
    size = float(np.linalg.norm(C[0:3].max(axis=1) - C[0:3].min(axis=1)))
    kmax = JOINT_KMAX if max_candidates is None else int(min(JOINT_KMAX,
                                                            max_candidates))
    res_normal = normal_arm(reps, sizes, walls, C, size)
    res_thickness = thickness_arm(reps, sizes, walls, C, size)
    res_shipped = select_union_lines(
        reps, sizes, C0, C1, C, JOINT_MAX_CANDIDATES, line_rule=line_rule,
        base_orient=False, tri_select=False)
    merged = merge_lines(res_normal, res_thickness, res_shipped,
                         dedup_deg=JOINT_DEDUP_DEG, kmax=kmax,
                         include_shipped_secondaries=True)
    if merged is None:
        return np.zeros((6, 1)), np.zeros(1)
    return orient_merged(merged, C, base_orient=base_orient)
