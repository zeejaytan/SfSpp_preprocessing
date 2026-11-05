#!/usr/bin/env python3
"""census307.py -- ticket 307 Stage B tables: the emitted axis set, shape and distance.

Two subcommands, both read released files from $CORP/Axes and ours from a run's out/:

  census307.py pota   --pota DIR --released DIR --out TSV
      One row per (arm, seed, piece): K ours, K released, and for each released line
      the smallest angle to any of our lines -> covered degrees {5,10,20}, plus the
      angle our line 0 makes to released line 0 (the primary-axis check).

  census307.py corpus --ours DIR --released DIR --out TSV --label NAME
      A2/C3: line counts per piece and per pot. Prints the per-pot table
      (pieces, ours lines, released lines, pieces differing, names) and the
      fewer/equal/more census, and writes one row per piece.

Angles are sign-agnostic (arccos |a.b| over the direction columns 3:6), the same
measure as io_axes.direction_angle_deg and analyse306c.py. Files are position-first,
6 columns, K rows (io_axes.py:4-5).
"""
import argparse, glob, os
import numpy as np


def read_axes(path):
    A = np.loadtxt(path, ndmin=2)
    if A.size == 0:
        return np.zeros((6, 0))
    return A.T


def ang(a, b):
    na = np.linalg.norm(a); nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return float("nan")
    c = abs(float(np.dot(a, b)) / (na * nb))
    return float(np.degrees(np.arccos(min(1.0, c))))


def parse_name(path):
    stem = os.path.basename(path)[:-4]          # Pot_A_Piece_01_Axis
    parts = stem.split("_")
    return parts[1], int(parts[3])


def do_pota(a):
    rows = []
    dirs = sorted(d for d in os.listdir(a.pota)
                  if os.path.isdir(os.path.join(a.pota, d)) and "_s" in d)
    for d in dirs:
        arm, seed = d.rsplit("_s", 1)
        for p in sorted(glob.glob(os.path.join(a.pota, d, "Pot_*_Piece_*_Axis.xyz"))):
            pot, nn = parse_name(p)
            O = read_axes(p)
            rel = os.path.join(a.released, os.path.basename(p))
            if not os.path.exists(rel):
                rows.append((arm, seed, pot, nn, O.shape[1], 0, 0, 0, 0, float("nan"), float("nan")))
                continue
            R = read_axes(rel)
            cov = [min(ang(R[3:6, j], O[3:6, i]) for i in range(O.shape[1]))
                   for j in range(R.shape[1])]
            best_ours = min(ang(O[3:6, i], R[3:6, j])
                            for i in range(O.shape[1]) for j in range(R.shape[1]))
            l0 = ang(O[3:6, 0], R[3:6, 0])
            rows.append((arm, seed, pot, nn, O.shape[1], R.shape[1],
                         sum(1 for c in cov if c <= 5.0),
                         sum(1 for c in cov if c <= 10.0),
                         sum(1 for c in cov if c <= 20.0), best_ours, l0))
    cols = ["arm", "seed", "pot", "piece", "K", "K_rel", "cov5", "cov10", "cov20",
            "best_deg", "line0_vs_line0_deg"]
    with open(a.out, "w", newline="\n") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(("%.3f" % v) if isinstance(v, float) else str(v) for v in r) + "\n")
    print("\n[Pot A] per arm-seed, per piece (released file = the authors' axes)")
    hdr = "arm     seed  " + "  ".join("p%02d K/Kr cov5" % i for i in range(1, 9))
    print(hdr)
    for d in dirs:
        arm, seed = d.rsplit("_s", 1)
        cells = []
        for nn in range(1, 9):
            rr = [r for r in rows if r[0] == arm and r[1] == seed and r[3] == nn]
            if not rr:
                cells.append("p%02d   -      -" % nn); continue
            r = rr[0]
            cells.append("p%02d %2d/%-2d %3d" % (nn, r[4], r[5], r[6]))
        print("%-7s %-5s %s" % (arm, seed, "  ".join(cells)))
    print("\n[Pot A] released-line coverage totals (out of 8 pieces; a piece counts if all its released lines are within 5 deg)")
    for d in dirs:
        arm, seed = d.rsplit("_s", 1)
        sub = [r for r in rows if r[0] == arm and r[1] == seed]
        allcov = sum(1 for r in sub if r[5] and r[6] == r[5])
        K = [r[4] for r in sub]
        print("%-7s %-5s  covered 5deg on %d/%d pieces   K total %d  (per piece %s)"
              % (arm, seed, allcov, len(sub), sum(K), ",".join(str(k) for k in K)))


def do_corpus(a):
    rows = []
    for p in sorted(glob.glob(os.path.join(a.ours, "Pot_*_Piece_*_Axis.xyz"))):
        pot, nn = parse_name(p)
        O = read_axes(p)
        rel = os.path.join(a.released, os.path.basename(p))
        K_rel = None
        if os.path.exists(rel):
            K_rel = read_axes(rel).shape[1]
        rows.append((pot, nn, O.shape[1], K_rel))
    with open(a.out, "w", newline="\n") as f:
        f.write("pot\tpiece\tK\tK_rel\tdelta\n")
        for pot, nn, k, kr in rows:
            d = "" if kr is None else ("%+d" % (k - kr))
            f.write("%s\t%02d\t%d\t%s\t%s\n" % (pot, nn, k, "-" if kr is None else kr, d))
    print("\n[corpus %s] line counts: ours (K rows) vs the released files" % a.label)
    print("pot  pieces  ours  released  fewer  equal  more  differing pieces")
    tot = [0, 0, 0, 0, 0]
    allnames = []
    for pot in sorted(set(r[0] for r in rows)):
        sub = [r for r in rows if r[0] == pot and r[3] is not None]
        fewer = [r for r in sub if r[2] < r[3]]
        equal = [r for r in sub if r[2] == r[3]]
        more = [r for r in sub if r[2] > r[3]]
        names = ", ".join("%02d(%d/%d)" % (r[1], r[2], r[3]) for r in sub if r[2] != r[3])
        print("%-4s %6d %5d %9d %6d %6d %5d  %s" % (
            pot, len(sub), sum(r[2] for r in sub), sum(r[3] for r in sub),
            len(fewer), len(equal), len(more), names if names else "-"))
        tot[0] += len(fewer); tot[1] += len(equal); tot[2] += len(more)
        tot[3] += sum(r[2] for r in sub); tot[4] += sum(r[3] for r in sub)
        allnames += ["%s%02d" % (pot, r[1]) for r in sub if r[2] != r[3]]
    n = sum(1 for r in rows if r[3] is not None)
    print("ALL  %6d %5d %9d %6d %6d %5d  (%d differing)" % (
        n, tot[3], tot[4], tot[0], tot[1], tot[2], len(allnames)))
    print("differing: " + " ".join(allnames))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["pota", "corpus"])
    ap.add_argument("--pota", default=None)
    ap.add_argument("--ours", default=None)
    ap.add_argument("--released", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--label", default="")
    a = ap.parse_args()
    if a.cmd == "pota":
        do_pota(a)
    else:
        do_corpus(a)


if __name__ == "__main__":
    main()
