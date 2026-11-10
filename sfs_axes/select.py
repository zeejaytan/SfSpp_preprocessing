"""Which candidate lines a piece hands the assembler (tickets 322, 323, 324).

Two steps over the union path's basins (run_potsac_union, normalized=True):

1. rank_by_profile: order the candidate lines by profile thickness (profile.py),
   refine the cheapest distinct ones on that same cost, re-order. The cost of every
   returned line is returned with it.
2. keep_lines: keep the first line, and each later line whose cost is at most
   tau times the first line's, at most kmax lines.

Why a ratio and why so few lines (ticket 323): the assembler scores every pair of
pieces over every pair of their lines and accepts a join when the two lines it used
agree within 25 deg; it never checks a piece's line against the assembly it joins.
Every extra line is another chance to build a self-consistent wrong group. The lines
that rescue a wrong first line cost 1.01-1.16x the first; wrong alternatives cost a
median 1.83x. tau = 1.2 with kmax = 3 held all ten pots at floor on both repeats
(20 of 20 runs). The ratio compares two costs of the same piece, so no millimetre
and no per-pot constant enters.
"""

import os

import numpy as np

from .io_axes import direction_angle_deg
from .normalized import refine_axis_normalized
from .profile import profile_cost, refine_axis_profile, stride

# Ticket 322 ranking budget. Counts, not lengths: the 60 most-drawn basins enter
# (the pool held a line within 10 deg of the reference on 163/163 pot pieces at 60),
# each normal-refined on at most 12,000 points, and the 8 cheapest distinct lines are
# refined on the profile cost before the final order is taken.
PROFILE_BASINS = 60
PROFILE_NREF = 12000
PROFILE_NORMAL_ITERS = 60
PROFILE_REFINE_K = 8
PROFILE_DEDUP_DEG = 15.0

# Ticket 323 keep rule. SFS_AXES_LINE_RULE=0 writes every ranked line (the axes322 set).
LINE_RULE = os.environ.get("SFS_AXES_LINE_RULE", "1") not in ("", "0")
LINE_RULE_TAU = 1.2
LINE_RULE_KMAX = 3


def _distinct(items, key, tol_deg):
    """Keep each item unless its line is within tol_deg of one already kept (first wins)."""
    kept = []
    for it in items:
        v = key(it)
        if all(direction_angle_deg(v[0:3], key(k)[0:3]) >= tol_deg for k in kept):
            kept.append(it)
    return kept


def rank_by_profile(vt, walls, centre, size, refine_k=PROFILE_REFINE_K,
                    dedup_deg=PROFILE_DEDUP_DEG, costs=None):
    """Order candidate lines by profile thickness, refining the cheapest distinct ones.

    vt: (6, m) candidate lines; walls: list of (6, n) wall clouds (already strided);
    centre, size: the piece's centroid and bounding-box diagonal (refinement scale).
    costs: profile costs of vt's columns, if already known.
    Sort by cost -> dedup_deg dedup -> refine the first refine_k on the profile cost
    -> re-sort -> dedup. Returns (vt_ranked (6, K), costs (K,)), cheapest first.
    """
    vt = np.asarray(vt, dtype=float)
    if costs is None:
        costs = [profile_cost(vt[:, j], walls) for j in range(vt.shape[1])]
    pool = sorted(zip(costs, [vt[:, j] for j in range(vt.shape[1])]), key=lambda x: x[0])
    top = _distinct([v for _, v in pool], lambda v: v, dedup_deg)[:refine_k]
    fin = []
    for v in top:
        v_ref, c_ref = refine_axis_profile(v, walls, centre, size)
        fin.append((c_ref, v_ref))
    fin.sort(key=lambda x: x[0])
    kept = _distinct(fin, lambda x: x[1], dedup_deg)
    return np.column_stack([v for _, v in kept]), np.array([c for c, _ in kept], dtype=float)


def keep_lines(costs, tau=LINE_RULE_TAU, kmax=LINE_RULE_KMAX):
    """Indices of the lines to keep: 0, then each later k with costs[k] <= tau * costs[0].

    The first line is always kept, whatever the others cost. At most kmax indices,
    in their original order.
    """
    costs = np.asarray(costs, dtype=float)
    if costs.size == 0 or kmax < 1:
        return []
    keep = [0] + [k for k in range(1, costs.size) if costs[k] <= tau * costs[0]]
    return keep[:kmax]


def select_union_lines(reps, sizes, C0, C1, C, max_candidates, line_rule=None,
                       tau=LINE_RULE_TAU, kmax=LINE_RULE_KMAX, verbose=False):
    """Ticket 324: from the union path's basins to the lines written for the piece.

    reps, sizes: basin representatives (6, m) and their draw counts (_cluster_union);
    C0, C1: the two walls; C: both walls together. Each of the PROFILE_BASINS most-drawn
    basins enters twice (its representative and that representative after the
    normal-cost refinement); the pool is ranked by rank_by_profile, cut to
    max_candidates, and, with line_rule (default LINE_RULE), reduced by keep_lines.
    Returns (vt (6, K), costs (K,)).
    """
    if line_rule is None:
        line_rule = LINE_RULE
    n = C.shape[1]
    centre = C[0:3].mean(axis=1)
    size = float(np.linalg.norm(C[0:3].max(axis=1) - C[0:3].min(axis=1)))
    walls = [stride(C0), stride(C1)]
    Cr = C[:, 0:n:max(1, int(np.ceil(n / PROFILE_NREF)))]
    lines, costs = [], []
    for j in np.argsort(-sizes, kind="stable")[:PROFILE_BASINS]:
        raw = reps[:, j]
        ref = refine_axis_normalized(raw, Cr, max_iters=PROFILE_NORMAL_ITERS, tolerance=1e-6)
        lines += [raw, ref]
        costs += [profile_cost(raw, walls), profile_cost(ref, walls)]
    vt, c = rank_by_profile(np.column_stack(lines), walls, centre, size, costs=costs)
    vt, c = vt[:, :max_candidates], c[:max_candidates]
    if line_rule:
        idx = keep_lines(c, tau=tau, kmax=kmax)
        vt, c = vt[:, idx], c[idx]
    if verbose:
        print("[POTSAC-UNION-PROFILE] %d basins scored, line_rule=%s, kept %d, costs %s"
              % (len(lines) // 2, bool(line_rule), vt.shape[1], [round(x, 4) for x in c]))
    return vt, c
