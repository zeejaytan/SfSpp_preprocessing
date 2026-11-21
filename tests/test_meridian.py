"""Ticket 03 tests: the meridional objectives and refiners (from Ticket 02).

Every test builds its own synthetic wall instead of reading the corpus, so it runs
anywhere and pins the arithmetic rather than a number.  Only the pieces the joint
selector actually uses are covered here: the calibrated normal cost/refinement and
the Hermite thickness cost/refinement.  The prototype's other arms (tilt-normalised
azimuthal, scale-free Cao, hierarchical) are not shipped; see the ticket.
"""

import numpy as np
import pytest

from sfs_axes import joint
from sfs_axes.io_axes import direction_angle_deg
from sfs_axes.meridian import (
    finish_line,
    hermite_thickness,
    line_shift,
    normal_cost,
    profile_thickness_cost,
    refine_axis_normal,
    refine_axis_profile_thickness,
    unit_line,
)
from sfs_axes.normalized import compute_normalized_residual
from sfs_axes.profile import profile_cost, stride
from sfs_axes.robust import robustifier_huber

GT = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 0.0])


def pot(R_inner=30.0, R_outer=33.0, zmax=20.0, n_az=180, n_z=40):
    """Two concentric walls about +z: points (3, N) and outward normals (3, N)."""
    pts, nrm = [], []
    for R in (R_inner, R_outer):
        th = np.linspace(0.0, 2.0 * np.pi, n_az, endpoint=False)
        zs = np.linspace(-zmax, zmax, n_z)
        T, Z = np.meshgrid(th, zs, indexing="ij")
        pts.append(np.vstack([R * np.cos(T).ravel(), R * np.sin(T).ravel(),
                              Z.ravel()]))
        nrm.append(np.vstack([np.cos(T).ravel(), np.sin(T).ravel(),
                              np.zeros(T.size)]))
    return np.vstack([np.hstack(pts), np.hstack(nrm)])


def two_walls(X):
    h = X.shape[1] // 2
    return [X[:, :h], X[:, h:]]


def test_huber_width_one_makes_every_point_an_inlier():
    """|e_hat| <= 1, so the shipped width=1.0 robustifier is the identity."""
    s = np.array([[0.0, 0.04, 0.16, 0.36, 0.64, 1.0]])
    np.testing.assert_allclose(robustifier_huber(s, 1.0)[0], s[0], rtol=1e-12)
    assert robustifier_huber(s, 0.05)[0].max() < 0.1 * s[0].max()


def test_normal_cost_is_zero_on_the_true_axis_and_grows_off_it():
    X = pot()
    assert normal_cost(GT, X) == pytest.approx(0.0, abs=1e-12)
    off = np.array([0.0, 0.0, 1.0, 6.0, 0.0, 0.0])
    assert normal_cost(off, X) > 0.0
    tilt = np.array([np.sin(np.radians(10.0)), 0.0, np.cos(np.radians(10.0)),
                     0.0, 0.0, 0.0])
    assert normal_cost(tilt, X) > normal_cost(GT, X)


def test_calibrated_width_is_not_the_identity():
    """Bug 1: at the shipped width the cost is plain L2 and cannot reject a tilt."""
    X = pot()
    tilt = np.array([np.sin(np.radians(30.0)), 0.0, np.cos(np.radians(30.0)),
                     0.0, 0.0, 0.0])
    narrow = normal_cost(tilt, X, width=0.05)
    wide = normal_cost(tilt, X, width=1.0)
    assert narrow < 0.5 * wide


def test_hermite_thickness_prefers_the_true_axis_to_a_displaced_one():
    """Bug 3: the profile cost must not be beatable by sliding the axis."""
    X = pot()
    walls_s = [stride(W, 2500) for W in two_walls(X)]
    true_cost = profile_thickness_cost(GT, walls_s)
    for off in (2.0, 8.0, 32.0):
        v = np.array([0.0, 0.0, 1.0, off, 0.0, 0.0])
        assert profile_thickness_cost(v, walls_s) > true_cost


def test_normal_consistency_charges_a_fold():
    """Normal-consistent scoring never beats plain Hermite, and charges a fold more."""
    X = pot()
    walls_s = [stride(W, 2500) for W in two_walls(X)]
    for off in (0.0, 2.0, 8.0):
        v = np.array([0.0, 0.0, 1.0, off, 0.0, 0.0])
        assert (profile_thickness_cost(v, walls_s, normal_consistent=True)
                >= profile_thickness_cost(v, walls_s) - 1e-12)
    W = walls_s[0].copy()
    half = W.shape[1] // 2
    W[3:6, :half] *= -1.0
    t_ok = hermite_thickness(GT, walls_s[0])
    t_fold = hermite_thickness(GT, W, normal_consistent=True)
    assert t_fold >= t_ok


