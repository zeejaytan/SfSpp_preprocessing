#!/usr/bin/env python3
"""Ticket 331: run the shipped axis estimator (sfs_axes.potsac.run_potsac_union) on one arm's
wall surfaces, with the shipped benchmark's arguments, and score the found directions against
the answer key.  This is scripts/run_benchmark_172.py's Juglet branch, made path-agnostic and
nothing else (same seeds=range(10), step=10, max_candidates=6, normalized=True, no line_rule
override, same output format and the same z>=0 canonicalisation).

usage: run_axes_t331.py --tree <extracted repo> --geom <dir with Juglet_Piece_<i>.S0/.S1>
                        --out <dir> --gt <Juglet_GT or Juglet_large> [--tag NAME]
"""
import os, sys, argparse
import numpy as np

def load_wall(path):
    with open(path, "r") as fh:
        first = fh.readline()
    if first.startswith("ply"):
        n = None
        with open(path, "r") as fh:
            for line in fh:
                if line.startswith("element vertex"):
                    n = int(line.split()[-1])
                if line.strip() == "end_header":
                    break
            rows = []
            for _ in range(n):
                parts = fh.readline().split()
                rows.append([float(v) for v in parts[:6]])
        return np.asarray(rows, dtype=float).T
    a = np.loadtxt(path, usecols=(0, 1, 2, 3, 4, 5), ndmin=2)
    return np.asarray(a, dtype=float).T

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", required=True)
    ap.add_argument("--geom", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--gt", required=True)
    ap.add_argument("--tag", default="arm")
    a = ap.parse_args()
    sys.path.insert(0, a.tree)
    import sfs_axes.potsac as ps
    from sfs_axes.io_axes import read_axes, direction_angle_deg
    os.makedirs(a.out, exist_ok=True)

    def canon(v):
        v = np.asarray(v, dtype=float).copy()
        if v[2] < 0:
            v[0:3] = -v[0:3]
        return v

    rows = []
    for i in range(1, 10):
        stem = "Juglet_Piece_%d" % i
        C0 = load_wall(os.path.join(a.geom, stem + ".S0"))
        C1 = load_wall(os.path.join(a.geom, stem + ".S1"))
        vt = ps.run_potsac_union(C0, C1, seeds=list(range(10)), step=10,
                                 max_candidates=6, normalized=True)
        K = int(vt.shape[1]) if vt.size else 0
        with open(os.path.join(a.out, stem + "_Axis.xyz"), "w") as fh:
            for k in range(K):
                v = canon(vt[:, k])
                fh.write(" ".join("%.17g" % x for x in np.r_[v[3:6], v[0:3]]) + "\n")
        gt = canon(read_axes(os.path.join(a.gt, stem + "_Axis.xyz"))[:, 0])
        angs = [direction_angle_deg(canon(vt[:, k])[:3], gt[:3]) for k in range(K)]
        rows.append((stem, K, angs[0] if K else float("nan"),
                     min(angs) if K else float("nan"),
                     " ".join("%.3f" % x for x in angs)))
        print("[AXES] %-16s K=%d rank0=%.3f deg  best=%.3f deg  all=%s"
              % (rows[-1][0], K, rows[-1][2], rows[-1][3], rows[-1][4]))
    with open(os.path.join(a.out, "axes_summary_%s.tsv" % a.tag), "w") as fh:
        fh.write("piece\tK\trank0_deg_vs_gt\tbest_deg_vs_gt\tall_deg\n")
        for r in rows:
            fh.write("%s\t%d\t%.6f\t%.6f\t%s\n" % r)
    print("[AXES] tag=%s geom=%s gt=%s" % (a.tag, a.geom, a.gt))

if __name__ == "__main__":
    main()
