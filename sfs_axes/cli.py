"""Command line — replaces extract_axis.m + 8x run_axis_piece_*.m.

Usage:
  python -m sfs_axes.cli extract-pot-a --surfaces DIR --out DIR [--seed N]
"""

import argparse
import os
import time

import numpy as np

from .io_axes import axis_filename, write_axes
from .io_surfaces import read_surfaces
from .potsac import adaptive_step, run_potsac


def extract_piece(surfaces_dir, out_dir, pot_id="A", frag_id=1, seed=0,
                  step=10, adaptive=False, truncate=True, verbose=False):
    """Run the full chain for one piece; write its assembly-layout axis file."""
    t0 = time.time()
    C0, C1 = read_surfaces(surfaces_dir, pot_id, frag_id,
                           truncate=truncate, verbose=verbose)
    n = C0.shape[1] + C1.shape[1]
    if adaptive:
        step = adaptive_step(n)
    rng = np.random.default_rng(seed)
    vt = run_potsac(C0, C1, rng=rng, step=step, verbose=verbose)
    if vt.shape[1] < 1:
        raise RuntimeError("piece %02d: no axis survived dedup" % frag_id)
    path = os.path.join(out_dir, axis_filename(pot_id, frag_id))
    write_axes(path, vt)
    dt = time.time() - t0
    d, p = vt[0:3, 0], vt[3:6, 0]
    print("piece %02d: K=%d seed=%d step=%d n=%d -> %s (%.1fs)"
          % (frag_id, vt.shape[1], seed, step, n, path, dt))
    print("  best pos=[%.4f %.4f %.4f] dir=[%.6f %.6f %.6f]"
          % (p[0], p[1], p[2], d[0], d[1], d[2]))
    return vt


def main(argv=None):
    ap = argparse.ArgumentParser(description="sfs_axes Pot A axis extraction")
    ap.add_argument("command", choices=["extract-pot-a"])
    ap.add_argument("--surfaces", required=True, help="dir with Surface_0/1 xyz")
    ap.add_argument("--out", required=True, help="output Axes dir")
    ap.add_argument("--pot", default="A")
    ap.add_argument("--pieces", default="1-8", help="e.g. 1-8 or 3,5")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--step", type=int, default=10,
                    help="candidate stride, paper-letter 10%% (default 10)")
    ap.add_argument("--adaptive", action="store_true",
                    help="working-tree adaptive step instead of paper 10%%")
    ap.add_argument("--no-truncate", action="store_true",
                    help="disable MATLAB equal-count truncation")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args(argv)
    if "-" in args.pieces:
        lo, hi = args.pieces.split("-")
        pieces = list(range(int(lo), int(hi) + 1))
    else:
        pieces = [int(x) for x in args.pieces.split(",")]
    os.makedirs(args.out, exist_ok=True)
    for frag in pieces:
        extract_piece(args.surfaces, args.out, args.pot, frag, args.seed,
                      args.step, args.adaptive,
                      truncate=not args.no_truncate, verbose=args.verbose)


if __name__ == "__main__":
    main()
