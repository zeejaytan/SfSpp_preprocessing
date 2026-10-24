#!/usr/bin/env python3
"""Ticket 287 reduced gate: score our edge output against the authors' breakline dots.

Primary path: the project scorer itself, score275.py (tickets 266/271/275), loaded as a module
exactly as score_ship.py does. Fallback (only if numpy is missing on the compute node): the same
formulas re-implemented in plain Python -- median = sorted(dn_o)[len//2], coverage = share within
2 mm, jumps = consecutive step > 10 mm, bar = med <= 2.0 and cov_o >= 90.
"""
import sys, os, importlib.util, math, glob

OUT = os.environ["OUT"]
LANES = [("H02", "Pot_H_Piece_02"), ("H10", "Pot_H_Piece_10"),
         ("C01", "Pot_C_Piece_01"), ("J01", "Pot_J_Piece_01")]
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
    out = []
    for a in src:
        out.append(min(math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2) for b in dst))
    return out

def pure_lane(o, a):
    dn_o, dn_a = pure_nn(o, a), pure_nn(a, o)
    srt = sorted(dn_o)
    med = srt[len(srt) // 2]
    cov_o = 100.0 * sum(1 for d in dn_o if d < 2.0) / len(dn_o)
    cov_a = 100.0 * sum(1 for d in dn_a if d < 2.0) / len(dn_a)
    steps = [math.sqrt(sum((o[i+1][k]-o[i][k])**2 for k in range(3))) for i in range(len(o)-1)] or [0.0]
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
    readpts, lane, AUTH = m.readpts, m.lane, m.AUTH
except Exception as exc:
    mode = "PURE-PYTHON FALLBACK (identical formulas), numpy/scorer unavailable: %r" % (exc,)
    readpts, lane = pure_readpts, pure_lane
    AUTH = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Breaklines/%s_Breakline_%d.pcd"

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
print("out dir: %s" % OUT)
rows, ident = [], []
for lab, piece in LANES:
    for st in (0, 1):
        ap = AUTH % (piece, st)
        for arm in ("before", "after"):
            f = os.path.join(OUT, "%s_%s" % (lab, arm), "%s_Breakline_%d.pcd" % (piece, st))
            if not os.path.exists(f):
                rows.append("%s\tBl%d\t%s\tMISSING OUTPUT" % (lab, st, arm)); continue
            if not os.path.exists(ap):
                rows.append("%s\tBl%d\t%s\tMISSING AUTHOR %s" % (lab, st, arm, ap)); continue
            o, a = readpts(f), readpts(ap)
            if len(o) == 0:
                rows.append("%s\tBl%d\t%s\tEMPTY" % (lab, st, arm)); continue
            n, med, co, ca, j, mx, ok = lane(o, a)
            rows.append("%s\tBl%d\t%s\tn=%d\tmed=%.3f\tcov_o=%.2f\tcov_a=%.2f\tjmp=%d\tmaxstep=%.3f\t%s"
                        % (lab, st, arm, n, med, co, ca, j, mx, "PASS" if ok else "below-bar"))
        pb = os.path.join(OUT, "%s_before" % lab, "%s_Breakline_%d.pcd" % (piece, st))
        pa = os.path.join(OUT, "%s_after" % lab, "%s_Breakline_%d.pcd" % (piece, st))
        if os.path.exists(pb) and os.path.exists(pa):
            n1, n2, d = cmp_pts(pb, pa)
            ident.append("%s\tBl%d\tIDENTITY\tn_before=%d\tn_after=%d\tmax_dxyz=%.6f\t%s"
                         % (lab, st, n1, n2, d, "identical" if (n1 == n2 and d == 0.0) else "DIFFERS"))
        else:
            ident.append("%s\tBl%d\tIDENTITY\tMISSING PAIR" % (lab, st))
print("\n== score rows (n, median mm, coverage ours->author, coverage author->ours, jumps, max step) ==")
for r in rows:
    print(r)
print("\n== before vs after, pointwise ==")
for r in ident:
    print(r)
