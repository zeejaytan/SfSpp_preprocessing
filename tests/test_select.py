"""Unit tests for sfs_axes.select (ticket 324): the keep rule and the profile ranking."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sfs_axes.io_axes import direction_angle_deg
from sfs_axes.select import (
    keep_lines,
    orient_base_axis,
    rank_by_profile,
    select_union_lines,
)


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

# --- Ticket 335: base -> rim sign orientation (orient_base_axis) ----------------


import subprocess

import sfs_axes.select as select_mod


def _base_disk_frame(d):
    """Orthonormal frame (e1, e2, d) whose third axis is d."""
    d = np.asarray(d, dtype=float)
    d = d / np.linalg.norm(d)
    ref = np.array([1.0, 0.0, 0.0]) if abs(d[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    e1 = np.cross(ref, d)
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(d, e1)
    return e1, e2, d


def _base_disk(rng, d=(0.0, 0.0, 1.0), n_cap=300, n_wall=60, r_out=22.0, half_h=10.0):
    """A base cap with the short skirt of wall rising from it, base -> rim along d.

    The cap is at local z = 0 with axial normals; the skirt spans local z in
    [0, 2 * half_h] with radial normals. Passing d with d[2] < 0 builds the
    inverted scan whose own base -> rim direction points down.
    """
    e1, e2, d = _base_disk_frame(d)
    r = rng.uniform(3.0, r_out, n_cap)
    th = rng.uniform(0.0, 2.0 * np.pi, n_cap)
    th_w = rng.uniform(0.0, 2.0 * np.pi, n_wall)
    z_w = rng.uniform(0.0, 2.0 * half_h, n_wall)
    P = np.concatenate([
        np.stack([r * np.cos(th), r * np.sin(th), np.zeros(n_cap)]),
        np.stack([r_out * np.cos(th_w), r_out * np.sin(th_w), z_w]),
    ], axis=1)
    cap_sign = np.where(rng.random(n_cap) < 0.5, -1.0, 1.0)
    N = np.concatenate([
        np.stack([np.zeros(n_cap), np.zeros(n_cap), cap_sign]),
        np.stack([np.cos(th_w), np.sin(th_w), np.zeros(n_wall)]),
    ], axis=1)
    rot = np.column_stack([e1, e2, d])
    return np.vstack([rot @ P, rot @ N])


def test_orient_base_axis_flips_an_inverted_tilted_base_disk():
    rng = np.random.default_rng(335)
    d = np.array([-0.25, 0.15, -0.95])
    C = _base_disk(rng, d=d)
    vt = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 0.0])
    out, info = orient_base_axis(vt, C, return_info=True)
    assert out.shape == (6,)
    assert info[0]["base"] is True
    assert info[0]["flipped"] is True
    assert info[0]["z_wall"] < info[0]["z_pole"]
    assert float(out[0:3] @ (d / np.linalg.norm(d))) > 0.9
    assert out[2] < 0.0
    out2, info2 = orient_base_axis(out, C, return_info=True)
    assert info2[0]["flipped"] is False
    assert np.array_equal(out2, out)


def test_orient_base_axis_leaves_an_upright_base_disk_bit_for_bit():
    rng = np.random.default_rng(336)
    C = _base_disk(rng)
    vt = np.array([0.0, 0.0, 1.0 + 1e-13, 0.0, 0.0, 0.0])
    out, info = orient_base_axis(vt, C, return_info=True)
    assert info[0]["base"] is True
    assert info[0]["flipped"] is False
    assert np.array_equal(out, vt)


def test_orient_base_axis_flips_a_non_base_piece_with_dir_z_below_zero():
    rng = np.random.default_rng(337)
    C0, C1 = _sherd_walls(rng)
    C = np.concatenate([C0, C1], axis=1)
    down = np.array([0.0, 0.0, -1.0, 0.0, 0.0, 0.0])
    out, info = orient_base_axis(down, C, return_info=True)
    assert info[0]["base"] is False
    assert info[0]["flipped"] is True
    np.testing.assert_allclose(out[0:3], [0.0, 0.0, 1.0])
    up = np.array([0.0, 0.0, 1.0, 3.0, -2.0, 1.0])
    out2, info2 = orient_base_axis(up, C, return_info=True)
    assert info2[0]["flipped"] is False
    assert np.array_equal(out2, up)


def test_orient_base_axis_is_invariant_to_the_normal_sign():
    rng = np.random.default_rng(338)
    C = _base_disk(rng, d=[-0.2, 0.1, -0.97])
    vt = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 0.0])
    out = orient_base_axis(vt, C)
    C_flipped = C.copy()
    C_flipped[3:6, :] = -C_flipped[3:6, :]
    assert np.array_equal(out, orient_base_axis(vt, C_flipped))


def test_orient_base_axis_quantile_fallbacks_when_the_masks_are_thin(monkeypatch):
    rng = np.random.default_rng(339)
    C = _base_disk(rng)
    vt = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 0.0])
    monkeypatch.setattr(select_mod, "BASE_ORIENT_MIN_COUNT", 10 ** 9)
    out, info = orient_base_axis(vt, C, return_info=True)
    rec = info[0]
    assert rec["base"] is True
    assert rec["n_wall"] > 300
    assert rec["n_pole"] == 300
    assert rec["flipped"] is False
    assert np.array_equal(out, vt)


def test_orient_base_axis_shapes_joined_walls_and_empty_inputs():
    rng = np.random.default_rng(340)
    C = _base_disk(rng, d=[-0.1, 0.0, -0.99])
    vt1 = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 0.0])
    assert orient_base_axis(vt1, C).shape == (6,)
    vt2 = np.column_stack([vt1, np.array([1.0, 0.0, 0.1, 5.0, 0.0, 0.0])])
    out2, info = orient_base_axis(vt2, C, return_info=True)
    assert out2.shape == (6, 2)
    assert len(info) == 2
    assert out2[2, 0] < 0.0
    half = C.shape[1] // 2
    joined = orient_base_axis(vt1, C)
    split = orient_base_axis(vt1, C[:, :half], C[:, half:])
    assert np.array_equal(joined, split)
    empty = np.zeros((6, 0))
    out3, info3 = orient_base_axis(empty, C, return_info=True)
    assert out3.shape == (6, 0)
    assert info3 == []
    no_cloud = np.zeros((6, 0))
    assert np.array_equal(orient_base_axis(vt1, no_cloud), vt1)
    down = np.array([0.0, 0.0, -1.0, 0.0, 0.0, 0.0])
    assert orient_base_axis(down, no_cloud)[2] > 0.0


def test_base_orient_env_switch_is_read_at_import():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    code = ("import sys; sys.path.insert(0, %r); import sfs_axes.select as s; "
            "print(int(bool(s.BASE_ORIENT)))" % root)
    for value, want in (("0", "0"), ("1", "1"), ("", "0")):
        env = dict(os.environ)
        env["SFS_AXES_BASE_ORIENT"] = value
        got = subprocess.check_output([sys.executable, "-c", code], env=env)
        assert got.decode().strip() == want


def test_select_union_lines_base_orient_on_an_inverted_base_disk():
    rng = np.random.default_rng(342)
    C = _base_disk(rng, d=[0.0, 0.0, -1.0], n_cap=400, n_wall=60)
    C0, C1 = C[:, :300], C[:, 300:]
    C = np.concatenate([C0, C1], axis=1)
    reps = np.column_stack([
        _line([0.03, 0.0, 1.0], [0.0, 0.0, 0.0]),
        _line([1.0, 0.0, 0.1], [0.0, 0.0, 0.0]),
    ])
    sizes = np.array([50, 20])
    v_off, _ = select_union_lines(reps, sizes, C0, C1, C, 2, line_rule=False,
                                  base_orient=False)
    assert np.all(v_off[2] >= 0.0)
    v_on, _ = select_union_lines(reps, sizes, C0, C1, C, 2, line_rule=False,
                                 base_orient=True)
    assert v_on.shape == v_off.shape
    for k in range(v_on.shape[1]):
        assert abs(float(v_on[0:3, k] @ v_off[0:3, k])) > 0.999
    assert np.any(v_on[2] < 0.0)


def test_select_union_lines_honours_the_module_base_orient_default(monkeypatch):
    rng = np.random.default_rng(343)
    C0, C1 = _sherd_walls(rng, n=300)
    C = np.concatenate([C0, C1], axis=1)
    reps = np.column_stack([
        _line([0.05, 0.0, 1.0], [2.0, 1.0, 0.0]),
        _line([1.0, 0.0, 0.2], [0.0, 0.0, 0.0]),
    ])
    sizes = np.array([40, 30])
    monkeypatch.setattr(select_mod, "BASE_ORIENT", False)
    v_off, _ = select_union_lines(reps, sizes, C0, C1, C, 2, line_rule=False,
                                  base_orient=None)
    assert np.all(v_off[2] >= 0.0)
    monkeypatch.setattr(select_mod, "BASE_ORIENT", True)
    v_on, _ = select_union_lines(reps, sizes, C0, C1, C, 2, line_rule=False,
                                 base_orient=None)
    assert np.array_equal(v_on, v_off)
