"""Robust kernels + Triggs correction — port of robustifier_*.m, apply_robustifier.m.

Each kernel maps squared residual norms s (N,) to Rho (3, N):
row 0 = rho, row 1 = rho', row 2 = rho''.

apply_robustifier is an exact-shape port: err (M, N) residual blocks,
Jt (D, M, N) transposed Jacobians. Note the MATLAB scaling subtlety
(lines 15/21/24): the Jacobian is scaled by sqrt(rho') = w1 while the
residual is scaled by rho'/D-like w = w1/D — NOT the same factor.
"""

import numpy as np

from .plucker import tmult


def robustifier_huber(s, width=1.0):
    """Port of robustifier_huber.m (default width 1.0)."""
    s = np.asarray(s, dtype=float).ravel()
    rho = np.zeros((3, s.size))
    rho[0, :] = s
    rho[1, :] = 1.0
    rho[2, :] = 0.0
    tau_sq = width * width
    out = s > tau_sq
    ss = s[out]
    sqrt_s = np.sqrt(ss)
    rho[0, out] = 2.0 * width * sqrt_s - tau_sq
    w = width / sqrt_s
    rho[1, out] = w
    rho[2, out] = -0.5 * (w / ss)
    return rho


def robustifier_gm(s, width=1.0):
    """Port of robustifier_gm.m (Geman-McClure, default width 1.0)."""
    s = np.asarray(s, dtype=float).ravel()
    tau_sq = width * width
    rho = np.empty((3, s.size))
    rho[2, :] = tau_sq / (s + tau_sq)
    rho[0, :] = 2 * s * rho[2, :]
    rho[1, :] = 2 * rho[2, :] ** 2
    rho[2, :] = -2 * rho[1, :] * rho[2, :] / tau_sq
    return rho


def robustifier_cauchy(s):
    """Port of robustifier_cauchy.m (width fixed at 1.0 upstream)."""
    s = np.asarray(s, dtype=float).ravel()
    rho = np.empty((3, s.size))
    sp1 = s + 1.0
    rho[0, :] = np.log(sp1)
    rho[1, :] = 1.0 / sp1
    rho[2, :] = -(rho[1, :] ** 2)
    return rho


def _as_2d(err):
    err = np.asarray(err, dtype=float)
    if err.ndim == 0:
        return err.reshape(1, 1)
    if err.ndim == 1:
        return err.reshape(1, -1)
    return err


def apply_robustifier(robustifier, err, Jt=None):
    """Port of apply_robustifier.m (Triggs correction).

    err: (M, N). Jt: optional (D, M, N). Returns cost (N,) and, when Jt is
    given, the weighted (err (M, N), Jt (D, M, N)). Mirrors MATLAB nargout:
    cost always; err/Jt only when Jt is passed.
    """
    err = _as_2d(err)
    sq_norm = np.sum(err ** 2, axis=0)
    rho = robustifier(sq_norm)
    cost = rho[0, :].copy()
    if Jt is None:
        return cost
    Jt = np.asarray(Jt, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        D = np.sqrt(1 + np.maximum(
            2 * sq_norm * rho[2, :] / (rho[1, :] - 1e-100), 0))
    w1 = np.sqrt(rho[1, :])          # Jacobian scale (line 15 then 21)
    w = w1 / D                       # residual scale (line 16 then 24)
    rho3 = np.maximum((1 - D) / (sq_norm - 1e-100), 0)
    E = err.reshape(err.shape[0], 1, err.shape[1])
    A = tmult(Jt, E)                 # (D, 1, N)
    B = (rho3 * err)[None, :, :]     # (1, M, N)
    Jt = Jt - A * B
    Jt = Jt * w1.reshape(1, 1, -1)
    err = err * w.reshape(1, -1)
    return cost, err, Jt
