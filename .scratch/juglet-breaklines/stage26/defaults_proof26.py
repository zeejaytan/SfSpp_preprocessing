#!/usr/bin/env python3
"""ticket 26 -- defaults reproduce today.

Compares, per pot / piece / surface, the new binary's default run against reference arms:
  A_old  = the pre-change binary (the commit before this ticket's diff)
  A2     = a second run of the new binary, to separate a real change from run-to-run spread
           (the mesh stage draws 30 unseeded ray-cast points, mesh_processing_headless.cpp:1526-1527)

No verdict is printed: the table carries npts, file md5 equality and nearest-neighbour
displacement in both directions at 6 decimals.

usage:
  defaults_proof26.py <cellroot> <pot> <new_tag> <ref_tags_csv> <piece> [piece...]
writes <dirname(cellroot)>/defaults_proof26_<pot>.tsv
"""
import sys, os, glob, hashlib
import numpy as np
from scipy.spatial import cKDTree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from measure_pairs26 import load_ply


def surf(cellroot, tag, pot, piece, k):
    d = os.path.join(cellroot, tag, pot, piece, "surfaces")
    f = sorted(glob.glob(os.path.join(d, "*_Surface_%d.ply" % k)))
    return f[0] if f else None


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def nn(a, b):
    if a.shape[0] == 0 or b.shape[0] == 0:
        return float("nan"), float("nan")
    d, _ = cKDTree(b).query(a, k=1)
    return float(np.median(d)), float(np.max(d))


def main(argv):
    if len(argv) < 6:
        print(__doc__)
        return 2
    cellroot, pot, new_tag, refs, pieces = argv[1], argv[2], argv[3], argv[4].split(","), argv[5:]
    cols = ["pot", "piece", "surface", "ref", "npts_new", "npts_ref", "md5_equal",
            "med_mm_new_to_ref", "max_mm_new_to_ref", "med_mm_ref_to_new", "max_mm_ref_to_new"]
    out = []
    worst = 0.0
    md5_all = True
    nsurf = 0
    for piece in pieces:
        for k in (0, 1):
            fn = surf(cellroot, new_tag, pot, piece, k)
            if not fn:
                continue
            A, _n = load_ply(fn)
            for ref in refs:
                fr = surf(cellroot, ref, pot, piece, k)
                if not fr:
                    out.append([pot, piece, str(k), ref, str(A.shape[0]), "MISSING", "missing"] + [""] * 4)
                    md5_all = False
                    nsurf += 1
                    continue
                R, _r = load_ply(fr)
                eq = "yes" if md5(fn) == md5(fr) else "no"
                if eq != "yes":
                    md5_all = False
                m1, x1 = nn(A, R)
                m2, x2 = nn(R, A)
                worst = max(worst, x1, x2)
                nsurf += 1
                out.append([pot, piece, str(k), ref, str(A.shape[0]), str(R.shape[0]), eq,
                            "%.6f" % m1, "%.6f" % x1, "%.6f" % m2, "%.6f" % x2])
    dest = os.path.join(os.path.dirname(cellroot), "defaults_proof26_%s.tsv" % pot)
    with open(dest, "w") as fh:
        fh.write("\t".join(cols) + "\n")
        for rec in out:
            fh.write("\t".join(rec) + "\n")
    print("[PROOF26] pot=%s surfaces=%d refs=%s md5_all_equal=%s worst_max_mm=%.6f written=%s"
          % (pot, nsurf, ",".join(refs), "yes" if md5_all else "no", worst, dest))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
