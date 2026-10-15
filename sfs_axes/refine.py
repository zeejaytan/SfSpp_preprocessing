"""Axis refinement — port of refine_axis.m, optimize_using_lm.m, cao_update_func.m.

Exact-shape Levenberg-Marquardt port: res_func returns err (M, N) and
J (M, 6, N); flattens use column-major order to match MATLAB err(:) and
reshape(permute(...), [], 6).

PROVENANCE FINDING (verified against optimize_using_lm.m:30-36): with
method 2 (biaxial, the only method run_potsac.m uses) the residual is a
whole-cloud scalar while J has one row per point, so grad = J'*err is a
dimension mismatch and MATLAB throws before the first update — refine_axis's
try/catch then returns the initial estimate. I.e. in the reference
implementation the two-stage "refinement" is a silent no-op and the shipped
axes are MLESAC+Pottmann+dedup+sort outputs. This port reproduces that
behaviour identically (numpy raises at the same product; same catch path),
so ORIG-axes parity holds. Method 1 shapes are consistent and refines
genuinely; it is kept for future use, not used by run_potsac.
"""

import numpy as np

from .cao import compute_biaxial_cao_error, compute_cao_error
from .robust import apply_robustifier, robustifier_huber


def cao_update_func(vt, dvt):
    """Port of cao_update_func.m: Euclidean step + manifold retraction."""
    vt = np.asarray(vt, dtype=float) + np.asarray(dvt, dtype=float)
    vt[0:3] = vt[0:3] / np.linalg.norm(vt[0:3])
    vt[3:6] = vt[3:6] - vt[0:3] * (vt[0:3] @ vt[3:6])
    return vt


def optimize_using_lm(x, res_func, update_func, robustifier,
                      max_iters=300, func_tol=1e-9, verbose=False):
    """Port of optimize_using_lm.m.

    res_func(x) -> (err (M, N), J (M, 6, N)). Returns (x, err, xlog);
    xlog is (6, evals+1). Raises on dimension mismatch exactly where
    MATLAB does (method-2 grad product); the caller catches it.
    """
    x = np.asarray(x, dtype=float).reshape(6)
    max_trials = 20
    max_lambda = 1e14
    min_lambda = 1e-14
    lam = 1e-1
    lambda_inc_factor = 2.0

    def weighted(x_):
        err_, J_ = res_func(x_)
        errM = np.asarray(err_, dtype=float)
        if errM.ndim == 0:
            errM = errM.reshape(1, 1)
        elif errM.ndim == 1:
            errM = errM.reshape(1, -1)
        Jt = np.transpose(np.asarray(J_, dtype=float), (1, 0, 2))  # (6, M, N)
        cost_, errw_, Jtw_ = apply_robustifier(robustifier, errM, Jt)
        # MATLAB reshape(permute(Jt,[2 3 1]), [], 6): column-major (M*N, 6)
        Jm = np.transpose(Jtw_, (1, 2, 0)).reshape(-1, 6, order="F")
        return cost_, errw_.reshape(-1, order="F"), Jm  # err(:) likewise

    cost, err, J = weighted(x)
    v = x[0:3]
    J[:, 0:3] = J[:, 0:3] @ (np.eye(3) - np.outer(v, v))
    JTJ = J.T @ J
    grad = J.T @ err  # raises here for method 2, as in MATLAB line 36
    if verbose:
        print("[iter][eval] cost actual_cost_change |grad| |TR| MQ")
        print("[%04d][%04d] %.6e %.3e %.2e %.2e %.2e" % (0, 0, 0.5 * cost.sum(), 0,
                                                         np.linalg.norm(grad), 1.0 / lam, 1.0))
    xs = [x.copy()]
    eye6 = np.eye(6)
    evals = 0
    cost_diff = np.inf
    for _it in range(1, max_iters + 1):
        trial = 0
        v = x[0:3]
        damp_block = np.block([[np.outer(v, v), np.zeros((3, 3))],
                               [np.zeros((3, 3)), np.outer(v, v)]])
        for trial in range(1, max_trials + 1):
            evals += 1
            try:
                dx = -np.linalg.solve(JTJ + damp_block + lam * eye6, grad)
            except np.linalg.LinAlgError:
                dx, *_ = np.linalg.lstsq(JTJ + damp_block + lam * eye6, -grad, rcond=None)
            x_cand = update_func(x, dx)
            xs.append(x_cand.copy())
            cost_cand, err_cand, J_cand = weighted(x_cand)
            with np.errstate(divide="ignore", invalid="ignore"):
                expected = 0.5 * (np.sum(err ** 2) - np.sum((err + J @ dx) ** 2))
                actual = 0.5 * np.sum(cost - cost_cand)
                mq = actual / expected  # literal; NaN/Inf behave as in MATLAB
            if verbose:
                print("[%04d][%04d] %.6e %.3e %.2e %.2e %.2e"
                      % (_it, evals, 0.5 * cost_cand.sum(), actual,
                         np.linalg.norm(grad), 1.0 / lam, mq))
            if mq > 0:
                x = x_cand
                J = J_cand
                v = x[0:3]
                J[:, 0:3] = J[:, 0:3] @ (np.eye(3) - np.outer(v, v))
                JTJ = J.T @ J
                err = err_cand
                cost_diff = actual
                cost = cost_cand
                grad = J.T @ err
                lam = max(min_lambda, lam * max(1.0 / 3.0, 1 - (2 * mq - 1) ** 3))
                lambda_inc_factor = 2.0
                break
            lam = min(lam * lambda_inc_factor, max_lambda)
            lambda_inc_factor *= 2.0
        if trial == max_trials:
            break
        if cost_diff < 0.5 * func_tol * cost.sum():
            break
        if np.all(cost < func_tol):  # MATLAB `if` on an array = all()
            break
    return x, err, np.column_stack(xs)


def refine_axis(vt_initial, X, method=2, max_iters=300, tolerance=1e-9, verbose=False):
    """Port of refine_axis.m (unused1/unused2 compatibility args dropped).

    method 1 = single-sided Cao error, 2 = biaxial (default, most robust).
    NOTE: method 2 raises inside optimize_using_lm exactly as MATLAB does
    and returns the initial estimate via the catch path (see module docstring).
    """
    vt = np.asarray(vt_initial, dtype=float).reshape(6)
    X = np.asarray(X, dtype=float)
    if method == 1:
        def res_func(v):
            return compute_cao_error(v, X, with_jacobian=True)
    elif method == 2:
        def res_func(v):
            return compute_biaxial_cao_error(v, X, with_jacobian=True)
    else:
        raise ValueError("Unknown refinement method: %r" % (method,))
    try:
        vt_ref, _err, _log = optimize_using_lm(
            vt, res_func, cao_update_func, robustifier_huber,
            max_iters, tolerance, verbose=verbose)
        vt_ref[0:3] = vt_ref[0:3] / np.linalg.norm(vt_ref[0:3])
        vt_ref[3:6] = vt_ref[3:6] - vt_ref[0:3] * (vt_ref[0:3] @ vt_ref[3:6])
        return vt_ref
    except Exception as exc:  # MATLAB catch: return initial estimate
        print("Warning: Axis refinement failed: %s" % exc)
        print("Returning initial axis estimate")
        return vt
