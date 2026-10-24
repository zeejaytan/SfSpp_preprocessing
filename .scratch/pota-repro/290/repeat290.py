#!/usr/bin/env python3
"""Ticket 290 follow-up - is a run from the frozen cloud reproducible?

Scores two independent edge runs (same frozen cloud, same mesh, same axis, same shipped
defaults) against the authors' reference, and compares their exported files byte for byte.

Usage: repeat290.py <run-dir> <lane-dir-A> <lane-dir-B>
Each lane dir holds <PIECE>_Breakline_{0,1}.pcd.
"""
import hashlib
import importlib.util
import os
import sys

SCORE275 = "/data/gpfs/projects/punim2657/SfSpp/runs/20261024-0329_1308298_p275-walker/score275.py"
AUTH = "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Breaklines/Pot_J_Piece_09_Breakline_%d.pcd"
PIECE = "Pot_J_Piece_09"


def load():
    spec = importlib.util.spec_from_file_location("score275", SCORE275)
    mod = importlib.util.module_from_spec(spec)
    argv = sys.argv
    sys.argv = ["x", "/nonexistent"]
    try:
        spec.loader.exec_module(mod)
    except SystemExit:
        pass
    finally:
        sys.argv = argv
    return mod


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def main():
    run, da, db = sys.argv[1], sys.argv[2], sys.argv[3]
    sm = load()
    print("%-4s %-3s %5s %8s %8s %8s %5s %9s %9s  %s"
          % ("rep", "st", "n", "med", "cov_o", "cov_a", "jmp", "maxstep", "len_mm", "bar"))
    same = True
    for st in (0, 1):
        fa = os.path.join(da, PIECE + "_Breakline_%d.pcd" % st)
        fb = os.path.join(db, PIECE + "_Breakline_%d.pcd" % st)
        if not (os.path.exists(fa) and os.path.exists(fb)):
            print("MISSING lane %d: %s %s" % (st, os.path.exists(fa), os.path.exists(fb)))
            same = False
            continue
        for tag, f in (("A", fa), ("B", fb)):
            o, a = sm.readpts(f), sm.readpts(AUTH % st)
            n, med, co, ca, j, mx, ok = sm.lane(o, a)
            import numpy as np
            d = np.sqrt(((o[1:] - o[:-1]) ** 2).sum(1)).sum() + np.sqrt(((o[0] - o[-1]) ** 2).sum())
            print("%-4s %-3d %5d %8.3f %8.2f %8.2f %5d %9.3f %9.2f  %s"
                  % (tag, st, n, med, co, ca, j, mx, d, "PASS" if ok else "below"))
        ha, hb = md5(fa), md5(fb)
        same = same and ha == hb
        print("[BYTES] Bl%d  A=%s  B=%s  identical=%s" % (st, ha, hb, ha == hb))
    print("[REPEAT] byte_identical_across_runs=%s" % ("YES" if same else "NO"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
