"""Ticket 04: wall-normal transfer at fixed sample points, and its fixtures.

Every target column keeps its position, index, face and multiplicity; only its last
three values can change, and only to the raw donor normal of the closest valid donor
point on the SAME face, in the native frame.  1.000 mm inclusive Euclidean cut, ties to
the first donor row in archive order, donor signs and lengths copied verbatim.
No registration, fits, point removal, reordering, resampling, dedup, normal estimation
or normal flipping lives here.
"""

import hashlib

import numpy as np

CUT_MM = 1.000
MIN_NORM = 1e-9
CHUNK = 256
SHAM = "SHAM"


def matrix_sha(a):
    """sha256 of the in-order little-endian contiguous float64 matrix (N x 3)."""
    A = np.ascontiguousarray(np.asarray(a, dtype="<f8"))
    return hashlib.sha256(A.tobytes()).hexdigest()


def sha_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def valid_mask(normals):
    """Finite components and norm > 1e-9 (ticket 04, 'a valid normal')."""
    N = np.asarray(normals, dtype=float)
    return np.isfinite(N).all(axis=1) & (np.linalg.norm(N, axis=1) > MIN_NORM)


def zero_rec(wall):
    """Transfer bookkeeping for a native or sham wall: no row was transferred."""
    n = np.asarray(wall).shape[1]
    return dict(matched=np.zeros(n, dtype=bool), changed=np.zeros(n, dtype=bool),
                invalid_target=~valid_mask(np.asarray(wall)[3:6].T),
                unmatched=np.zeros(n, dtype=bool),
                donor=np.full(n, -1, dtype=np.int64),
                distance=np.full(n, np.inf, dtype=float))


def match_face(txyz, tnorm, dxyz, dnorm, cut=CUT_MM):
    """Closest valid same-face donor for every target row.

    Returns the new normal matrix plus matched / changed / invalid_target / unmatched
    masks (the three latter partition the rows), the winning donor index and its
    distance in mm.  Rows are never reordered; the new normals start as a copy.
    """
    txyz = np.asarray(txyz, dtype=float)
    tnorm = np.asarray(tnorm, dtype=float)
    dxyz = np.asarray(dxyz, dtype=float)
    dnorm = np.asarray(dnorm, dtype=float)
    if txyz.shape != tnorm.shape or dxyz.shape != dnorm.shape:
        raise ValueError("xyz/normal shape mismatch: %r %r %r %r"
                         % (txyz.shape, tnorm.shape, dxyz.shape, dnorm.shape))
    n = txyz.shape[0]
    tv = valid_mask(tnorm)
    dv = valid_mask(dnorm)
    out = tnorm.copy()
    matched = np.zeros(n, dtype=bool)
    donor = np.full(n, -1, dtype=np.int64)
    dist = np.full(n, np.inf, dtype=float)
    ti = np.nonzero(tv)[0]
    di = np.nonzero(dv)[0]
    if ti.size and di.size:
        D = dxyz[di]
        for s in range(0, ti.size, CHUNK):
            rows = ti[s:s + CHUNK]
            dd = np.linalg.norm(txyz[rows, None, :] - D[None, :, :], axis=2)
            j = np.argmin(dd, axis=1)          # first donor row wins an exact tie
            best = dd[np.arange(rows.size), j]
            ok = best <= cut                   # inclusive
            rr = rows[ok]
            matched[rr] = True
            donor[rr] = di[j[ok]]
            dist[rr] = best[ok]
            out[rr] = dnorm[di[j[ok]]]
    changed = matched & np.any(out != tnorm, axis=1)
    return dict(normals=out, matched=matched, changed=changed,
                invalid_target=~tv, unmatched=tv & ~matched,
                donor=donor, distance=dist)


