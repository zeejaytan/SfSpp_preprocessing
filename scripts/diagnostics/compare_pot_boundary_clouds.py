"""
Ticket 08: is the ordering defect Juglet-specific, or general?

Consumes the per-sherd boundary-cloud snapshots that run_scope_check.sh
captures (Temp_edge/ is overwritten per sherd, so a plain run leaves only
the last one) and measures BOTH pots with identical definitions.

The question this can answer
---------------------------
Ticket 01 established the mechanism: the walk truncates where part of the
rim is sampled at least K times denser than the rim's median spacing, or
where points scatter further off the rim than the local spacing.

That mechanism is a property of INPUT GEOMETRY, not of a particular pot.
Pot_A is the control -- it produces 15/15 correct joins. So:

  - if Pot_A's boundary clouds are near-uniformly sampled AND the walk
    covers them, the mechanism holds and the defect is conditional on
    sampling. "This pot is awkward material" is then a defensible
    description, and the fix is a better ordering step.
  - if Pot_A ALSO shows large spacing variation and still gets full
    coverage, THE MECHANISM IS WRONG and ticket 03 must not be built on it.
  - if Pot_A shows large spacing variation AND truncation, the defect is
    general and Pot_A survives by luck of sampling, not by merit.

The middle case is the one that matters and the one nobody has checked.

Usage:
    python compare_pot_boundary_clouds.py <snapshot-root>
    (expects <root>/Juglet/boundary_*.pcd and <root>/Pot_A/boundary_*.pcd)
"""

import os
import sys
from collections import Counter

import numpy as np
from scipy.spatial import cKDTree
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree

import diagnose_walk as dw
from find_stall_trigger import walk_instrumented


def mst_total(pts):
    tree = cKDTree(pts)
    d = tree.sparse_distance_matrix(tree, np.inf).toarray()
    d = np.maximum(d, d.T)
    mst = minimum_spanning_tree(csr_matrix(d))
    return float(mst.data[mst.data > 0].sum())


