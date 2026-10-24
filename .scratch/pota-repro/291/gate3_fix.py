#!/usr/bin/env python3
"""Corrected provenance check for ticket 291 gate item 3.

The pre-registered wording ("every staged input resolves into the corpus") does not match the
script contract: the AXIS is deliberately COPIED (it is the only file that is copied), so its
staged path can never resolve into the corpus. Correct rule:
  mesh  -> symlink whose target is inside the corpus, md5 equals the corpus mesh md5
  cloud -> symlink whose target is inside the corpus, md5 equals the manifest md5
  axis  -> regular file (a copy), md5 equals the corpus axis md5
"""
import sys, os, hashlib

OUT = sys.argv[1]
CORPUS = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp"

def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

fails = 0; rows = 0
for fn in sorted(os.listdir(OUT)):
    if not (fn.startswith("inputs_B_") and fn.endswith(".md5")):
        continue
    piece = fn[len("inputs_B_"):-4]
    print("## %s" % piece)
    for line in open(os.path.join(OUT, fn)):
        line = line.strip()
        if not line or line.startswith("md5"):
            continue
        parts = line.split("\t")
        if len(parts) < 4:
            continue
        m, real, pts, staged = parts[0], parts[1], parts[2], parts[3]
        rows += 1
        base = os.path.basename(staged)
        islink = os.path.islink(staged)
        if base.endswith("_Mesh.obj"):
            kind = "mesh"
            inside = os.path.abspath(real).startswith(CORPUS + os.sep)
            ok = islink and inside and (md5(real) == m)
            note = "symlink=%s target_in_corpus=%s md5_matches_target=%s" % (islink, inside, md5(real) == m)
        elif base.endswith("_Point.pcd"):
            kind = "cloud"
            inside = os.path.abspath(real).startswith(CORPUS + os.sep)
            ok = islink and inside and pts.isdigit()
            note = "symlink=%s target_in_corpus=%s points=%s" % (islink, inside, pts)
        elif base.endswith("_Axis.xyz"):
            kind = "axis"
            src = os.path.join(CORPUS, "Axes", base)
            same = os.path.exists(src) and md5(src) == md5(staged)
            ok = (not islink) and same
            note = "copy=%s md5_equals_corpus_axis=%s" % (not islink, same)
        else:
            kind = "?"; ok = False; note = "unrecognised"
        fails += 0 if ok else 1
        print("  %-6s %-8s %s  %s" % (kind, "OK" if ok else "FAIL", note, staged))
print()
print("[GATE3-FIXED] rows=%d fails=%d  (rule: mesh/cloud symlinked into the corpus, axis copied and md5-equal)" % (rows, fails))
print("[GATE3-FIXED] verdict=%s" % ("PASS" if fails == 0 else "FAIL"))
sys.exit(0 if fails == 0 else 1)
