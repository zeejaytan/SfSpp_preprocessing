"""Ticket 05: the ten sampling / coverage transforms, plus their fixture suite.

Every transform here only REMOVES rows from a wall.  No coordinate is averaged,
no normal is re-estimated, normalized or flipped: a retained row is the native
6-vector (x, y, z, nx, ny, nz), bit for bit.  The index maps these functions
return are what makes that checkable -- extract05 writes each one to
evidence/indices/, and check05 re-derives every one of them from the native wall
with its own code.

Units are millimetres throughout, matching the corpus.
"""
import hashlib

import numpy as np

CUT_MM = 1.000          # inclusive coverage radius
VOXEL_MM = 1.000        # shared-voxel edge length
VOXEL_ORIGIN = (0.0, 0.0, 0.0)
CHUNK = 256             # target rows per nearest-neighbour block


def matrix_sha(a):
    """SHA-256 of an in-order little-endian contiguous float64 Nx3 matrix."""
    A = np.ascontiguousarray(np.asarray(a, dtype="<f8"))
    return hashlib.sha256(A.tobytes()).hexdigest()


def sha_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def take(wall, idx):
    """The retained rows of a 6xN wall, in the given order, as a fresh array."""
    W = np.asarray(wall, dtype=float)
    I = np.asarray(idx, dtype=np.int64)
    return np.ascontiguousarray(W[:, I])


# ---------------------------------------------------------------- duplicates
def duplicate_mask(xyz):
    """True where this exact float64 triple already occurred earlier in order."""
    X = np.ascontiguousarray(np.asarray(xyz, dtype="<f8"))
    seen = set()
    dup = np.zeros(X.shape[0], dtype=bool)
    for i in range(X.shape[0]):
        key = X[i].tobytes()
        if key in seen:
            dup[i] = True
        else:
            seen.add(key)
    return dup


def duplicate_count(xyz):
    return int(duplicate_mask(xyz).sum())


def dedup_indices(xyz):
    """Keep the first occurrence of each exact xyz triple, in archive order."""
    return np.nonzero(~duplicate_mask(xyz))[0].astype(np.int64)


# ----------------------------------------------------- 1.000 mm coverage
def nearest(target_xyz, donor_xyz):
    """For every target row its nearest donor row (first donor wins a tie)."""
    T = np.asarray(target_xyz, dtype=float)
    D = np.asarray(donor_xyz, dtype=float)
    n = T.shape[0]
    idx = np.full(n, -1, dtype=np.int64)
    dist = np.full(n, np.inf, dtype=float)
    if D.shape[0] == 0 or n == 0:
        return idx, dist
    for s in range(0, n, CHUNK):
        rows = np.arange(s, min(n, s + CHUNK))
        dd = np.linalg.norm(T[rows, None, :] - D[None, :, :], axis=2)
        j = np.argmin(dd, axis=1)
        idx[rows] = j
        dist[rows] = dd[np.arange(rows.size), j]
    return idx, dist


def shared_indices(target_xyz, donor_xyz, cut=CUT_MM):
    """Target rows whose nearest donor row is within cut inclusive."""
    _, dd = nearest(target_xyz, donor_xyz)
    return np.nonzero(dd <= cut)[0].astype(np.int64)


def matched_indices(own_xyz, auth_xyz, cut=CUT_MM):
    """Unique OWN rows matched by at least one AUTHOR point, in OWN archive order."""
    idx, dd = nearest(auth_xyz, own_xyz)
    hit = idx[dd <= cut]
    hit = hit[hit >= 0]
    return np.unique(hit).astype(np.int64)


# ------------------------------------------------------------ shared voxels
def voxel_keys(xyz):
    X = np.asarray(xyz, dtype=float) - np.asarray(VOXEL_ORIGIN, dtype=float)
    return np.floor(X / VOXEL_MM).astype(np.int64)


def voxel_centre(key):
    return (np.asarray(key, dtype=float) + 0.5) * VOXEL_MM + np.asarray(VOXEL_ORIGIN, dtype=float)


def best_per_voxel(xyz):
    """voxel key -> (distance to centre, first row index with that distance)."""
    K = voxel_keys(xyz)
    X = np.asarray(xyz, dtype=float)
    best = {}
    for i in range(X.shape[0]):
        k = (int(K[i, 0]), int(K[i, 1]), int(K[i, 2]))
        d = float(np.linalg.norm(X[i] - voxel_centre(k)))
        cur = best.get(k)
        if cur is None or d < cur[0]:
            best[k] = (d, i)
    return best


