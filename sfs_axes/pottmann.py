"""Pottmann 6-point axis solver — port of compute_pottmann_axis.m."""

import numpy as np

from .plucker import euc2plucker


def compute_pottmann_axis(X):
    """Symmetric axis from 6-D [point; normal] samples. Port of compute_pottmann_axis.m.

    X: (6, N). Returns vt (6,) = [direction; moment]: unit direction v and
    position part cross(v, vbar) (MATLAB convention [dir; pos]).
    """
    X = np.asarray(X, dtype=float)
    J = euc2plucker(X[np.r_[3:6, 0:3], :])
    J = J[np.r_[3:6, 0:3], :].T  # (N, 6)
    JTJ = J.T @ J
    M11 = JTJ[0:3, 0:3]
    M12 = JTJ[0:3, 3:6]
    M22 = JTJ[3:6, 3:6]
    try:  # MATLAB \ on the square M22: LU solve; lstsq only as singular fallback
        Minv_M12t = np.linalg.solve(M22, M12.T)
    except np.linalg.LinAlgError:
        Minv_M12t = np.linalg.lstsq(M22, M12.T, rcond=None)[0]
    M = M11 - M12 @ Minv_M12t
    _U, s, Vt = np.linalg.svd(M)
    v = Vt[-1, :]  # np singular values descend: last row = smallest (MATLAB ia(1))
    try:
        vbar = np.linalg.solve(M22, -(M12.T @ v))
    except np.linalg.LinAlgError:
        vbar, *_ = np.linalg.lstsq(M22, -(M12.T @ v), rcond=None)
    return np.concatenate([v, np.cross(v, vbar)])
