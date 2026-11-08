"""Unit tests for sfs_axes.normalized (Ticket 313 Acceptance Criterion A1)."""

import os
import sys

import numpy as np
try:
    import pytest
except ImportError:
    pytest = None

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


def test_base_classification_rejects_perpendicular_wall_slicing():
    rng = np.random.default_rng(202)
    # A wall sherd at R=75 mm with small azimuth span (e.g. 20 deg) and height 40 mm
    th = rng.uniform(-0.15, 0.15, 300)
    z = rng.uniform(-20.0, 20.0, 300)
    P = np.stack([75.0 * np.cos(th), 75.0 * np.sin(th), z])
    N = np.stack([np.cos(th), np.sin(th), np.zeros(300)])
    X = np.vstack([P, N])
    C = np.mean(P, axis=1)

    # A perpendicular axis piercing through the wall: a ~= n_wall = [1, 0, 0]
    vt_perp = np.array([1.0, 0.0, 0.0, C[0], C[1], C[2]])

    from sfs_axes.normalized import is_base_fragment
    # Must NOT be classified as a base fragment
    assert not is_base_fragment(X, vt_perp)


def test_base_classification_accepts_true_base_disk():
    rng = np.random.default_rng(303)
    # A base disk covering the bottom of a pot: radius up to 40 mm, z in [0, 20], normals vertical
    r = np.sqrt(rng.uniform(0.0, 40.0**2, 400))
    th = rng.uniform(0.0, 2 * np.pi, 400)
    z = rng.uniform(0.0, 20.0, 400)  # base floor + footring height
    P = np.stack([r * np.cos(th), r * np.sin(th), z])
    # Normals mostly axial: [0, 0, 1]
    N = np.stack([rng.normal(0, 0.05, 400), rng.normal(0, 0.05, 400), np.ones(400)])
    N /= np.linalg.norm(N, axis=0, keepdims=True)
    X = np.vstack([P, N])

    # True axis passes through (0, 0, 0) pointing in z [0, 0, 1]
    vt_base = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 0.0])

    from sfs_axes.normalized import is_base_fragment
    assert is_base_fragment(X, vt_base)


def test_large_radius_penalty_on_degenerate_cands():
    rng = np.random.default_rng(404)
    # A wall sherd at R=75 mm with small azimuth span [0, pi/4]
    th = rng.uniform(0.0, np.pi / 4.0, 200)
    z = rng.uniform(-20.0, 20.0, 200)
    P = np.stack([75.0 * np.cos(th), 75.0 * np.sin(th), z])
    N = np.stack([np.cos(th), np.sin(th), np.zeros(200)])
    X = np.vstack([P, N])

    # Candidate at true axis (0, 0, 0): centroid distance ~75 mm (physical)
    vt_phys = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 0.0])
    # Candidate at d = 250 mm from centroid (degenerate plane decoy)
    C = np.mean(P, axis=1)
    vt_degen = np.array([0.0, 0.0, 1.0, C[0] + 250.0, C[1], 0.0])

    cost_phys = worst_wall_normalized_cost(vt_phys, X, min_clearance_mm=25.0)
    cost_degen = worst_wall_normalized_cost(vt_degen, X, min_clearance_mm=25.0)

    # Degenerate infinite-radius candidate must incur large-radius penalty
    assert cost_phys < 0.1
    assert cost_degen > cost_phys + 1.0

def test_conical_shoulder_retains_true_axis_at_rank_0():
    from sfs_axes.potsac import run_potsac_union

    rng = np.random.default_rng(42)
    # Synthetic conical sherd: slope 45 deg, radius 55 mm, 60 deg azimuth patch
    def make_conical_patch(n=500, r0=55.0, half_h=15.0, arc=np.pi/3.0):
        th = rng.uniform(-arc/2, arc/2, n)
        z = rng.uniform(-half_h, half_h, n)
        r = r0 + z
        P = np.stack([r * np.cos(th), r * np.sin(th), z])
        c45 = 1.0 / np.sqrt(2.0)
        N = np.stack([c45 * np.cos(th), c45 * np.sin(th), -c45 * np.ones(n)])
        return np.vstack([P, N])

    C0 = make_conical_patch(n=500, r0=55.0)
    S1 = make_conical_patch(n=500, r0=51.0)

    # Axial mean of surface normal is ~0.707 (> 0.50)
    mean_ax = np.mean(np.abs(C0[5, :]))
    assert 0.65 < mean_ax < 0.75

    # Run potsac candidate extraction
    vt = run_potsac_union(C0, S1, seeds=range(3), normalized=True)
    assert vt.shape[1] >= 1

    # True axis [0, 0, 1] must be retained at Rank 0 within < 5 degrees
    err_deg = direction_angle_deg(vt[:3, 0], [0, 0, 1])
    assert err_deg < 5.0

def test_flared_conical_bowl_promotes_cone_at_rank_0():
    from sfs_axes.potsac import run_potsac_union

    rng = np.random.default_rng(101)
    # Synthetic flared conical bowl sherd: slope 38 deg, radius dc ~= 38 mm, 70 deg arc
    slope_rad = np.radians(38.0)
    tan_slope = np.tan(slope_rad)
    cos_slope = np.cos(slope_rad)
    sin_slope = np.sin(slope_rad)

    def make_bowl_patch(n=600, r0=38.0, half_h=15.0, arc=np.radians(70.0)):
        th = rng.uniform(-arc / 2, arc / 2, n)
        z = rng.uniform(-half_h, half_h, n)
        r = r0 + z * tan_slope
        P = np.stack([r * np.cos(th), r * np.sin(th), z])
        N = np.stack([cos_slope * np.cos(th), cos_slope * np.sin(th), -sin_slope * np.ones(n)])
        return np.vstack([P, N])

    C0 = make_bowl_patch(n=600, r0=38.0)
    S1 = make_bowl_patch(n=600, r0=34.0)

    # Axial mean of surface normal is ~sin(38 deg) ~= 0.616 (> 0.50)
    mean_ax = np.mean(np.abs(C0[5, :]))
    assert 0.55 < mean_ax < 0.68

    vt = run_potsac_union(C0, S1, seeds=range(3), normalized=True)
    assert vt.shape[1] >= 1

    # True conical axis [0, 0, 1] must be promoted to Rank 0 within < 5 degrees
    err_deg = direction_angle_deg(vt[:3, 0], [0, 0, 1])
    assert err_deg < 5.0

if __name__ == "__main__":
    names = sorted(n for n, f in sorted(globals().items())
                   if n.startswith("test_") and callable(f))
    for n in names:
        globals()[n]()
        print("PASS", n)
    print("all %d tests passed" % len(names))
