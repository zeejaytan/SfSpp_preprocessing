#!/usr/bin/env python3
"""Six axis residuals for ticket 71, and a 4-degree-of-freedom minimiser.

X is (6, n): rows 0-2 points (mm), rows 3-5 normals.
vt is (6,): rows 0-2 a unit direction, rows 3-5 a point on the axis (mm),
with the point kept perpendicular to the direction.

The formulas are the ticket's, written out against the same T1, T2, T3 as
compute_cao_error.m / sfs_axes/cao.py:

    T1 = x - p
    T2 = T1 x v
    T3 = n x v

    cao_shipped   T2 - sqrt(sum |T2|^2 / sum |T3|^2) * T3     one scale, whole cloud
    cao_perpoint  T2 - (|T2| / |T3|) * T3                     positive scale, per point
    proj_signed   T2 - ((T2 . T3) / |T3|^2) * T3              signed scale, per point
    cross         T2 x T3                                     the parallel-or-antiparallel test
    triple        T1 . T3                                     scalar, one per point
    sin_normal    n . v                                       direction only

A point whose normal is degenerate, or whose T3 vanishes, contributes nothing:
the axis-normal cross product carries no radius there.

The minimiser is Levenberg-Marquardt in the tangent space of the axis
(two direction coordinates, two position coordinates). Nothing here reads
or writes SFS_AXES_COST; the shipped Cao function is untouched.
"""
import numpy as np

COSTS = ("cao_shipped", "cao_perpoint", "proj_signed", "cross", "triple", "sin_normal")

# A neighbour this far below the cost counts as "not a minimum". Absolute
# noise on an exact zero residual sits well under this.
_LOWER = 1e-8


def canonicalize(vt):
    vt = np.asarray(vt, dtype=float).reshape(6).copy()
    n = np.linalg.norm(vt[0:3])
    if n == 0.0:
        vt[0:3] = np.array([0.0, 0.0, 1.0])
    else:
        vt[0:3] /= n
    vt[3:6] -= vt[0:3] * float(vt[0:3] @ vt[3:6])
    return vt


def tangent_basis(v):
    """Two unit vectors spanning the plane perpendicular to v."""
    v = np.asarray(v, dtype=float).reshape(3)
    i = int(np.argmin(np.abs(v)))
    a = np.zeros(3)
    a[i] = 1.0
    e1 = np.cross(v, a)
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(v, e1)
    return e1, e2


def retract(vt, delta):
    """Step (d1, d2, p1, p2) in the current tangent basis, then re-orthonormalise."""
    vt = canonicalize(vt)
    d = np.asarray(delta, dtype=float).reshape(4)
    e1, e2 = tangent_basis(vt[0:3])
    v = vt[0:3] + d[0] * e1 + d[1] * e2
    n = np.linalg.norm(v)
    v = vt[0:3] if n == 0.0 else v / n
    p = vt[3:6] + d[2] * e1 + d[3] * e2
    p = p - v * float(v @ p)
    return np.concatenate([v, p])


def perturb(vt, deg, mm):
    """Exact tilt of `deg` about one perpendicular, plus `mm` along the other.

    The offset stays perpendicular to the tilted direction, so the radial
    error against the original axis is `mm` when `deg` is 0, and the
    direction error is exactly `deg`.
    """
    vt = canonicalize(vt)
    e1, e2 = tangent_basis(vt[0:3])
    th = np.radians(deg)
    v = np.cos(th) * vt[0:3] + np.sin(th) * e1
    v /= np.linalg.norm(v)
    p = vt[3:6] + float(mm) * e2
    p = p - v * float(v @ p)
    return np.concatenate([v, p])


def _frames(vt, X):
    vt = canonicalize(vt)
    v = vt[0:3]
    p = vt[3:6]
    pts = np.asarray(X[0:3], dtype=float)
    raw = np.asarray(X[3:6], dtype=float)
    ln = np.linalg.norm(raw, axis=0)
    nrm = np.zeros_like(raw)
    ok = ln > 1e-12
    nrm[:, ok] = raw[:, ok] / ln[ok]
    T1 = pts - p[:, None]
    vv = np.repeat(v[:, None], pts.shape[1], axis=1)
    T2 = np.cross(T1, vv, axis=0)
    T3 = np.cross(nrm, vv, axis=0)
    bad = (~ok) | (np.sum(T3 * T3, axis=0) < 1e-20)
    return v, nrm, T1, T2, T3, bad


def _kill_columns(R, bad):
    if np.any(bad):
        R = R.copy()
        R[:, bad] = 0.0
    return R


