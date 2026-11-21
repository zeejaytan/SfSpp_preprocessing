"""Scale-free meridional objectives and refiners (ticket 03, from Ticket 02/06).

Two residuals are defined on a line (direction a, foot p0) and a wall cloud
X = [points (3, N); normals (3, N)]:

  e_hat_i = (p_i - p0) . (n_i x a) / ||(p_i - p0) x a||      normalized.py

e_hat is bounded by 1, but its magnitude is multiplied by ||n_i x a|| = sin(angle
between n and a), so tilting a toward the mean sherd normal shrinks it without
reducing the azimuthal error (ticket 01).  The shipped refine_axis_normalized
passes robustifier_huber with its default width = 1.0; with |e_hat| <= 1 every
point is an inlier, so its "robust" step is plain L2.  normal_cost and
refine_axis_normal here pass the width explicitly (NORMAL_WIDTH), which is what
calibrates the kernel and what Ticket 06 measured.

The profile cost keeps the (r, z) meridional straightening of profile.py but makes
the neighbour distance a Hermite thickness: the distance from a neighbour to the
tangent plane spanned by the point's own meridional normal m_hat_i, where
m_i = (n_i . r_hat_i, n_i . a).  profile.py uses blind PCA on the (r, z)
neighbourhood, which is minimised by sliding the axis so that points from opposite
walls collapse: the Hermite plane is normal to the surface and cannot be flattened
by that move.

Every constant here is either dimensionless or expressed in the piece's own
geometry (bounding-box diagonal, median radius), so the same numbers apply to a
33 mm juglet and a 300 mm vessel.  Nothing reads a reference axis or a GT pose.
"""

import numpy as np
from scipy.optimize import minimize
from scipy.spatial import cKDTree

from .profile import PROFILE_K, PROFILE_KEEP, stride
from .refine import cao_update_func, optimize_using_lm
from .robust import robustifier_huber

# Huber width on the normalised residual, i.e. sin(azimuthal departure).  The
# residual is dimensionless, so this is not a per-object number: 0.05 admits
# departures up to 0.05 (2.9 deg of azimuthal error) as inliers.
NORMAL_WIDTH = 0.05
# Floor on ||meridional normal|| (dimensionless), the pole where r_hat is undefined.
MERIDIAN_EPS_N = 0.1


def unit_line(vt):
    """(unit direction, foot point projected off the direction) from a 6-vector."""
    vt = np.asarray(vt, dtype=float).reshape(6)
    a = vt[0:3]
    na = np.linalg.norm(a)
    a = a / na if na > 1e-12 else np.array([0.0, 0.0, 1.0])
    p0 = vt[3:6] - float(vt[3:6] @ a) * a
    return a, p0


def finish_line(vt):
    """Re-unit the direction and project the foot perpendicular to it."""
    vt = np.asarray(vt, dtype=float).reshape(6).copy()
    n = np.linalg.norm(vt[0:3])
    vt[0:3] = vt[0:3] / n if n > 1e-12 else np.array([0.0, 0.0, 1.0])
    vt[3:6] = vt[3:6] - float(vt[3:6] @ vt[0:3]) * vt[0:3]
    return vt


def _frame(vt, X):
    """Unit direction, foot, radial displacement, axial coordinate and radius."""
    a, p0 = unit_line(vt)
    dp = X[0:3, :] - p0[:, None]
    z = a @ dp
    rad = dp - a[:, None] * z[None, :]
    r = np.sqrt(np.sum(rad ** 2, axis=0))
    return a, p0, dp, z, rad, r


def normal_cost(vt, X, width=NORMAL_WIDTH):
    """Mean robustified normalised azimuthal residual of one wall (dimensionless)."""
    from .normalized import compute_normalized_residual

    e_hat = compute_normalized_residual(vt, X, with_jacobian=False)[0, :]
    return float(np.mean(robustifier_huber(e_hat ** 2, width)[0, :]))


def refine_axis_normal(vt, X, width=NORMAL_WIDTH, max_iters=60, tolerance=1e-6):
    """LM on e_hat with the Huber width calibrated in the residual's own units."""
    from .normalized import compute_normalized_residual

    def res_func(v):
        return compute_normalized_residual(v, X, with_jacobian=True)

    def rob(s):
        return robustifier_huber(s, width)

    try:
        out, _err, _log = optimize_using_lm(
            np.asarray(vt, dtype=float).reshape(6), res_func, cao_update_func, rob,
            max_iters=max_iters, func_tol=tolerance)
    except Exception:
        return finish_line(vt)
    return finish_line(out)


def meridional_normals(vt, X):
    """Unit meridional normal m_hat_i (2, N) and the (r, z) coordinates (2, N).

    m_i = (n_i . r_hat_i, n_i . a); the floor guards the pole where r_hat is
    undefined.  A base point has m ~ (0, +-1) (normal along the axis) and a wall
    point m ~ (+-1, 0); both are handled by the same normalisation.
    """
    a, _p0, _dp, z, rad, r = _frame(vt, X)
    rs = np.maximum(r, 1e-12)
    r_hat = rad / rs[None, :]
    N = np.asarray(X, dtype=float)[3:6, :]
    m = np.vstack([np.sum(N * r_hat, axis=0), a @ N])          # (2, N)
    nm = np.sqrt(np.sum(m ** 2, axis=0))
    m_hat = m / np.maximum(nm, MERIDIAN_EPS_N)
    return m_hat, np.vstack([r, z]), nm


