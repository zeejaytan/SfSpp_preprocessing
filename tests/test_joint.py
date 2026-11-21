"""Ticket 03 tests: the joint selector (calibrated normal + thickness + shipped).

Ordering, the merge dedup angle, the shipped-secondaries switch, the three-line cap
and the None/empty fallbacks are tested against stubbed arms, so every assertion is
about this module's merge rule.  The geometry the selector depends on -- base-to-rim
sign preservation after the single orient pass, and normal-sign invariance of the
arms' costs -- is tested on a synthetic base sherd through the shipped
orient_base_axis and meridian's cost functions.  The switch itself is tested through
select_union_lines: off must run the shipped body and never touch this module.
"""

import os
import subprocess
import sys

import numpy as np
import pytest

from sfs_axes import joint
from sfs_axes.io_axes import direction_angle_deg
from sfs_axes.joint import (
    merge_lines,
    orient_merged,
    select_joint_lines,
)
from sfs_axes.meridian import normal_cost, profile_thickness_cost
from sfs_axes.normalized import is_base_fragment
from sfs_axes.select import orient_base_axis, select_union_lines

Z = np.array([0.0, 0.0, 1.0])
X = np.array([1.0, 0.0, 0.0])
Y = np.array([0.0, 1.0, 0.0])
EMPTY = np.zeros((6, 0))


def line(d, p=(0.0, 0.0, 0.0)):
    v = np.zeros(6)
    v[0:3] = np.asarray(d, dtype=float)
    v[3:6] = np.asarray(p, dtype=float)
    return v


def result(*dirs, costs=None):
    if not dirs:
        return EMPTY, np.zeros(0)
    vt = np.column_stack([line(d) for d in dirs])
    c = (np.arange(1.0, len(dirs) + 1.0) if costs is None
         else np.asarray(costs, dtype=float))
    return vt, c


def res_of(*vs, costs=None):
    vt = np.column_stack(vs)
    c = (np.arange(1.0, len(vs) + 1.0) if costs is None
         else np.asarray(costs, dtype=float))
    return vt, c


def merged(res_normal, res_thickness, res_shipped, C=EMPTY, **kw):
    """The production body of the selector's tail: merge, then orient once."""
    return orient_merged(merge_lines(res_normal, res_thickness, res_shipped, **kw), C)


def tilted(deg):
    a = np.radians(deg)
    return np.array([np.sin(a), 0.0, np.cos(a)])


def pot(R_inner=30.0, R_outer=33.0, zmax=20.0, n_az=90, n_z=20):
    """Two concentric walls about +z: points (3, N) and outward normals (3, N)."""
    pts, nrm = [], []
    for R in (R_inner, R_outer):
        th = np.linspace(0.0, 2.0 * np.pi, n_az, endpoint=False)
        zs = np.linspace(-zmax, zmax, n_z)
        T, Zg = np.meshgrid(th, zs, indexing="ij")
        pts.append(np.vstack([R * np.cos(T).ravel(), R * np.sin(T).ravel(),
                              Zg.ravel()]))
        nrm.append(np.vstack([np.cos(T).ravel(), np.sin(T).ravel(),
                              np.zeros(T.size)]))
    return np.vstack([np.hstack(pts), np.hstack(nrm)])


def base_cloud(flip_normals=False):
    """A synthetic base sherd: 400-point cap disk at z=0 plus a 120-point wall.

    All points lie within r < 25 mm of the z axis, 400/520 have axial normals, the
    azimuthal span is 360 deg and the axial extent is 40 mm, so is_base_fragment
    accepts the z line through the centroid.
    """
    rng = np.random.default_rng(0)
    n_disk = 400
    r = 20.0 * np.sqrt(rng.uniform(0.0, 1.0, n_disk))
    th = rng.uniform(0.0, 2.0 * np.pi, n_disk)
    P1 = np.vstack([r * np.cos(th), r * np.sin(th), np.zeros(n_disk)])
    N1 = np.vstack([np.zeros(n_disk), np.zeros(n_disk), np.ones(n_disk)])
    n_wall = 120
    th2 = rng.uniform(0.0, 2.0 * np.pi, n_wall)
    zz = rng.uniform(-40.0, -5.0, n_wall)
    P2 = np.vstack([20.0 * np.cos(th2), 20.0 * np.sin(th2), zz])
    N2 = np.vstack([np.cos(th2), np.sin(th2), np.zeros(n_wall)])
    P = np.hstack([P1, P2])
    N = np.hstack([N1, N2])
    if flip_normals:
        N = -N
    return np.vstack([P, N])


