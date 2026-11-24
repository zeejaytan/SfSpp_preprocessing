#!/usr/bin/env python3
"""Ticket 05 acceptance gate: every table checked against the frozen run and the code.

This is a reader, not a runner.  It re-derives every retained index map, every
hash and every angle from the native walls and the axis files with its own
implementations (nothing is imported from extract05 or sampling05), so a
transcription bug in the transforms cannot hide behind them.

  python check05.py --run <run dir>
  python check05.py --run <run dir> --expect-terminal
"""
import argparse
import glob
import hashlib
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SHIP = "/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-ship"
T19 = "/data/gpfs/projects/punim2657/SfSpp/runs/20261124-0443_21446b8_t19-decisions"
IMPL = os.path.join(SHIP, "work", "impl_t03")
CUT = 1.000
VOX = 1.000
CHUNK = 256

os.environ.setdefault("SFS_IMPL", IMPL)
for p in (os.path.join(SHIP, "work"), IMPL, os.path.join(IMPL, "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

import t03_lib as dl                                      # noqa: E402

STEMS = [("Pot_E_Piece_27", 27), ("Pot_E_Piece_28", 28)]
ARM_SPEC = {
    "OWN": ("own", 10),
    "AUTHOR": ("authors", 10),
    "OWN_DEDUP": ("own", 10),
    "OWN_STRIDE1": ("own", 1),
    "OWN_DEDUP_STRIDE1": ("own", 1),
    "OWN_SHARED_1MM": ("own", 10),
    "AUTHOR_SHARED_1MM": ("authors", 10),
    "OWN_MATCHED_TO_AUTHOR": ("own", 10),
    "OWN_COMMON_VOXEL": ("own", 10),
    "AUTHOR_COMMON_VOXEL": ("authors", 10),
}
ARMS = list(ARM_SPEC)
NATIVE = ("OWN", "AUTHOR")
NON_NATIVE = [a for a in ARMS if a not in NATIVE]
ZERO_DUP = ("OWN_DEDUP", "OWN_DEDUP_STRIDE1", "OWN_MATCHED_TO_AUTHOR",
            "OWN_COMMON_VOXEL", "AUTHOR_COMMON_VOXEL")
FIXTURES = ["dedup_first_order", "shared_inclusive_cut", "shared_same_face",
            "matched_unique_order", "voxel_shared_center_tie", "voxel_negative_coords",
            "normals_verbatim", "stride_override"]
TERMINAL = {"COMPLETED", "FAILED", "CANCELLED", "TIMEOUT", "NODE_FAIL", "PREEMPTED",
            "OUT_OF_MEMORY", "BOOT_FAIL", "DEADLINE"}

INPUT_COLS = ["sherd", "arm", "face", "native_points", "points", "duplicate_xyz",
              "retained_fraction", "xyz_sha256", "normals_sha256", "source_sha256"]
RUN_COLS = ["sherd", "arm", "status", "k", "axes_sha256", "archive_ok",
            "requested_step", "effective_stride", "drawn_points", "basins", "reason"]
RUN_OPT = ["archived_sha256", "archive_rank_count_agree", "archive_max_abs", "secs"]
AXIS_COLS = ["sherd", "arm", "rank", "oriented_deg", "line_deg", "anchor_mm",
             "pos_x", "pos_y", "pos_z", "dir_x", "dir_y", "dir_z", "cost"]
CHANGE_COLS = ["sherd", "arm", "parent_arm", "k_parent", "k_arm", "axes_bytes_identical",
               "best_ref_line_deg_parent", "best_ref_line_deg_arm",
               "best_ref_anchor_mm_parent", "best_ref_anchor_mm_arm",
               "max_rank_line_delta_deg", "max_rank_anchor_delta_mm"]
SOURCE_COLS = ["kind", "name", "path", "sha256"]
CODE_WANT = ["t03_lib.py", "t03_extract.py", "run_benchmark_172.py", "potsac.py",
             "profile.py", "select.py", "joint.py", "io_axes.py",
             "sampling05.py", "extract05.py", "check05.py", "submit.sbatch"]

FAILS = []
CHECKS = [0]


def check(name, cond, detail=""):
    CHECKS[0] += 1
    if cond:
        print("PASS  %s" % name)
    else:
        print("FAIL  %s  %s" % (name, detail))
        FAILS.append((name, detail))
    return bool(cond)


# ------------------------------------------------------- independent helpers
def sha_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def matrix_sha(a):
    A = np.ascontiguousarray(np.asarray(a, dtype="<f8"))
    return hashlib.sha256(A.tobytes()).hexdigest()


def read_tsv(path):
    if not os.path.isfile(path):
        return [], []
    with open(path) as fh:
        lines = [ln.rstrip("\n") for ln in fh if ln.strip()]
    if not lines:
        return [], []
    head = lines[0].split("\t")
    rows = []
    for ln in lines[1:]:
        vals = ln.split("\t")
        rows.append(dict(zip(head, vals)))
    return head, rows


def fnum(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def read_axis_rows(path):
    rows = []
    if not os.path.isfile(path):
        return rows
    for line in open(path):
        c = line.split()
        if len(c) < 6:
            continue
        v = np.array([float(x) for x in c[:6]], dtype=float)
        rows.append((v[0:3], v[3:6]))
    return rows


def unit(v):
    n = float(np.linalg.norm(v))
    return np.asarray(v, dtype=float) / n if n else np.asarray(v, dtype=float)


def ang_deg(u, v):
    c = float(np.clip(unit(u) @ unit(v), -1.0, 1.0))
    return float(np.degrees(np.arccos(c)))


def line_dist(p0, g0, gd):
    gd = unit(gd)
    d = np.asarray(p0, dtype=float) - np.asarray(g0, dtype=float)
    return float(np.linalg.norm(d - (d @ gd) * gd))


def anchor_point(pos, g0, gd):
    gd = unit(gd)
    d = np.asarray(g0, dtype=float) - np.asarray(pos, dtype=float)
    return np.asarray(pos, dtype=float) + float(d @ gd) * gd


def dup_count(xyz):
    seen = set()
    n = 0
    X = np.ascontiguousarray(np.asarray(xyz, dtype="<f8"))
    for i in range(X.shape[0]):
        k = X[i].tobytes()
        if k in seen:
            n += 1
        else:
            seen.add(k)
    return n


def nn_index(target, donor):
    T = np.asarray(target, dtype=float)
    D = np.asarray(donor, dtype=float)
    idx = np.full(T.shape[0], -1, dtype=np.int64)
    dist = np.full(T.shape[0], np.inf, dtype=float)
    if D.shape[0] == 0 or T.shape[0] == 0:
        return idx, dist
    for s in range(0, T.shape[0], CHUNK):
        rows = np.arange(s, min(T.shape[0], s + CHUNK))
        dd = np.linalg.norm(T[rows, None, :] - D[None, :, :], axis=2)
        j = np.argmin(dd, axis=1)
        idx[rows] = j
        dist[rows] = dd[np.arange(rows.size), j]
    return idx, dist


def dedup_map(xyz):
    seen = set()
    keep = []
    X = np.ascontiguousarray(np.asarray(xyz, dtype="<f8"))
    for i in range(X.shape[0]):
        k = X[i].tobytes()
        if k not in seen:
            seen.add(k)
            keep.append(i)
    return np.array(keep, dtype=np.int64)


def vox_keys(xyz):
    return np.floor(np.asarray(xyz, dtype=float) / VOX).astype(np.int64)


def vox_best(xyz):
    K = vox_keys(xyz)
    X = np.asarray(xyz, dtype=float)
    best = {}
    for i in range(X.shape[0]):
        k = (int(K[i, 0]), int(K[i, 1]), int(K[i, 2]))
        c = (np.array(k, dtype=float) + 0.5) * VOX
        d = float(np.linalg.norm(X[i] - c))
        if k not in best or d < best[k][0]:
            best[k] = (d, i)
    return best


def arm_map(arm, own, auth):
    """Independent native index maps (i0, i1) for an arm.

    own/auth: per-face 6xN native walls.
    """
    ox = [own[f][0:3].T for f in (0, 1)]
    ax = [auth[f][0:3].T for f in (0, 1)]
    if arm in ("OWN", "OWN_STRIDE1"):
        return [np.arange(ox[f].shape[0], dtype=np.int64) for f in (0, 1)]
    if arm == "AUTHOR":
        return [np.arange(ax[f].shape[0], dtype=np.int64) for f in (0, 1)]
    if arm in ("OWN_DEDUP", "OWN_DEDUP_STRIDE1"):
        return [dedup_map(ox[f]) for f in (0, 1)]
    if arm in ("OWN_SHARED_1MM", "AUTHOR_SHARED_1MM"):
        t, d = (ox, ax) if arm.startswith("OWN") else (ax, ox)
        out = []
        for f in (0, 1):
            _, dist = nn_index(t[f], d[f])
            out.append(np.nonzero(dist <= CUT)[0].astype(np.int64))
        return out
    if arm == "OWN_MATCHED_TO_AUTHOR":
        out = []
        for f in (0, 1):
            dd = dedup_map(ox[f])
            idx, dist = nn_index(ax[f], ox[f][dd])
            hit = idx[dist <= CUT]
            hit = hit[hit >= 0]
            out.append(dd[np.unique(hit)])
        return out
    if arm in ("OWN_COMMON_VOXEL", "AUTHOR_COMMON_VOXEL"):
        src, other = (ox, ax) if arm.startswith("OWN") else (ax, ox)
        out = []
        for f in (0, 1):
            sb = vox_best(src[f])
            ob = vox_best(other[f])
            keys = sorted(set(sb) & set(ob))
            out.append(np.array([sb[k][1] for k in keys], dtype=np.int64)
                       if keys else np.zeros(0, dtype=np.int64))
        return out
    raise KeyError(arm)


def eff_step(n, step):
    import sfs_axes.potsac as ps
    return int(ps.effective_step(int(n), step))


def best_ref(ax_rows):
    if not ax_rows:
        return None, None
    b = min(ax_rows, key=lambda r: (fnum(r["line_deg"]), int(r["rank"])))
    return fnum(b["line_deg"]), fnum(b["anchor_mm"])


# ---------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--expect-terminal", action="store_true")
    args = ap.parse_args()
    run = os.path.abspath(args.run)
    ev = os.path.join(run, "evidence")
    idxdir = os.path.join(ev, "indices")
    axroot = os.path.join(run, "out", "axes05")
    rdir = os.path.join(run, "renders")
    names = ["inputs", "runs", "axes", "changes", "sources", "fixtures", "renders",
             "jobs"]
    check("run_layout", all(os.path.isdir(d) for d in (ev, idxdir, axroot, rdir)),
          "missing a run subdirectory")
    for nm in names:
        p = os.path.join(ev, nm + ".tsv")
        check("evidence_%s_exists" % nm, os.path.isfile(p) and os.path.getsize(p) > 0, p)

    # ------------------------------------------------------------ native
    own = {}
    auth = {}
    ownp = {}
    authp = {}
    for stem, sid in STEMS:
        o0, o1, _ = dl.walls(stem, surfaces="own")
        a0, a1, _ = dl.walls(stem, surfaces="authors")
        own[sid] = [np.asarray(o0, dtype=float), np.asarray(o1, dtype=float)]
        auth[sid] = [np.asarray(a0, dtype=float), np.asarray(a1, dtype=float)]
        pot = dl.pot_of(stem)
        ownp[sid] = [os.path.join(dl.OWN[pot], stem + ".S0"),
                     os.path.join(dl.OWN[pot], stem + ".S1")]
        _, c0p, c1p, _, _ = dl.rb.get_piece_info(stem)
        authp[sid] = [c0p, c1p]
    srcwalls = {"own": own, "authors": auth}
    srcpaths = {"own": ownp, "authors": authp}

    # ------------------------------------------------------------ inputs
    head, rows = read_tsv(os.path.join(ev, "inputs.tsv"))
    check("inputs_header", head == INPUT_COLS, "header %s" % head)
    want = {(sid, arm, f) for _, sid in STEMS for arm in ARMS for f in (0, 1)}
    got = {(int(r["sherd"]), r["arm"], int(r["face"])) for r in rows}
    check("inputs_rows", len(rows) == 40 and got == want,
          "rows=%d unique=%d missing=%s extra=%s"
          % (len(rows), len(got), sorted(want - got)[:4], sorted(got - want)[:4]))

    table = {}
    for r in rows:
        sid, arm, f = int(r["sherd"]), r["arm"], int(r["face"])
        table[(sid, arm, f)] = r
        tag = "%d/%s/f%d" % (sid, arm, f)
        if arm not in ARM_SPEC:
            check("inputs_arm_%s" % tag, False, "unknown arm")
            continue
        source = ARM_SPEC[arm][0]
        native = srcwalls[source][sid][f]
        npz = os.path.join(idxdir, "E%d_%s_f%d.npz" % (sid, arm, f))
        if not check("npz_%s" % tag, os.path.isfile(npz), npz):
            continue
        d = np.load(npz)
        wall = np.asarray(d["wall"], dtype=np.float64)
        idx = np.asarray(d["idx"])
        ok_shape = (idx.ndim == 1 and idx.dtype == np.int64
                    and wall.shape == (6, idx.shape[0])
                    and wall.dtype == np.float64)
        check("npz_shape_%s" % tag, ok_shape,
              "idx %s %s wall %s %s" % (idx.shape, idx.dtype, wall.shape, wall.dtype))
        if not ok_shape:
            continue
        check("npz_bounds_%s" % tag,
              bool(idx.size == 0 or (idx.min() >= 0 and idx.max() < native.shape[1])),
              "idx outside the native wall")
        verbatim = (idx.size == 0 or np.array_equal(wall, native[:, idx]))
        check("verbatim_%s" % tag, verbatim,
              "retained rows are not the native 6-vectors at idx")
        check("hash_xyz_%s" % tag, matrix_sha(wall[0:3].T) == r["xyz_sha256"], "")
        check("hash_normals_%s" % tag, matrix_sha(wall[3:6].T) == r["normals_sha256"], "")
        check("hash_source_%s" % tag,
              sha_file(srcpaths[source][sid][f]) == r["source_sha256"],
              srcpaths[source][sid][f])
        check("points_%s" % tag, int(r["points"]) == wall.shape[1],
              "%s vs %d" % (r["points"], wall.shape[1]))
        check("native_points_%s" % tag, int(r["native_points"]) == native.shape[1],
              "%s vs %d" % (r["native_points"], native.shape[1]))
        frac = fnum(r["retained_fraction"])
        check("retained_fraction_%s" % tag,
              frac is not None and abs(frac - wall.shape[1] / native.shape[1]) <= 1e-6,
              r["retained_fraction"])
        check("duplicate_count_%s" % tag, dup_count(wall[0:3].T) == int(r["duplicate_xyz"]),
              "table %s" % r["duplicate_xyz"])
        if arm in ZERO_DUP:
            check("duplicate_zero_%s" % tag, int(r["duplicate_xyz"]) == 0,
                  "%s duplicates survived" % r["duplicate_xyz"])
        exp = arm_map(arm, own[sid], auth[sid])[f]
        check("arm_indices_%s" % tag, np.array_equal(idx, exp),
              "index map differs from the independent re-derivation")

    # ------------------------------------------------ voxel pair agreement
    for stem, sid in STEMS:
        for f in (0, 1):
            ra = table.get((sid, "OWN_COMMON_VOXEL", f))
            rb = table.get((sid, "AUTHOR_COMMON_VOXEL", f))
            tag = "%d/f%d" % (sid, f)
            if ra is None or rb is None:
                check("voxel_points_%s" % tag, False, "missing row")
                continue
            check("voxel_points_%s" % tag, ra["points"] == rb["points"],
                  "OWN %s vs AUTHOR %s" % (ra["points"], rb["points"]))
            da = np.load(os.path.join(idxdir, "E%d_OWN_COMMON_VOXEL_f%d.npz" % (sid, f)))
            db = np.load(os.path.join(idxdir, "E%d_AUTHOR_COMMON_VOXEL_f%d.npz" % (sid, f)))
            ka = vox_keys(np.asarray(da["wall"])[0:3].T)
            kb = vox_keys(np.asarray(db["wall"])[0:3].T)
            check("voxel_keys_sorted_%s" % tag,
                  ka.shape == kb.shape and np.array_equal(ka, kb)
                  and all(tuple(ka[i]) <= tuple(ka[i + 1]) for i in range(max(0, ka.shape[0] - 1))),
                  "shared voxel key sequences differ or are unsorted")
            if ka.shape[0] and ka.shape == kb.shape:
                check("voxel_distinct_%s" % tag,
                      len({tuple(k) for k in ka}) == ka.shape[0], "repeated voxel key")

    # -------------------------------------------------------------- runs
    rhead, rrows = read_tsv(os.path.join(ev, "runs.tsv"))
    check("runs_header", rhead[:11] == RUN_COLS and set(rhead[11:]) <= set(RUN_OPT),
          "header %s" % rhead)
    rwant = {(sid, arm) for _, sid in STEMS for arm in ARMS}
    rgot = {(int(r["sherd"]), r["arm"]) for r in rrows}
    check("runs_rows", len(rrows) == 20 and rgot == rwant,
          "rows=%d missing=%s" % (len(rrows), sorted(rwant - rgot)[:4]))
    rtab = {}
    for r in rrows:
        sid, arm = int(r["sherd"]), r["arm"]
        rtab[(sid, arm)] = r
        tag = "%d/%s" % (sid, arm)
        axfile = os.path.join(axroot, "Pot_E_Piece_%d" % sid, "%s_Axis.xyz" % arm)
        k_file = len(read_axis_rows(axfile))
        check("runs_file_%s" % tag, os.path.isfile(axfile), axfile)
        check("runs_k_%s" % tag, int(r["k"]) == k_file, "%s vs %d rows" % (r["k"], k_file))
        check("runs_sha_%s" % tag, sha_file(axfile) == r["axes_sha256"], "")
        status = r["status"]
        check("runs_status_%s" % tag,
              (status == "ok" and k_file >= 1 and r["reason"] == "")
              or (status == "no_axis" and k_file == 0 and r["reason"] != ""),
              "status=%s k=%d reason=%s" % (status, k_file, r["reason"]))
        step = int(r["requested_step"])
        check("runs_requested_step_%s" % tag, step == ARM_SPEC[arm][1],
              "%d vs %d" % (step, ARM_SPEC[arm][1]))
        n_arm = sum(int(table[(sid, arm, f)]["points"]) for f in (0, 1))
        check("runs_stride_%s" % tag, int(r["effective_stride"]) == eff_step(n_arm, step),
              "%s vs %d" % (r["effective_stride"], eff_step(n_arm, step)))
        drawn = len(range(0, n_arm, int(r["effective_stride"])))
        check("runs_drawn_%s" % tag, int(r["drawn_points"]) == drawn,
              "%s vs %d" % (r["drawn_points"], drawn))
        check("runs_basins_%s" % tag, int(r["basins"]) >= 0, r["basins"])
        if arm in NATIVE:
            src = ARM_SPEC[arm][0]
            arch = os.path.join(T19, "axes", "OWN" if src == "own" else "AUTHOR",
                                "Pot_E_Piece_%d_Axis.xyz" % sid)
            sha_a = sha_file(arch)
            same_bytes = sha_file(axfile) == sha_a
            a = read_axis_rows(arch)
            b = read_axis_rows(axfile)
            agree = int(len(a) == len(b) and len(a) > 0)
            maxabs = 0.0
            if agree:
                for (pa, da_), (pb, db) in zip(a, b):
                    maxabs = max(maxabs, float(np.max(np.abs(pa - pb))),
                                 float(np.max(np.abs(da_ - db))))
            ok = int(same_bytes or (agree and maxabs <= 1e-9))
            check("runs_archive_ok_%s" % tag, int(r["archive_ok"]) == ok,
                  "table %s recomputed %d" % (r["archive_ok"], ok))
            check("runs_archive_sha_%s" % tag, r.get("archived_sha256") == sha_a, "")
            check("runs_archive_agree_%s" % tag,
                  int(r.get("archive_rank_count_agree") or 0) == agree,
                  "table %s recomputed %d" % (r.get("archive_rank_count_agree"), agree))
            if agree and not same_bytes:
                v = fnum(r.get("archive_max_abs"))
                check("runs_archive_maxabs_%s" % tag,
                      v is not None and abs(v - maxabs) <= 1e-12,
                      "table %s recomputed %.6g" % (r.get("archive_max_abs"), maxabs))
            elif same_bytes:
                check("runs_archive_maxabs_%s" % tag,
                      fnum(r.get("archive_max_abs")) == 0.0, "byte match needs 0")
        else:
            check("runs_archive_blank_%s" % tag, r["archive_ok"] in ("", None),
                  "archive_ok must be blank for %s" % arm)

    # -------------------------------------------------------------- axes
    ahead, arows = read_tsv(os.path.join(ev, "axes.tsv"))
    check("axes_header", ahead == AXIS_COLS, "header %s" % ahead)
    by_arm = {}
    for r in arows:
        by_arm.setdefault((int(r["sherd"]), r["arm"]), []).append(r)
    for key, rs in by_arm.items():
        rs.sort(key=lambda r: int(r["rank"]))
    for _, sid in STEMS:
        gt = dl.gt_axis("Pot_E_Piece_%d" % sid)
        gd = unit(gt[0:3])
        gp = np.asarray(gt[3:6], dtype=float)
        for arm in ARMS:
            tag = "%d/%s" % (sid, arm)
            rs = by_arm.get((sid, arm), [])
            rrow = rtab.get((sid, arm))
            if rrow is None:
                check("axes_ranks_%s" % tag, False, "no runs row for %s" % arm)
                continue
            k = int(rrow["k"])
            check("axes_ranks_%s" % tag,
                  [int(r["rank"]) for r in rs] == list(range(1, k + 1)),
                  "ranks %s for k=%d" % ([int(r["rank"]) for r in rs], k))
            axfile = os.path.join(axroot, "Pot_E_Piece_%d" % sid, "%s_Axis.xyz" % arm)
            frows = read_axis_rows(axfile)
            check("axes_file_rows_%s" % tag, len(frows) == k, "%d vs %d" % (len(frows), k))
            worst = 0.0
            for r in rs:
                i = int(r["rank"]) - 1
                if i >= len(frows):
                    break
                pos, di = frows[i]
                oriented = ang_deg(di, gd)
                line = min(oriented, 180.0 - oriented)
                anchor = line_dist(pos, gp, gd)
                worst = max(worst, abs(fnum(r["oriented_deg"]) - oriented),
                            abs(fnum(r["line_deg"]) - line),
                            abs(fnum(r["anchor_mm"]) - anchor))
                cmp_p = max(abs(fnum(r["pos_%s" % c]) - pos[j])
                            for j, c in enumerate("xyz"))
                cmp_d = max(abs(fnum(r["dir_%s" % c]) - di[j])
                            for j, c in enumerate("xyz"))
                check("axes_components_%s_r%d" % (tag, i + 1), cmp_p <= 1e-9 and cmp_d <= 1e-9,
                      "pos %.3g dir %.3g" % (cmp_p, cmp_d))
                check("axes_ranges_%s_r%d" % (tag, i + 1),
                      0.0 <= fnum(r["oriented_deg"]) <= 180.0
                      and 0.0 <= fnum(r["line_deg"]) <= 90.0
                      and fnum(r["anchor_mm"]) >= 0.0, "")
            check("axes_recompute_%s" % tag, worst <= 1e-5, "worst %.3g" % worst)

    # ----------------------------------------------------------- changes
    chead, crows = read_tsv(os.path.join(ev, "changes.tsv"))
    check("changes_header", chead == CHANGE_COLS, "header %s" % chead)
    cwant = {(sid, arm) for _, sid in STEMS for arm in NON_NATIVE}
    cgot = {(int(r["sherd"]), r["arm"]) for r in crows}
    check("changes_rows", len(crows) == 16 and cgot == cwant,
          "rows=%d missing=%s" % (len(crows), sorted(cwant - cgot)[:4]))
    for r in crows:
        sid, arm = int(r["sherd"]), r["arm"]
        tag = "%d/%s" % (sid, arm)
        parent = "AUTHOR" if ARM_SPEC[arm][0] == "authors" else "OWN"
        check("changes_parent_%s" % tag, r["parent_arm"] == parent,
              "%s vs %s" % (r["parent_arm"], parent))
        if (sid, parent) not in rtab or (sid, arm) not in rtab:
            check("changes_k_%s" % tag, False, "missing runs row")
            continue
        kp = int(rtab[(sid, parent)]["k"])
        ka = int(rtab[(sid, arm)]["k"])
        check("changes_k_%s" % tag, int(r["k_parent"]) == kp and int(r["k_arm"]) == ka,
              "table %s/%s recomputed %d/%d" % (r["k_parent"], r["k_arm"], kp, ka))
        pa = os.path.join(axroot, "Pot_E_Piece_%d" % sid, "%s_Axis.xyz" % parent)
        aa = os.path.join(axroot, "Pot_E_Piece_%d" % sid, "%s_Axis.xyz" % arm)
        same = int(sha_file(pa) == sha_file(aa))
        check("changes_bytes_%s" % tag, int(r["axes_bytes_identical"]) == same,
              "table %s recomputed %d" % (r["axes_bytes_identical"], same))
        bl_p, ba_p = best_ref(by_arm.get((sid, parent), []))
        bl_a, ba_a = best_ref(by_arm.get((sid, arm), []))
        if bl_p is None or bl_a is None:
            check("changes_best_ref_%s" % tag,
                  r["best_ref_line_deg_parent"] == "" and r["best_ref_line_deg_arm"] == "",
                  "an arm with no axes must leave both best_ref columns empty")
        else:
            check("changes_best_ref_%s" % tag,
                  abs(fnum(r["best_ref_line_deg_parent"]) - bl_p) <= 1e-6
                  and abs(fnum(r["best_ref_line_deg_arm"]) - bl_a) <= 1e-6
                  and abs(fnum(r["best_ref_anchor_mm_parent"]) - ba_p) <= 1e-6
                  and abs(fnum(r["best_ref_anchor_mm_arm"]) - ba_a) <= 1e-6,
                  "parent %s/%s arm %s/%s" % (r["best_ref_line_deg_parent"],
                                              r["best_ref_anchor_mm_parent"],
                                              r["best_ref_line_deg_arm"],
                                              r["best_ref_anchor_mm_arm"]))
        m = min(kp, ka)
        if m == 0:
            check("changes_max_rank_%s" % tag,
                  r["max_rank_line_delta_deg"] == "" and r["max_rank_anchor_delta_mm"] == "",
                  "no comparable rank must leave the deltas empty")
        else:
            lp = read_axis_rows(pa)
            la = read_axis_rows(aa)
            gt = dl.gt_axis("Pot_E_Piece_%d" % sid)
            gd = unit(gt[0:3])
            gp = np.asarray(gt[3:6], dtype=float)
            dl_max = 0.0
            da_max = 0.0
            for i in range(m):
                pp, dp = lp[i]
                pn, dn = la[i]
                c = float(np.clip(abs(unit(dp) @ unit(dn)), -1.0, 1.0))
                dl_max = max(dl_max, float(np.degrees(np.arccos(c))))
                da_max = max(da_max,
                             float(np.linalg.norm(anchor_point(pp, gp, gd)
                                                  - anchor_point(pn, gp, gd))))
            v_l = fnum(r["max_rank_line_delta_deg"])
            v_a = fnum(r["max_rank_anchor_delta_mm"])
            check("changes_max_rank_%s" % tag,
                  v_l is not None and abs(v_l - dl_max) <= 1e-6
                  and v_a is not None and abs(v_a - da_max) <= 1e-6,
                  "line %s/%.6g anchor %s/%.6g" % (r["max_rank_line_delta_deg"], dl_max,
                                                   r["max_rank_anchor_delta_mm"], da_max))
            check("changes_line_range_%s" % tag, 0.0 <= v_l <= 90.0,
                  "line delta %s outside 0-90" % r["max_rank_line_delta_deg"])

    # ---------------------------------------------------------- fixtures
    fhead, frows = read_tsv(os.path.join(ev, "fixtures.tsv"))
    check("fixtures_header", fhead == ["fixture", "status", "detail"], "header %s" % fhead)
    check("fixtures_names", [r["fixture"] for r in frows] == FIXTURES,
          "names %s" % [r["fixture"] for r in frows])
    check("fixtures_pass", all(r["status"] == "PASS" for r in frows) and len(frows) == 8,
          "statuses %s" % [(r["fixture"], r["status"]) for r in frows
                           if r["status"] != "PASS"])

    # ----------------------------------------------------------- renders
    rhead2, rrows2 = read_tsv(os.path.join(ev, "renders.tsv"))
    check("renders_header", rhead2 == ["sherd", "path", "scale_bar_mm"], "header %s" % rhead2)
    check("renders_rows", len(rrows2) == 2 and {int(r["sherd"]) for r in rrows2} == {27, 28},
          "rows %s" % [r.get("sherd") for r in rrows2])
    for r in rrows2:
        tag = "renders_%s" % r["sherd"]
        p = r["path"]
        full = os.path.join(run, p)
        check("renders_relative_%s" % tag, not os.path.isabs(p), p)
        ok = os.path.isfile(full) and os.path.getsize(full) > 20000
        magic = False
        if os.path.isfile(full):
            with open(full, "rb") as fh:
                magic = fh.read(8) == b"\x89PNG\r\n\x1a\n"
        check("renders_png_%s" % tag, ok and magic, "%s size=%s"
              % (full, os.path.getsize(full) if os.path.isfile(full) else "missing"))
        check("renders_scale_%s" % tag, int(r["scale_bar_mm"]) == 20, r["scale_bar_mm"])

    # -------------------------------------------------------------- jobs
    jhead, jrows = read_tsv(os.path.join(ev, "jobs.tsv"))
    check("jobs_header", jhead == ["job_id", "state", "exit_code"], "header %s" % jhead)
    check("jobs_rows", len(jrows) >= 1 and jrows[0]["job_id"].isdigit(),
          "rows %s" % [(r.get("job_id"), r.get("state")) for r in jrows])
    if args.expect_terminal:
        ids = {r["job_id"] for r in jrows}
        term = {}
        for r in jrows:
            if r["state"] in TERMINAL:
                term.setdefault(r["job_id"], []).append(r)
        ok = all(i in term for i in ids)
        check("jobs_terminal_rows", ok, "no terminal row for %s"
              % [i for i in ids if i not in term])
        for i in ids:
            rs = term.get(i, [])
            check("jobs_terminal_code_%s" % i,
                  bool(rs) and all(re.fullmatch(r"\d+:\d+", r["exit_code"] or "")
                                   for r in rs),
                  "exit codes %s" % [r.get("exit_code") for r in rs])
        first = jrows[0]["job_id"]
        rs = term.get(first, [])
        check("jobs_completed", bool(rs) and rs[-1]["state"] == "COMPLETED"
              and rs[-1]["exit_code"] == "0:0",
              "%s %s" % (rs[-1]["state"] if rs else "?", rs[-1]["exit_code"] if rs else "?"))
        idx = "/data/gpfs/projects/punim2657/SfSpp/runs/index.tsv"
        ihead, irows = read_tsv(idx)
        mine = [r for r in irows if r["runid"] == os.path.basename(run)]
        check("index_row", len(mine) == 1, "%d rows for %s"
              % (len(mine), os.path.basename(run)))
        if mine:
            check("index_verdict_empty", (mine[0].get("verdict") or "") == "",
                  mine[0].get("verdict"))
            check("index_human_note_empty", (mine[0].get("human_note") or "") == "",
                  mine[0].get("human_note"))
            check("index_columns", ihead[:4] == ["runid", "jobid", "commit", "tag"],
                  "header %s" % ihead)
            check("index_jobid", mine[0]["jobid"] == first, mine[0]["jobid"])

    # ----------------------------------------------------------- sources
    shead, srows = read_tsv(os.path.join(ev, "sources.tsv"))
    check("sources_header", shead == SOURCE_COLS, "header %s" % shead)
    kinds = {r["kind"] for r in srows}
    check("sources_kinds", {"root", "input_wall", "reference", "archive_axis",
                            "code"} <= kinds, "kinds %s" % sorted(kinds))
    bad = []
    for r in srows:
        if r["kind"] == "root":
            continue
        if not os.path.isfile(r["path"]) or sha_file(r["path"]) != r["sha256"]:
            bad.append(r["path"])
    check("sources_hashes", not bad, "bad %s" % bad[:4])
    have = {r["name"] for r in srows if r["kind"] == "code"}
    check("sources_code", all(n in have for n in CODE_WANT),
          "missing %s" % [n for n in CODE_WANT if n not in have])
    npz_all = glob.glob(os.path.join(idxdir, "*.npz"))
    check("indices_count", len(npz_all) == 40, "%d npz files" % len(npz_all))

    print("SUMMARY checks=%d failures=%d" % (CHECKS[0], len(FAILS)))
    if FAILS:
        for nm, detail in FAILS:
            print("  failed: %s %s" % (nm, detail))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
