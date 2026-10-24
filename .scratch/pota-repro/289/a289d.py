#!/usr/bin/env python3
# Ticket 289 - the two-draw comparison. Same mesh, same binary, same flags; the only
# difference is the CloudCompare sampling draw (the sampler takes no seed), so this file
# answers one question: how far apart are the two exported lanes from two independent draws?
# It imports the project's own scorer so the lane numbers are the project's numbers.
import os, sys, glob
import numpy as np

RUN = sys.argv[1]
sys.argv = ["score275", "/nonexistent"]          # score275.main() runs at import
spec = "/data/gpfs/projects/punim2657/SfSpp/runs/20261024-0329_1308298_p275-walker/score275.py"
import importlib.util
s = importlib.util.spec_from_file_location("score275", spec)
m = importlib.util.module_from_spec(s)
try:
    s.loader.exec_module(m)
except SystemExit:
    pass
PIECE = "Pot_J_Piece_09"

def pts(p):
    return m.readpts(p)

def hdr_points(p):
    for line in open(p, errors="replace"):
        if line.startswith("POINTS"):
            return int(line.split()[1])
        if line.startswith("DATA"):
            break
    return -1

def closed_len(a):
    if len(a) < 2:
        return 0.0
    d = np.sqrt(((a[1:] - a[:-1]) ** 2).sum(1))
    return float(d.sum() + np.sqrt(((a[0] - a[-1]) ** 2).sum()))

def setdist(a, b):
    d_ab = m.nn(a, b)
    d_ba = m.nn(b, a)
    return float(d_ab.max()), float(d_ba.max()), float(d_ab.mean()), float(d_ba.mean())

print("[SETUP] run=%s scorer=%s" % (RUN, spec))
draws = {}
for dn in ("d1", "d2"):
    for ln in (0, 1):
        p = os.path.join(RUN, "out", dn, "lane%d.pcd" % ln)
        if not os.path.isfile(p):
            print("[MISSING] %s" % p)
            continue
        draws[(dn, ln)] = pts(p)
    cp = os.path.join(RUN, "out", dn, "cloud.pcd")
    print("[CLOUD] %s points=%d md5file=%s" % (dn, hdr_points(cp) if os.path.isfile(cp) else -1,
          os.path.basename(cp)))

print("")
print("%-4s %-4s %5s %8s %8s %8s %4s %9s %9s %s" % ("draw", "lane", "n", "med", "cov_o", "cov_a", "jmp", "maxjump", "len_mm", "bar"))
for dn in ("d1", "d2"):
    for ln in (0, 1):
        key = (dn, ln)
        if key not in draws:
            continue
        o = draws[key]
        a = pts("/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Breaklines/%s_Breakline_%d.pcd" % (PIECE, ln))
        n, med, cov_o, cov_a, jmp, mx, ok = m.lane(o, a)
        print("[DRAW] %-4s %-4d %5d %8.3f %8.2f %8.2f %4d %9.3f %9.2f %s" % (
            dn, ln, n, med, cov_o, cov_a, jmp, mx, closed_len(o), "PASS" if ok else "below"))

print("")
for ln in (0, 1):
    k1, k2 = ("d1", ln), ("d2", ln)
    if k1 not in draws or k2 not in draws:
        print("[DELTA] lane%d: a draw is missing" % ln)
        continue
    a, b = draws[k1], draws[k2]
    msg = "[DELTA] lane%d n1=%d n2=%d" % (ln, len(a), len(b))
    if len(a) == len(b):
        d = np.sqrt(((a - b) ** 2).sum(1))
        msg += " pointwise_max=%.6f pointwise_mean=%.6f" % (float(d.max()), float(d.mean()))
    else:
        msg += " pointwise=N/A (n differs)"
    smax_ab, smax_ba, smean_ab, smean_ba = setdist(a, b)
    msg += " set_max_12=%.4f set_max_21=%.4f set_mean_12=%.4f set_mean_21=%.4f" % (smax_ab, smax_ba, smean_ab, smean_ba)
    print(msg)

print("")
for ln in (0, 1):
    a = pts("/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Breaklines/%s_Breakline_%d.pcd" % (PIECE, ln))
    print("[AUTH] lane%d n=%d len_mm=%.2f" % (ln, len(a), closed_len(a)))
print("[END]")
