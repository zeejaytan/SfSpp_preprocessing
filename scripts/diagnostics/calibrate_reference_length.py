"""
Calibrate the reference length the seam test will assert against.

A rim walk's output length should match the rim it covers. The rim's length
is not directly observable for a 3-D, non-planar sherd edge, so the test
needs a reference computed only from the cloud.

CANDIDATE: total length of the minimum spanning tree. For points sampled
along a smooth 1-D closed curve the MST length is a standard, computable
proxy for the curve length. This script measures the ratio
traced/MST on cases where the true answer is known (a circle of known
circumference), so the test's tolerance is calibrated rather than guessed.

Also reports the ratio on the real Juglet cloud, which is the case that has
to fail.

A tolerance set from a guess is how a test ends up passing for the wrong
reason, or failing for the right one and getting "fixed" by loosening the
number until it went away.
"""

import numpy as np
from scipy.spatial import cKDTree
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree

import diagnose_walk as dw
from find_stall_trigger import walk_instrumented, ring


def mst_total_length(pts):
    tree = cKDTree(pts)
    d = tree.sparse_distance_matrix(tree, np.inf).toarray()
    d = np.maximum(d, d.T)
    mst = minimum_spanning_tree(csr_matrix(d))
    return float(mst.data[mst.data > 0].sum())


def traced_length(pts, seq):
    if len(seq) < 2:
        return 0.0
    return float(np.linalg.norm(np.diff(pts[seq], axis=0), axis=1).sum())


def report(label, pts, truth=None):
    seq, stalls = walk_instrumented(pts)
    ref = mst_total_length(pts)
    traced = traced_length(pts, seq)
    ratio = traced / ref if ref else float("nan")
    line = (f"  {label:34s} in={len(pts):5d} out={len(seq):5d} "
            f"cov={len(seq)/len(pts):5.3f} traced={traced:8.3f} "
            f"mst={ref:8.3f} traced/mst={ratio:6.3f}")
    if truth:
        line += f"  (true rim {truth:7.3f}, mst/true={ref/truth:5.3f})"
    print(line)
    return ratio, len(seq) / len(pts), stalls


def main():
    print("=" * 88)
    print("CALIBRATION: how well does MST length stand in for rim length?")
    print("=" * 88)
    print()
    print("A. circles of known circumference, evenly sampled. MST/true shows")
    print("   the systematic bias of the reference; traced/mst shows the")
    print("   spread a tolerance must cover.")
    print()
    print("  case                                traced/mst   (mst/true)")
    ratios = []
    for radius in (6.3, 15.0, 40.0):
        circumference = 2 * np.pi * radius
        for n in (59, 129, 400, 1200):
            pts = ring(n, radius=radius)
            r, cov, _ = report(f"circle R={radius} n={n}", pts, circumference)
            ratios.append(r)
    print()
    print(f"  traced/mst on circles: min={min(ratios):.4f} max={max(ratios):.4f}")
    print()

    print("B. circles with the damage the walk actually meets: uneven spacing")
    print("   and off-plane noise. A tolerance calibrated only on clean circles")
    print("   would be calibrated on a case that never occurs.")
    print()
    ratios2 = []
    for jit in (0.0, 0.2, 0.4):
        for plane in (0.0, 0.2, 0.6):
            pts = ring(400, radius=15.0, jitter_frac=jit, plane_mm=plane, seed=3)
            r, cov, _ = report(f"jitter={jit} plane={plane}mm", pts,
                               2 * np.pi * 15.0)
            ratios2.append(r)
    print()
    print(f"  traced/mst on damaged circles: min={min(ratios2):.4f} "
          f"max={max(ratios2):.4f}")
    print()

    print("C. THE CASE THAT MUST FAIL: the real Juglet boundary cloud.")
    print()
    for path in ("fixtures/boundary.pcd", "fixtures/boundaryImproved.pcd"):
        try:
            _, pts = dw.load_pcd_xyz(path)
        except FileNotFoundError:
            continue
        report(path, pts)
    print()
    print("D. the synthetic that reproduces the real failure exactly")
    print("   (40x density contrast, 15% dense) -- mechanism, not measurement")
    print()
    from test_density_contrast import ring_with_contrast
    report("40x contrast, 15% dense", ring_with_contrast(59, dense_frac=0.15,
                                                        dense_squeeze=40.0, seed=1),
           2 * np.pi * 15.0)
    print()
    print("=" * 88)
    print("SUGGESTED TEST BOUNDS, from the calibration above:")
    lo = min(ratios + ratios2)
    hi = max(ratios + ratios2)
    print(f"  a healthy traversal has traced/mst in [{lo:.3f}, {hi:.3f}]")
    print(f"  the real Juglet cloud sits far below that -- see section C")
    print("=" * 88)


if __name__ == "__main__":
    main()
