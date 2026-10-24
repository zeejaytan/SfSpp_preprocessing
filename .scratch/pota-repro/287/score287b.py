#!/usr/bin/env python3
"""Ticket 287 OPTIONAL probe: before-vs-after identity on the AUTHORS' own surfaces.

Identity evidence only. These lanes reproduce no bar number: every bar in the ticket was measured
on OUR sheets from OUR mesh stage. Lane scores against the authors' own breakline dots are printed
as BEHAVIOUR, not as bar results, for the same reason.
"""
import sys, os, importlib.util, math

OUT = os.environ["OUT"]
LANES = [("D03", "Pot_D_Piece_03"), ("B01", "Pot_B_Piece_01")]
AUTHB = "/data/gpfs/projects/punim2657/sfs_main/original_samples_backup/SfS_pp"
SP = "/data/gpfs/projects/punim2657/SfSpp/runs/20261024-0329_1308298_p275-walker/score275.py"

def pure_readpts(p):
    pts, started = [], False
    with open(p, "r", errors="ignore") as f:
        for line in f:
            if not started:
                if line.startswith("DATA"):
                    started = True
                continue
            s = line.split()
            if len(s) >= 3:
                pts.append((float(s[0]), float(s[1]), float(s[2])))
    return pts

def pure_nn(src, dst):
    return [min(math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2) for b in dst) for a in src]

def pure_lane(o, a):
    dn_o, dn_a = pure_nn(o, a), pure_nn(a, o)
    srt = sorted(dn_o); med = srt[len(srt) // 2]
    steps = [math.sqrt(sum((o[i+1][k]-o[i][k])**2 for k in range(3))) for i in range(len(o)-1)] or [0.0]
    cov_o = 100.0 * sum(1 for d in dn_o if d < 2.0) / len(dn_o)
    cov_a = 100.0 * sum(1 for d in dn_a if d < 2.0) / len(dn_a)
    return len(o), med, cov_o, cov_a, sum(1 for s in steps if s > 10.0), max(steps), (med <= 2.0 and cov_o >= 90.0)

mode = "score275.py (project scorer)"
try:
    import numpy as np
    spec = importlib.util.spec_from_file_location("s275", SP)
    m = importlib.util.module_from_spec(spec)
    sys.argv = ["x", "/nonexistent"]
    try:
        spec.loader.exec_module(m)
    except SystemExit:
        pass
    readpts, lane = m.readpts, m.lane
except Exception as exc:
    mode = "PURE-PYTHON FALLBACK (identical formulas): %r" % (exc,)
    readpts, lane = pure_readpts, pure_lane

def cmp_pts(p, q):
    a, b = readpts(p), readpts(q)
    if len(a) != len(b):
        return len(a), len(b), -1.0
    d = 0.0
    for i in range(len(a)):
        for k in range(3):
            e = abs(float(a[i][k]) - float(b[i][k]))
            if e > d:
                d = e
    return len(a), len(b), d

print("scorer: %s" % mode)
print("out dir: %s   (authors' sheets; IDENTITY evidence only)" % OUT)
print("\n== identity: before vs after, pointwise ==")
for lab, piece in LANES:
    for st in (0, 1):
        f = "_Breakline_%d.pcd" % st
        pb = os.path.join(OUT, "%s_before" % lab, piece + f)
        pa = os.path.join(OUT, "%s_after" % lab, piece + f)
        if not (os.path.exists(pb) and os.path.exists(pa)):
            print("%s\tBl%d\tMISSING PAIR" % (lab, st)); continue
        n1, n2, d = cmp_pts(pb, pa)
        print("%s\tBl%d\tn_before=%d\tn_after=%d\tmax_dxyz=%.6f\t%s" % (lab, st, n1, n2, d, "identical" if (n1 == n2 and d == 0.0) else "DIFFERS"))
print("\n== BEHAVIOUR ONLY (authors' surfaces vs authors' breakline dots; NOT bar evidence) ==")
for lab, piece in LANES:
    for st in (0, 1):
        ap = os.path.join(AUTHB, "Breaklines", "%s_Breakline_%d.pcd" % (piece, st))
        for arm in ("before", "after"):
            f = os.path.join(OUT, "%s_%s" % (lab, arm), "%s_Breakline_%d.pcd" % (piece, st))
            if not os.path.exists(f) or not os.path.exists(ap):
                print("%s\tBl%d\t%s\tMISSING" % (lab, st, arm)); continue
            o, a = readpts(f), readpts(ap)
            if len(o) == 0:
                print("%s\tBl%d\t%s\tEMPTY OUTPUT" % (lab, st, arm)); continue
            n, med, co, ca, j, mx, ok = lane(o, a)
            print("%s\tBl%d\t%s\tn=%d\tmed=%.3f\tcov_o=%.2f\tcov_a=%.2f\tjmp=%d\tmaxstep=%.3f" % (lab, st, arm, n, med, co, ca, j, mx))
