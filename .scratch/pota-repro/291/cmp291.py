#!/usr/bin/env python3
"""Ticket 291 gate: does a symlinked stage behave identically to a copied one?

Reads the exports, stage censuses and provenance records the job wrote into <RUN>/out and prints the
four pre-registered gate items. Nothing here writes geometry; nothing here decides a method claim.
"""
import sys, os
import numpy as np

RUN = sys.argv[1] if len(sys.argv) > 1 else "."
OUT = os.path.join(RUN, "out")
SCORER = "/data/gpfs/projects/punim2657/SfSpp/runs/20261024-0329_1308298_p275-walker/score275.py"
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"
PIECES = [("Pot_J", "Pot_J_Piece_09"), ("Pot_H", "Pot_H_Piece_02")]

import importlib.util
_argv = sys.argv[:]
sys.argv = ["cmp291", "/nonexistent"]
spec = importlib.util.spec_from_file_location("score275", SCORER)
sm = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(sm)
except SystemExit:
    pass
sys.argv = _argv


def length(p):
    if len(p) < 2:
        return 0.0
    d = float(np.sqrt(((p[1:] - p[:-1]) ** 2).sum(1)).sum())
    return d + float(np.linalg.norm(p[0] - p[-1]))


def manifest():
    m = {}
    p = os.path.join(CORPUS, "Point", "MANIFEST_released.tsv")
    if os.path.exists(p):
        for line in open(p):
            f = line.rstrip("\n").split("\t")
            if len(f) >= 5 and f[0] != "pot":
                m[f[1]] = f[4]
    p = os.path.join(CORPUS, "Point", "MANIFEST_derived.tsv")
    if os.path.exists(p):
        for line in open(p):
            f = line.rstrip("\n").split("\t")
            if len(f) >= 5 and f[0] != "piece":
                m.setdefault(f[0], f[4])
    return m


MAN = manifest()
gate1 = []
gate2 = []
gate3 = []

print("=" * 96)
print("[GATE1] identity: exported lane from a COPIED stage (A) vs a SYMLINKED stage (B)")
print("%-16s %-3s %5s %5s %10s %10s %10s" % ("piece", "bl", "n_A", "n_B", "max|dxyz|", "mean|dxyz|", "set_max"))
for pot, piece in PIECES:
    for bl in (0, 1):
        fa = os.path.join(OUT, "A_%s_Bl%d.pcd" % (piece, bl))
        fb = os.path.join(OUT, "B_%s_Bl%d.pcd" % (piece, bl))
        if not (os.path.exists(fa) and os.path.exists(fb)):
            print("%-16s %-3d %s" % (piece, bl, "MISSING EXPORT"))
            gate1.append(False)
            continue
        a, b = sm.readpts(fa), sm.readpts(fb)
        if len(a) == len(b):
            d = np.sqrt(((a - b) ** 2).sum(1))
            mx, mn, smax, note = float(d.max()), float(d.mean()), float(d.max()), "pointwise"
        else:
            mx = mn = float("nan")
            smax = float(max(sm.nn(a, b).max(), sm.nn(b, a).max()))
            note = "n differs"
        ok = (len(a) == len(b)) and (note == "pointwise") and mx == 0.0
        gate1.append(ok)
        print("%-16s %-3d %5d %5d %10.6f %10.6f %10.4f  %s %s"
              % (piece, bl, len(a), len(b), mx, mn, smax, note, "IDENTICAL" if ok else "DIFFERS"))

print()
print("[SCORE] same scorer, same authors lane, both stages (a gate record, not a bar claim)")
print("%-16s %-3s %-1s %5s %8s %8s %8s %4s %8s %9s" %
      ("piece", "bl", "arm", "n", "med", "cov_o", "cov_a", "jmp", "maxstep", "len"))
