#!/usr/bin/env python3
"""Ticket 06: wall records and axis extraction for the four Pot E surface sets.

The estimator is Ticket 03's frozen shipped one, imported read-only from the
SHIP run (SFS_IMPL); nothing in it is re-implemented or re-tuned here.

  axes06.py walls_axes --set SET --src DIR --axes-out DIR --walls-tsv F --axes-tsv F
                       [--axes-from DIR] [--dedupe] [--pins F]
  axes06.py fixtures  --fixtures F --posecheck P --ship S

SET is OWN_NOV5, OWN_NOV5_DEDUP or OWN_MAIN_T09.  With --axes-from the axis
file is read from that directory (a byte copy, e.g. the Ticket 19 pack) and the
extractor is not re-run; without it the 31 axis files are extracted into
--axes-out.  --dedupe removes exact duplicate float64 (x, y, z) rows per face
keeping the first occurrence in archive order; the retained rows are the native
6-vectors, unmodified.

Row definitions (check06.py re-derives every one of them with its own code):
  points          rows in the wall after any de-duplication
  duplicate_xyz   exact-duplicate xyz triples still present in that wall
  xyz_sha256      sha256 of the wall's xyz as (N,3) C-order little-endian float64
  normals_sha256  the same for its (N,3) normals
  source_sha256   sha256 of the file the wall was read from
  effective_stride/drawn_points  sfs_axes.potsac.effective_step(n, 10) and ceil(n/stride)
  rank1_*         rank-1 line's angle to the reference direction and its anchor distance
  best_*          the best (smallest angle) rank's same two numbers
"""
import argparse
import hashlib
import os
import sys

import numpy as np

