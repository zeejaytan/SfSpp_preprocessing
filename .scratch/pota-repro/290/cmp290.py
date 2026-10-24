#!/usr/bin/env python3
"""Ticket 290 follow-up - two edge runs from identical inputs give the same scores but not the
same file. Where do the bytes differ, and are the point records the same?

Usage: cmp290.py <fileA> <fileB>
"""
import hashlib
import sys

import numpy as np


def split_header(p):
    lines = []
    with open(p, "rb") as f:
        for raw in f:
            lines.append(raw)
            if raw.startswith(b"DATA"):
                break
    return lines


def readpts(p):
    pts = []
    with open(p, "r", errors="ignore") as f:
        started = False
        for line in f:
            if not started:
                if line.startswith("DATA"):
                    started = True
                continue
            s = line.split()
            if len(s) >= 3:
                pts.append((float(s[0]), float(s[1]), float(s[2])))
    return np.array(pts, dtype=float).reshape(-1, 3)


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def main():
    a, b = sys.argv[1], sys.argv[2]
    ha, hb = split_header(a), split_header(b)
    print("[FILE] A %s bytes=%d md5=%s" % (a, len(open(a, "rb").read()), md5(a)))
    print("[FILE] B %s bytes=%d md5=%s" % (b, len(open(b, "rb").read()), md5(b)))
    print("[HEADER] lines A=%d B=%d identical=%s" % (len(ha), len(hb), ha == hb))
    if ha != hb:
        for i, (la, lb) in enumerate(zip(ha, hb)):
            if la != lb:
                print("[HEADER] first differing line %d: A=%r B=%r" % (i + 1, la, lb))
                break
    pa, pb = readpts(a), readpts(b)
    print("[POINTS] n A=%d B=%d" % (len(pa), len(pb)))
    if len(pa) == len(pb):
        print("[POINTS] same order bytewise-equal=%s  max|dxyz| ordered=%.6f"
              % (np.array_equal(pa, pb), float(np.abs(pa - pb).max())))
        sa = pa[np.lexsort((pa[:, 2], pa[:, 1], pa[:, 0]))]
        sb = pb[np.lexsort((pb[:, 2], pb[:, 1], pb[:, 0]))]
        print("[POINTS] same set after sorting=%s" % np.array_equal(sa, sb))
        da = np.sqrt(((pa[:, None, :] - pb[None, :, :]) ** 2).sum(-1)).min(axis=1)
        db = np.sqrt(((pb[:, None, :] - pa[None, :, :]) ** 2).sum(-1)).min(axis=1)
        print("[POINTS] nearest-neighbour A->B max %.6f mean %.6f | B->A max %.6f mean %.6f mm"
              % (da.max(), da.mean(), db.max(), db.mean()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
