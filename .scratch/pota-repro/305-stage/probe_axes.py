#!/usr/bin/env python3
"""probe_axes.py RELEASED CANDIDATE... : print every candidate line's angle (deg) to every
released line, plus K.  Lines are 6 numbers: position(3) direction(3)."""
import sys, numpy as np

def readlines(p):
    out = []
    for ln in open(p):
        f = ln.split()
        if len(f) >= 6:
            out.append(np.array([float(x) for x in f[:6]]))
    return out

def ang(a, b):
    a = a / np.linalg.norm(a); b = b / np.linalg.norm(b)
    c = abs(float(np.dot(a, b)))
    return np.degrees(np.arccos(min(1.0, c)))

def main():
    rel = readlines(sys.argv[1])
    print("released lines: %d" % len(rel))
    for p in sys.argv[2:]:
        c = readlines(p)
        if not c:
            print("%-70s EMPTY" % p.split("/")[-1]); continue
        cells = []
        for q in c:
            best = min(ang(q[3:], r[3:]) for r in rel)
            cells.append("%.2f" % best)
        print("%-70s K=%d  angles=%s" % ("/".join(p.split("/")[-3:-1]), len(c), " ".join(cells)))

main()
