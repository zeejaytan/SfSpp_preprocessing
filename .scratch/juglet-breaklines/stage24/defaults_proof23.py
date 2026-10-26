#!/usr/bin/env python3
"""Ticket 23: defaults proof in displacement form.

Compares arm A (new binary, no switches) against
  A_old   the pre-change binary built from 158ddc6 -- the defaults must still do what they did
  A2      a second pass of the new binary   -- the run-to-run spread the B-spline step's unseeded
          pcl::RandomSample(10000) already has, which is the yardstick A-vs-A_old is read against.

md5 is reported but is not the test: the ASCII PLY carries digits beyond the 4-decimal distance,
so two runs can agree to 0.0000 mm and still differ byte for byte.

Usage: defaults_proof23.py <cellroot> <pot> <pieces...>  ->  <cellroot>/defaults_proof23_<pot>.tsv
(set SFS_PROOF_OUT to name the output file explicitly; the per-pot default exists because one
call per pot wrote the same path and the second pot truncated the first pot's rows).
"""
import hashlib
import os
import sys

import numpy as np
from scipy.spatial import cKDTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from measure_arm23 import load_ply  # noqa: E402

REFS = ("A_old", "A2")


def dists(a, b):
    if len(a) == 0 or len(b) == 0:
        return float("nan"), float("nan")
    d, _ = cKDTree(b).query(a, k=1)
    return float(np.median(d)), float(d.max())


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def surf(cellroot, tag, pot, piece, k):
    return os.path.join(cellroot, tag, pot, piece, "surfaces", "%s_Surface_%d.ply" % (piece, k))


def main():
    cellroot, pot = sys.argv[1], sys.argv[2]
    pieces = sys.argv[3:]
    rows = []
    for piece in pieces:
        for k in (0, 1):
            pa = surf(cellroot, "A", pot, piece, k)
            for ref in REFS:
                pr = surf(cellroot, ref, pot, piece, k)
                if not os.path.exists(pa) or not os.path.exists(pr):
                    rows.append([pot, piece, "Surface_%d" % k, ref, "NA", "NA", "NA", "NA",
                                 "NA", "NA", "NA", "NA"])
                    continue
                xa, _ = load_ply(pa)
                xr, _ = load_ply(pr)
                same_md5 = md5(pa) == md5(pr)
                same_bytes = os.path.getsize(pa) == os.path.getsize(pr)
                m1, x1 = dists(xa, xr)
                m2, x2 = dists(xr, xa)
                rows.append([pot, piece, "Surface_%d" % k, ref, len(xa), len(xr),
                             "yes" if same_md5 else "no", "yes" if same_bytes else "no",
                             "%.4f" % m1, "%.4f" % x1, "%.4f" % m2, "%.4f" % x2])
    out = os.environ.get("SFS_PROOF_OUT") or os.path.join(
        cellroot, "defaults_proof23_%s.tsv" % pot)
    with open(out, "w") as fh:
        fh.write("pot\tpiece\tsurface\tref\tnpts_A\tnpts_ref\tmd5_equal\tbytes_equal"
                 "\tmed_mm_A_to_ref\tmax_mm_A_to_ref\tmed_mm_ref_to_A\tmax_mm_ref_to_A\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    print("wrote %s (%d rows)" % (out, len(rows)))


if __name__ == "__main__":
    main()
