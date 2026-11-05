#!/usr/bin/env python3
"""census308.py -- ticket 308 Stage A tables: the axis set, its lines, its drift.

  census308.py k    --ours DIR --ref DIR --out TSV [--label NAME]
      One row per piece: K ours, K ref, delta, angle(line 0 ours, line 0 ref),
      and the smallest angle from any of our lines to any ref line.  Angles are
      sign-agnostic (arccos |a.b| on the direction columns 3:6), the same measure
      as io_axes.direction_angle_deg / census307.py.  Files are position-first,
      6 columns, K rows.

  census308.py md5  --ours DIR --ref DIR --out TSV [--label NAME]
      One row per piece: md5 of each file and equal/differ, plus the counts.
      Used for fresh-vs-reused provenance (A1) and for the 305-reproduction check.

Prints a short summary; the tsv is the record.
"""
import argparse, glob, hashlib, os
import numpy as np


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


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
    parts = os.path.basename(path)[:-4].split("_")
    return parts[1], int(parts[3])


def do_k(a):
    rows = []
    for p in sorted(glob.glob(os.path.join(a.ours, "Pot_*_Piece_*_Axis.xyz"))):
        pot, nn = parse_name(p)
        rel = os.path.join(a.ref, os.path.basename(p))
        O = read_axes(p)
        if not os.path.exists(rel):
            rows.append((pot, nn, O.shape[1], None, None, float("nan"), float("nan")))
            continue
        R = read_axes(rel)
        l0 = ang(O[3:6, 0], R[3:6, 0]) if O.shape[1] and R.shape[1] else float("nan")
        best = min((ang(O[3:6, i], R[3:6, j])
                    for i in range(O.shape[1]) for j in range(R.shape[1])),
                   default=float("nan"))
        rows.append((pot, nn, O.shape[1], R.shape[1], O.shape[1] - R.shape[1], l0, best))
    with open(a.out, "w", newline="\n") as f:
        f.write("pot\tpiece\tK_ours\tK_ref\tdelta\tline0_deg\tbest_deg\n")
        for r in rows:
            f.write("\t".join(("%.3f" % v) if isinstance(v, float) else
                              ("-" if v is None else str(v)) for v in r) + "\n")
    ok = [r for r in rows if r[3] is not None]
    d = [r for r in ok if r[4] != 0]
    a0 = np.array([r[5] for r in ok if not np.isnan(r[5])])
    b0 = np.array([r[6] for r in ok if not np.isnan(r[6])])
    print("[%s] pieces %d  K ours %d  K ref %d  line-count differs on %d"
          % (a.label, len(ok), sum(r[2] for r in ok), sum(r[3] for r in ok), len(d)))
    if a0.size:
        print("      line0 angle: median %.3f  p90 %.3f  <=5deg %d/%d"
              % (float(np.median(a0)), float(np.percentile(a0, 90)),
                 int((a0 <= 5).sum()), a0.size))
        print("      best-line angle: median %.3f  p90 %.3f  <=5deg %d/%d"
              % (float(np.median(b0)), float(np.percentile(b0, 90)),
                 int((b0 <= 5).sum()), b0.size))
    if d:
        print("      differing: " + " ".join("%s%02d(%d/%d)" % (r[0], r[1], r[2], r[3]) for r in d))


def do_md5(a):
    rows = []
    for p in sorted(glob.glob(os.path.join(a.ours, "*.xyz"))):
        b = os.path.basename(p)
        q = os.path.join(a.ref, b)
        m1 = md5(p)
        m2 = md5(q) if os.path.exists(q) else "-"
        rows.append((b, m1, m2, "equal" if m1 == m2 else ("missing" if m2 == "-" else "differ")))
    with open(a.out, "w", newline="\n") as f:
        f.write("file\tmd5_ours\tmd5_ref\tverdict\n")
        for r in rows:
            f.write("\t".join(r) + "\n")
    eq = sum(1 for r in rows if r[3] == "equal")
    df = [r for r in rows if r[3] != "equal"]
    print("[%s] files %d  equal %d  differ %d" % (a.label, len(rows), eq, len(df)))
    for r in df[:20]:
        print("      DIFFER " + r[0])
    return 0 if not df else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["k", "md5"])
    ap.add_argument("--ours", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--label", default="")
    a = ap.parse_args()
    (do_k if a.cmd == "k" else do_md5)(a)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
