"""Unit tests for sfs_axes.select (ticket 324): the keep rule and the profile ranking."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sfs_axes.io_axes import direction_angle_deg
from sfs_axes.select import keep_lines, rank_by_profile, select_union_lines


def test_keep_lines_ratio_just_inside_and_just_outside():
    assert keep_lines([1.0, 1.19, 1.21]) == [0, 1]
    assert keep_lines([2.0, 2.42, 2.38]) == [0, 2]


def test_keep_lines_ratio_exactly_tau_is_kept():
    assert keep_lines([1.0, 1.2]) == [0, 1]


def test_keep_lines_cap_of_three_against_cheaper_fourth():
    # The fourth line is the cheapest after the first, but the cap is on count in rank order.
    assert keep_lines([1.0, 1.1, 1.15, 1.01]) == [0, 1, 2]


def test_keep_lines_one_line_only():
    assert keep_lines([3.7]) == [0]


def test_keep_lines_all_equal_costs():
    assert keep_lines([0.5] * 6) == [0, 1, 2]
    assert keep_lines([0.5] * 6, kmax=6) == [0, 1, 2, 3, 4, 5]


def test_keep_lines_first_line_already_worst_is_still_kept():
    assert keep_lines([5.0, 1.0, 2.0]) == [0, 1, 2]
    assert keep_lines([5.0, 7.0, 9.0]) == [0]


def test_keep_lines_empty_and_zero_cap():
    assert keep_lines([]) == []
    assert keep_lines([1.0, 1.0], kmax=0) == []


def test_keep_lines_never_returns_an_index_not_offered():
    rng = np.random.default_rng(324)
    for _ in range(2000):
        m = int(rng.integers(1, 9))
        costs = rng.uniform(0.01, 3.0, m)
        tau = float(rng.uniform(0.5, 3.0))
        kmax = int(rng.integers(1, 7))
        idx = keep_lines(costs, tau=tau, kmax=kmax)
        assert idx[0] == 0
        assert idx == sorted(set(idx))
        assert all(0 <= k < m for k in idx)
        assert len(idx) <= kmax
        assert all(costs[k] <= tau * costs[0] for k in idx[1:])


def _sherd_walls(rng, n=400, r_in=80.0, wall=6.0, arc=0.9, half_h=30.0):
    """Two coaxial wall patches of a vessel whose axis is the z axis."""
    walls = []
    for r in (r_in, r_in + wall):
        th = rng.uniform(-arc / 2, arc / 2, n)
        z = rng.uniform(-half_h, half_h, n)
        P = np.stack([r * np.cos(th), r * np.sin(th), z])
        N = np.stack([np.cos(th), np.sin(th), np.zeros(n)])
        walls.append(np.vstack([P, N]))
    return walls


def _line(d, p):
    d = np.asarray(d, dtype=float)
    d = d / np.linalg.norm(d)
    p = np.asarray(p, dtype=float)
    return np.r_[d, p - (p @ d) * d]


def test_rank_by_profile_puts_the_true_axis_first_and_returns_its_costs():
    rng = np.random.default_rng(0)
    C0, C1 = _sherd_walls(rng)
    C = np.concatenate([C0, C1], axis=1)
    centre = C[0:3].mean(axis=1)
    size = float(np.linalg.norm(C[0:3].max(axis=1) - C[0:3].min(axis=1)))
    vt = np.column_stack([
        _line([1.0, 0.0, 0.2], [0.0, 0.0, 0.0]),     # wrong: 79 deg off
        _line([0.05, 0.0, 1.0], [2.0, 1.0, 0.0]),    # near the true axis
        _line([0.0, 1.0, 0.0], [80.0, 0.0, 0.0]),    # wrong: 90 deg off
    ])
    out, costs = rank_by_profile(vt, [C0, C1], centre, size, refine_k=3)
    assert out.shape[0] == 6 and out.shape[1] == costs.size >= 1
    assert np.all(np.diff(costs) >= 0)
    assert direction_angle_deg(out[0:3, 0], [0.0, 0.0, 1.0]) < 3.0


def test_select_union_lines_rule_is_a_subset_of_the_ranked_set():
    rng = np.random.default_rng(1)
    C0, C1 = _sherd_walls(rng, n=300)
    C = np.concatenate([C0, C1], axis=1)
    reps = np.column_stack([
        _line([0.05, 0.0, 1.0], [2.0, 1.0, 0.0]),
        _line([1.0, 0.0, 0.2], [0.0, 0.0, 0.0]),
        _line([0.0, 1.0, 0.0], [80.0, 0.0, 0.0]),
        _line([0.7, 0.7, 0.2], [0.0, 0.0, 10.0]),
    ])
    sizes = np.array([40, 30, 20, 10])
    vt_all, c_all = select_union_lines(reps, sizes, C0, C1, C, 6, line_rule=False)
    vt_k, c_k = select_union_lines(reps, sizes, C0, C1, C, 6, line_rule=True)
    idx = keep_lines(c_all)
    assert np.array_equal(vt_k, vt_all[:, idx])
    assert np.array_equal(c_k, c_all[idx])
    assert 1 <= vt_k.shape[1] <= 3