scored = 0
for pot, piece in PIECES:
    for bl in (0, 1):
        auth = os.path.join(CORPUS, "Breaklines", "%s_Breakline_%d.pcd" % (piece, bl))
        if not os.path.exists(auth):
            print("%-16s %-3d no authors lane" % (piece, bl))
            continue
        ap = sm.readpts(auth)
        for lab in ("A", "B"):
            f = os.path.join(OUT, "%s_%s_Bl%d.pcd" % (lab, piece, bl))
            if not os.path.exists(f):
                continue
            o = sm.readpts(f)
            n, med, co, ca, jmp, mx, ok = sm.lane(o, ap)
            scored += 1
            print("%-16s %-3d %-1s %5d %8.3f %8.2f %8.2f %4d %8.3f %9.2f"
                  % (piece, bl, lab, n, med, co, ca, jmp, mx, length(o)))

print()
print("[GATE2] no geometry in the symlinked stage (pre-run census)")
for pot, piece in PIECES:
    f = os.path.join(OUT, "census_B_%s.txt" % piece)
    if not os.path.exists(f):
        print("%-16s census missing" % piece)
        gate2.append(False)
        continue
    txt = open(f).read()
    big = int(txt.split("-- count: ")[1].split()[0]) if "-- count: " in txt else -1
    links = int(txt.split("-- symlinks: ")[1].split()[0]) if "-- symlinks: " in txt else -1
    du = txt.split("-- du: ")[1].split()[0] if "-- du: " in txt else "?"
    ok = (big == 0) and (links == 2)
    gate2.append(ok)
    print("%-16s files>1MiB=%d symlinks=%d du=%s  %s" % (piece, big, links, du, "OK" if ok else "FAIL"))

print()
print("[GATE3] provenance: every staged input resolves into the corpus and matches its manifest md5")
for pot, piece in PIECES:
    f = os.path.join(OUT, "inputs_B_%s.md5" % piece)
    if not os.path.exists(f):
        print("%-16s inputs.md5 missing" % piece)
        gate3.append(False)
        continue
    okp = True
    for i, line in enumerate(open(f)):
        if i == 0:
            continue
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 4:
            continue
        md5, real, pts, staged = parts[0], parts[1], parts[2], parts[3]
        inside = real.startswith(CORPUS + os.sep)
        want = MAN.get(piece, "")
        is_cloud = staged.endswith("_Point.pcd")
        is_axis = staged.endswith("_Axis.xyz")
        checked = ""
        if is_cloud:
            checked = "manifest" if (want and want == md5) else ("MISMATCH" if want else "unlisted")
        okrow = inside and (not is_cloud or checked == "manifest")
        okp = okp and okrow
        print("%-16s %-8s inside_corpus=%s md5_manifest=%s  %s"
              % (piece, os.path.basename(staged), "yes" if inside else "NO", checked or "-",
                 "OK" if okrow else "FAIL"))
        print("                 %s" % real)
    gate3.append(okp)

print()
print("[SHEETS] mesh stage determinism: are the two stages partitions equal?")
sheets_ok = True
for pot, piece in PIECES:
    fa = os.path.join(OUT, "sheets_A_%s.md5" % piece)
    fb = os.path.join(OUT, "sheets_B_%s.md5" % piece)
    if not (os.path.exists(fa) and os.path.exists(fb)):
        print("%-16s sheets record missing" % piece)
        sheets_ok = False
        continue
    a, b = open(fa).read().strip(), open(fb).read().strip()
    same = a == b
    sheets_ok = sheets_ok and same
    print("%-16s %s" % (piece, "identical" if same else "DIFFER"))
    if not same:
        print("  A: " + a.replace("\n", "\n     "))
        print("  B: " + b.replace("\n", "\n     "))

print()
print("[CORPUS] did anything write into the input corpus?")
cc = os.path.join(OUT, "corpus_check.txt")
if os.path.exists(cc):
    print(open(cc).read().strip())
else:
    print("corpus_check.txt missing")

print()
v1 = all(gate1)
v2 = all(gate2)
v3 = all(gate3)
print("[VERDICT] item1 identity=%s   item2 no-geometry=%s   item3 provenance=%s   item4 scores_reported=%d   sheets=%s"
      % ("PASS" if v1 else "FAIL", "PASS" if v2 else "FAIL", "PASS" if v3 else "FAIL", scored,
         "identical" if sheets_ok else "differ"))
print("[VERDICT] gate=%s" % ("PASS" if (v1 and v2 and v3) else "FAIL"))
sys.exit(0 if (v1 and v2 and v3) else 1)