@pytest.fixture()
def stub(monkeypatch):
    def install(res_normal, res_thickness, res_shipped):
        monkeypatch.setattr(joint, "normal_arm", lambda *a, **k: res_normal)
        monkeypatch.setattr(joint, "thickness_arm", lambda *a, **k: res_thickness)
        monkeypatch.setattr(joint, "select_union_lines", lambda *a, **k: res_shipped)
    return install


# ---------------------------------------------------------------- ordering


def test_normal_rank0_is_first():
    out = merged(result(Z, X), result(Y), result(tilted(50.0)))
    assert out is not None
    lines, costs = out
    assert lines.shape[1] == 3
    assert direction_angle_deg(lines[0:3, 0], Z) < 1e-9
    assert costs.shape == (3,)


def test_thickness_is_appended_before_the_shipped_rank0():
    out = merged(result(Z), result(X), result(Y))
    lines, _ = out
    assert lines.shape[1] == 3
    assert direction_angle_deg(lines[0:3, 0], Z) < 1e-9
    assert direction_angle_deg(lines[0:3, 1], X) < 1e-9
    assert direction_angle_deg(lines[0:3, 2], Y) < 1e-9


def test_shipped_rank0_is_dropped_when_it_agrees_with_a_kept_line():
    out = merged(result(Z), result(X), result(tilted(2.0)))
    lines, _ = out
    assert lines.shape[1] == 2
    assert direction_angle_deg(lines[0:3, 1], X) < 1e-9


def test_shipped_rank0_is_used_when_both_arms_are_missing():
    out = merged(None, None, result(X, Y), include_shipped_secondaries=False)
    lines, _ = out
    assert lines.shape[1] == 1
    assert direction_angle_deg(lines[0:3, 0], X) < 1e-9


# ---------------------------------------------------------------- dedup angle


@pytest.mark.parametrize("dedup", [8.0, 10.0, 15.0])
def test_dedup_boundary_is_the_requested_angle(dedup):
    far = merge_lines(result(Z), result(tilted(dedup + 1.0)), None, dedup_deg=dedup)
    assert far[0].shape[1] == 2
    near = merge_lines(result(Z), result(tilted(dedup - 1.0)), None, dedup_deg=dedup)
    assert near[0].shape[1] == 1


def test_dedup_checks_every_kept_line_not_only_the_first():
    # The thickness candidate is 12 deg from the normal one, so it is kept; the
    # shipped rank-0 is 20 deg from the normal arm (it would pass a test against
    # that line alone) but 8 deg from the thickness line, so it is dropped.
    out = merged(result(Z), result(tilted(12.0)), result(tilted(20.0)),
                 dedup_deg=10.0)
    lines, _ = out
    assert lines.shape[1] == 2
    assert direction_angle_deg(lines[0:3, 1], tilted(12.0)) < 1e-9


# ---------------------------------------------------------------- secondaries


def test_shipped_secondaries_are_scanned_only_when_asked():
    off = merged(result(Z), None, result(Z, X, Y),
                 include_shipped_secondaries=False)
    assert off[0].shape[1] == 1
    on = merged(result(Z), None, result(Z, X, Y),
                include_shipped_secondaries=True)
    lines, _ = on
    assert lines.shape[1] == 3
    assert direction_angle_deg(lines[0:3, 1], X) < 1e-9
    assert direction_angle_deg(lines[0:3, 2], Y) < 1e-9


def test_the_default_includes_the_shipped_secondaries():
    """The shipped variant is the measured winner, so the default is on."""
    out = merged(result(Z), None, result(Z, X, Y))
    assert out[0].shape[1] == 3


# ---------------------------------------------------------------- cap and costs


def test_kmax_caps_at_three():
    out = merged(result(Z), result(X), result(Y, tilted(60.0)),
                 include_shipped_secondaries=True)
    assert out[0].shape[1] == 3


def test_costs_follow_the_kept_candidates():
    _, costs = merged(result(Z, costs=[7.0]), result(X, costs=[2.5]),
                      result(Y, costs=[9.0]))
    assert np.allclose(costs, [7.0, 2.5, 9.0])


def test_select_joint_lines_writes_at_most_three_lines(stub):
    stub(result(Z), result(X), result(Y, tilted(60.0)))
    C = np.zeros((6, 1))
    out = select_joint_lines(None, None, C, C, C, None)
    assert out is not None
    assert out[0].shape[1] == 3


# ---------------------------------------------------------------- fallbacks


def test_missing_normal_arm_uses_thickness_then_shipped():
    out = merged(None, result(X), result(Y), include_shipped_secondaries=False)
    lines, _ = out
    assert lines.shape[1] == 2
    assert direction_angle_deg(lines[0:3, 0], X) < 1e-9
    assert direction_angle_deg(lines[0:3, 1], Y) < 1e-9


