"""
Faithful Python reproduction of SfS++ getPointsInSequence, for diagnosis.

WHY A SIMULATOR: the C++ seam test (ticket 01) is the artefact that has to
live in the repo. But diagnosing *why* the walk stalls is faster here --
seconds on the laptop instead of a build in a held allocation -- and this
script is checked against the C++ result before anything is believed.

THE FAITHFULNESS QUESTION MATTERS. If this simulator and the C++ function
disagree, every conclusion drawn from the simulator is void. So
`verify_against_cpp()` compares them point-for-point and the ticket records
the comparison, not the simulator's word.

The transcribed rule, from edge_line_ordering.cpp:

    K = max(5, min(50, n / 10))
    push cloud[0]
    for t in 1 .. n-1:
        knn = K nearest to current          (sorted by distance)
        if t == 1:
            push knn[1]                     # second nearest, no unused test
            continue
        for x in 0 .. K-1:
            if knn[x] not in sequenced (EXACT float equality):
                push knn[x]; break

Two details that are the whole story:
  - the "unused" test is exact float equality, so near-duplicates count as
    new and the walk crawls through them;
  - when all K candidates are already used the inner loop appends nothing
    and the outer loop spins on. Truncation, not derailment.
"""

import sys
import numpy as np
from scipy.spatial import cKDTree

PCD_FIELDS_XYZ = 3


def load_pcd_xyz(path):
    """Read an ASCII .PCD, returning points and the header dict."""
    header, pts = {}, []
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        in_data = False
        for line in fh:
            line = line.strip()
            if not line:
                continue
            if in_data:
                f = line.split()
                if len(f) >= PCD_FIELDS_XYZ:
                    pts.append([float(v) for v in f[:PCD_FIELDS_XYZ]])
                continue
            if line.startswith("DATA"):
                in_data = True
                continue
            if line.startswith("#") or " " not in line:
                continue
            k, v = line.split(None, 1)
            header[k] = v
    return header, np.asarray(pts, dtype=np.float64)


