"""Ticket 310 B4 comparison: two packages' axis files, compared to the last bit."""
import argparse
import glob
import os
import sys

import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--label", default="A vs B")
    ap.add_argument("--good", default="")
    a = ap.parse_args()
    good = None
    if a.good and os.path.exists(a.good):
        good = np.asarray(np.loadtxt(a.good, ndmin=2).T, float)[:, 0]
    files = sorted(glob.glob(os.path.join(a.a, "*", "*.npy")))
    if not files:
        print("[cmp] no files under %s" % a.a)
        sys.exit(2)
    worst = 0.0
    nbad = 0
    for fa in files:
        fb = os.path.join(a.b, os.path.relpath(fa, a.a))
        if not os.path.exists(fb):
            print("[cmp] MISSING %s" % fb)
            nbad += 1
            continue
        A = np.load(fa)
        B = np.load(fb)
        if A.shape != B.shape:
            print("[cmp] SHAPE %s %s vs %s" % (fa, A.shape, B.shape))
            nbad += 1
            continue
        d = float(np.max(np.abs(A - B))) if A.size else 0.0
        worst = max(worst, d)
        tag = os.path.relpath(fa, a.a)
        extra = ""
        if good is not None:
            ang = [np.degrees(np.arccos(min(1.0, abs(float(
                A[0:3, k] @ good[0:3] / np.linalg.norm(A[0:3, k])
                / np.linalg.norm(good[0:3])))))) for k in range(A.shape[1])]
            extra = " ang_good=" + ",".join("%.2f" % x for x in ang)
        print("[cmp] %-16s K=%d max|dA|=%.3e%s" % (tag, A.shape[1], d, extra))
        if d > 0:
            nbad += 1
    print("[cmp] %s: %d files, max|dA|=%.3e, files differing=%d"
          % (a.label, len(files), worst, nbad))
    print("[cmp] VERDICT: %s" % ("BIT-IDENTICAL" if nbad == 0 else "DIFFERS"))


if __name__ == "__main__":
    main()