def test_missing_arms_keep_the_normal_one():
    assert merged(result(Z), None, None)[0].shape[1] == 1


def test_all_missing_is_none():
    assert merged(None, None, None) is None


def test_empty_candidate_arrays_are_safe():
    assert merged(result(), result(), result()) is None
    assert merged(result(), result(X), result())[0].shape[1] == 1


# ---------------------------------------------------------------- geometry


def test_orient_is_applied_once_and_keeps_the_base_sign():
    C = base_cloud()
    p0 = (0.0, 0.0, float(C[2, :].mean()))
    assert is_base_fragment(C, line(Z, p0)) is True
    up = merged(res_of(line(Z, p0)), None, None, C)[0]
    assert up[2, 0] < 0.0, "orient_base_axis must point the base sherd base -> rim"
    down = merged(res_of(line(-Z, p0)), None, None, C)[0]
    assert down[2, 0] < 0.0, "an inverted base disk must not be canonicalized"
    assert np.allclose(up, down)


def test_orient_does_not_touch_wall_columns():
    C = base_cloud()
    p0 = (0.0, 0.0, float(C[2, :].mean()))
    out = merged(res_of(line(Z, p0)), res_of(line(X, p0)), None, C)
    lines, costs = out
    assert lines.shape[1] == 2 and costs.shape == (2,)
    # the wall line is untouched by the base-sherd orientation; only the base line's
    # sign is decided
    assert np.allclose(lines[0:3, 1], X) and np.allclose(
        lines[3:6, 1], (0.0, 0.0, p0[2]))


def test_orient_merged_can_be_switched_off_with_the_shipped_flag():
    C = base_cloud()
    p0 = (0.0, 0.0, float(C[2, :].mean()))
    raw = merge_lines(res_of(line(-Z, p0)), None, None)
    lines, _ = orient_merged(raw, C, base_orient=False)
    assert lines[2, 0] < 0.0
    assert np.allclose(lines, raw[0])


def test_normal_sign_invariance_of_the_arms_costs():
    C = base_cloud()
    Cf = base_cloud(flip_normals=True)
    v = line(Z, (0.0, 0.0, -8.0))
    assert np.isclose(normal_cost(v, C), normal_cost(v, Cf), atol=1e-12)
    assert np.isclose(profile_thickness_cost(v, [C], normal_consistent=True),
                      profile_thickness_cost(v, [Cf], normal_consistent=True),
                      atol=1e-12)


def test_orient_base_axis_is_idempotent_on_the_merged_set():
    C = base_cloud()
    p0 = (0.0, 0.0, float(C[2, :].mean()))
    once = merged(res_of(line(Z, p0)), None, None, C)[0]
    assert np.allclose(once, orient_base_axis(once, C))


# ---------------------------------------------------------------- the switch


def test_switch_off_runs_the_shipped_body(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("tri_select=False must not enter the joint selector")

    monkeypatch.setattr(joint, "select_joint_lines", boom)
    X6 = pot()
    C0, C1 = X6[:, :X6.shape[1] // 2], X6[:, X6.shape[1] // 2:]
    reps = np.column_stack([line(Z), line(tilted(6.0))])
    sizes = np.array([500.0, 400.0])
    vt, c = select_union_lines(reps, sizes, C0, C1, X6, 6, tri_select=False)
    assert vt.shape[0] == 6 and vt.shape[1] >= 1
    assert c.shape[0] == vt.shape[1]
    assert np.all(np.isfinite(vt))


def test_switch_on_dispatches_to_the_joint_selector(monkeypatch):
    sentinel = (np.full((6, 2), 0.5), np.array([1.0, 2.0]))

    def fake(*a, **k):
        return sentinel

    monkeypatch.setattr(joint, "select_joint_lines", fake)
    X6 = np.zeros((6, 4))
    vt, c = select_union_lines(None, None, X6, X6, X6, 6, tri_select=True)
    assert np.allclose(vt, sentinel[0]) and np.allclose(c, sentinel[1])


def test_switch_default_is_on_and_read_at_import():
    """SFS_AXES_TRI_SELECT defaults to 1 and is read when the module loads."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    code = "import sfs_axes.select as s; print(s.TRI_SELECT)"
    env = dict(os.environ)
    env.pop("SFS_AXES_TRI_SELECT", None)
    on = subprocess.run([sys.executable, "-c", code], cwd=root, env=env,
                        capture_output=True, text=True)
    assert on.stdout.strip() == "True"
    env["SFS_AXES_TRI_SELECT"] = "0"
    off = subprocess.run([sys.executable, "-c", code], cwd=root, env=env,
                         capture_output=True, text=True)
    assert off.stdout.strip() == "False"
