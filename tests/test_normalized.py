"""Unit tests for sfs_axes.normalized (Ticket 313 Acceptance Criterion A1)."""

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sfs_axes.io_axes import direction_angle_deg
from sfs_axes.normalized import (
    centroid_distance,
    compute_normalized_residual,
    normalized_huber_cost,
    refine_axis_least_squares,
    refine_axis_normalized,
    worst_wall_normalized_cost,
)


def make_cylinder(rng, n=500, r=80.0, half_h=50.0):
    th = rng.uniform(0, 2 * np.pi, n)
    z = rng.uniform(-half_h, half_h, n)
    P = np.stack([r * np.cos(th), r * np.sin(th), z])
    N = np.stack([np.cos(th), np.sin(th), np.zeros(n)])
    return np.vstack([P, N])


def test_normalized_residual_exact_on_cylinder():
    rng = np.random.default_rng(42)
    X = make_cylinder(rng)
    vt_true = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 0.0])
    err = compute_normalized_residual(vt_true, X)
    assert np.max(np.abs(err)) < 1e-12


def test_analytical_jacobian_vs_finite_diff():
    rng = np.random.default_rng(123)
    # Test on multiple points and orientations
    for _ in range(5):
        vt = rng.standard_normal(6)
        vt[:3] /= np.linalg.norm(vt[:3])
        vt[3:6] -= (vt[3:6] @ vt[:3]) * vt[:3]

        P = rng.standard_normal((3, 10)) * 50.0
        N = rng.standard_normal((3, 10))
        N /= np.linalg.norm(N, axis=0, keepdims=True)
        X = np.vstack([P, N])

        err_ana, J_ana = compute_normalized_residual(vt, X, with_jacobian=True)

        # Finite difference gradient
        eps = 1e-7
        J_num = np.zeros_like(J_ana)
        for i in range(6):
            vt_p = vt.copy(); vt_p[i] += eps
            vt_m = vt.copy(); vt_m[i] -= eps
            ep = compute_normalized_residual(vt_p, X)
            em = compute_normalized_residual(vt_m, X)
            J_num[0, i, :] = (ep[0, :] - em[0, :]) / (2 * eps)

        # On direction a, project J_num on tangent space of unit sphere
        P_mat = np.eye(3) - np.outer(vt[:3], vt[:3])
        J_num_proj_a = P_mat @ J_num[0, :3, :]

        # Check a derivative
        np.testing.assert_allclose(J_ana[0, :3, :], J_num_proj_a, atol=1e-5, rtol=1e-4)
        # Check p0 derivative
        np.testing.assert_allclose(J_ana[0, 3:6, :], J_num[0, 3:6, :], atol=1e-5, rtol=1e-4)


def test_sign_invariance_under_normal_flip():
    rng = np.random.default_rng(456)
    X = make_cylinder(rng, n=200)
    vt = np.array([0.1, 0.05, 1.0, 5.0, -3.0, 0.0])
    vt[:3] /= np.linalg.norm(vt[:3])

    cost_fwd = normalized_huber_cost(vt, X)

    # Flip all normals
    X_rev = X.copy()
    X_rev[3:6, :] = -X_rev[3:6, :]
    cost_rev = normalized_huber_cost(vt, X_rev)

    assert abs(cost_fwd - cost_rev) < 1e-12


def test_refinement_converges_from_perturbed():
    rng = np.random.default_rng(789)
    X = make_cylinder(rng, n=600)
    # Perturb initial axis by ~8 degrees and 10 mm
    v0 = np.array([0.1, 0.08, 1.0, 10.0, -5.0, 0.0])
    v0[:3] /= np.linalg.norm(v0[:3])

    v_ref = refine_axis_normalized(v0, X, max_iters=100, tolerance=1e-9)
    ang = direction_angle_deg(v_ref[:3], [0, 0, 1])
    pos_err = np.linalg.norm(v_ref[3:6])
    assert ang < 0.05
    assert pos_err < 0.05


def test_clearance_prior_penalizes_centroid_slicing():
    rng = np.random.default_rng(101)
    # Sherd at radius 80 mm spanning small azimuth (e.g. 30 deg)
    th = rng.uniform(0.0, np.pi / 6.0, 200)
    z = rng.uniform(-20.0, 20.0, 200)
    P = np.stack([80.0 * np.cos(th), 80.0 * np.sin(th), z])
    N = np.stack([np.cos(th), np.sin(th), np.zeros(200)])
    X = np.vstack([P, N])
    C = np.mean(P, axis=1)

    # True axis: passes through (0, 0, 0)
    vt_true = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 0.0])
    d_true = centroid_distance(vt_true, X)
    assert d_true > 70.0  # ~77 mm

    # Fake axis passing directly through sherd centroid C
    vt_fake = np.array([0.0, 0.0, 1.0, C[0], C[1], 0.0])
    d_fake = centroid_distance(vt_fake, X)
    assert d_fake < 1.0

    cost_true = worst_wall_normalized_cost(vt_true, X, min_clearance_mm=25.0)
    cost_fake = worst_wall_normalized_cost(vt_fake, X, min_clearance_mm=25.0)

    # False axis must incur massive clearance penalty
    assert cost_fake > 1000.0
    assert cost_true < 0.01