def hermite_thickness(vt, X, k=PROFILE_K, keep=None, normal_consistent=False,
                      min_normal_agreement=0.5):
    """Hermite thickness (mm) of one wall about the line vt.

    For point i the k nearest neighbours j in (r, z); the thickness contribution is
    |(q_j - q_i) . m_hat_i|, the distance from the neighbour to the tangent plane
    normal to the point's own meridional normal.

    profile.py instead takes the smallest eigenvalue of the neighbourhood's (r, z)
    covariance -- the minimum over every direction, not along the surface normal --
    and averages only the best keep fraction of the points.  A decoy can buy both
    allowances: crowding near a displaced axis makes a minority of points
    arbitrarily thin, and a best-fraction mean then reports the crowd.  The median
    of the prescribed normal's projection cannot be bought that way, so keep=None
    is the default; keep=<fraction> reproduces the trimmed habit for comparison.

    normal_consistent weights each contribution by (1 - |m_hat_i . m_hat_j|)
    floored at min_normal_agreement, charging neighbours whose meridional normals
    disagree (two walls collapsing onto one another).
    """
    m_hat, Q, _nm = meridional_normals(vt, X)
    n = Q.shape[1]
    k = int(min(k, n))
    if k < 3:
        return float("nan")
    _dist, idx = cKDTree(Q.T).query(Q.T, k=k)   # rows are samples for the tree
    if idx.ndim == 1:
        idx = idx[:, None]
    d = Q[:, idx] - Q[:, :, None]                     # (2, n, k)
    t = np.abs(np.einsum("in,ink->nk", m_hat, d))     # (n, k)
    if normal_consistent:
        mj = m_hat[:, idx.ravel()].reshape(2, n, k)
        dis = 1.0 - np.abs(np.einsum("in,ink->nk", m_hat, mj))   # 0 agrees, 1 flips
        t = t * (1.0 + dis)
    per_point = np.mean(t, axis=1)
    if keep is None:
        return float(np.median(per_point))
    per_point = np.sort(per_point)
    return float(per_point[: max(1, int(keep * per_point.size))].mean())


def profile_thickness_cost(vt, walls, k=PROFILE_K, keep=None,
                           normal_consistent=False):
    """Mean Hermite thickness over the piece's walls (mm), NaN as absent, not as 0."""
    vals = [hermite_thickness(vt, X, k=k, keep=keep,
                              normal_consistent=normal_consistent)
            for X in walls]
    return float(np.nanmean(vals))


def _parametrisation(vt, centre, size):
    """Two tilts and two foot shifts about the start (profile.py's parametrisation)."""
    a, foot = unit_line(vt)
    foot = foot + ((centre - foot) @ a) * a
    e1 = np.cross(a, [1.0, 0, 0] if abs(a[0]) < 0.9 else [0, 1.0, 0])
    e1 = e1 / np.linalg.norm(e1)
    e2 = np.cross(a, e1)
    step = 0.1 * size

    def line(x):
        d = a + x[0] * e1 + x[1] * e2
        d = d / np.linalg.norm(d)
        p = foot + step * (x[2] * e1 + x[3] * e2)
        return np.r_[d, p - float(p @ d) * d]

    return line


def refine_axis_profile_thickness(vt, walls, centre, size, normal_consistent=False,
                                  k=PROFILE_K, keep=PROFILE_KEEP, maxfev=400):
    """4-DoF Nelder-Mead on the Hermite (or normal-consistent) thickness cost.

    The simplex is the same shape on any object: tilts are unit-vector steps and
    shifts are in units of 0.1 * the piece's bounding-box diagonal.
    """
    line = _parametrisation(vt, centre, size)
    res = minimize(
        lambda x: profile_thickness_cost(line(x), walls, k=k, keep=keep,
                                        normal_consistent=normal_consistent),
        np.zeros(4), method="Nelder-Mead",
        options=dict(xatol=1e-4, fatol=1e-5, maxfev=maxfev,
                     initial_simplex=np.vstack([np.zeros(4), 0.08 * np.eye(4)])))
    return finish_line(line(res.x)), float(res.fun)


def piece_scale(C):
    """The piece's own length scale: bounding-box diagonal (mm)."""
    C = np.asarray(C, dtype=float)
    return float(np.linalg.norm(C[0:3].max(axis=1) - C[0:3].min(axis=1)))


def _at_piece(v, c):
    """The point of the line closest to c."""
    p = np.asarray(v[3:6], dtype=float)
    d = np.asarray(v[0:3], dtype=float)
    d = d / max(float(np.linalg.norm(d)), 1e-12)
    w = np.asarray(c, dtype=float) - p
    return p + float(w @ d) * d


def line_shift(v1, v2, C):
    """How far a line moved, measured at the piece (mm).

    The feet of a pot's axis are far from the sherd, so a small rotation moves a
    foot a long way; what matters is the movement where the material is.  This is
    the distance between the two lines' closest points to the cloud centroid.
    """
    c = np.asarray(C, dtype=float)[0:3].mean(axis=1)
    return float(np.linalg.norm(_at_piece(v1, c) - _at_piece(v2, c)))
