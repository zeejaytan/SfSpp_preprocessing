#!/usr/bin/env python3
"""Ticket 288 gate: score the lanes built from the committed source (main 8e1e514) against the
authors' breaklines, then check them against ticket 287's recorded "after" column.

Expected column is read from the 287 run directory itself (its out/score287.txt), not retyped, so
the gate compares against what was scored rather than against a transcription.
Tolerances from ticket 288: n exact; median +-0.05 mm; coverage +-1.0; jumps equal.
"""
import sys, os, importlib.util, math, glob

OUT = os.environ["OUT"]
REF = os.environ.get("REF287", "")
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
    return [min(math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2) for b in dst) for a in src]

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

# --- what ticket 287 recorded for these lanes, straight from its own score file ---------------
expected = {}
refpath = os.path.join(REF, "score287.txt") if REF else ""
if refpath and os.path.exists(refpath):
    for line in open(refpath):
        f = line.rstrip("\n").split("\t")
        if len(f) >= 9 and f[2] == "after" and f[1].startswith("Bl"):
            expected[(f[0], f[1])] = dict(n=int(f[3].split("=")[1]), med=float(f[4].split("=")[1]),
                                          cov_o=float(f[5].split("=")[1]), cov_a=float(f[6].split("=")[1]),
                                          jmp=int(f[7].split("=")[1]))
    print("expected column: %s (%d rows)" % (refpath, len(expected)))
else:
    print("expected column: MISSING (%r) -- tolerances cannot be checked, raw rows only" % (refpath,))

print("scorer: %s" % mode)
print("out dir: %s" % OUT)
rows, verdicts = [], []
hdr = "%-4s %-3s %5s %6s %6s %6s %4s %7s | %5s %6s %6s %6s %4s | %s"
print("\n== lanes built from the commit, scored against the authors' breaklines ==")
print("lane st     n median  cov_o  cov_a  jmp  maxstep |  n287 med287 cov287 jmp287 | verdict")
for lab, piece in LANES:
    for st in (0, 1):
        ap = AUTH % (piece, st)
        f = os.path.join(OUT, "%s_commit" % lab, "%s_Breakline_%d.pcd" % (piece, st))
        if not os.path.exists(f):
            print("%s Bl%d MISSING OUTPUT %s" % (lab, st, f)); verdicts.append((lab, st, "MISSING")); continue
        if not os.path.exists(ap):
            print("%s Bl%d MISSING AUTHOR %s" % (lab, st, ap)); verdicts.append((lab, st, "MISSING")); continue
        o, a = readpts(f), readpts(ap)
        if len(o) == 0:
            print("%s Bl%d EMPTY" % (lab, st)); verdicts.append((lab, st, "EMPTY")); continue
        n, med, co, ca, j, mx, ok = lane(o, a)
        key = (lab, "Bl%d" % st)
        e = expected.get(key)
        if e is None:
            print(hdr % (lab, "Bl%d" % st, n, "%.3f" % med, "%.2f" % co, "%.2f" % ca, j, "%.3f" % mx,
                         "-", "-", "-", "-", "-", "NO EXPECTATION")); verdicts.append((lab, st, "NO-EXP")); continue
        why = []
        if n != e["n"]: why.append("n %d!=%d" % (n, e["n"]))
        if abs(med - e["med"]) > 0.05: why.append("med %+.3f" % (med - e["med"]))
        if abs(co - e["cov_o"]) > 1.0: why.append("cov_o %+.2f" % (co - e["cov_o"]))
        if abs(ca - e["cov_a"]) > 1.0: why.append("cov_a %+.2f" % (ca - e["cov_a"]))
        if j != e["jmp"]: why.append("jmp %d!=%d" % (j, e["jmp"]))
        v = "REPRODUCES" if not why else "DIVERGES: " + ", ".join(why)
        print(hdr % (lab, "Bl%d" % st, n, "%.3f" % med, "%.2f" % co, "%.2f" % ca, j, "%.3f" % mx,
                     e["n"], "%.3f" % e["med"], "%.2f" % e["cov_o"], e["jmp"], "",
                     v + ("" if ok else " [below bar]")))
        verdicts.append((lab, st, "REPRODUCES" if not why else "DIVERGES"))

print("\n== pointwise: this build vs the 287 after exports (same program means identical files) ==")
for lab, piece in LANES:
    for st in (0, 1):
        f_new = os.path.join(OUT, "%s_commit" % lab, "%s_Breakline_%d.pcd" % (piece, st))
        f_old = os.path.join(REF, "..", "out", "%s_after" % lab, "%s_Breakline_%d.pcd" % (piece, st)) if REF else ""
        f_old = os.path.normpath(f_old)
        if os.path.exists(f_new) and os.path.exists(f_old):
            n1, n2, d = cmp_pts(f_new, f_old)
            print("%s Bl%d n_new=%d n_287after=%d max_dxyz=%.6f %s"
                  % (lab, st, n1, n2, d, "identical" if (n1 == n2 and d == 0.0) else "DIFFERS"))
        else:
            print("%s Bl%d no 287 after file to compare (%s)" % (lab, st, f_old))

good = sum(1 for v in verdicts if v[2] == "REPRODUCES")
print("\n== summary ==\nreproduces: %d of %d lanes" % (good, len(verdicts)))
print("answer: %s" % ("YES - the binary built from the committed source reproduces the scored behaviour" if good == len(verdicts) else "NO - see the DIVERGES rows above"))
