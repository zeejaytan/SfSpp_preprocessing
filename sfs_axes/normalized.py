"""Distance-invariant (radial-distance-normalized) axis error, refinement, and ranking.

Addresses Cao/Mumford lever-arm bias (ticket 312): unnormalized error e_i = (p_i - p_0) . (n_i x a)
mechanically favors false axes slicing through sherd centroids because ||p_i - p_0|| collapses by
50-75%, dropping unnormalized costs up to 7x.

Normalized formulation:
  e_hat_i = ((p_i - p_0) . (n_i x a)) / ||(p_i - p_0) x a||
measures the pure azimuthal normal departure sin(phi_i) independent of distance to the axis.
"""

import numpy as np
from scipy.optimize import least_squares

from .cao import compute_biaxial_cao_error
from .refine import cao_update_func, optimize_using_lm
from .robust import apply_robustifier, robustifier_huber

# Ticket 325: scale-free gate constants. Every threshold below is a ratio of two
# lengths measured on the SAME piece, so the gates ask the same question on a
# 33 mm juglet and a 300 mm pot. They replace the 2026 mm-calibrated constants
# (25/35/110/115/120/200/250 mm) that made the axis gates size branches.
#
# CLEARANCE_FLOOR_FRAC: material clearance u_clr = r_q01 / r_mean, where r_q01
#   is the 1st-percentile point-to-line radial distance and r_mean the mean.
#   A true wall axis never comes closer to the pottery than its own profile
#   allows. Calibrated on the corpus (ticket 325 measurement run
#   20261110-1416_22151d0_t325-measure): trusted wall axes bottom out at
#   u_clr = 0.077 (Pot J 18, released), so 0.05 admits every wall with a
#   1.55x margin while dense-cloud slicing lines measure 0.001-0.02. Unlike
#   a d_c (centroid-distance) floor this admits hollow-centered axes at any
#   wrap angle.
# RADIUS_CEILING_FRAC: implied radius v = r_mean / D (D = piece bbox diagonal).
#   A wall band's mean radius cannot exceed the piece's own diagonal by much;
#   far decoys (line hundreds of mm off) reach v >= 3.6 on synthetic tests.
CLEARANCE_FLOOR_FRAC = 0.05
RADIUS_CEILING_FRAC = 2.5


def line_radial_gates(vt, X):
    """Scale-free per-candidate geometry: u_clr, v, u1, z_frac.

    u_clr   r_q01 / r_mean   material clearance (floor test)
    v       r_mean / D       implied radius vs piece size (ceiling test)
    u1      d_c / r_mean     wall standoff ratio (prior input)
    z_frac  axial extent of ALL points / D (flatness test; thin wall sheets
            measured along a perpendicular axis fall under ~0.02, true base
            depth sits near 0.15)
    """
    vt = np.asarray(vt, dtype=float).reshape(6)
    a = vt[0:3] / np.linalg.norm(vt[0:3])
    p0 = vt[3:6] - (vt[3:6] @ a) * a
    P = X[0:3, :]
    dp = P - p0[:, None]
    z = a @ dp
    r_vec = dp - a[:, None] * z[None, :]
    r = np.linalg.norm(r_vec, axis=0)
    r_q01 = float(np.percentile(r, 1))
    r_mean = float(r.mean())
    D = float(np.linalg.norm(P.max(axis=1) - P.min(axis=1)))
    d_c = centroid_distance(vt, X)
    u_clr = r_q01 / r_mean if r_mean > 0 else np.inf
    return dict(u_clr=u_clr, v=(r_mean / D if D > 0 else np.inf), u1=(d_c / r_mean if r_mean > 0 else np.inf),
                z_frac=(float(z.max() - z.min()) / D if D > 0 else np.inf), r_mean=r_mean, d_c=d_c, D=D)


