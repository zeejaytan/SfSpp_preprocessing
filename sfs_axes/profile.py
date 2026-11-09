"""Profile-thickness axis objective (ticket 322).

About the true axis of a surface of revolution every point of a wall maps, in the
(r, z) plane (r = distance from the axis, z = position along it), onto one curve: the
vessel's profile. That holds for every shape a sherd can come from -- cylinder, cone,
shallow dish, globular body, base -- so it needs no shape class and no size prior.

The cost of an axis on one wall is how far that (r, z) cloud is from being a curve:
for every point, the smallest principal standard deviation of its k nearest
neighbours in the (r, z) plane, averaged over the best `keep` fraction of points
(the trim drops what is not revolved: handle roots, chips, segmentation spill).
A piece's cost is the mean over its two walls. The cost is in the piece's own
millimetres and is only ever compared between axes of the same piece, so no
distance constant enters the ranking.

Measured (ticket 322, 172 pieces): refined from the reference axis, this cost moves
a median 1.5 deg (>10 deg on 9/163 pot pieces), where the distance-invariant normal
cost moves 6.4 deg (>10 deg on 70/163).

Not called by run_potsac or run_potsac_union: no shipped path ranks by this cost.
"""

import numpy as np
from scipy.optimize import minimize
from scipy.spatial import cKDTree

PROFILE_K = 24
PROFILE_KEEP = 0.8
PROFILE_POINTS = 2500


def stride(X, n=PROFILE_POINTS):
    """Deterministic stride of a (6, m) cloud down to at most n points."""
    return X[:, 0:X.shape[1]:max(1, int(np.ceil(X.shape[1] / n)))]


def wall_thickness(vt, X, k=PROFILE_K, keep=PROFILE_KEEP):
    """Trimmed mean local thickness (mm) of wall X's (r, z) profile about axis vt."""
    a = vt[0:3] / np.linalg.norm(vt[0:3])
    p0 = vt[3:6] - (vt[3:6] @ a) * a
    dp = X[0:3] - p0[:, None]
    z = a @ dp
    r = np.linalg.norm(dp - np.outer(a, z), axis=0)
    Q = np.c_[r, z]
    k = min(k, Q.shape[0])
    _, idx = cKDTree(Q).query(Q, k=k)
    nb = Q[idx] - Q[idx].mean(1, keepdims=True)
    lam = np.linalg.eigvalsh(np.einsum("nki,nkj->nij", nb, nb) / k)[:, 0]
    t = np.sort(np.sqrt(np.maximum(lam, 0.0)))
    return float(t[: max(1, int(keep * len(t)))].mean())


def profile_cost(vt, walls):
    """Mean wall thickness over the piece's walls (list of (6, m) arrays)."""
    return float(np.mean([wall_thickness(vt, X) for X in walls]))


def refine_axis_profile(vt, walls, centre, size, maxfev=400):
    """Nelder-Mead on profile_cost over the line's 4 degrees of freedom.

    Parametrised about the start: two tilts of the direction and two shifts of the
    foot point nearest `centre`, the shifts in units of 0.1 * size (the piece's own
    bounding-box diagonal), so the simplex is the same shape on any object.
    """
    a = vt[0:3] / np.linalg.norm(vt[0:3])
    e1 = np.cross(a, [1.0, 0, 0] if abs(a[0]) < 0.9 else [0, 1.0, 0])
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(a, e1)
    foot = vt[3:6] + ((centre - vt[3:6]) @ a) * a
    step = 0.1 * size

    def line(x):
        d = a + x[0] * e1 + x[1] * e2
        d /= np.linalg.norm(d)
        p = foot + step * (x[2] * e1 + x[3] * e2)
        return np.r_[d, p - (p @ d) * d]

    res = minimize(lambda x: profile_cost(line(x), walls), np.zeros(4), method="Nelder-Mead",
                   options=dict(xatol=1e-4, fatol=1e-5, maxfev=maxfev,
                                initial_simplex=np.vstack([np.zeros(4), 0.08 * np.eye(4)])))
    return line(res.x), float(res.fun)
