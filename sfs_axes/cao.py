"""Cao / biaxial-Cao errors — port of compute_cao_error.m,
compute_biaxial_cao_error.m (repmat-fix revision, working tree).

Conventions: X (6, n) [points; normals], vt (6,) [direction; position].
"""

import numpy as np

from .plucker import cross2mat, tmult


def compute_cao_error(vt, X, reversed=False, with_jacobian=False):
    """Cao-Mumford error. Port of compute_cao_error.m (repmat-fix revision).

    Returns R (3, n); with Jacobian also J (3, 6, n).
    """
    vt = np.asarray(vt, dtype=float).reshape(6)
    X = np.asarray(X, dtype=float)
    if reversed:
        X = X.copy()
        X[3:6, :] = -X[3:6, :]
    v = vt[0:3]
    p = vt[3:6]
    n = X.shape[1]
    with np.errstate(divide="ignore", invalid="ignore"):
        T1 = X[0:3, :] - p[:, None]
        v_rep = np.repeat(v[:, None], n, axis=1)
        T2 = np.cross(T1, v_rep, axis=0)
        T3 = np.cross(X[3:6, :], v_rep, axis=0)
        nT2 = np.sqrt(np.sum(T2 ** 2, axis=0))
        nT3 = np.sqrt(np.sum(T3 ** 2, axis=0))
        ratio = np.sqrt(np.sum(T2 ** 2, axis=0) / np.sum(T3 ** 2, axis=0))
        R = T2 - ratio * T3
        if not with_jacobian:
            return R
        cross_T1 = cross2mat(T1)
        cross_vhat = cross2mat(v_rep)
        cross_nhat = cross2mat(X[3:6, :])
        T4 = (T2 / nT2).reshape(3, 1, n)
        T5 = (T3 / nT3).reshape(3, 1, n)
        r3 = ratio.reshape(1, 1, n)
        J = np.empty((3, 6, n))
        J[:, 0:3, :] = (cross_T1 - tmult(T5, tmult(T4, cross_T1, True))
                        - cross_nhat * r3
                        + tmult(T5, tmult(T5, cross_nhat, True)) * r3)
        J[:, 3:6, :] = cross_vhat - tmult(T5, tmult(T4, cross_vhat, True))
        P = np.eye(3) - np.outer(v, v)
        J[:, 0:3, :] = (tmult(J[:, 0:3, :], P)
                        - tmult(tmult(J[:, 3:6, :], v.reshape(3, 1)),
                                p.reshape(1, 3)))
        return R, J


def compute_biaxial_cao_error(vt, X, with_jacobian=False):
    """Biaxial (normal-sign-agnostic) Cao error. Port of compute_biaxial_cao_error.m.

    Single-output MATLAB behaviour returns a scalar (log-sum-exp of the two
    whole-cloud costs, s = 100). Returns R (scalar); with Jacobian also
    J (1, 6, n).
    """
    s = 100.0
    if not with_jacobian:
        fwd = compute_cao_error(vt, X)
        rev = compute_cao_error(vt, X, reversed=True)
        cost_fwd = float(np.sum(fwd ** 2))
        cost_rev = float(np.sum(rev ** 2))
        c = min(cost_fwd, cost_rev)
        return (-1.0 / s * np.log(np.exp(s * -(cost_fwd - c))
                                + np.exp(s * -(cost_rev - c))) + c)
    R_fwd, J_fwd = compute_cao_error(vt, X, with_jacobian=True)
    R_rev, J_rev = compute_cao_error(vt, X, reversed=True, with_jacobian=True)
    cost_fwd = float(np.sum(R_fwd ** 2))
    cost_rev = float(np.sum(R_rev ** 2))
    c = min(cost_fwd, cost_rev)
    base_fwd = np.exp(s * -(cost_fwd - c))
    base_rev = np.exp(s * -(cost_rev - c))
    base = base_fwd + base_rev
    R = -1.0 / s * np.log(base) + c
    g_fwd = tmult(J_fwd, R_fwd.reshape(R_fwd.shape[0], 1, R_fwd.shape[1]), True)[:, 0, :]
    g_rev = tmult(J_rev, R_rev.reshape(R_rev.shape[0], 1, R_rev.shape[1]), True)[:, 0, :]
    J = 2 * (g_fwd * (base_fwd / base) + g_rev * (base_rev / base))
    return R, J[None, :, :]