def compute_normalized_residual(vt, X, with_jacobian=False, eps=1e-6):
    """Compute radial-distance-normalized normal alignment residual e_hat_i.

    Parameters
    ----------
    vt : array-like of shape (6,)
        [direction (3); position (3)] of candidate axis.
    X : array-like of shape (6, N)
        [points (3, N); normals (3, N)].
    with_jacobian : bool
        If True, also return Jacobian of shape (1, 6, N).
    eps : float
        Numerical safety floor for radial distance.

    Returns
    -------
    err : ndarray of shape (1, N)
        Per-point normalized error e_hat_i.
    J : ndarray of shape (1, 6, N), optional
        Jacobian with respect to [a; p_0].
    """
    vt = np.asarray(vt, dtype=float).reshape(6)
    X = np.asarray(X, dtype=float)

    a = vt[0:3]
    norm_a = np.linalg.norm(a)
    if norm_a < 1e-12:
        a = np.array([0.0, 0.0, 1.0])
    else:
        a = a / norm_a

    p0 = vt[3:6] - (vt[3:6] @ a) * a

    P = X[0:3, :]  # (3, N)
    N = X[3:6, :]  # (3, N)
    num_pts = P.shape[1]

    dp = P - p0[:, None]  # (3, N)
    z = a @ dp  # (N,)
    r_vec = dp - a[:, None] * z[None, :]  # (3, N)
    r = np.sqrt(np.sum(r_vec ** 2, axis=0))  # (N,)
    r_safe = np.maximum(r, eps)  # (N,)
    r_hat = r_vec / r_safe[None, :]  # (3, N)

    n_cross_a = np.cross(N, a[:, None], axis=0)  # (3, N)
    w = np.sum(dp * n_cross_a, axis=0)  # (N,)
    e_hat = w / r_safe  # (N,)

    err = e_hat.reshape(1, num_pts)
    if not with_jacobian:
        return err

    # Analytical Jacobian:
    # d_p0 = - (n x a) / r + (e_hat / r) * r_hat
    d_p0 = (-n_cross_a / r_safe[None, :]
            + (e_hat / r_safe)[None, :] * r_hat)  # (3, N)

    # d_a (projected on tangent space of unit sphere P = I - a a^T):
    dp_cross_n = np.cross(dp, N, axis=0)  # (3, N)
    P_mat = np.eye(3) - np.outer(a, a)
    d_a_unproj = (dp_cross_n / r_safe[None, :]
                  + ((e_hat * z) / r_safe)[None, :] * r_hat)  # (3, N)
    d_a = P_mat @ d_a_unproj  # (3, N)

    # Shape: (1, 6, N) matching optimize_using_lm conventions
    J = np.empty((1, 6, num_pts), dtype=float)
    J[0, 0:3, :] = d_a
    J[0, 3:6, :] = d_p0
    return err, J


def compute_biaxial_normalized_error(vt, X, with_jacobian=False, s=100.0):
    """Sign-agnostic biaxial normalized error.

    Because e_hat_i(-n) = - e_hat_i(n), under any even loss function
    rho(e) = rho(-e), the forward and reverse errors are mathematically identical.
    Here we compute the softmin log-sum-exp over forward and reverse normal orientations
    to match the biaxial interface.
    """
    if not with_jacobian:
        err = compute_normalized_residual(vt, X, with_jacobian=False)  # (1, N)
        e2 = err[0, :] ** 2
        # softmin(e2, e2) = e2 - log(2)/s
        return e2 - np.log(2.0) / s

    err, J = compute_normalized_residual(vt, X, with_jacobian=True)  # (1, N), (1, 6, N)
    e2 = err[0, :] ** 2
    R = e2 - np.log(2.0) / s
    # Gradient of e2 wrt params: 2 * e * J
    J_biax = 2.0 * err[None, :, :] * J
    return R.reshape(1, -1), J_biax


def centroid_distance(vt, X):
    """Orthogonal distance from candidate axis line to sherd centroid C."""
    vt = np.asarray(vt, dtype=float).reshape(6)
    a = vt[0:3] / np.linalg.norm(vt[0:3])
    p0 = vt[3:6]
    C = np.mean(X[0:3, :], axis=1)
    return float(np.linalg.norm(np.cross(C - p0, a)))


def is_base_fragment(X, vt=None, r_base_frac=0.75, normal_axial_thresh=0.70):
    """Detect whether a piece is a base fragment containing the vessel bottom.

    Ticket 325: all tests are scale-free; no millimetre appears. A true base
    fragment containing the vessel rotation axis satisfies:
    1. Substantial points near the axis (r < r_base_frac * r_mean, the piece's
       own mean radius) with axial normals (|a . n| >= normal_axial_thresh).
       A line far from the piece fails here on count, which replaces the old
       d_c < 25 mm first test.
    2. Azimuthal span of near points delta_theta >= 160 degrees around the axis.
    3. Axial extent of ALL points >= 0.05 * D (D = piece bbox diagonal):
       a base carries real depth along the axis relative to the piece (large
       synthetic base disk 0.075, full-height base 0.17), while a thin wall
       sheet measured along a perpendicular axis carries under 2% of D
       (synthetic wall slice: 0.018). The depth often lives in the rim rise
       outside the near set, so the extent is taken over all points, exactly
       as the 15.0 mm test this replaces did.
    """
    if vt is None:
        return False
    a = vt[0:3] / np.linalg.norm(vt[0:3])
    p0 = vt[3:6] - (vt[3:6] @ a) * a
    P = X[0:3, :]
    N = X[3:6, :]
    dp = P - p0[:, None]
    z = a @ dp
    r_vec = dp - a[:, None] * z[None, :]
    r = np.linalg.norm(r_vec, axis=0)
    r_mean = float(r.mean())
    near = r < r_base_frac * r_mean
    if np.sum(near) < 80:
        return False
    axial_normals = np.abs(a @ N[:, near])
    if np.mean(axial_normals) < normal_axial_thresh:
        return False
    ref = np.array([1.0, 0.0, 0.0])
    if abs(np.dot(ref, a)) > 0.9:
        ref = np.array([0.0, 1.0, 0.0])
    u = ref - np.dot(ref, a) * a
    u /= np.linalg.norm(u)
    v = np.cross(a, u)
    r_near = r_vec[:, near]
    x_proj = u @ r_near
    y_proj = v @ r_near
    angles = np.sort(np.arctan2(y_proj, x_proj))
    gaps = np.diff(angles)
    wrap_gap = 2 * np.pi - (angles[-1] - angles[0])
    max_gap = np.max(np.append(gaps, wrap_gap))
    span_deg = 360.0 - np.degrees(max_gap)
    if span_deg < 160.0:
        return False
    D = float(np.linalg.norm(P.max(axis=1) - P.min(axis=1)))
    z_extent = float(np.max(z) - np.min(z))
    if z_extent < 0.05 * D:
        return False
    return True


