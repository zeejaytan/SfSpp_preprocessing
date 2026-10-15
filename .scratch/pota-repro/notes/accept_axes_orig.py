"""POTA-05 ORIG-first acceptance: 8 pieces x seeds (0,1,2), paper step=10.

Compares recomputed best axes vs NURBS anchors (piece-local frames):
  (a) direction <= 5 deg, radial/axial <= 2 mm; 8/8 files load.
  (b) strict-gate-(b): per-point (h,r) profile under recomputed vs anchor
      frames: median|dh| <= 2.0mm, median|dr| <= 2.0mm, cos(angle) > 0.85.
      (task3_gate_probe.py takes no axes input, so the gate is re-expressed
      in axis frames; the ORIG-vs-ORIG 15/15 control is re-run verbatim.)
  (c) rim >= 7/8: a rim segment exists with std(h)<1.0mm, std(r)<1.0mm,
      len>=20 (check_base_and_rim.m:116-122 thresholds), reported under
      both recomputed and anchor axes.
Also reports seed stability (max pairwise best-axis angle across seeds).

Usage: python accept_axes_orig.py   (run from repo root or anywhere)
Writes axes to .scratch/pota-repro/notes/accept_out/seed<N>/.
"""

import os
import sys

import numpy as np

REPO = r"C:\PR\SfSpp_preprocessing"
sys.path.insert(0, REPO)

from sfs_axes.cli import extract_piece  # noqa: E402
from sfs_axes.io_axes import (direction_angle_deg, radial_axial_errors,  # noqa: E402
                              read_axes)

ORIG = r"C:\Users\hermi\AppData\Local\Temp\swaptest\orig"
ANCHOR = REPO + r"\NURBS_Dataset_20251103\SfS_pp\Axes\Pot_A_Piece_%02d_NURBS_Axis.xyz"
ORIG_BL = (REPO + r"\artifacts\untouched_pota_verify_20261015\task3_orig_bl"
           r"\Pot_A_Piece_%02d_Breakline_0.pcd")
OUT = REPO + r"\.scratch\pota-repro\notes\accept_out"
SEEDS = (0, 1, 2)
PIECES = range(1, 9)


def load_anchor(piece):
    arr = np.loadtxt(ANCHOR % piece, dtype=float)
    if arr.ndim == 1:
        arr = arr[None, :]
    rows = []
    for row in arr:  # position-first file -> [dir; pos] vt rows
        rows.append(np.r_[row[3:6], row[0:3]])
    return rows  # list of (6,) vt; row 0 = reference


def load_breakline(path):
    lines = open(path).read().splitlines()
    segs = []
    for ln in lines[2:]:
        if ln.startswith("#"):
            a = list(map(int, ln[1:].split()))
            if len(a) >= 3:
                segs.append((a[0] - 1, a[1] - 1))
        else:
            break
    rows = []
    for ln in lines:
        s = ln.split()
        if len(s) >= 6 and not ln.startswith(
                ("#", "VERSION", "FIELDS", "SIZE", "TYPE", "COUNT",
                 "WIDTH", "HEIGHT", "VIEWPOINT", "POINTS", "DATA")):
            try:
                rows.append([float(x) for x in s[:6]])
            except ValueError:
                pass
    pts = np.array(rows)
    if not segs and len(pts):
        segs = [(0, len(pts) - 1)]  # segment-less file: whole-cloud fallback
    return segs, pts


def hr_profile(pts_xyz, vt):
    d = vt[0:3] / np.linalg.norm(vt[0:3])
    rel = pts_xyz - vt[3:6]
    h = rel @ d
    r = np.linalg.norm(rel - np.outer(h, d), axis=1)
    return h, r


def main():
    os.makedirs(OUT, exist_ok=True)
    best = {}  # (seed, piece) -> vt (6, K)
    for seed in SEEDS:
        sdir = os.path.join(OUT, "seed%d" % seed)
        os.makedirs(sdir, exist_ok=True)
        for p in PIECES:
            vt = extract_piece(ORIG, sdir, "A", p, seed=seed, step=10,
                               adaptive=False, truncate=True, verbose=False)
            best[(seed, p)] = vt

    print("\n== (a) anchor comparison, seed 0 ==")
    n_load = 0
    for p in PIECES:
        vt = best[(0, p)][:, 0]
        anch = load_anchor(p)[0]
        n_load += 1
        ang = direction_angle_deg(vt[0:3], anch[0:3])
        rad, axi = radial_axial_errors(vt[3:6], anch[0:3], anch[3:6])
        print("p%02d K=%d ang=%.3fdeg radial=%.3fmm axial=%.3fmm %s"
              % (p, best[(0, p)].shape[1], ang, rad, axi,
                 "PASS" if (ang <= 5 and rad <= 2 and axi <= 2) else "FAIL"))

    print("\n== seed stability: max pairwise best-axis angle ==")
    for p in PIECES:
        ds = [best[(s, p)][0:3, 0] for s in SEEDS]
        m = max(direction_angle_deg(a, b) for a in ds for b in ds)
        print("p%02d maxspread=%.3fdeg" % (p, m))

    print("\n== (b) strict-gate-(b): (h,r) frame agreement, seed 0 ==")
    for p in PIECES:
        vt = best[(0, p)][:, 0]
        anch = load_anchor(p)[0]
        _segs, pts = load_breakline(ORIG_BL % p)
        h1, r1 = hr_profile(pts[:, :3], vt)
        h0, r0 = hr_profile(pts[:, :3], anch)
        mh, mr = float(np.median(np.abs(h1 - h0))), float(np.median(np.abs(r1 - r0)))
        cosv = float(abs(vt[0:3] @ anch[0:3]) / (np.linalg.norm(vt[0:3]) *
                                                np.linalg.norm(anch[0:3])))
        ok = mh <= 2.0 and mr <= 2.0 and cosv > 0.85
        print("p%02d n=%d med|dh|=%.3f med|dr|=%.3f cos=%.4f %s"
              % (p, len(pts), mh, mr, cosv, "HELD" if ok else "BROKEN"))

    print("\n== (c) rim coherence, seed 0 (thresholds: std_h<1 std_r<1 len>=20) ==")
    for p in PIECES:
        vt = best[(0, p)][:, 0]
        anch = load_anchor(p)[0]
        segs, pts = load_breakline(ORIG_BL % p)
        h1, r1 = hr_profile(pts[:, :3], vt)
        h0, r0 = hr_profile(pts[:, :3], anch)
        found = False
        for (a, b) in segs:
            if b - a + 1 < 20:
                continue
            sh, sr = float(np.std(h1[a:b + 1])), float(np.std(r1[a:b + 1]))
            if sh < 1.0 and sr < 1.0:
                ah = float(np.median(np.abs(h1[a:b + 1] - h0[a:b + 1])))
                ar = float(np.median(np.abs(r1[a:b + 1] - r0[a:b + 1])))
                print("p%02d seg[%d:%d] len=%d std_h=%.3f std_r=%.3f "
                      "agree(dh=%.3f dr=%.3f) RIM-PASS"
                      % (p, a, b, b - a + 1, sh, sr, ah, ar))
                found = True
                break
        if not found:
            print("p%02d NO coherent rim segment RIM-FAIL" % p)
    print("\nloaded %d/8 axis files" % n_load)


if __name__ == "__main__":
    main()
