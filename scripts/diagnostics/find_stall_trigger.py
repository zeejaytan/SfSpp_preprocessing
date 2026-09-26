"""
WHAT exactly stalls the walk on the real Juglet boundary cloud?

The saturation hypothesis is dead: on clean rings the walk covers 100% of
the rim at every K and every density (test_saturation_bound.py, sections
A and B). So the trigger is a property of the REAL cloud, not of K.

This finds the property by instrumenting the stall -- the exact step where
the inner loop appends nothing -- and reading off the K candidates the walk
had to choose from.

Then it searches for the MINIMAL perturbation of an ideal ring that
reproduces the stall, by adding one real-world ingredient at a time:

  1. uneven angular spacing (an eroded rim is not evenly sampled)
  2. off-plane noise (the rim is a 3D curve on a rough surface)
  3. the rim folding so two distant stretches pass close together

Knowing which ingredient is required matters: it tells the fix whether the
problem is sampling, noise, or 3D self-approach -- three different answers.
"""

import numpy as np
from scipy.spatial import cKDTree

import diagnose_walk as dw


def walk_instrumented(pts, K=None):
    """The walk, plus a record of every step where nothing was appended."""
    n = len(pts)
    if n == 0:
        return [], []
    if K is None:
        K = max(5, min(50, n // 10))
    K = min(K, n)
    tree = cKDTree(pts)

    seq, stalls = [0], []
    used = {tuple(pts[0])}
    current = 0

    for t in range(1, n):
        d, idx = tree.query(pts[current], k=K)
        idx = np.atleast_1d(idx)
        if t == 1:
            if len(idx) < 2:
                stalls.append((t, current, idx, d, list(seq)))
                continue
            current = int(idx[1])
            seq.append(current)
            used.add(tuple(pts[current]))
            continue
        picked = None
        for x in range(len(idx)):
            cand = int(idx[x])
            if tuple(pts[cand]) not in used:
                picked = cand
                break
        if picked is None:
            # THE STALL: every candidate in the K-window was already used.
            stalls.append((t, current, idx, d, list(seq)))
        else:
            current = picked
            seq.append(picked)
            used.add(tuple(pts[current]))
    return seq, stalls


def describe_stall(pts, t, current, idx, d, seq, label):
    n = len(pts)
    print(f"  [{label}] first stall at outer-loop step t={t}, "
          f"after {len(seq)} of {n} points appended")
    print(f"    stalled at point #{current} = "
          f"({pts[current][0]:.3f}, {pts[current][1]:.3f}, {pts[current][2]:.3f})")
    used = set(seq)
    print(f"    the K={len(idx)} candidates the walk could choose from:")
    for x in range(len(idx)):
        j = int(idx[x])
        mark = "USED" if j in used else "free"
        print(f"      x={x}  #{j:3d}  dist={float(d[x]):7.4f}  {mark}")
    # How much of the whole cloud sits within a few NN spacings of here?
    nn = np.linalg.norm(pts - pts[current], axis=1)
    near = np.sort(nn)[1:11]
    print(f"    10 nearest distances from the stall point: "
          f"{np.array2string(near, precision=3, max_line_width=200)}")
    print(f"    cloud median NN spacing: "
          f"{np.median(np.sort(cKDTree(pts).query(pts, k=2)[0][:, 1])):.4f} mm")
    print()


def shape_report(pts, label):
    centre = pts.mean(axis=0)
    sv = np.linalg.svd(pts - centre, compute_uv=False)
    nn = cKDTree(pts).query(pts, k=2)[0][:, 1]
    # Self-approach: how close does a point get to its 10th neighbour
    # compared with the typical spacing? A rim that folds brings distant
    # stretches into each other's neighbourhoods.
    tenth = cKDTree(pts).query(pts, k=11)[0][:, -1]
    print(f"  [{label}] shape of the cloud")
    print(f"    singular values        {np.array2string(sv, precision=3)}")
    print(f"    planarity (s3/s2)      {sv[2]/max(sv[1],1e-12):.4f}"
          f"   (0 = flat ring, 1 = volumetric blob)")
    print(f"    NN spacing  min/med/max "
          f"{nn.min():.4f} / {np.median(nn):.4f} / {nn.max():.4f} mm")
    print(f"    spacing ratio max/min  {nn.max()/max(nn.min(),1e-12):.1f}x")
    print(f"    10th-NN / median NN    {np.median(tenth)/np.median(nn):.2f}"
          f"   (>1 means neighbourhoods overlap -- points crowd)")
    print()


def ring(n, radius=15.0, jitter_frac=0.0, plane_mm=0.0, seed=0, fold=False):
    """An ideal ring with realistic damage added one ingredient at a time."""
    rng = np.random.default_rng(seed)
    t = 2.0 * np.pi * np.arange(n) / n
    if jitter_frac:
        # uneven angular spacing: each gap scaled by a random factor
        gaps = 1.0 + rng.uniform(-jitter_frac, jitter_frac, n)
        gaps = np.clip(gaps, 1e-3, None)
        ang = np.cumsum(gaps) * 2.0 * np.pi / gaps.sum()
        t = ang
    r = np.full(n, radius)
    if fold:
        # bring one arc radially inward so it approaches the far side
        arc = (t > np.pi * 0.9) & (t < np.pi * 1.1)
        r[arc] = radius * 0.35
    z = rng.normal(0.0, plane_mm, n) if plane_mm else np.zeros(n)
    return np.column_stack([r * np.cos(t), r * np.sin(t), z])


def try_ring(label, pts):
    seq, stalls = walk_instrumented(pts)
    n, out = len(pts), len(seq)
    steps = np.linalg.norm(np.diff(pts[seq], axis=0), axis=1) if out > 1 else np.zeros(0)
    traced = float(steps.sum())
    rim = 2 * np.pi * 15.0
    print(f"  {label:44s} out={out:5d}/{n:<5d} cov={out/n:5.3f} "
          f"traced={traced:7.2f}mm ({traced/rim:5.3f} of rim) "
          f"stalls={len(stalls)}")
    return out, n, stalls


def main():
    print("=" * 78)
    print("1. THE REAL CLOUD -- what does the stall look like?")
    print("=" * 78)
    for path in ("fixtures/boundary.pcd", "fixtures/boundaryImproved.pcd"):
        try:
            _, pts = dw.load_pcd_xyz(path)
        except FileNotFoundError:
            print(f"  ({path} missing)")
            continue
        print()
        print(f"--- {path} ---")
        shape_report(pts, path)
        seq, stalls = walk_instrumented(pts)
        if stalls:
            t, cur, idx, d, s = stalls[0]
            describe_stall(pts, t, cur, idx, d, s, path)
        else:
            print("  no stall; walk covered", len(seq), "of", len(pts))
        print()

    print("=" * 78)
    print("2. WHICH INGREDIENT REPRODUCES THE STALL?")
    print("   ideal ring, n=59 to match the real cloud, K=5")
    print("=" * 78)
    print()
    cases = [
        ("ideal ring", dict()),
        ("+ uneven spacing 10%", dict(jitter_frac=0.10)),
        ("+ uneven spacing 30%", dict(jitter_frac=0.30)),
        ("+ uneven spacing 50%", dict(jitter_frac=0.50)),
        ("+ uneven 30% & off-plane 0.1mm", dict(jitter_frac=0.30, plane_mm=0.1)),
        ("+ uneven 30% & off-plane 0.5mm", dict(jitter_frac=0.30, plane_mm=0.5)),
        ("+ uneven 50% & off-plane 0.5mm", dict(jitter_frac=0.50, plane_mm=0.5)),
        ("+ rim folded (arc brought inward)", dict(fold=True)),
        ("+ folded & uneven 30%", dict(fold=True, jitter_frac=0.30)),
    ]
    first_stall_case = None
    for label, kw in cases:
        pts = ring(59, **kw)
        out, n, stalls = try_ring(label, pts)
        if stalls and first_stall_case is None:
            first_stall_case = (label, pts, stalls)

    print()
    if first_stall_case:
        label, pts, stalls = first_stall_case
        print("=" * 78)
        print(f"3. THE STALL IN THE FIRST REPRODUCING CASE: {label}")
        print("=" * 78)
        t, cur, idx, d, s = stalls[0]
        describe_stall(pts, t, cur, idx, d, s, label)
    else:
        print("=" * 78)
        print("3. No synthetic case reproduced a stall. The trigger is not any")
        print("   of: spacing unevenness, off-plane noise, or rim folding.")
        print("   It is something else in the real cloud, and the honest next")
        print("   step is to diff the real cloud's neighbourhood structure")
        print("   against these rings rather than guess another ingredient.")
        print("=" * 78)


if __name__ == "__main__":
    main()