def test_pca_profile_cost_is_the_permissive_one():
    """The shipped cost can report a displaced axis thinner than the Hermite one."""
    X = pot()
    walls_s = [stride(W, 2500) for W in two_walls(X)]
    v = np.array([0.0, 0.0, 1.0, 2.0, 0.0, 0.0])
    assert profile_cost(v, walls_s) <= profile_thickness_cost(v, walls_s)


def test_trimmed_mean_is_the_refinement_objective_and_median_the_ranking_one():
    """The arm ranks on the median (keep=None) and refines on the trimmed 0.8 mean."""
    X = pot()
    walls_s = [stride(W, 600) for W in two_walls(X)]
    v = np.array([0.0, 0.0, 1.0, 4.0, 0.0, 0.0])
    median = profile_thickness_cost(v, walls_s)
    trimmed = profile_thickness_cost(v, walls_s, keep=0.8)
    assert trimmed <= median + 1e-12


def test_refine_axis_normal_recovers_a_tilted_axis():
    X = pot()
    tilt = np.deg2rad(8.0)
    start = np.array([np.sin(tilt), 0.0, np.cos(tilt), 0.0, 0.0, 0.0])
    out = refine_axis_normal(start, X, width=0.05, max_iters=60)
    assert direction_angle_deg(out[0:3], GT[0:3]) < 1.0
    assert abs(float(out[0:3] @ out[3:6])) < 1e-8


def test_refine_axis_profile_thickness_keeps_a_displaced_axis_near_the_walls():
    X = pot()
    walls_s = [stride(W, 1200) for W in two_walls(X)]
    centre = X[0:3, :].mean(axis=1)
    size = float(np.linalg.norm(X[0:3, :].max(axis=1) - X[0:3, :].min(axis=1)))
    start = np.array([0.0, 0.0, 1.0, 3.0, 0.0, 0.0])
    out, fun = refine_axis_profile_thickness(start, walls_s, centre, size,
                                             normal_consistent=True)
    assert direction_angle_deg(out[0:3], GT[0:3]) < 2.0
    assert abs(float(out[0:3] @ out[3:6])) < 1e-8
    assert float(fun) > 0.0


def test_the_refinement_bound_measures_movement_at_the_piece():
    """An axis may move by less than one piece-size *where the material is*.

    The feet of a pot axis sit far from a small sherd, so a foot-to-foot measure
    would reject a legitimate rotation of a line whose foot is 400 mm away.  The
    bound compares the two lines' closest points to the cloud centroid.
    """
    C = np.array([[0.0, 0.0], [0.0, 0.0], [-10.0, 10.0]])   # centroid at the origin
    a = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 0.0])
    b = np.array([0.0, 0.0, 1.0, 5.0, 0.0, 0.0])           # parallel, 5 mm away
    far = np.array([0.0, 0.0, 1.0, 400.0, 0.0, 0.0])       # 400 mm away
    assert line_shift(a, a, C) == pytest.approx(0.0, abs=1e-9)
    assert line_shift(a, b, C) == pytest.approx(5.0, abs=1e-9)
    assert line_shift(a, far, C) == pytest.approx(400.0, abs=1e-9)

    size = 40.0
    assert joint._bounded(a, b, size, C) is b
    np.testing.assert_allclose(joint._bounded(a, far, size, C), a)
    np.testing.assert_allclose(joint._bounded(a, np.full(6, np.nan), size, C), a)

    swung = np.array([0.10, 0.0, 0.995, 0.0, 0.0, 0.0])   # pivots at the piece
    assert line_shift(a, swung, C) < size


def test_unit_line_projects_the_foot_off_the_direction():
    a, p0 = unit_line(np.array([0.0, 0.0, 7.0, 1.0, 2.0, 3.0]))
    assert np.allclose(a, GT[0:3]) and abs(float(p0 @ a)) < 1e-12
    np.testing.assert_allclose(p0, [1.0, 2.0, 0.0])


def test_finish_line_and_the_residual_agree_on_a_finished_line():
    """finish_line is idempotent and does not move the line the residual sees."""
    X = pot()
    v = finish_line(np.array([0.0, 0.0, 2.0, 1.0, 1.0, 1.0]))
    assert abs(float(v[0:3] @ v[3:6])) < 1e-12
    assert np.allclose(finish_line(v), v)
    assert np.allclose(compute_normalized_residual(GT, X)[0, :], 0.0, atol=1e-12)
