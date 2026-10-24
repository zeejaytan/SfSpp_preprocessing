#!/usr/bin/env python3
"""Determinism probe for ticket 291: is the Pot H 02 mesh stage reproducible at all?

Compares, pointwise and as sets, the two Surface sheets and the two exports produced by
four mesh-stage runs on the SAME frozen input: A2/A3 staged by cp, B2/B3 staged by
scripts/stage_piece.sh (symlinks). If cp-vs-cp differs as much as cp-vs-symlink, the
difference seen in the gate job is the pipeline, not the staging method.
"""
import sys, os, glob
import numpy as np

OUT = sys.argv[1]

def load_xyz(p):
    a = np.loadtxt(p, dtype=np.float64)
    if a.ndim == 1:
        a = a.reshape(1, -1)
    return a[:, :3]

def nn_max_mean(a, b, chunk=2000):
    """max and mean nearest-neighbour distance a->b, and the same b->a max."""
    if len(a) == 0 or len(b) == 0:
        return float("nan"), float("nan"), float("nan")
    dmax = 0.0; tot = 0.0
    for i in range(0, len(a), chunk):
        blk = a[i:i + chunk]
        d = np.sqrt(((blk[:, None, :] - b[None, :, :]) ** 2).sum(-1)).min(1)
        dmax = max(dmax, float(d.max())); tot += float(d.sum())
    rmax = 0.0
    for i in range(0, len(b), chunk):
        blk = b[i:i + chunk]
        d = np.sqrt(((blk[:, None, :] - a[None, :, :]) ** 2).sum(-1)).min(1)
        rmax = max(rmax, float(d.max()))
    return dmax, tot / len(a), rmax

def readpts(p):
    pts = []; hdr = True
    with open(p) as f:
        for line in f:
            if hdr:
                if line.startswith("DATA"):
                    hdr = False
                continue
            s = line.split()
            if len(s) >= 3:
                pts.append((float(s[0]), float(s[1]), float(s[2])))
    return np.array(pts, dtype=np.float64)

def report(kind, tag, pa, pb):
    if not (os.path.exists(pa) and os.path.exists(pb)):
        print("[%s] %-28s MISSING FILE  %s | %s" % (kind, tag, pa, pb))
        return None, None, None
    a = load_xyz(pa) if kind == "SHEETS" else readpts(pa)
    b = load_xyz(pb) if kind == "SHEETS" else readpts(pb)
    mx, mean, rmx = nn_max_mean(a, b)
    print("[%s] %-28s n_a=%-6d n_b=%-6d max=%.6f mean=%.6f max_rev=%.6f"
          % (kind, tag, len(a), len(b), mx, mean, rmx))
    return mx, mean, rmx

print("=== determinism probe: four mesh-stage runs on one frozen input (Pot H 02) ===")
print("stages: A2 A3 staged by cp ; B2 B3 staged by scripts/stage_piece.sh (symlinks)")
print()
sheet_pairs = [("A2", "A3"), ("B2", "B3"), ("A2", "B2"), ("A2", "B3"), ("A3", "B2")]
print("--- Surface sheets (Temp/Data/Pot_H/<piece>_Surface_<i>.xyz) ---")
worst = {}
for i in (0, 1):
    for x, y in sheet_pairs:
        pa = "%s/sheets/%s_%s_Surface_%d.xyz" % (OUT, "Pot_H_Piece_02", x, i)
        pb = "%s/sheets/%s_%s_Surface_%d.xyz" % (OUT, "Pot_H_Piece_02", y, i)
        mx, mean, rmx = report("SHEETS", "Surface_%d %s-vs-%s" % (i, x, y), pa, pb)
        if mx is not None:
            worst[(x, y)] = max(worst.get((x, y), 0.0), mx)
print()
print("--- exported breaklines (edge stage) ---")
for lane in (0, 1):
    for x, y in (("A2", "A3"), ("A2", "B2"), ("B2", "B3")):
        pa = "%s/det/%s_Bl%d.pcd" % (OUT, x, lane)
        pb = "%s/det/%s_Bl%d.pcd" % (OUT, y, lane)
        mx, mean, rmx = report("EXPORT", "Bl%d %s-vs-%s" % (lane, x, y), pa, pb)
        if mx is not None:
            worst[(x, y)] = max(worst.get((x, y), 0.0), mx)
print()
print("--- classification lines, one per run (counts must agree if only order differs) ---")
for lab in ("A2", "A3", "B2", "B3"):
    p = "%s/det_classify_%s.txt" % (OUT, lab)
    if os.path.exists(p):
        for line in open(p):
            if "classify:" in line:
                print("%s  %s" % (lab, line.strip()))
print()
print("--- sheet sizes (dots per sheet) ---")
for lab in ("A2", "A3", "B2", "B3"):
    for i in (0, 1):
        p = "%s/sheets/Pot_H_Piece_02_%s_Surface_%d.xyz" % (OUT, lab, i)
        if os.path.exists(p):
            print("%s Surface_%d rows=%d" % (lab, i, sum(1 for _ in open(p))))
print()
cp = max([v for k, v in worst.items() if set(k) == {"A2", "A3"}] or [0.0])
ss = max([v for k, v in worst.items() if set(k) == {"B2", "B3"}] or [0.0])
cs = max([v for k, v in worst.items() if set(k) == {"A2", "B2"}] or [0.0])
print("[DET] cp_vs_cp_max=%.6f  sym_vs_sym_max=%.6f  cp_vs_symlink_max=%.6f" % (cp, ss, cs))
if cp == 0.0 and ss == 0.0 and cs == 0.0:
    print("[DET] all four runs agree exactly: the mesh stage is reproducible on this piece")
    print("[VERDICT] staging_causes_no_difference=YES")
elif cp > 0.0:
    print("[DET] two cp runs of the same input already differ by %.6f mm" % cp)
    if cs <= max(cp, ss) * 1.5 + 1e-9:
        print("[VERDICT] the spread is the pipeline's, not the staging method's"
              " (cp-vs-symlink %.6f is within the cp-vs-cp spread %.6f)" % (cs, cp))
    else:
        print("[VERDICT] cp-vs-symlink (%.6f) EXCEEDS the cp-vs-cp spread (%.6f): staging must be investigated" % (cs, cp))
else:
    print("[VERDICT] cp runs agree but symlink runs differ: staging must be investigated")
