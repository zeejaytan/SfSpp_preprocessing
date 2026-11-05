"""Command line — replaces extract_axis.m + 8x run_axis_piece_*.m.

Usage:
  python -m sfs_axes.cli extract-pot-a --surfaces DIR --out DIR [--seed N]

Ticket 306 defaults: no equal-count wall truncation, and the authors' paper
chain (one seed, 10-degree dedup, the cost < cost[0]*1.1 prune).  --union
switches to the multi-seed union; ticket 306 measured that arm worse on the
corpus and catastrophic on the assembler (Pot A 4/8 5/15), so it is opt-in
only.  --truncate restores the equal-count wall cut (read_surfaces.m:34-37)
for MATLAB parity.
"""

import argparse
import os
import time

import numpy as np

from .io_axes import axis_filename, write_axes
from .io_surfaces import read_surfaces
from .potsac import UNION_MAX, UNION_SEEDS, adaptive_step, run_potsac, run_potsac_union


def extract_piece(surfaces_dir, out_dir, pot_id="A", frag_id=1, seed=0,
                  step=10, adaptive=False, truncate=False, verbose=False,
                  paper_chain=True, union_seeds=None, max_candidates=None):
    """Run the full chain for one piece; write its assembly-layout axis file.

    Default (ticket 306): both walls whole and the authors' paper chain -
    run_potsac, one seed, 10-degree dedup, the cost < cost[0]*1.1 prune.
    paper_chain=False runs run_potsac_union instead: the Pottmann basins over
    union_seeds deterministic seeds, capped at max_candidates lines (default 6,
    the most the authors ever release for one piece) and ordered by the worse
    wall's cost per point.  Ticket 306 measured the union arm worse on all 163
    corpus pieces and catastrophic on the Pot A assembler (4/8 5/15), so it is
    not the default.
    """
    t0 = time.time()
    C0, C1 = read_surfaces(surfaces_dir, pot_id, frag_id,
                           truncate=truncate, verbose=verbose)
    n = C0.shape[1] + C1.shape[1]
    if adaptive:
        step = adaptive_step(n)
    if paper_chain:
        vt = run_potsac(C0, C1, rng=np.random.default_rng(seed), step=step,
                        verbose=verbose)
        mode = "paper-chain"
        if vt.shape[1] < 1:
            raise RuntimeError("piece %02d: no axis survived dedup" % frag_id)
    else:
        vt = run_potsac_union(C0, C1, seeds=union_seeds, step=step,
                              max_candidates=max_candidates, verbose=verbose)
        mode = "union"
        if vt.shape[1] < 1:
            raise RuntimeError("piece %02d: no axis found" % frag_id)
    path = os.path.join(out_dir, axis_filename(pot_id, frag_id))
    write_axes(path, vt)
    dt = time.time() - t0
    d, p = vt[0:3, 0], vt[3:6, 0]
    print("piece %02d: K=%d mode=%s step=%d truncate=%s n=%d -> %s (%.1fs)"
          % (frag_id, vt.shape[1], mode, step, bool(truncate), n, path, dt))
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
    ap.add_argument("--seed", type=int, default=0,
                    help="seed for --paper-chain only; the union path uses the "
                         "fixed seed set 0..N-1 so its output is deterministic")
    ap.add_argument("--step", type=int, default=10,
                    help="candidate stride, paper-letter 10%% (default 10); "
                         "pieces under 5,000 points use 1 (run_potsac.m:19-20, "
                         "ticket 304 — SFS_AXES_ADAPTIVE_UNDER_5K=0 to disable)")
    ap.add_argument("--adaptive", action="store_true",
                    help="working-tree adaptive step instead of paper 10%%")
    ap.add_argument("--truncate", action="store_true",
                    help="cut both walls to the shorter one (read_surfaces.m:34-37; "
                         "ticket 306: this loses Piece 08's second axis)")
    ap.add_argument("--no-truncate", action="store_true",
                    help="no equal-count cut (the default; overrides --truncate)")
    ap.add_argument("--paper-chain", action="store_true",
                    help="the authors' chain: one seed, 10-degree dedup, the "
                         "cost < cost[0]*1.1 prune (the default; the flag is "
                         "kept so older invocations keep working)")
    ap.add_argument("--union", action="store_true",
                    help="multi-seed union of the Pottmann basins instead of "
                         "the paper chain (ticket 306: worse on the corpus, "
                         "Pot A 4/8 5/15 on the assembler; diagnostic only)")
    ap.add_argument("--union-seeds", type=int, default=UNION_SEEDS,
                    help="seeds whose draws are unioned (default %d)" % UNION_SEEDS)
    ap.add_argument("--max-candidates", type=int, default=UNION_MAX,
                    help="cap on lines written per piece (default %d)" % UNION_MAX)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args(argv)
    if "-" in args.pieces:
        lo, hi = args.pieces.split("-")
        pieces = list(range(int(lo), int(hi) + 1))
    else:
        pieces = [int(x) for x in args.pieces.split(",")]
    # Ticket 306 B1: the equal-count cut is opt-in everywhere, including the
    # paper chain.  --paper-chain alone keeps both walls whole; add --truncate
    # for the MATLAB-faithful reproduction (read_surfaces.m:34-37).
    truncate = bool(args.truncate) and not args.no_truncate
    os.makedirs(args.out, exist_ok=True)
    for frag in pieces:
        extract_piece(args.surfaces, args.out, args.pot, frag, args.seed,
                      args.step, args.adaptive, truncate=truncate,
                      verbose=args.verbose, paper_chain=not args.union,
                      union_seeds=args.union_seeds,
                      max_candidates=args.max_candidates)


if __name__ == "__main__":
    main()
