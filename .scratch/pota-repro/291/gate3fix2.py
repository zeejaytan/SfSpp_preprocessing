#!/usr/bin/env python3
"""Judge ticket 291 GATE3 (provenance) from freshly staged trees.

Corrected rule, after the first gate run: the mesh and the cloud must be SYMLINKS whose
target is inside the frozen corpus and whose md5 equals the manifest entry; the axis must
be a REGULAR file (a copy, per the contract) whose md5 equals the corpus axis. The first
checker resolved every row through its own readlink column, so the mesh/cloud rows could
never read as symlinks and the axis row could never resolve into the corpus.
"""
import sys, os, hashlib

CORPUS = os.path.realpath(sys.argv[1])
STAGES = sys.argv[2:]

def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def load_manifests():
    rel, der = {}, {}
    p = os.path.join(CORPUS, "Point", "MANIFEST_released.tsv")
    if os.path.exists(p):
        with open(p) as f:
            next(f, None)
            for line in f:
                c = line.rstrip("\n").split("\t")
                if len(c) >= 5:
                    rel[c[1]] = c[4]
    p = os.path.join(CORPUS, "Point", "MANIFEST_derived.tsv")
    if os.path.exists(p):
        with open(p) as f:
            next(f, None)
            for line in f:
                c = line.rstrip("\n").split("\t")
                if len(c) >= 5:
                    der[c[0]] = (c[4], c[2])
    return rel, der

REL, DER = load_manifests()
print("corpus: %s" % CORPUS)
print("manifests: released=%d derived=%d" % (len(REL), len(DER)))
print()
rows, bad = 0, 0
for stage in STAGES:
    p = os.path.join(stage, "inputs.md5")
    if not os.path.exists(p):
        print("[GATE3FIX] %s NO inputs.md5" % stage); bad += 1; continue
    with open(p) as f:
        next(f, None)
        for line in f:
            c = line.rstrip("\n").split("\t")
            if len(c) < 4:
                continue
            rec, realpath, points, staged = c[0], c[1], c[2], c[3]
            kind = ("mesh" if "/Dataset/Mesh/" in staged else
                    "cloud" if "/Dataset/Point/" in staged else "axis")
            base = os.path.basename(staged)
            piece = base[:14]
            rows += 1
            if kind == "axis":
                is_link = os.path.islink(staged)
                m = md5(staged) if os.path.exists(staged) else "MISSING"
                src = os.path.join(CORPUS, "Axes", base)
                sm = md5(src) if os.path.exists(src) else "MISSING"
                ok = (not is_link) and m == rec and m == sm
                print("[GATE3FIX] %-22s %-5s symlink=%-5s md5=%s corpus_axis=%s %s"
                      % (piece, kind, is_link, m[:12], sm[:12], "PASS" if ok else "FAIL"))
            else:
                is_link = os.path.islink(staged)
                tgt = os.path.realpath(staged) if is_link else ""
                inside = bool(tgt) and (tgt == CORPUS or tgt.startswith(CORPUS + os.sep))
                m = md5(staged) if os.path.exists(staged) else "MISSING"
                want = REL.get(piece) if kind == "cloud" else None
                if want is None and kind == "cloud" and piece in DER:
                    want = DER[piece][0]
                if want is None and kind == "mesh" and piece in DER:
                    want = DER[piece][1]
                if want is None:
                    want = rec
                ok = is_link and inside and m == rec and m == want
                print("[GATE3FIX] %-22s %-5s symlink=%-5s in_corpus=%-3s md5=%s manifest=%s points=%s %s"
                      % (piece, kind, is_link, "YES" if inside else "NO", m[:12], want[:12], points,
                         "PASS" if ok else "FAIL"))
                if not ok:
                    print("             target=%s" % (tgt or "-"))
            if not ok:
                bad += 1
print()
print("[GATE3FIX] rows=%d failed=%d" % (rows, bad))
print("[GATE3FIX] item3_provenance=%s" % ("PASS" if bad == 0 and rows >= 6 else "FAIL"))