def normalized_huber_cost(vt, X, width=1.0):
    """Normalized Huber cost per point on cloud X."""
    err = compute_normalized_residual(vt, X, with_jacobian=False)  # (1, N)
    rob = apply_robustifier(robustifier_huber, err[0, :], None)
    return float(np.mean(rob))


def worst_wall_normalized_cost(vt, C0, C1=None, width=1.0, min_clearance_frac=CLEARANCE_FLOOR_FRAC):
    """Worst-wall normalized Huber cost with scale-free clearance prior.

    E_hat_worst(a, p0) = max(E0, E1) + clearance_penalty.

    Ticket 325: the prior is ratio-based, so it bites identically at any object
    size. u_clr = r_q01 / r_mean < CLEARANCE_FLOOR_FRAC (line cutting into the
    material) draws 1000 * (floor - u_clr)^2 on non-base pieces; an implied
    radius v = r_mean / D above RADIUS_CEILING_FRAC (far decoy) draws
    10 * (v - ceiling)^2. min_clearance_frac=0.0 disables the floor penalty.
    """
    c0 = normalized_huber_cost(vt, C0, width=width)
    if C1 is None or C1.shape[1] == 0:
        cost = c0
        X_all = C0
    else:
        c1 = normalized_huber_cost(vt, C1, width=width)
        cost = max(c0, c1)
        X_all = np.concatenate([C0, C1], axis=1)

    gates = line_radial_gates(vt, X_all)
    base = is_base_fragment(X_all, vt)
    if min_clearance_frac > 0 and gates["u_clr"] < min_clearance_frac and not base:
        # Heavy penalty for slicing through the sherd body
        cost += 1000.0 * (min_clearance_frac - gates["u_clr"]) ** 2
    if gates["v"] > RADIUS_CEILING_FRAC and not base:
        # Penalize degenerate infinite-radius / planar decoys
        cost += 10.0 * (gates["v"] - RADIUS_CEILING_FRAC) ** 2
    return cost


def refine_axis_normalized(vt_initial, X, max_iters=300, tolerance=1e-9, verbose=False):
    """Refine axis under normalized residual using Levenberg-Marquardt."""
    vt = np.asarray(vt_initial, dtype=float).reshape(6)
    X = np.asarray(X, dtype=float)

    def res_func(v):
        return compute_normalized_residual(v, X, with_jacobian=True)

    try:
        vt_ref, _err, _log = optimize_using_lm(
            vt, res_func, cao_update_func, robustifier_huber,
            max_iters=max_iters, func_tol=tolerance, verbose=verbose)
        vt_ref[0:3] = vt_ref[0:3] / np.linalg.norm(vt_ref[0:3])
        vt_ref[3:6] = vt_ref[3:6] - vt_ref[0:3] * (vt_ref[0:3] @ vt_ref[3:6])
        return vt_ref
    except Exception as exc:
        if verbose:
            print("Warning: Normalized LM refinement failed: %s; trying least_squares" % exc)
        return refine_axis_least_squares(vt, X)


def refine_axis_least_squares(vt_initial, X, loss="huber", f_scale=0.1, max_nfev=300):
    """Robust manifold least-squares refinement fallback using scipy."""
    vt = np.asarray(vt_initial, dtype=float).reshape(6)
    a0 = vt[0:3] / np.linalg.norm(vt[0:3])
    p0 = vt[3:6] - (vt[3:6] @ a0) * a0

    def residual(params):
        v = params.copy()
        norm_v = np.linalg.norm(v[:3])
        if norm_v < 1e-12:
            return np.ones(X.shape[1]) * 1e3
        v[:3] /= norm_v
        v[3:6] -= (v[3:6] @ v[:3]) * v[:3]
        e = compute_normalized_residual(v, X, with_jacobian=False)[0, :]
        return e

    res = least_squares(residual, np.r_[a0, p0], loss=loss, f_scale=f_scale, max_nfev=max_nfev)
    v_opt = res.x.copy()
    v_opt[:3] /= np.linalg.norm(v_opt[:3])
    v_opt[3:6] -= (v_opt[3:6] @ v_opt[:3]) * v_opt[:3]
    return v_opt
