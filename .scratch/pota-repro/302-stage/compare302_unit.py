#!/usr/bin/env python3
"""Ticket 302 stage 1: port-vs-MATLAB unit proof.

Reads CELLS/<cell>/{X.tsv, vt.tsv, ml_R1.tsv, ml_J6.tsv, ml_R3.tsv}, computes
the same quantities with the WORKTREE-FIXED sfs_axes (uploaded under work/),
and reports per-cell max relative and absolute differences. PASS requires
max rel diff <= 1e-9 on entries with |matlab| > 1e-9 for R1 and J6.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "sfs_axes")))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "sfs_axes")))

from sfs_axes.cao import compute_biaxial_cao_error, compute_cao_error  # noqa: E402

REL_TOL = 1e-9


def reldiff(a, b):
    a = np.asarray(a, dtype=float).ravel()
    b = np.asarray(b, dtype=float).ravel()
    m = np.abs(b) > 1e-9
    rel = np.abs(a[m] - b[m]) / np.abs(b[m])
    return (float(rel.max()) if rel.size else 0.0,
            float(np.abs(a - b).max()) if a.size else 0.0, int(m.sum()),
            int(a.size))


def main(inputs, out_tsv):
    rows = []
    ok_all = True
    for cell in sorted(os.listdir(os.path.join(inputs, "CELLS"))):
        cd = os.path.join(inputs, "CELLS", cell)
        X = np.loadtxt(os.path.join(cd, "X.tsv")).T
        vt = np.loadtxt(os.path.join(cd, "vt.tsv")).ravel()
        ml_R1 = np.loadtxt(os.path.join(cd, "ml_R1.tsv")).ravel()
        ml_J6 = np.loadtxt(os.path.join(cd, "ml_J6.tsv"))
        ml_R3 = np.loadtxt(os.path.join(cd, "ml_R3.tsv")).T
        R1, J = compute_biaxial_cao_error(vt, X, with_jacobian=True)
        R3 = compute_cao_error(vt, X)
        r1_rel, r1_abs, n1m, n1 = reldiff(R1, ml_R1)
        j_rel, j_abs, njm, nj = reldiff(J[0].T, ml_J6)
        r3_rel, r3_abs, _, _ = reldiff(R3, ml_R3)
        ok = r1_rel <= REL_TOL and j_rel <= REL_TOL
        ok_all = ok_all and ok
        rows.append((cell, X.shape[1], r1_rel, r1_abs, j_rel, j_abs,
                     r3_rel, r3_abs, "PASS" if ok else "FAIL"))
        print("%-12s n=%6d  R1 rel=%.3e abs=%.3e  J rel=%.3e abs=%.3e  R3 rel=%.3e  %s"
              % (cell, X.shape[1], r1_rel, r1_abs, j_rel, j_abs, r3_rel,
                 "PASS" if ok else "FAIL"))
    with open(out_tsv, "w") as fh:
        fh.write("cell\tn\tR1_rel\tR1_abs\tJ_rel\tJ_abs\tR3_rel\tR3_abs\tverdict\n")
        for r in rows:
            fh.write("\t".join(("%.17g" % v if isinstance(v, float) else str(v))
                                for v in r) + "\n")
    print("OVERALL:", "PASS" if ok_all else "FAIL")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