def experimental_pair(t0, t1, d0=None, d1=None, cut=CUT_MM):
    """The one experimental wrapper every arm goes through.

    d0/d1 None: a sham -- both native walls are copied and handed on untouched, and
    every transfer count is zero.  Otherwise each target wall gets its same-face
    donor normals.  Returns (walls, records) with records per face.
    """
    if (d0 is None) != (d1 is None):
        raise ValueError("give both donors or neither")
    T0 = np.array(t0, dtype=float, copy=True)
    T1 = np.array(t1, dtype=float, copy=True)
    if d0 is None:
        return (T0, T1), [zero_rec(T0), zero_rec(T1)]
    outs, recs = [], []
    for T, D in ((T0, d0), (T1, d1)):
        D = np.asarray(D, dtype=float)
        rec = match_face(T[0:3].T, T[3:6].T, D[0:3].T, D[3:6].T, cut)
        T[3:6] = rec["normals"].T
        outs.append(T)
        recs.append(rec)
    return (outs[0], outs[1]), recs


# --------------------------------------------------------------------------- fixtures

def _wall(pts, nrm):
    A = np.zeros((6, len(pts)), dtype=float)
    A[0:3] = np.asarray(pts, dtype=float).T
    A[3:6] = np.asarray(nrm, dtype=float).T
    return A


def _norm(w, i):
    return np.array(w[3:6, i], dtype=float)