def measure(pts):
    """Every quantity the ticket needs, on one boundary cloud."""
    n = len(pts)
    K = max(5, min(50, n // 10))
    tree = cKDTree(pts)
    nn = tree.query(pts, k=2)[0][:, 1]
    med = float(np.median(nn))
    counts = np.asarray(tree.query_ball_point(pts, r=K * med, return_length=True))

    seq, stalls = walk_instrumented(pts)
    out = len(seq)
    steps = (np.linalg.norm(np.diff(pts[seq], axis=0), axis=1)
             if out > 1 else np.zeros(0))
    traced = float(steps.sum())
    ref = mst_total(pts)

    # Spacing variation must be measured with percentiles, NOT max/min.
    # Where a cloud holds exact duplicates nn_min is 0.0, so max/min divides
    # by ~1e-12 and prints ratios of 1e12 -- which silently poisons any
    # comparison between pots. p90/p10 is finite unless the cloud is itself
    # degenerate, and it is the spread the walk actually feels.
    p10, p90 = np.percentile(nn, 10), np.percentile(nn, 90)
    dup = int(np.sum(nn <= 0.0))

    return {
        "n": n,
        "K": K,
        "nn_min": float(nn.min()),
        "nn_med": med,
        "nn_max": float(nn.max()),
        "nn_spread": float(p90 / p10) if p10 > 0 else float("inf"),
        "n_exact_dup": dup,
        "frac_window_full": float(np.mean(counts >= K)),
        "out": out,
        "coverage": out / n,
        "traced_mm": traced,
        "ref_mm": ref,
        "traced_over_ref": traced / ref if ref else float("nan"),
        "stalls": len(stalls),
    }


def fmt(m):
    return (f"n={m['n']:4d} K={m['K']:3d} "
            f"nn={m['nn_min']:.3f}/{m['nn_med']:.3f}/{m['nn_max']:.3f} "
            f"spread(p90/p10)={m['nn_spread']:7.1f}x dup={m['n_exact_dup']:3d} "
            f"winfull={m['frac_window_full']:.2f} | "
            f"out={m['out']:4d} cov={m['coverage']:.3f} "
            f"traced/ref={m['traced_over_ref']:.3f} stalls={m['stalls']:3d}")


def summarise(pot, rows):
    if not rows:
        print(f"  {pot}: no snapshots found")
        return None
    cov = np.array([r["coverage"] for r in rows])
    spread = np.array([r["nn_spread"] for r in rows])
    win = np.array([r["frac_window_full"] for r in rows])
    tr = np.array([r["traced_over_ref"] for r in rows], dtype=float)
    ns = np.array([r["n"] for r in rows])
    dup = np.array([r["n_exact_dup"] for r in rows])
    print(f"  {pot:8s} sherds={len(rows):2d}  "
          f"coverage  min={cov.min():.3f} med={np.median(cov):.3f} max={cov.max():.3f}  "
          f"full-coverage sherds={int((cov >= 0.9).sum())}/{len(rows)}")
    print(f"           nn spread(p90/p10)  min={spread.min():.1f}x "
          f"med={np.median(spread):.1f}x max={spread.max():.1f}x")
    print(f"           exact-duplicate points       min={dup.min()} "
          f"med={int(np.median(dup))} max={dup.max()}")
    print(f"           win-full frac     min={win.min():.2f} med={np.median(win):.2f} "
          f"max={win.max():.2f}")
    print(f"           traced/ref        min={np.nanmin(tr):.3f} "
          f"med={np.nanmedian(tr):.3f} max={np.nanmax(tr):.3f}")
    print(f"           cloud size        min={ns.min()} med={int(np.median(ns))} "
          f"max={ns.max()}")
    return {"cov": cov, "spread": spread, "win": win, "tr": tr, "n": ns,
            "dup": dup}


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    root = sys.argv[1]
    pots = [p for p in ("Juglet", "Pot_A")
            if os.path.isdir(os.path.join(root, p))]

    all_rows = {}
    for pot in pots:
        d = os.path.join(root, pot)
        files = sorted(f for f in os.listdir(d) if f.endswith(".pcd"))
        print("=" * 100)
        print(f"{pot}: {len(files)} boundary-cloud snapshots")
        print("=" * 100)
        rows = []
        for fn in files:
            _, pts = dw.load_pcd_xyz(os.path.join(d, fn))
            if len(pts) < 3:
                print(f"  {fn}: only {len(pts)} points, skipped")
                continue
            m = measure(pts)
            rows.append(m)
            print(f"  {fn[:22]}  {fmt(m)}")
        print()
        all_rows[pot] = rows

    print("=" * 100)
    print("SUMMARY")
    print("=" * 100)
    summ = {p: summarise(p, all_rows[p]) for p in pots}

    if "Juglet" in summ and "Pot_A" in summ and summ["Juglet"] and summ["Pot_A"]:
        j, a = summ["Juglet"], summ["Pot_A"]
        print()
        print("VERDICT -- which of the three is it?")
        print()
        j_full = int((j["cov"] >= 0.9).sum())
        a_full = int((a["cov"] >= 0.9).sum())
        j_sp, a_sp = float(np.median(j["spread"])), float(np.median(a["spread"]))
        print(f"  Juglet: {j_full}/{len(j['cov'])} sherds fully covered, "
              f"spacing spread {j_sp:.0f}x (median)")
        print(f"  Pot_A : {a_full}/{len(a['cov'])} sherds fully covered, "
              f"spacing spread {a_sp:.0f}x (median)")
        print()
        # The spread threshold is the Juglet's own measured value, rounded:
        # the defect was established at ~20x. "Near-uniform" means clearly
        # below that, not "under some other arbitrary line".
        UNIFORM = 5.0
        if a_full == len(a["cov"]) and a_sp < UNIFORM:
            print("  -> DEFECT IS CONDITIONAL ON SAMPLING. Pot_A is near-uniformly")
            print("     sampled and fully covered; the Juglet is not. The mechanism")
            print("     holds. A better ordering step is the right fix, and the")
            print("     Juglet's failure is a property of that material, not of the")
            print("     method in general.")
        elif a_full == len(a["cov"]) and a_sp >= UNIFORM:
            print("  -> ** MECHANISM SUSPECT. Pot_A is ALSO unevenly sampled but")
            print("     still fully covered, so spacing contrast alone does not")
            print("     explain the truncation. Ticket 03 must NOT be built on the")
            print("     current diagnosis until this is explained.")
        elif a_full < len(a["cov"]):
            print("  -> DEFECT IS GENERAL. Pot_A also truncates, so Pot_A's 15/15")
            print("     is partly luck of sampling rather than merit. Any claim")
            print("     that the method works on well-preserved sherds needs")
            print("     re-examining.")
        else:
            print("  -> INCONCLUSIVE. See the per-sherd tables above; the two pots")
            print("     do not separate cleanly and the diagnosis needs revisiting.")
        print()
        print(f"  (uniformity threshold {UNIFORM}x spread, against the ~20x at which")
        print("   the defect was established on the Juglet)")
    else:
        print()
        print("  Only one pot present, so no comparison is possible. The mechanism")
        print("  remains unconfirmed outside the Juglet.")


if __name__ == "__main__":
    main()
