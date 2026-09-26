"""
Is the trigger LOCAL DENSITY CONTRAST -- a dense patch holding more than K
points inside a short arc?

The instrumented stall says yes, and gives two numbers to match:

  real boundary.pcd:  NN spacing 0.096 .. 1.958 mm   (20.4x ratio)
                      10th-NN / median-NN = 7.47

A K=5 window spans about 5 x (local spacing) of arc. Where the local
spacing is 0.1 mm that window covers 0.5 mm -- five points and nothing
else, so the walk saturates on its own back-track. Where spacing is
2 mm the same window covers 10 mm and the walk flies.

Two things must both hold for that to be the explanation, and each can
fail:

  TEST 1: the real cloud really does contain a dense patch of >= K points
          inside a short arc. Measured, not assumed.
  TEST 2: a ring built with THAT measured contrast reproduces the stall at
          the real cloud's coverage. If it does not, density contrast is
          not sufficient and the cause is still unidentified.

TEST 2 is the one that can refute. TEST 1 alone would be correlation.
"""

import numpy as np
from scipy.spatial import cKDTree

import diagnose_walk as dw
from find_stall_trigger import walk_instrumented, describe_stall


def density_profile(pts, label):
    """Walk the cloud's own neighbourhood graph and measure local spacing.

    Builds a minimum spanning tree, whose edge lengths ARE the local
    spacings, then reports how the edge lengths are distributed. A rim with
    uniform sampling has a narrow distribution; one with a dense patch has
    a long left tail of short edges.
    """
    from scipy.sparse.csgraph import minimum_spanning_tree
    from scipy.sparse import csr_matrix

    tree = cKDTree(pts)
    # The third argument of sparse_distance_matrix is a DISTANCE CUTOFF, not
    # a format flag -- passing 0.0 returns (almost) nothing, which is why two
    # earlier attempts produced an empty MST. inf means "all pairs".
    d = tree.sparse_distance_matrix(tree, np.inf).toarray()
    d = np.maximum(d, d.T)
    if not np.isfinite(d).all():
        raise RuntimeError("distance matrix has non-finite entries")
    mst = minimum_spanning_tree(csr_matrix(d))
    edges = np.sort(mst.data[mst.data > 0])
    if edges.size == 0:
        raise RuntimeError(
            f"MST still empty: {len(edges)} positive edges from a "
            f"{len(pts)}-point cloud -- refusing to report a spacing summary")
    nn = tree.query(pts, k=2)[0][:, 1]
    print(f"  [{label}] local spacing, from the minimum spanning tree")
    print(f"    MST edge length  min/med/p90/max  "
          f"{edges.min():.4f} / {np.median(edges):.4f} / "
          f"{np.percentile(edges,90):.4f} / {edges.max():.4f} mm")
    print(f"    NN spacing       min/med/max      "
          f"{nn.min():.4f} / {np.median(nn):.4f} / {nn.max():.4f} mm")
    print(f"    max/min ratio                    {nn.max()/max(nn.min(),1e-12):.1f}x")
    # The decisive one: how many points fall inside K x the MEDIAN spacing?
    # That is the arc a K-nearest window actually covers.
    n = len(pts)
    K = max(5, min(50, n // 10))
    med = float(np.median(nn))
    counts = np.asarray(tree.query_ball_point(pts, r=K * med, return_length=True))
    print(f"    K={K}, median spacing {med:.4f} mm")
    print(f"    points within K x median spacing:  "
          f"min={counts.min()} med={int(np.median(counts))} max={counts.max()}")
    print(f"    fraction of points whose K-window holds >= K points: "
          f"{float(np.mean(counts >= K)):.3f}")
    print(f"    fraction whose K-window holds >= 2K points:          "
          f"{float(np.mean(counts >= 2*K)):.3f}")
    print()
    return {"nn": nn, "counts": counts, "K": K, "med": med}


def ring_with_contrast(n, radius=15.0, dense_frac=0.25, dense_squeeze=20.0,
                       seed=0, plane_mm=0.0):
    """A ring where `dense_frac` of the points are packed into a small arc.

    dense_squeeze is the spacing ratio between the dense patch and the rest,
    matching the 20.4x measured on the real cloud. The patch is placed at a
    random start so the test does not depend on where the walk begins.
    """
    rng = np.random.default_rng(seed)
    n_dense = max(K_MIN, int(n * dense_frac))
    n_sparse = n - n_dense
    # dense arc: n_dense points over a 1/dense_squeeze fraction of the ring
    dense_arc = (2 * np.pi) / dense_squeeze
    t_dense = np.linspace(0.0, dense_arc, n_dense, endpoint=False)
    t_sparse = np.linspace(dense_arc, 2 * np.pi, n_sparse, endpoint=False)
    t = np.concatenate([t_dense, t_sparse])
    t = np.sort(t + rng.uniform(0, 2 * np.pi))  # rotate
    z = rng.normal(0.0, plane_mm, n) if plane_mm else np.zeros(n)
    return np.column_stack([radius * np.cos(t), radius * np.sin(t), z])


K_MIN = 6


def main():
    print("=" * 78)
    print("TEST 1: does the real cloud contain a dense patch that saturates K?")
    print("=" * 78)
    print()
    for path in ("fixtures/boundary.pcd", "fixtures/boundaryImproved.pcd"):
        try:
            _, pts = dw.load_pcd_xyz(path)
        except FileNotFoundError:
            print(f"  ({path} missing)")
            continue
        print(f"--- {path} ---")
        density_profile(pts, path)
        seq, stalls = walk_instrumented(pts)
        print(f"    walk: {len(seq)} of {len(pts)}, {len(stalls)} stalled steps")
        print()

    print("=" * 78)
    print("TEST 2: does a ring with THAT contrast reproduce the stall?")
    print("   n=59, K=5, to match the real cloud directly")
    print("=" * 78)
    print()
    print("   squeeze   dense_frac   out/59   coverage   traced/rim   stalls")
    for squeeze in (2.0, 5.0, 10.0, 20.0, 40.0):
        for frac in (0.15, 0.25, 0.40):
            pts = ring_with_contrast(59, dense_frac=frac, dense_squeeze=squeeze, seed=1)
            seq, stalls = walk_instrumented(pts)
            steps = (np.linalg.norm(np.diff(pts[seq], axis=0), axis=1)
                     if len(seq) > 1 else np.zeros(0))
            traced = float(steps.sum())
            print(f"   {squeeze:6.1f}x  {frac:9.2f}   {len(seq):3d}/59   "
                  f"{len(seq)/59:7.3f}   {traced/(2*np.pi*15):9.3f}   {len(stalls):5d}")
    print()
    print("   the real cloud, for comparison:")
    _, rp = dw.load_pcd_xyz("fixtures/boundary.pcd")
    rseq, rstalls = walk_instrumented(rp)
    rsteps = np.linalg.norm(np.diff(rp[rseq], axis=0), axis=1)
    print(f"   (measured)          {len(rseq):3d}/59   {len(rseq)/59:7.3f}   "
          f"{rsteps.sum()/(2*np.pi*6.29):9.3f}   {len(rstalls):5d}")
    print()
    print("   NOTE the rim radius differs: the real sherd's rim is ~6.3 mm,")
    print("   the test ring is 15 mm, so traced/rim is comparable but the")
    print("   absolute arc lengths are not. Coverage and stall count are the")
    print("   like-for-like figures.")


if __name__ == "__main__":
    main()