def fixture_suite():
    """The nine ticket fixtures.  Each asserts its own invariant and returns a note."""
    rows = []

    def case(name, fn):
        try:
            rows.append((name, "PASS", fn()))
        except AssertionError as exc:
            rows.append((name, "FAIL", str(exc) or "assertion"))

    def inclusive_cut():
        t = _wall([[0.0, 0.0, 0.0]], [[0.0, 0.0, 1.0]])
        d = _wall([[1.0, 0.0, 0.0]], [[1.0, 0.0, 0.0]])
        (o, _), (r, _) = experimental_pair(t, np.zeros((6, 0)), d, np.zeros((6, 0)))
        assert r["matched"][0] and not r["invalid_target"][0] and not r["unmatched"][0], r
        assert np.array_equal(_norm(o, 0), [1.0, 0.0, 0.0]), _norm(o, 0)
        return "distance 1.000 mm matched (inclusive)"

    def outside_cut():
        t = _wall([[0.0, 0.0, 0.0]], [[0.0, 0.0, 1.0]])
        d = _wall([[1.000001, 0.0, 0.0]], [[1.0, 0.0, 0.0]])
        (o, _), (r, _) = experimental_pair(t, np.zeros((6, 0)), d, np.zeros((6, 0)))
        assert not r["matched"][0] and r["unmatched"][0], r
        assert np.array_equal(_norm(o, 0), [0.0, 0.0, 1.0]), _norm(o, 0)
        return "1.000001 mm unmatched, original normal kept"

    def same_face():
        t0 = _wall([[0.0, 0.0, 0.0]], [[0.0, 0.0, 1.0]])
        t1 = _wall([[0.0, 0.0, 0.0]], [[1.0, 0.0, 0.0]])
        d0 = _wall([[0.0, 0.0, 0.0]], [[0.0, 1.0, 0.0]])
        d1 = _wall([[0.0, 0.0, 0.0]], [[1.0, 0.0, 0.0]])
        (o0, o1), (r0, r1) = experimental_pair(t0, t1, d0, d1, 1.0)
        assert r0["matched"][0] and r1["matched"][0], (r0, r1)
        assert np.array_equal(_norm(o0, 0), [0.0, 1.0, 0.0]), _norm(o0, 0)
        assert np.array_equal(_norm(o1, 0), [1.0, 0.0, 0.0]), _norm(o1, 0)
        (ob, _), (rb, _) = experimental_pair(t0, np.zeros((6, 0)),
                                             np.zeros((6, 0)), d1, 1.0)
        assert not rb["matched"][0] and rb["unmatched"][0], rb
        assert np.array_equal(_norm(ob, 0), [0.0, 0.0, 1.0]), _norm(ob, 0)
        return "face-0 takes only face-0 donors, face-1 only face-1 (distance 0)"

    def invalid_target():
        t = _wall([[0.0, 0.0, 0.0]], [[0.0, 0.0, 0.0]])
        d = _wall([[0.1, 0.0, 0.0]], [[1.0, 0.0, 0.0]])
        (o, _), (r, _) = experimental_pair(t, np.zeros((6, 0)), d, np.zeros((6, 0)))
        assert r["invalid_target"][0] and not r["matched"][0] and not r["unmatched"][0], r
        assert np.array_equal(_norm(o, 0), [0.0, 0.0, 0.0])
        return "zero target normal kept unchanged, counted invalid"

    def invalid_donor():
        t = _wall([[0.0, 0.0, 0.0]], [[0.0, 0.0, 1.0]])
        d = _wall([[0.1, 0.0, 0.0], [0.2, 0.0, 0.0]],
                  [[0.0, 0.0, 0.0], [float("nan"), 0.0, 1.0]])
        (o, _), (r, _) = experimental_pair(t, np.zeros((6, 0)), d, np.zeros((6, 0)))
        assert r["unmatched"][0] and not r["matched"][0], r
        assert np.array_equal(_norm(o, 0), [0.0, 0.0, 1.0])
        return "zero and NaN donors skipped, original kept"

    def tie_first():
        t = _wall([[0.0, 0.0, 0.0]], [[0.0, 0.0, 1.0]])
        d = _wall([[0.5, 0.0, 0.0], [-0.5, 0.0, 0.0]],
                  [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
        (o, _), (r, _) = experimental_pair(t, np.zeros((6, 0)), d, np.zeros((6, 0)))
        assert r["donor"][0] == 0, r["donor"]
        assert np.array_equal(_norm(o, 0), [1.0, 0.0, 0.0])
        return "equidistant donors: row 0 (archive order) wins"

    def duplicates_preserved():
        t = _wall([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [5.0, 0.0, 0.0]],
                  [[0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        d = _wall([[0.2, 0.0, 0.0]], [[1.0, 0.0, 0.0]])
        (o, _), (r, _) = experimental_pair(t, np.zeros((6, 0)), d, np.zeros((6, 0)))
        assert o.shape == t.shape, (o.shape, t.shape)
        assert np.array_equal(o[0:3], t[0:3]), "XYZ or row order changed"
        assert r["matched"][:2].all() and r["donor"][0] == r["donor"][1] == 0
        assert np.array_equal(_norm(o, 0), [1.0, 0.0, 0.0])
        assert np.array_equal(_norm(o, 1), [1.0, 0.0, 0.0])
        return "repeated XYZ keeps both rows and its own multiplicity"

    def normal_sign():
        n = np.array([-0.6, 0.0, 0.8]) * 3.7
        t = _wall([[0.0, 0.0, 0.0]], [[0.0, 0.0, 1.0]])
        d = _wall([[0.3, 0.0, 0.0]], [n])
        (o, _), (r, _) = experimental_pair(t, np.zeros((6, 0)), d, np.zeros((6, 0)))
        assert np.array_equal(_norm(o, 0), n), _norm(o, 0)
        assert abs(float(np.linalg.norm(_norm(o, 0))) - 3.7) < 1e-12
        return "negative unit vector of length 3.7 copied verbatim"

    def identity_order():
        t = _wall([[0.0, 0.0, 0.0], [4.0, 0.0, 0.0], [8.0, 0.0, 0.0],
                   [12.0, 0.0, 0.0], [16.0, 0.0, 0.0]],
                  [[0.0, 0.0, 1.0]] * 5)
        d = _wall([[8.2, 0.0, 0.0]], [[1.0, 0.0, 0.0]])
        (o, _), (r, _) = experimental_pair(t, np.zeros((6, 0)), d, np.zeros((6, 0)))
        assert o.shape == t.shape and np.array_equal(o[0:3], t[0:3])
        for i in (0, 1, 3, 4):
            assert np.array_equal(_norm(o, i), _norm(t, i)), i
        assert r["matched"][2] and np.array_equal(_norm(o, 2), [1.0, 0.0, 0.0])
        assert r["matched"].sum() == 1 and r["changed"].sum() == 1
        return "only row 3 rewritten; other rows and XYZ bitwise unchanged"

    case("inclusive_cut", inclusive_cut)
    case("outside_cut", outside_cut)
    case("same_face", same_face)
    case("invalid_target", invalid_target)
    case("invalid_donor", invalid_donor)
    case("tie_first", tie_first)
    case("duplicates_preserved", duplicates_preserved)
    case("normal_sign", normal_sign)
    case("identity_order", identity_order)
    return rows
