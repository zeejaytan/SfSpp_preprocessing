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
from .normalized import is_base_fragment, refine_axis_normalized
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

# Ticket 335 base-to-rim sign orientation. SFS_AXES_BASE_ORIENT=0 restores the
# previous behaviour (every direction canonicalized to dir_z >= 0, which writes an
# inverted base scan rim-to-base). The masks and their 50-point fallbacks are the
# ticket 366 prototype's.
BASE_ORIENT = os.environ.get("SFS_AXES_BASE_ORIENT", "1") not in ("", "0")
BASE_ORIENT_MAX_POINTS = 30000
BASE_ORIENT_POLE_AX = 0.85
BASE_ORIENT_WALL_AX = 0.50
BASE_ORIENT_MIN_COUNT = 50

# Ticket 03: the union path's default selector is the joint one (joint.py) -- the
# calibrated-normal arm, the thickness arm and this selector's own ranking, merged
# at 10 deg, at most three lines, oriented once. SFS_AXES_TRI_SELECT=0 (or
# --no-tri-select) restores the axes335 selector byte-for-byte; run_potsac (the
# paper chain) and the UNION_RANKER=="normal" path never come through here.
TRI_SELECT = os.environ.get("SFS_AXES_TRI_SELECT", "1") not in ("", "0")


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


def orient_base_axis(vt, C0, C1=None, max_points=BASE_ORIENT_MAX_POINTS,
                     return_info=False):
    """Point every candidate line base -> rim, blindly (ticket 335).

    PotSAC returns an undirected line: +a and -a cost the same, so an inverted base
    scan (one whose own frame has the vessel bottom along -z) comes out rim-to-base
    once it is canonicalized to dir_z >= 0. This rewrites that sign from the piece's
    own geometry: for a base fragment (normalized.is_base_fragment), the cap points
    (|a . n| > 0.85) and the wall points (|a . n| < 0.50) are separated along the
    line and the direction is negated when the wall sits below the cap. Non-base
    fragments keep the old dir_z >= 0 canonicalization. Nothing here reads a
    reference axis, a GT pose, or a per-piece constant.

    vt: (6,) or (6, K) candidate lines (direction, point). C0, C1: the piece's
    walls (C1 optional); together they are the cloud the masks are taken on.
    Strided to max_points columns, which is a no-op below 30,000 points.
    Returns (6,) / (6, K) with the input's dimensionality. Only out[0:3, k] is ever
    touched, and only negated: positions and directions are never renormalized or
    rewritten, so an unflipped column is byte-identical to its input.
    return_info: also return a list of per-column dicts (cand, base, flipped,
    z_wall, z_pole, z_wall_minus_z_pole, n_pole, n_wall).
    """
    vt = np.asarray(vt, dtype=float)
    one_d = vt.ndim == 1
    vt2d = vt.reshape(6, 1) if one_d else vt
    out = vt2d.copy()
    info = []

    C_all = np.asarray(C0, dtype=float)
    if C1 is not None:
        C_all = np.concatenate([C_all, np.asarray(C1, dtype=float)], axis=1)
    C_s = stride(C_all, n=max_points) if C_all.shape[1] > 0 else C_all
    if C_s.shape[1] > 0:
        n_norm = np.linalg.norm(C_s[3:6, :], axis=0)
        N_unit = C_s[3:6, :] / np.maximum(n_norm, 1e-12)

    for k in range(out.shape[1]):
        rec = dict(cand=k, base=False, flipped=False, z_wall=None, z_pole=None,
                   z_wall_minus_z_pole=None, n_pole=0, n_wall=0)
        norm_d = float(np.linalg.norm(out[0:3, k]))
        if norm_d < 1e-12:
            info.append(rec)
            continue
        a = out[0:3, k] / norm_d
        p0 = out[3:6, k] - float(out[3:6, k] @ a) * a
        line = np.r_[a, p0]
        if C_s.shape[1] > 0 and is_base_fragment(C_s, line):
            z = a @ (C_s[0:3, :] - p0[:, None])
            n_ax = np.abs(a @ N_unit)
            pole = n_ax > BASE_ORIENT_POLE_AX
            if int(pole.sum()) < BASE_ORIENT_MIN_COUNT:
                pole = n_ax >= np.quantile(n_ax, 0.90)
            wall = n_ax < BASE_ORIENT_WALL_AX
            if int(wall.sum()) < BASE_ORIENT_MIN_COUNT:
                wall = n_ax <= np.quantile(n_ax, 0.50)
            z_wall = float(z[wall].mean())
            z_pole = float(z[pole].mean())
            rec["base"] = True
            rec["z_wall"] = round(z_wall, 4)
            rec["z_pole"] = round(z_pole, 4)
            rec["z_wall_minus_z_pole"] = round(z_wall - z_pole, 4)
            rec["n_pole"] = int(pole.sum())
            rec["n_wall"] = int(wall.sum())
            if z_wall < z_pole:
                out[0:3, k] = -out[0:3, k]
                rec["flipped"] = True
        elif out[2, k] < 0:
            out[0:3, k] = -out[0:3, k]
            rec["flipped"] = True
        info.append(rec)

    out_shaped = out[:, 0] if one_d else out
    return (out_shaped, info) if return_info else out_shaped


def select_union_lines(reps, sizes, C0, C1, C, max_candidates, line_rule=None,
                       tau=LINE_RULE_TAU, kmax=LINE_RULE_KMAX, base_orient=None,
                       verbose=False, tri_select=None):
    """Ticket 324: from the union path's basins to the lines written for the piece.

    reps, sizes: basin representatives (6, m) and their draw counts (_cluster_union);
    C0, C1: the two walls; C: both walls together. Each of the PROFILE_BASINS most-drawn
    basins enters twice (its representative and that representative after the
    normal-cost refinement); the pool is ranked by rank_by_profile, cut to
    max_candidates, and, with line_rule (default LINE_RULE), reduced by keep_lines.
    base_orient (default BASE_ORIENT, ticket 335) then points each kept line base ->
    rim on the combined cloud C. Returns (vt (6, K), costs (K,)).
    tri_select (default TRI_SELECT, ticket 03) hands the three hypotheses to
    joint.select_joint_lines instead: this function's own ranking is then one of
    the three, so the merge calls back here with tri_select=False. The switch off
    runs the body below unchanged.
    """
    if tri_select is None:
        tri_select = TRI_SELECT
    if tri_select:
        from .joint import select_joint_lines

        return select_joint_lines(
            reps, sizes, C0, C1, C, max_candidates,
            line_rule=LINE_RULE if line_rule is None else line_rule,
            base_orient=BASE_ORIENT if base_orient is None else base_orient)
    if line_rule is None:
        line_rule = LINE_RULE
    if base_orient is None:
        base_orient = BASE_ORIENT
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
    if base_orient:
        vt = orient_base_axis(vt, C)
    if verbose:
        print("[POTSAC-UNION-PROFILE] %d basins scored, line_rule=%s, kept %d, costs %s"
              % (len(lines) // 2, bool(line_rule), vt.shape[1], [round(x, 4) for x in c]))
    return vt, c
