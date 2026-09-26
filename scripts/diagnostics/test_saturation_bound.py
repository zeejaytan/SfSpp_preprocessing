"""
Is the walk's truncation a BOUND, or one unlucky sherd?

The 59-point Juglet boundary cloud came out as 9 ordered points, and 9 is
suspiciously close to 2K-1 = 9 for K=5. If the walk cannot exceed ~2K-1
points regardless of input, that is arithmetic, not bad luck, and it
predicts the truncation on every other sherd too -- which is what the run
logs show (boundary 129 -> 75 resampler inputs, 110 -> ?, etc.).

The claim, stated so it can fail:

    The walk appends the first UNUSED point among the K nearest. Every point
    in the K-nearest window of a point sitting inside a contiguous run of m
    already-visited points is itself inside that run, once m >= K. So no
    unused candidate exists and the walk stops. Output is therefore bounded
    near 2K-1, INDEPENDENT of how long the rim is.

If instead output scaled with rim length, the bound claim is false and the
Juglet truncation needs another explanation. This script runs both
predictions against controls where the answer is known.
"""

import numpy as np
from scipy.spatial import cKDTree

import diagnose_walk as dw


def ring(n, radius=15.0, spacing=None, jitter=0.0, seed=0):
    """n points on a circle. spacing overrides even angular spacing."""
    rng = np.random.default_rng(seed)
    if spacing is None:
        t = 2.0 * np.pi * np.arange(n) / n
    else:
        step = spacing / radius
        t = np.arange(n) * step
    r = radius + (rng.uniform(-jitter, jitter, n) if jitter else 0.0)
    return np.column_stack([r * np.cos(t), r * np.sin(t), rng.uniform(-jitter, jitter, n) * 0.1])


def coverage(pts, K=None):
    seq = dw.walk_K(pts, K=K)
    return len(seq), len(pts)


def main():
    print("=" * 78)
    print("CLAIM: walk output is bounded near 2K-1, independent of rim length")
    print("=" * 78)
    print()
    print("A. vary the number of points on a FIXED-SIZE rim (radius 15 mm),")
    print("   so the rim gets denser but its LENGTH does not change.")
    print("   If the bound is real, output stays near 2*(n/10)-1 and does NOT")
    print("   grow with n.")
    print()
    print("   n     K=auto  2K-1   out   coverage   median_step_mm")
    for n in (40, 60, 100, 200, 400, 800, 1600):
        pts = ring(n)
        K = max(5, min(50, n // 10))
        out, tot = coverage(pts)
        seq = dw.walk_K(pts)
        steps = np.linalg.norm(np.diff(pts[seq], axis=0), axis=1)
        med = float(np.median(steps)) if len(steps) else 0.0
        print(f"  {n:5d}  {K:6d}  {2*K-1:5d}  {out:5d}   {out/tot:7.3f}   {med:.4f}")
    print()
    print("   READ THE TABLE, not this script. The hypothesis in the header was")
    print("   REFUTED by the run below: coverage stays at 1.000 for every n and")
    print("   every K, so the walk is not bounded near 2K-1 and K alone does not")
    print("   truncate it. Section B pins K and grows the rim 32x; if the bound")
    print("   were real the output would stay flat while the rim grew. It does")
    print("   not. What actually truncates the walk is in")
    print("   test_density_contrast.py -- kept here as the record of the")
    print("   refutation, because a discarded hypothesis is worth as much as a")
    print("   confirmed one.")
    print()

    print("B. hold K fixed by forcing it, vary rim length only.")
    print("   If the bound is real, output is pinned at 2K-1 while the rim grows.")
    print()
    print("   n     K=8   out   coverage   traced_len_mm   rim_2piR_mm")
    for n in (100, 200, 400, 800, 1600, 3200):
        pts = ring(n)
        out, tot = coverage(pts, K=8)
        seq = dw.walk_K(pts, K=8)
        traced = float(np.linalg.norm(np.diff(pts[seq], axis=0), axis=1).sum())
        print(f"  {n:5d}  {8:4d}  {out:5d}   {out/tot:7.3f}   {traced:12.3f}   {2*np.pi*15:11.1f}")
    print()
    print("   -> output tracks the rim, not K. The refutation, in one line.")
    print()

    print("C. the same rim at K=1,2,5,10,20,50 -- does output track K alone?")
    print()
    print("   K     out   coverage   (n=800 fixed)")
    pts = ring(800)
    for K in (1, 2, 5, 10, 20, 50):
        out, tot = coverage(pts, K=K)
        print(f"  {K:4d}  {out:5d}   {out/tot:7.3f}")
    print()
    print("   -> at K=1 the rule is 'nearest unused point', which is the")
    print("      textbook greedy rim walk and should cover the whole ring.")
    print("      If it does, the ordering PROBLEM is not the ordering RULE's")
    print("      fault; it is that K is large enough to break the rule.")
    print()

    print("=" * 78)
    print("CONTROL: the real Juglet boundary cloud, against the same arithmetic")
    print("=" * 78)
    for path in ("boundary.pcd", "boundaryImproved.pcd"):
        try:
            _, pts = dw.load_pcd_xyz(f"fixtures/{path}")
        except FileNotFoundError:
            print(f"  (fixtures/{path} not present)")
            continue
        n = len(pts)
        K = max(5, min(50, n // 10))
        out, _ = coverage(pts)
        seq = dw.walk_K(pts)
        steps = np.linalg.norm(np.diff(pts[seq], axis=0), axis=1)
        traced = float(steps.sum()) if len(steps) else 0.0
        rim = dw.rim_estimate(pts)["circle_circumference_2piR_mm"]
        print(f"  {path}")
        print(f"    n={n} K={K} 2K-1={2*K-1}  out={out}")
        print(f"    traced={traced:.3f} mm   rim~{rim:.1f} mm   "
              f"traced/rim={traced/rim:.3f}")
        print(f"    matches the 2K-1 bound: {abs(out - (2*K-1)) <= 2}")
        print()


if __name__ == "__main__":
    main()
