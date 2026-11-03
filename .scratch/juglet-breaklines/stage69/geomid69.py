#!/usr/bin/env python3
"""geomid69.py -- ticket 69 Part D: the RESTATED geometry-identity gate.

An md5 of the lane .pcd is NOT a valid test. Two runs of the SAME arm already differ in md5
(lead's job 34275026: unset_a vs unset_b, both 203 dots, different md5), because the writer
emits the normal columns and a curvature column that are not bit-stable. So identity is
measured on the GEOMETRY, in the three parts the ticket's gate now names:

  (a) identical dot COUNTS            -> dots_a, dots_b
  (b) identical POSITION columns      -> max_pos_mm (row-by-row, same order) and pos_md5
  (c) identical header POINTS field   -> points_hdr_a, points_hdr_b
and, reported as a MEASURED NUMBER rather than a verdict, the normal-column delta in degrees.

Usage: geomid69.py A.pcd B.pcd   ->   one tab-separated line:
  dots_a dots_b pos_md5_a pos_md5_b max_pos_mm norm_med_deg norm_max_deg points_hdr_a points_hdr_b same_counts same_positions
"""
import hashlib, sys
import numpy as np


def read_pcd(path):
    """(n,6) xyz+normal and the header POINTS field, ascii or binary PCD."""
    hdr, points_hdr, data_start, fields, sizes, types, counts = {}, None, None, [], [], [], []
    with open(path, 'rb') as f:
        raw = f.read()
    pos = 0
    while True:
        nl = raw.find(b'\n', pos)
        if nl < 0:
            raise SystemExit('no DATA line in ' + path)
        line = raw[pos:nl].decode('utf-8', 'replace').strip()
        pos = nl + 1
        up = line.upper()
        if up.startswith('POINTS'):
            points_hdr = int(line.split()[1])
        elif up.startswith('FIELDS'):
            fields = line.split()[1:]
        elif up.startswith('SIZE'):
            sizes = [int(v) for v in line.split()[1:]]
        elif up.startswith('TYPE'):
            types = line.split()[1:]
        elif up.startswith('COUNT'):
            counts = [int(v) for v in line.split()[1:]]
        elif up.startswith('DATA'):
            data_start = pos
            fmt = line.split()[1].lower()
            break
    if not counts:
        counts = [1] * len(fields)
    n = points_hdr
    if fmt == 'ascii':
        rows = []
        for ln in raw[data_start:].decode('utf-8', 'replace').splitlines():
            s = ln.split()
            if len(s) < 6:
                continue
            rows.append([float(v) for v in s[:6]])
        return np.asarray(rows, float), points_hdr, fmt
    # binary: only the 6 columns this project writes (x y z normal_x normal_y normal_z curvature)
    dt = []
    for nm, sz, ty, ct in zip(fields, sizes, types, counts):
        base = {'F': 'f', 'U': 'u', 'I': 'i'}[ty]
        dt.append((nm, ('<' if base != 'u' else '<u') + str(sz), (ct,)))
    arr = np.frombuffer(raw[data_start:], dtype=np.dtype(dt), count=n)
    out = np.zeros((n, 6))
    for k, nm in enumerate(('x', 'y', 'z', 'normal_x', 'normal_y', 'normal_z')):
        out[:, k] = arr[nm]
    return out, points_hdr, fmt


def pos_md5(A):
    return hashlib.md5('\n'.join('%.6f %.6f %.6f' % tuple(r) for r in A[:, :3]).encode()).hexdigest()


def normal_angles(A, B):
    """Angle (deg) between the two normal columns, row by row."""
    a = A[:, 3:6]
    b = B[:, 3:6]
    na = np.linalg.norm(a, axis=1)
    nb = np.linalg.norm(b, axis=1)
    ok = (na > 0) & (nb > 0)
    if not ok.any():
        return float('nan'), float('nan')
    c = np.clip((a[ok] * b[ok]).sum(axis=1) / (na[ok] * nb[ok]), -1.0, 1.0)
    ang = np.degrees(np.arccos(c))
    return float(np.median(ang)), float(np.max(ang))


def main():
    a, b = sys.argv[1], sys.argv[2]
    A, ha, fa = read_pcd(a)
    B, hb, fb = read_pcd(b)
    same_n = len(A) == len(B)
    max_pos = float('nan')
    if same_n and same_n != 0:
        max_pos = float(np.max(np.linalg.norm(A[:, :3] - B[:, :3], axis=1)))
    med, mx = normal_angles(A, B) if same_n and len(A) else (float('nan'), float('nan'))
    same_pos = 'yes' if (same_n and len(A) and max_pos < 5e-7) else 'no'
    print('\t'.join([
        str(len(A)), str(len(B)),
        pos_md5(A) if len(A) else '-', pos_md5(B) if len(B) else '-',
        '%.6f' % max_pos, '%.3f' % med, '%.3f' % mx,
        str(ha), str(hb),
        'yes' if same_n else 'no', same_pos,
    ]))


if __name__ == '__main__':
    main()