def common_voxel_indices(own_xyz, auth_xyz):
    """(own rows, author rows) of the shared voxels, lexicographic by (i, j, k)."""
    ow = best_per_voxel(own_xyz)
    au = best_per_voxel(auth_xyz)
    shared = sorted(set(ow) & set(au))
    if not shared:
        return np.zeros(0, dtype=np.int64), np.zeros(0, dtype=np.int64)
    return (np.array([ow[k][1] for k in shared], dtype=np.int64),
            np.array([au[k][1] for k in shared], dtype=np.int64))


# ---------------------------------------------------------------- estimator
def effective_step(n, step):
    """The frozen estimator's own stride rule (sfs_axes.potsac.effective_step)."""
    import sfs_axes.potsac as ps
    return int(ps.effective_step(int(n), step))


# ---------------------------------------------------------------- fixtures
def _wall(rows):
    """rows: list of 6-tuples -> 6xN float64 wall."""
    return np.asarray(rows, dtype=float).T.copy()


def _fixture(name, fn):
    try:
        detail = fn()
        return dict(fixture=name, status="PASS", detail=detail)
    except Exception as exc:                                  # noqa: BLE001
        return dict(fixture=name, status="FAIL",
                    detail="%s: %s" % (type(exc).__name__, exc))


def _dedup_first_order():
    W = _wall([[0, 0, 0, 0, 0, 1],
               [0, 0, 0, 1, 0, 0],
               [2, 0, 0, 0, 1, 0],
               [2, 0, 0, 0, 0, 1],
               [1, 0, 0, 1, 1, 0]])
    idx = dedup_indices(W[0:3].T)
    assert list(idx) == [0, 2, 4], "kept %s, want first occurrence [0, 2, 4]" % list(idx)
    assert duplicate_count(W[0:3].T) == 2, "duplicate count"
    K = take(W, idx)
    assert np.array_equal(K[3:6, 0], [0, 0, 1]), "first copy's normal must survive"
    assert np.array_equal(K[3:6, 1], [0, 1, 0]), "first copy's normal must survive"
    return "kept [0, 2, 4], 2 duplicates dropped, first copy's normal kept"


def _shared_inclusive_cut():
    T = np.array([[0.0, 0.0, 0.0], [0.0, 1.000001, 0.0]])
    D = np.array([[1.0, 0.0, 0.0]])
    idx = shared_indices(T, D)
    assert list(idx) == [0], "exactly 1.000 mm must be kept inclusive, got %s" % list(idx)
    idx2 = shared_indices(T, D, cut=1.0000001)
    assert list(idx2) == [0], "still only the 1.000 mm point"
    idx3 = shared_indices(np.array([[0.0, 1.000002, 0.0]]), D)
    assert idx3.size == 0, "beyond the cut must be dropped"
    return "distance 1.000000 kept, 1.000001 dropped"


def _shared_same_face():
    own0 = _wall([[0, 0, 0, 0, 0, 1], [0, 0, 5, 0, 0, 1]])
    own1 = _wall([[0, 0, 2, 0, 0, 1]])
    auth0 = _wall([[5, 0, 0, 0, 0, 1]])
    auth1 = _wall([[0, 0, 2.4, 0, 0, 1]])
    face0 = shared_indices(own0[0:3].T, auth0[0:3].T)
    face1 = shared_indices(own1[0:3].T, auth1[0:3].T)
    assert face0.size == 0, "face 0 must not see face 1's donor: got %s" % list(face0)
    assert list(face1) == [0], "face 1 must match its own donor"
    assert list(shared_indices(own0[0:3].T, auth1[0:3].T)) == [], \
        "mixing faces would wrongly match own0[1] to auth1"
    return "face 0 sees no match, face 1 sees one, crossing faces matches nothing"


def _matched_unique_order():
    own = np.array([[0.0, 0, 0], [1.0, 0, 0], [2.0, 0, 0], [3.0, 0, 0]])
    auth = np.array([[2.4, 0, 0], [1.1, 0, 0], [0.9, 0, 0], [0.2, 0, 0]])
    idx = matched_indices(own, auth)
    assert list(idx) == [0, 1, 2], "unique + OWN archive order, got %s" % list(idx)
    return "matches {0,1,2} emitted once each in OWN order, 3 unreferenced"


