"""Plucker / tensor helpers — port of euc2plucker.m, cross2mat.m, tmult.m.

Conventions (MATLAB-compatible, 0-based):
  X : (6, n) array, rows 0-2 points, rows 3-5 normals.
  vt: (6,) axis, rows 0-2 direction (unit), rows 3-5 position (orthogonal).
"""

import numpy as np


def euc2plucker(line_euc, normalize=True):
    """Convert Euclidean lines [l; c] (6, n) to Plucker [l; lbar] (6, n).

    Port of euc2plucker.m: normalises the direction rows, then
    lbar = cross(c, l) per column.
    """
    line_euc = np.asarray(line_euc, dtype=float)
    if normalize:
        n = np.sqrt(np.sum(line_euc[0:3, :] ** 2, axis=0))
        line_euc = line_euc.copy()
        line_euc[0:3, :] = line_euc[0:3, :] / n
    moment = np.cross(line_euc[3:6, :], line_euc[0:3, :], axis=0)
    return np.vstack([line_euc[0:3, :], moment])


def cross2mat(omega):
    """Skew-symmetric matrix form of cross product. Port of cross2mat.m.

    omega: (3, n) -> S: (3, 3, n) with S[:, :, i] @ v == cross(omega[:, i], v).
    """
    omega = np.asarray(omega, dtype=float)
    n = omega.shape[1]
    S = np.zeros((3, 3, n))
    S[2, 1, :] = omega[0, :]
    S[1, 2, :] = -omega[0, :]
    S[0, 2, :] = omega[1, :]
    S[2, 0, :] = -omega[1, :]
    S[1, 0, :] = omega[2, :]
    S[0, 1, :] = -omega[2, :]
    return S


def tmult(A, B, transpose_flag=False):
    """Tensor matrix multiplication along last two dims. Port of tmult.m.

    C[:, :, i] = A[:, :, i] @ B[:, :, i]; with transpose_flag,
    C[:, :, i] = A[:, :, i].T @ B[:, :, i]. 2-D inputs behave as matmul.
    A 2-D operand is repeated across the slices of a 3-D operand.
    """
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    if A.ndim == 2 and B.ndim == 2:
        return A.T @ B if transpose_flag else A @ B
    if A.ndim == 2:
        A = np.repeat(A[:, :, None], B.shape[2], axis=2)
    if B.ndim == 2:
        B = np.repeat(B[:, :, None], A.shape[2], axis=2)
    na, nb = A.shape[2], B.shape[2]
    if na == 1 and nb > 1:
        A = np.repeat(A, nb, axis=2)
    if nb == 1 and na > 1:
        B = np.repeat(B, na, axis=2)
    if transpose_flag:
        return np.einsum("jin,jkn->ikn", A, B)
    return np.einsum("ijn,jkn->ikn", A, B)