def residual_matrix(name, vt, X):
    """Residual as a 1-D or 2-D array, before ravel. Shape depends on the cost."""
    v, nrm, T1, T2, T3, bad = _frames(vt, X)
    if name == "cao_shipped":
        s2 = float(np.sum(T2 * T2))
        s3 = float(np.sum(T3 * T3))
        ratio = np.sqrt(s2 / s3) if s3 > 1e-18 else 0.0
        return _kill_columns(T2 - ratio * T3, bad)
    if name == "cao_perpoint":
        n2 = np.sqrt(np.sum(T2 * T2, axis=0))
        n3 = np.sqrt(np.sum(T3 * T3, axis=0))
        ratio = np.divide(n2, n3, out=np.zeros_like(n2), where=n3 > 1e-12)
        return _kill_columns(T2 - ratio * T3, bad)
    if name == "proj_signed":
        n3sq = np.sum(T3 * T3, axis=0)
        dot = np.sum(T2 * T3, axis=0)
        scale = np.divide(dot, n3sq, out=np.zeros_like(dot), where=n3sq > 1e-18)
        return _kill_columns(T2 - scale * T3, bad)
    if name == "cross":
        return _kill_columns(np.cross(T2, T3, axis=0), bad)
    if name == "triple":
        r = np.sum(T1 * T3, axis=0)
        if np.any(bad):
            r = r.copy()
            r[bad] = 0.0
        return r
    if name == "sin_normal":
        r = nrm.T @ v
        if np.any(bad):
            r = r.copy()
            r[bad] = 0.0
        return r
    raise ValueError("unknown cost %r" % (name,))


def residual(name, vt, X):
    return np.ravel(residual_matrix(name, vt, X))


def cost_value(name, vt, X):
    r = residual(name, vt, X)
    if not np.all(np.isfinite(r)):
        return float("inf")
    return float(r @ r)


def _fd_jacobian(name, vt, X, r):
    J = np.empty((r.size, 4))
    steps = (1e-6, 1e-6, 1e-4, 1e-4)
    for k, eps in enumerate(steps):
        d = np.zeros(4)
        d[k] = eps
        rp = residual(name, retract(vt, d), X)
        J[:, k] = (rp - r) / eps
    return J


def minimize_cost(name, vt0, X, max_iters=60):
    """Levenberg-Marquardt. Returns (vt, sum_of_squares, iterations, capped).

    `capped` is 1 when the iteration budget ran out with the cost still falling.
    """
    vt = canonicalize(vt0)
    r = residual(name, vt, X)
    cost = float(r @ r) if np.all(np.isfinite(r)) else float("inf")
    if cost <= 1e-22:
        return vt, cost, 0, 0
    lam = 1e-2
    it_done = 0
    capped = 1
    for it in range(1, max_iters + 1):
        it_done = it
        J = _fd_jacobian(name, vt, X, r)
        A = J.T @ J
        g = J.T @ r
        scale = np.maximum(np.diag(A), 1e-18)
        accepted = False
        delta = np.zeros(4)
        for _trial in range(12):
            try:
                delta = -np.linalg.solve(A + lam * np.diag(scale), g)
            except np.linalg.LinAlgError:
                delta, *_ = np.linalg.lstsq(A + lam * np.diag(scale), -g, rcond=None)
            if not np.all(np.isfinite(delta)) or np.linalg.norm(delta) > 1e6:
                lam = min(lam * 10.0, 1e12)
                continue
            vt_new = retract(vt, delta)
            r_new = residual(name, vt_new, X)
            if not np.all(np.isfinite(r_new)):
                lam = min(lam * 10.0, 1e12)
                continue
            cost_new = float(r_new @ r_new)
            dropped = cost - cost_new
            step = float(np.linalg.norm(delta))
            # A step that does not actually lower the cost is not progress.
            # Accepting ties lets a flat direction (sin_normal's position)
            # walk off along numerical noise.
            if dropped > max(1e-16, 1e-12 * max(cost, 1.0)):
                vt, r, cost = vt_new, r_new, cost_new
                lam = max(lam / 3.0, 1e-14)
                accepted = True
                break
            if step < 1e-10:
                break
            lam = min(lam * 8.0, 1e12)
        if not accepted:
            capped = 0
            break
        if cost <= 1e-22 or np.linalg.norm(delta) < 1e-12:
            capped = 0
            break
        if it == max_iters:
            capped = 1
    return vt, cost, it_done, capped


def lower_neighbor(name, vt, X, deg=0.5, mm=0.5):
    """True when a 0.5 deg / 0.5 mm neighbour has a strictly lower cost.

    Eight neighbours: plus and minus each of the four tangent coordinates.
    A flat direction (sin_normal's position) is not counted as lower.
    """
    base = cost_value(name, vt, X)
    vt = canonicalize(vt)
    e1, e2 = tangent_basis(vt[0:3])
    th = np.radians(deg)
    shifts = []
    for sgn in (1.0, -1.0):
        v = np.cos(th) * vt[0:3] + sgn * np.sin(th) * e1
        v = v / np.linalg.norm(v)
        shifts.append(np.concatenate([v, vt[3:6] - v * float(v @ vt[3:6])]))
        v = np.cos(th) * vt[0:3] + sgn * np.sin(th) * e2
        v = v / np.linalg.norm(v)
        shifts.append(np.concatenate([v, vt[3:6] - v * float(v @ vt[3:6])]))
        p = vt[3:6] + sgn * mm * e1
        shifts.append(np.concatenate([vt[0:3], p - vt[0:3] * float(vt[0:3] @ p)]))
        p = vt[3:6] + sgn * mm * e2
        shifts.append(np.concatenate([vt[0:3], p - vt[0:3] * float(vt[0:3] @ p)]))
    for s in shifts:
        c = cost_value(name, s, X)
        if c < base - _LOWER:
            return True, base, c
    return False, base, base