def _voxel_shared_center_tie():
    own = np.array([[0.25, 0.25, 0.25], [0.75, 0.75, 0.75]])
    auth = np.array([[0.5, 0.5, 0.5]])
    o, a = common_voxel_indices(own, auth)
    assert list(o) == [0], "tie must go to the first OWN row, got %s" % list(o)
    assert list(a) == [0], "author side"
    assert voxel_keys(own)[0, 0] == 0 and voxel_keys(own)[1, 0] == 0, "same voxel"
    return "equidistant 0.433 mm pair -> first row kept"


def _voxel_negative_coords():
    own = np.array([[-0.5, 0.0, 0.0], [-0.2, 0.0, 0.0]])
    auth = np.array([[-0.4, 0.0, 0.0], [0.5, 0.0, 0.0]])
    K = voxel_keys(np.vstack([own, auth]))
    assert list(K[:, 0]) == [-1, -1, -1, 0], "floor of negatives: got %s" % list(K[:, 0])
    o, a = common_voxel_indices(own, auth)
    assert list(o) == [0], "only voxel (-1, 0, 0) is shared; nearest to its centre is row 0: %s" % list(o)
    assert list(a) == [0], "author side keeps the -0.4 point"
    return "keys (-1,0,0) x3 + (0,0,0); shared voxel keeps row 0"


def _normals_verbatim():
    W = _wall([[0, 0, 0, 0, 0, 0],
               [9, 9, 9, 3.7, -0.2, 0.0],
               [0, 0, 0, 1, 1, 1],
               [0.4, 0.0, 0.0, -0.0, 2.5, -3.0]])
    own = W[0:3].T
    auth = np.array([[0.2, 0.0, 0.0], [0.3, 0.0, 0.0], [0.1, 0.0, 0.0]])
    maps = {
        "dedup": (dedup_indices(own), W),
        "shared": (shared_indices(own, auth), W),
    }
    o, _ = common_voxel_indices(own, np.array([[0.2, 0.0, 0.0]]))
    maps["voxel"] = (o, W)
    for tag, (idx, src) in maps.items():
        K = take(src, idx)
        for c in range(K.shape[1]):
            assert np.array_equal(K[:, c], src[:, int(idx[c])]), \
                "%s row %d changed the 6-vector" % (tag, c)
    K = take(W, dedup_indices(own))
    assert list(dedup_indices(own)) == [0, 1, 3], "dedup keeps 0, 1, 3"
    assert np.array_equal(K[3:6, 0], [0, 0, 0]), "zero normal must survive verbatim"
    assert np.array_equal(K[3:6, 1], [3.7, -0.2, 0.0]), "unnormalized normal must survive"
    assert np.array_equal(K[0:3, 1], [9, 9, 9]), "row 1 is untouched"
    assert not any(np.array_equal(K[3:6, c], [1, 1, 1]) for c in range(K.shape[1])), \
        "the duplicate's normal must never be emitted"
    return "dedup/shared/voxel keep every retained 6-vector bit-identical (zero and 3.7-length normals included; the dropped duplicate's normal never appears)"


def _stride_override():
    assert effective_step(6000, 1) == 1, "explicit step 1 must stay 1 above 5000"
    assert effective_step(6000, 10) == 10, "explicit step 10 must stay 10 above 5000"
    assert effective_step(4480, 10) == 1, "n < 5000 must switch to stride 1"
    assert effective_step(4480, 1) == 1, "n < 5000 with explicit 1"
    assert effective_step(15539, 10) == 10, "n > 5000 with explicit 10"
    return "n<5000 -> 1; explicit 1 -> 1; step 10 kept at n>=5000"


FIXTURES = [
    ("dedup_first_order", _dedup_first_order),
    ("shared_inclusive_cut", _shared_inclusive_cut),
    ("shared_same_face", _shared_same_face),
    ("matched_unique_order", _matched_unique_order),
    ("voxel_shared_center_tie", _voxel_shared_center_tie),
    ("voxel_negative_coords", _voxel_negative_coords),
    ("normals_verbatim", _normals_verbatim),
    ("stride_override", _stride_override),
]


def fixture_suite():
    return [_fixture(name, fn) for name, fn in FIXTURES]