def walk_K(pts, K=None, unused_is_exact=True, tol=0.0):
    """The walk, as written. Returns the ordered index list."""
    n = len(pts)
    if n == 0:
        return []
    if K is None:
        K = max(5, min(50, n // 10))
    K = min(K, n)  # PCL returns fewer than K when n < K
    tree = cKDTree(pts)

    seq = [0]
    current = 0
    # Exact float equality via a set of coordinate tuples. Same semantics as
    # the C++ p1.x==q.x && p1.y==q.y && p1.z==q.z, O(1) instead of O(n).
    # Safe because the C++ compares float32 and we compare the parsed
    # decimals: two equal decimals parse equal in both, two different
    # decimals differ in both, so the equality relation is preserved.
    used = {tuple(pts[0])}
    for t in range(1, n):
        d, idx = tree.query(pts[current], k=K)
        idx = np.atleast_1d(idx)
        if t == 1:
            # second nearest, unconditionally -- no unused test at all
            seq.append(int(idx[1]))
            current = int(idx[1])
            used.add(tuple(pts[current]))
            continue
        for x in range(K):
            cand = int(idx[x])
            key = tuple(pts[cand])
            hit = (key in used) if unused_is_exact else False
            if not hit:
                seq.append(cand)
                current = cand
                used.add(key)
                break
    return seq


def walk_always_unused(pts, K=None):
    """The walk with the unused test removed -- a control, not a proposal.

    Isolates how much of the damage is the K-window and how much is the
    exact-equality test. If dropping the unused test recovers coverage
    while leaving K large still derails, the two defects are separable and
    worth separate tickets.
    """
    n = len(pts)
    if n == 0:
        return []
    if K is None:
        K = max(5, min(50, n // 10))
    K = min(K, n)
    tree = cKDTree(pts)
    seq, current = [0], 0
    for t in range(1, n):
        d, idx = tree.query(pts[current], k=K)
        idx = np.atleast_1d(idx)
        pick = int(idx[1]) if t == 1 else int(idx[0])
        seq.append(pick)
        current = pick
    return seq


def geometry_report(pts, seq):
    """What the traversal looks like as a curve."""
    out = pts[seq]
    steps = np.linalg.norm(np.diff(out, axis=0), axis=1) if len(out) > 1 else np.zeros(0)
    return {
        "n_in": len(pts),
        "n_out": len(seq),
        "coverage": len(seq) / len(pts) if len(pts) else 0.0,
        "traced_len_mm": float(steps.sum()),
        "median_step_mm": float(np.median(steps)) if len(steps) else 0.0,
        "worst_step_mm": float(steps.max()) if len(steps) else 0.0,
    }


def cluster_report(pts, eps=1e-4):
    """How tightly packed is the cloud? The suspected cause of the stall."""
    tree = cKDTree(pts)
    d, _ = tree.query(pts, k=2)
    nn = d[:, 1]
    # Connected components at eps: groups of mutually-near points. The walk
    # stalls when one such group holds >= K points, because then the whole
    # K-nearest window is spent on ground already covered.
    from scipy.sparse.csgraph import connected_components
    from scipy.sparse import coo_matrix
    a = tree.sparse_distance_matrix(tree, eps, output_type="coo_matrix")
    ncomp, labels = connected_components(a, directed=False)
    sizes = np.bincount(labels)
    return {
        "nn_dist_median_mm": float(np.median(nn)),
        "nn_dist_min_mm": float(nn.min()),
        "n_exact_duplicate_pairs": int(
            sum(1 for i in range(len(pts)) for j in range(i + 1, len(pts))
                if np.array_equal(pts[i], pts[j]))
        ),
        "components_at_1e-4": int(ncomp),
        "largest_component": int(sizes.max()),
        "K_saturating_groups": int((sizes >= max(5, min(50, len(pts) // 10))).sum()),
    }


def rim_estimate(pts):
    """A rough rim length, for the coverage figure. PCA plane + hull.

    Only used to say "the traversal covered x% of the rim it should have".
    Concave-hull length is a lower bound on the true rim, so a traversal
    near or above it is not being called short on a technicality.
    """
    from scipy.spatial import ConvexHull
    centre = pts.mean(axis=0)
    _, _, vt = np.linalg.svd(pts - centre, full_matrices=False)
    normal = vt[2]
    basis = vt[:2]
    flat = (pts - centre) @ basis.T
    try:
        hull = ConvexHull(flat)
        perim = hull.perimeter
    except Exception:
        perim = float("nan")
    r = float(np.median(np.linalg.norm(flat, axis=1)))
    return {
        "pca_plane_normal": normal.tolist(),
        "convex_hull_perimeter_mm": float(perim),
        "median_radius_mm": r,
        "circle_circumference_2piR_mm": float(2 * np.pi * r),
    }


def main():
    for path in sys.argv[1:]:
        header, pts = load_pcd_xyz(path)
        n = len(pts)
        K = max(5, min(50, n // 10))
        print("=" * 72)
        print(f"{path}")
        print(f"  points={n}  K={K}")
        print()
        print("  cluster structure (the suspected cause):")
        for k, v in cluster_report(pts).items():
            print(f"    {k:28s} {v}")
        print()
        print("  rim estimate:")
        for k, v in rim_estimate(pts).items():
            print(f"    {k:28s} {v}")
        print()
        print("  the walk, as written:")
        seq = walk_K(pts)
        g = geometry_report(pts, seq)
        for k, v in g.items():
            print(f"    {k:28s} {v}")
        print()
        print("  control -- exact-equality test removed, same K:")
        seq2 = walk_always_unused(pts)
        g2 = geometry_report(pts, seq2)
        for k, v in g2.items():
            print(f"    {k:28s} {v}")
        print()
        print("  same walk, K forced to 2 (the refuted tuning patch):")
        seq3 = walk_K(pts, K=2)
        g3 = geometry_report(pts, seq3)
        for k, v in g3.items():
            print(f"    {k:28s} {v}")
        print()


if __name__ == "__main__":
    main()
