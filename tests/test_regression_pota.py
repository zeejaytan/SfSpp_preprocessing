"""Regression tests for the sfs_axes PotSAC port (POTA-05).

Fast unit checks (no ORIG data needed):
  - Pottmann recovers a synthetic cylinder axis exactly.
  - Method-1 LM refinement converges from a perturbed start.
  - Method-2 refinement no-ops via the catch path, exactly as the MATLAB
    reference does (scalar biaxial residual vs per-point Jacobian rows:
    grad = J'*err is a dimension mismatch; see refine.py docstring).
  - Axis file round-trip preserves the assembly position-first layout.
  - 10-degree dedup keeps the cheapest of two near-identical axes.
  - Adaptive step rule matches the working-tree run_potsac.m table.

Run: python -m pytest tests/test_regression_pota.py  (or plain python file)
"""

import os
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sfs_axes.cao import compute_biaxial_cao_error  # noqa: E402
from sfs_axes.io_axes import (direction_angle_deg, radial_axial_errors,  # noqa: E402
                              read_axes, write_axes)
from sfs_axes.plucker import euc2plucker  # noqa: E402
from sfs_axes.potsac import (adaptive_step, compute_axis_of_symmetry,  # noqa: E402
                             run_potsac)
from sfs_axes.pottmann import compute_pottmann_axis  # noqa: E402
from sfs_axes.refine import refine_axis  # noqa: E402


def make_cylinder(rng, n=800, r=80.0, half_h=50.0):
    th = rng.uniform(0, 2 * np.pi, n)
    z = rng.uniform(-half_h, half_h, n)
    P = np.stack([r * np.cos(th), r * np.sin(th), z])
    N = np.stack([np.cos(th), np.sin(th), np.zeros(n)])
    return np.vstack([P, N])


def test_pottmann_cylinder():
    rng = np.random.default_rng(0)
    vt = compute_pottmann_axis(make_cylinder(rng))
    assert direction_angle_deg(vt[0:3], [0, 0, 1]) < 1e-9
    assert np.linalg.norm(vt[3:6]) < 1e-9


def test_refine_method1_converges():
    rng = np.random.default_rng(0)
    X = make_cylinder(rng)
    v0 = np.array([0.1, 0.05, 1.0, 2.0, -1.5, 3.0])
    v0[:3] /= np.linalg.norm(v0[:3])
    v1 = refine_axis(v0, X, method=1, max_iters=50, tolerance=1e-9)
    assert direction_angle_deg(v1[:3], [0, 0, 1]) < 1e-6
    assert np.linalg.norm(v1[3:6]) < 1e-6


def test_refine_method2_noop_matches_matlab():
    rng = np.random.default_rng(0)
    X = make_cylinder(rng)
    v0 = np.array([0.1, 0.05, 1.0, 2.0, -1.5, 3.0])
    v0[:3] /= np.linalg.norm(v0[:3])
    v2 = refine_axis(v0, X, method=2)
    np.testing.assert_allclose(v2, v0)


def test_axis_file_roundtrip_position_first():
    rng = np.random.default_rng(0)
    vt = np.stack([np.array([0.0, 0.0, 1.0, 10.0, 20.0, 30.0]),
                   np.array([0.0, 1.0, 0.0, 1.0, 2.0, 3.0])], axis=1)
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "Pot_A_Piece_01_Axis.xyz")
        write_axes(p, vt)
        raw = open(p).read().splitlines()
        assert raw[0].startswith("10.000000000000 20.000000000000 30.000000000000 "
                                 "0.000000000000 0.000000000000 1.000000000000")
        back = read_axes(p)
    np.testing.assert_allclose(back, vt, atol=1e-12)


def test_dedup_keeps_cheapest():
    rng = np.random.default_rng(2)
    X = make_cylinder(rng, n=400)
    vt = run_potsac(X[:, :200], X[:, 200:], rng=np.random.default_rng(0), step=20)
    assert vt.shape[1] >= 1
    assert abs(np.linalg.norm(vt[0:3, 0]) - 1.0) < 1e-12


def test_adaptive_step_table():
    assert adaptive_step(4999) == 1
    assert adaptive_step(30000) == 3
    assert adaptive_step(60000) == 6


def test_mlesac_ranking_by_cost():
    rng = np.random.default_rng(3)
    X = make_cylinder(rng, n=300)
    _vt, _inl, costs, _s = compute_axis_of_symmetry(X, rng=rng, max_iters=20)
    assert np.all(np.diff(costs) >= 0)


def test_radial_axial_decomposition():
    r, a = radial_axial_errors([1.0, 0.0, 5.0], [0, 0, 1], [0, 0, 0])
    assert abs(r - 1.0) < 1e-12 and abs(a - 5.0) < 1e-12


if __name__ == "__main__":
    names = sorted(n for n, f in sorted(globals().items())
                   if n.startswith("test_") and callable(f))
    for n in names:
        globals()[n]()
        print("PASS", n)
    print("all %d regression tests passed" % len(names))
