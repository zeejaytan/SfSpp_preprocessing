"""Axis file I/O — replaces read_axis.m + write_axis.m + extract_axis.m save (G3).

Single ORIG-compatible convention (no Plt_/Pot_/axis_output variants):
  Axes/Pot_A_Piece_0i_Axis.xyz, ascii K x 6, position-first
  (px py pz dx dy dz, position mm + unit direction, row 1 = best/lowest cost).

This is what the untouched assembly BreakLine::ReadAxis parses
(structure-from-sherds-pp class/data_structure.cpp:146-187: operator>> reads
six doubles per line; each line = one axis candidate). In-memory convention
stays MATLAB-like: vt (6, K) = [direction; position].
"""

import numpy as np


def axis_filename(pot_id, frag_id):
    """Assembly-layout axis file name (data_path.h:1417-1426)."""
    return "Pot_%s_Piece_%02d_Axis.xyz" % (pot_id, frag_id)


def write_axes(path, vt):
    """Write vt (6, K) [dir; pos] as K x 6 position-first, %.12f (extract_axis.m:24)."""
    vt = np.asarray(vt, dtype=float)
    if vt.ndim == 1:
        vt = vt[:, None]
    pos_first = vt[np.r_[3:6, 0:3], :].T  # (K, 6)
    with open(path, "w") as fh:
        for row in pos_first:
            fh.write("%.12f %.12f %.12f %.12f %.12f %.12f\n" % tuple(row))


def read_axes(path):
    """Read an axis file -> vt (6, K) [dir; pos]. Mirrors ReadAxis parsing."""
    arr = np.loadtxt(path, dtype=float)
    if arr.ndim == 1:
        arr = arr[None, :]
    if arr.shape[1] != 6:
        raise ValueError("axis file %s: expected 6 columns, got %s"
                         % (path, arr.shape))
    return arr.T[np.r_[3:6, 0:3], :]  # back to [dir; pos]


def split_axis(vt):
    """vt (6,) -> (direction (3,) unit, position (3,))."""
    vt = np.asarray(vt, dtype=float).reshape(6)
    d = vt[0:3] / np.linalg.norm(vt[0:3])
    return d, vt[3:6]


def direction_angle_deg(a, b):
    """Unsigned angle between directions in degrees (sign-agnostic)."""
    a = np.asarray(a, dtype=float).reshape(3)
    b = np.asarray(b, dtype=float).reshape(3)
    c = np.clip(abs(a @ b) / (np.linalg.norm(a) * np.linalg.norm(b)), -1, 1)
    return float(np.degrees(np.arccos(c)))


def radial_axial_errors(new_pos, ref_dir, ref_pos):
    """Position error decomposed vs reference axis: (radial, axial) mm."""
    new_pos = np.asarray(new_pos, dtype=float).reshape(3)
    ref_dir = np.asarray(ref_dir, dtype=float).reshape(3)
    ref_dir = ref_dir / np.linalg.norm(ref_dir)
    ref_pos = np.asarray(ref_pos, dtype=float).reshape(3)
    delta = new_pos - ref_pos
    axial = float(ref_dir @ delta)
    radial = float(np.linalg.norm(delta - axial * ref_dir))
    return radial, abs(axial)
