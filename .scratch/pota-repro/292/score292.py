#!/usr/bin/env python3
"""score292.py -- score one exported breakline lane against the authors' lane of the SAME index.

Semantics are those of tickets 266/287/289/290 and are deliberately fixed (ticket 292):

  median    50th percentile, in mm, of the distance from each of OUR dots to the nearest AUTHOR dot
  cov_ours  % of OUR dots under 2.0 mm
  cov_auth  % of AUTHOR dots with one of ours under 2.0 mm (one-way coverage lets a short stub on
            the line score 100, so both directions are reported)
  jumps     consecutive exported steps over 10 mm
  max_step  the largest consecutive step, in mm
  at_bar    median <= 2.0 AND cov_ours >= 90

Usage:
  score292.py <pot> <piece> <lane 0|1> <ours.pcd> <author.pcd>
  score292.py --selftest

Prints one tab-separated row (no header):
  pot piece lane n_ours n_auth median cov_ours cov_auth jumps max_step len_ours len_auth at_bar
"""
import sys

import numpy as np
from scipy.spatial import cKDTree


def read_pcd(path):
    """Return an (n, 3) float array from an ascii or binary PCD, whatever the field order."""
    with open(path, 'rb') as f:
        header = []
        while True:
            line = f.readline()
            if not line:
                raise ValueError('truncated header: %s' % path)
            header.append(line.decode('ascii', 'replace').strip())
            if line.startswith(b'DATA'):
                break
        fields, sizes, types, counts, n, mode = None, None, None, None, None, None
        for line in header:
            parts = line.split()
            if not parts:
                continue
            if parts[0] == 'FIELDS':
                fields = parts[1:]
            elif parts[0] == 'SIZE':
                sizes = [int(x) for x in parts[1:]]
            elif parts[0] == 'TYPE':
                types = parts[1:]
            elif parts[0] == 'COUNT':
                counts = [int(x) for x in parts[1:]]
            elif parts[0] == 'WIDTH':
                n = int(parts[1])
            elif parts[0] == 'DATA':
                mode = parts[1]
        if fields is None or n is None or mode is None:
            raise ValueError('no FIELDS/WIDTH/DATA in %s' % path)
        if 'x' not in fields or 'y' not in fields or 'z' not in fields:
            raise ValueError('no x/y/z in %s' % path)
        if mode == 'ascii':
            body = f.read().decode('ascii', 'replace').split()
            values = np.array([float(v) for v in body[:n * len(fields)]], dtype=np.float64)
            table = values.reshape(n, len(fields))
            return table[:, [fields.index('x'), fields.index('y'), fields.index('z')]]
        if mode != 'binary':
            raise ValueError('unsupported DATA %s in %s' % (mode, path))
        kind = {'F': 'f', 'U': 'u', 'I': 'i'}[types[0][0].upper()]
        width = sizes[0]
        packed = np.dtype([(nm, '<' + kind + str(width)) for nm in fields])
        raw = f.read(n * packed.itemsize)
        table = np.frombuffer(raw, dtype=packed, count=n)
        return np.vstack([table['x'], table['y'], table['z']]).T.astype(np.float64)


def polyline_length(points):
    if len(points) < 2:
        return 0.0
    return float(np.sum(np.linalg.norm(np.diff(points, axis=0), axis=1)))


def score(ours, author, bar_median=2.0, bar_coverage=90.0, jump_mm=10.0):
    steps = np.linalg.norm(np.diff(ours, axis=0), axis=1) if len(ours) > 1 else np.zeros(0)
    jumps = int(np.sum(steps > jump_mm))
    max_step = float(steps.max()) if len(steps) else 0.0
    if len(ours) == 0 or len(author) == 0:
        return dict(n_ours=len(ours), n_auth=len(author), median=float('nan'), cov_ours=0.0,
                    cov_auth=0.0, jumps=jumps, max_step=max_step,
                    len_ours=polyline_length(ours), len_auth=polyline_length(author), at_bar='no')
    d_ours, _ = cKDTree(author).query(ours)
    d_auth, _ = cKDTree(ours).query(author)
    median = float(np.median(d_ours))
    cov_ours = 100.0 * float(np.mean(d_ours < 2.0))
    cov_auth = 100.0 * float(np.mean(d_auth < 2.0))
    at_bar = 'yes' if (median <= bar_median and cov_ours >= bar_coverage) else 'no'
    return dict(n_ours=len(ours), n_auth=len(author), median=median, cov_ours=cov_ours,
                cov_auth=cov_auth, jumps=jumps, max_step=max_step,
                len_ours=polyline_length(ours), len_auth=polyline_length(author), at_bar=at_bar)


def selftest():
    """Two hand-built lanes with known answers, so a silent misread cannot pass for a result."""
    rng = np.random.default_rng(292)
    t = np.linspace(0.0, 2.0 * np.pi, 400, endpoint=False)
    ring = np.vstack([100.0 * np.cos(t), 100.0 * np.sin(t), np.zeros_like(t)]).T
    shifted = ring.copy()
    shifted[:, 0] += 1.0                      # exactly 1.0 mm outward
    result = score(shifted, ring)
    assert result['n_ours'] == 400 and result['n_auth'] == 400, result
    assert 0.98 <= result['median'] <= 1.02, result        # 1 mm offset, ring spacing 1.57 mm
    assert result['cov_ours'] == 100.0 and result['cov_auth'] == 100.0, result
    assert result['jumps'] == 0 and result['at_bar'] == 'yes', result
    stub = ring[:20]
    result = score(stub, ring)
    assert result['cov_auth'] < 10.0, result               # the stub covers 5% of the ring
    broken = ring.copy()
    broken[200:, 0] += 40.0
    result = score(broken, ring)
    assert result['jumps'] == 1 or result['jumps'] == 2, result
    print('selftest ok')


def main(argv):
    if len(argv) == 2 and argv[1] == '--selftest':
        selftest()
        return 0
    if len(argv) != 6:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    pot, piece, lane, ours_path, author_path = argv[1:6]
    if lane not in ('0', '1'):
        print('lane must be 0 or 1', file=sys.stderr)
        return 2
    result = score(read_pcd(ours_path), read_pcd(author_path))
    print('\t'.join([pot, piece, lane] + [
        str(result['n_ours']), str(result['n_auth']), '%.3f' % result['median'],
        '%.2f' % result['cov_ours'], '%.2f' % result['cov_auth'], str(result['jumps']),
        '%.3f' % result['max_step'], '%.3f' % result['len_ours'], '%.3f' % result['len_auth'],
        result['at_bar']]))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