SHIP = "/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-ship"
T19 = "/data/gpfs/projects/punim2657/SfSpp/runs/20261124-0443_21446b8_t19-decisions"
os.environ.setdefault("SFS_IMPL", os.path.join(SHIP, "work", "impl_t03"))
for _p in (os.path.join(SHIP, "work"), os.environ["SFS_IMPL"],
           os.path.join(os.environ["SFS_IMPL"], "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import run_benchmark_172 as rb  # noqa: E402
import sfs_axes.potsac as ps  # noqa: E402
import t03_extract as ex  # noqa: E402
import t03_lib as dl  # noqa: E402

PIECES = ["Pot_E_Piece_%02d" % p for p in range(1, 32)]
WALL_COLS = ("sherd", "surface_set", "face", "points", "duplicate_xyz",
             "xyz_sha256", "normals_sha256", "source_sha256")
AXIS_COLS = ("sherd", "arm", "status", "k", "axes_sha256", "effective_stride",
             "drawn_points", "best_line_deg", "best_anchor_mm",
             "rank1_line_deg", "rank1_anchor_mm")
FIXTURES = ("dedup_first_order", "verbatim_6vec", "author_zero_dup",
            "posecheck_completeness")


def sha_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def matrix_sha(a):
    """sha256 of a (N,3) matrix as C-order little-endian float64."""
    A = np.ascontiguousarray(np.asarray(a, dtype="<f8"))
    return hashlib.sha256(A.tobytes()).hexdigest()


def duplicate_mask(xyz):
    """True where this exact float64 triple already occurred earlier, in order."""
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


def dedup(wall):
    """(retained 6xN wall, duplicates removed) keeping first occurrences in order."""
    W = np.asarray(wall, dtype=float)
    keep = np.nonzero(~duplicate_mask(W[0:3, :].T))[0]
    return np.ascontiguousarray(W[:, keep]), int(W.shape[1] - keep.size)


def unit(v):
    v = np.asarray(v, dtype=float)
    n = float(np.linalg.norm(v))
    return v / n if n > 0 else v


def ang_deg(a, b):
    c = float(np.clip(unit(a) @ unit(b), -1.0, 1.0))
    return float(np.degrees(np.arccos(c)))


def line_dist(pos, gp, gd):
    q = np.asarray(pos, dtype=float) - np.asarray(gp, dtype=float)
    perp = q - (q @ gd) * gd
    return float(np.linalg.norm(perp))


def wall_rows(stem, sid, set_name, W0, W1, src0, src1):
    """Two wall rows, one per face, for one surface set."""
    rows = []
    for face, W, src in ((0, W0, src0), (1, W1, src1)):
        W = np.asarray(W, dtype=float)
        rows.append([str(sid), set_name, str(face), str(W.shape[1]),
                     str(int(duplicate_mask(W[0:3, :].T).sum())),
                     matrix_sha(W[0:3, :].T), matrix_sha(W[3:6, :].T),
                     sha_file(src)])
    return rows


def axis_metrics(stem, lines):
    """rank1_* and best_* (line angle and anchor mm) from a 6xK direction-first block."""
    gt = dl.gt_axis(stem)
    gd = unit(gt[0:3])
    gp = np.asarray(gt[3:6], dtype=float)
    vals = []
    for k in range(lines.shape[1]):
        d = np.asarray(lines[0:3, k], dtype=float)
        pos = np.asarray(lines[3:6, k], dtype=float)
        oriented = ang_deg(d, gd)
        vals.append((min(oriented, 180.0 - oriented), line_dist(pos, gp, gd)))
    if not vals:
        return "", ""
    rank1 = vals[0]
    best = min(vals, key=lambda x: (x[0],))
    return (rank1, best)


def write_row(fh, cols, vals):
    fh.write("\t".join(str(v) for v in vals) + "\n")


def read_pins(path):
    pins = {}
    if not path or not os.path.isfile(path):
        return pins
    with open(path) as fh:
        for ln in fh:
            f = ln.rstrip("\n").split("\t")
            if len(f) >= 4 and f[0] != "arm":
                pins[(f[0], int(f[1]))] = (int(f[2]), f[3])
    return pins


def cmd_walls_axes(a):
    pins = read_pins(a.pins)
    os.makedirs(a.axes_out, exist_ok=True)
    n_walls = 0
    n_axes = 0
    bad = []
    with open(a.walls_tsv, "a") as fw, open(a.axes_tsv, "a") as fa:
        for sid, stem in enumerate(PIECES, start=1):
            if a.authors:
                W0, W1 = dl.walls(stem, "authors")[0:2]
                src0 = src1 = "corpus:authors:" + stem
            else:
                src0 = os.path.join(a.src, stem + ".S0")
                src1 = os.path.join(a.src, stem + ".S1")
                W0 = rb.load_wall(src0)
                W1 = rb.load_wall(src1)
            if a.dedupe:
                W0, _ = dedup(W0)
                W1, _ = dedup(W1)
            if not a.no_walls:
                for row in wall_rows(stem, sid, a.set, W0, W1, src0, src1):
                    write_row(fw, WALL_COLS, row)
                    n_walls += 1
            C = np.concatenate([W0, W1], axis=1)
            stride = int(ps.effective_step(C.shape[1], 10))
            drawn = int(np.ceil(C.shape[1] / float(stride))) if stride > 0 else 0
            out_path = os.path.join(a.axes_out, stem + "_Axis.xyz")
            if a.axes_from:
                src_axis = os.path.join(a.axes_from, stem + "_Axis.xyz")
                if os.path.abspath(src_axis) != os.path.abspath(out_path):
                    with open(src_axis, "rb") as fh_in, open(out_path, "wb") as fh_out:
                        fh_out.write(fh_in.read())
                lines = np.zeros((6, 0))
                with open(out_path) as fh:
                    k = sum(1 for ln in fh if ln.split())
                status = "ok" if k > 0 else "empty"
            else:
                pool = dl.draw_pool(C, seeds=10, step=10)
                # draw_pool returns 5 values, or 6 ending in 0 when the pool is empty
                reps, sizes = pool[0], pool[1]
                stride = int(pool[3])
                drawn = int(pool[4])
                if reps.shape[1] == 0:
                    open(out_path, "w").close()
                    k, status, lines = 0, "empty", np.zeros((6, 0))
                else:
                    out = ex.select_lines(reps, sizes, W0, W1, C, 6, None)
                    if out is None or out[0].shape[1] == 0:
                        open(out_path, "w").close()
                        k, status, lines = 0, "empty", np.zeros((6, 0))
                    else:
                        lines = out[0]
                        ex.write_lines(out_path, lines)
                        k, status = int(lines.shape[1]), "ok"
            if a.axes_from:
                # read the copied pack back so the readout measures the file, not intent
                rows = []
                with open(out_path) as fh:
                    for ln in fh:
                        v = ln.split()
                        if len(v) >= 6:
                            rows.append([float(x) for x in v[:6]])
                if rows:
                    R = np.asarray(rows, dtype=float)
                    lines = np.vstack([R[:, 3:6].T, R[:, 0:3].T])
                    k = R.shape[0]
                    status = "ok"
            rank1b, bestb = axis_metrics(stem, lines)
            rank1 = "" if rank1b == "" else "%.6f" % rank1b[0]
            rank1a = "" if rank1b == "" else "%.6f" % rank1b[1]
            best = "" if bestb == "" else "%.6f" % bestb[0]
            besta = "" if bestb == "" else "%.6f" % bestb[1]
            sha = sha_file(out_path)
            write_row(fa, AXIS_COLS, [str(sid), a.set, status, str(k), sha,
                                      str(stride), str(drawn), best, besta,
                                      rank1, rank1a])
            n_axes += 1
            want = pins.get((a.set, sid))
            if want is not None:
                if (int(k), sha) != want:
                    bad.append("%s piece %d: k/sha %s/%s expected %s/%s"
                               % (a.set, sid, k, sha[:12], want[0], want[1][:12]))
                    print("PIN-FAIL %s" % bad[-1])
                else:
                    print("PIN-OK   %s piece %d k=%d sha=%s" % (a.set, sid, k, sha[:12]))
            print("AXIS %s %s k=%d stride=%d drawn=%d sha=%s"
                  % (a.set, stem, k, stride, drawn, sha[:12]))
    print("WROTE walls=%d axes=%d set=%s dedupe=%s"
          % (n_walls, n_axes, a.set, bool(a.dedupe)))
    return 3 if bad else 0


def cmd_fixtures(a):
    rows = []

    # 1. first occurrence kept, archive order preserved
    xyz = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [1.0, 2.0, 3.0],
                    [7.0, 8.0, 9.0], [4.0, 5.0, 6.0]], dtype=float)
    W = np.vstack([xyz.T, np.arange(15.0).reshape(3, 5)])
    Dw, removed = dedup(W)
    idx = np.nonzero(~duplicate_mask(xyz))[0]
    ok1 = (list(idx) == [0, 1, 3] and removed == 2
           and np.array_equal(Dw[0:3, :].T, xyz[[0, 1, 3]])
           and np.array_equal(Dw[3:6, :], W[3:6, :][:, [0, 1, 3]]))
    rows.append(("dedup_first_order", "PASS" if ok1 else "FAIL",
                 "duplicates at 2,4 removed; survivors 0,1,3 in archive order; "
                 "1 face, 2 duplicates, %d rows" % Dw.shape[1]))

    # 2. retained rows are the native 6-vectors, bit for bit
    src = np.array([[0.1, 0.2, 0.3, -0.5, 0.25, 0.75],
                    [0.1, 0.2, 0.3, 0.9, 0.9, 0.9],
                    [1.0, 2.0, 3.0, 1.0, 0.0, 0.0]], dtype=float).T
    Dw2, _ = dedup(src)
    ok2 = (Dw2.shape[1] == 2
           and Dw2[:, 0].tobytes() == src[:, 0].tobytes()
           and Dw2[:, 1].tobytes() == src[:, 2].tobytes())
    rows.append(("verbatim_6vec", "PASS" if ok2 else "FAIL",
                 "duplicate row's differing normal dropped with the duplicate; "
                 "both survivors byte-identical to their source rows"))

    # 3. the authors' own walls carry no exact duplicate: dedup must be a no-op there
    ok3 = True
    detail = []
    for sid in (27, 28):
        stem = "Pot_E_Piece_%02d" % sid
        C0, C1, C = dl.walls(stem, "authors")
        d0 = int(duplicate_mask(C0[0:3, :].T).sum())
        d1 = int(duplicate_mask(C1[0:3, :].T).sum())
        detail.append("%s %d/%d" % (stem, d0, d1))
        ok3 = ok3 and d0 == 0 and d1 == 0
    rows.append(("author_zero_dup", "PASS" if ok3 else "FAIL",
                 "authors' walls duplicate_xyz face0/face1: " + ", ".join(detail)))

    # 4. posecheck06.sh: 31/31 pass, 3-missing fail, empty-file fail
    rc = os.system("bash %s --self-test > %s 2>&1" % (a.posecheck, a.posecheck_log))
    out = ""
    if os.path.isfile(a.posecheck_log):
        out = open(a.posecheck_log).read()
    ok4 = (rc == 0 and "SELF-TEST 31/31 PASS" in out
           and "SELF-TEST 3-missing FAIL" in out and "SELF-TEST empty FAIL" in out)
    rows.append(("posecheck_completeness", "PASS" if ok4 else "FAIL",
                 "31/31 nonempty accepted; 3 missing rejected; 1 empty rejected "
                 "(rc=%d)" % rc))

    with open(a.fixtures, "w") as fh:
        fh.write("fixture\tstatus\tdetail\n")
        for r in rows:
            fh.write("\t".join(r) + "\n")
    for r in rows:
        print("FIXTURE %s %s :: %s" % (r[0], r[1], r[2]))
    bad = [r for r in rows if r[1] != "PASS"]
    print("FIXTURES %d/4 PASS" % (len(rows) - len(bad)))
    return 4 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("walls_axes")
    w.add_argument("--set", required=True)
    w.add_argument("--src", default="")
    w.add_argument("--axes-out", required=True)
    w.add_argument("--walls-tsv", required=True)
    w.add_argument("--axes-tsv", required=True)
    w.add_argument("--axes-from", default="")
    w.add_argument("--dedupe", action="store_true")
    w.add_argument("--authors", action="store_true")
    w.add_argument("--no-walls", action="store_true")
    w.add_argument("--pins", default="")
    f = sub.add_parser("fixtures")
    f.add_argument("--fixtures", required=True)
    f.add_argument("--posecheck", required=True)
    f.add_argument("--posecheck-log", default="/tmp/posecheck06_selftest.log")
    f.add_argument("--ship", default=SHIP)
    a = ap.parse_args(argv)
    if a.cmd == "walls_axes":
        return cmd_walls_axes(a)
    return cmd_fixtures(a)


if __name__ == "__main__":
    sys.exit(main())
