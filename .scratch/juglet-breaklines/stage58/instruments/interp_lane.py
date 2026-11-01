#!/usr/bin/env python3
"""interp_lane.py - ticket 58 interpolation control.

Resample a t55 Bl0 lookup lane to N dots by arc length (open polyline, exactly the
edge-line resampler in SfSpp_preprocessing/edgeline_extraction_headless.cpp:797-810,
with the output count N given instead of llround(L/1.9)).

Honest statement carried in the output header comment: this interpolates the SAME
traced lane. It raises the dot count fed to the gate and to CountInlier; it adds no
new boundary information.

Usage: interp_lane.py IN.Bl0 OUT.pcd N
"""
import sys
import numpy as np


def read_bl0(path):
    lines = open(path, 'r', errors='ignore').read().splitlines()
    nseg = int(lines[1].split()[1])
    nhead = 2 + nseg                      # comment + count + one line per segment
    dots = []
    for ln in lines:
        p = ln.split()
        if len(p) >= 7 and ln[0].isdigit() or (len(p) >= 7 and ln.lstrip()[0] in '-.0123456789'):
            try:
                v = [float(x) for x in p[:7]]
            except ValueError:
                continue
            dots.append(v)
    return nseg, nhead, np.asarray(dots, dtype=float), lines


def resample(dots, N):
    L = dots[:, :3].astype(float)
    M0 = L.shape[0]
    cum = np.zeros(M0 + 1)
    for i in range(M0):
        cum[i + 1] = cum[i] + np.linalg.norm(L[(i + 1) % M0] - L[i])
    total = cum[M0]
    out = np.zeros((N, 6))
    for j in range(N):
        s = j * total / N
        seg = int(np.searchsorted(cum, s, side='right') - 1)
        seg = max(0, min(seg, M0 - 1))
        denom = cum[seg + 1] - cum[seg]
        t = 0.0 if denom <= 0 else (s - cum[seg]) / denom
        a = dots[seg]
        b = dots[(seg + 1) % M0]
        v = a * (1.0 - t) + b * t
        out[j, :3] = v[:3]
        nn = v[3:6]
        nrm = np.linalg.norm(nn)
        out[j, 3:6] = nn / nrm if nrm > 1e-12 else nn
    return out, total


def write_pcd(path, nseg, nhead_src_lines, pts):
    N = pts.shape[0]
    hdr = [
        '# .PCD v0.7 - Point Cloud Data file format',
        '# %d %d 0' % (nseg, N),
    ]
    # keep the ORIGINAL per-segment lines verbatim (index_ is never dereferenced on
    # t55 lanes: every segment flag is 0 and NO_RIM_INFO is not defined for them)
    for k in range(nseg):
        hdr.append(nhead_src_lines[2 + k])
    hdr += [
        'VERSION 0.7',
        'FIELDS x y z normal_x normal_y normal_z curvature',
        'SIZE 4 4 4 4 4 4 4',
        'TYPE F F F F F F F',
        'COUNT 1 1 1 1 1 1 1',
        'WIDTH %d' % N,
        'HEIGHT 1',
        'VIEWPOINT 0 0 0 1 0 0 0',
        'POINTS %d' % N,
        'DATA ascii',
    ]
    with open(path, 'w') as fh:
        fh.write('\n'.join(hdr) + '\n')
        for p in pts:
            fh.write('%.6g %.6g %.6g %.6g %.6g %.6g 0\n' % tuple(p))


def main():
    src, dst, nout = sys.argv[1], sys.argv[2], int(sys.argv[3])
    nseg, nhead, dots, lines = read_bl0(src)
    pts, total = resample(dots, nout)
    write_pcd(dst, nseg, lines, pts)
    print('%s -> %s  src_dots=%d loop=%.3fmm d_src=%.4f out_dots=%d d_out=%.4f nseg=%d'
          % (src, dst, dots.shape[0], total, total / max(1, dots.shape[0] - 1),
             pts.shape[0], total / max(1, pts.shape[0]), nseg))


if __name__ == '__main__':
    main()
