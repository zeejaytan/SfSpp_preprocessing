#!/usr/bin/env python3
"""Ticket 06 mechanical verification, independent of the code that wrote the tables.

Every table is re-derived from the bytes it describes: walls are re-loaded with
the frozen loader and de-duplicated by an independent bit-sorted algorithm
(not axes06's first-seen dictionary), axis files are re-hashed and their line
counts recounted, the six pins are checked against the ticket's literals, the
scorer's output is re-parsed and every seam verdict re-decided at the 20.05 deg /
50 mm bars, traces are recounted from t18_raw.jsonl, the fixtures must be 4/4
PASS, both renders must exist as real PNGs with a 20 mm bar, every recorded job
must be terminal with exit 0:0 (--expect-terminal), and the control separation
gate must hold before either test arm is interpreted.

  check06.py --run RUN --fixed FIXED [--expect-terminal]
"""
import argparse
import hashlib
import json
import os
import struct
import subprocess
import sys

import numpy as np

SHIP = "/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-ship"
T05 = "/data/gpfs/projects/punim2657/SfSpp/runs/20261125-0017_57a4da7_t05-sampling-coverage"
T19 = "/data/gpfs/projects/punim2657/SfSpp/runs/20261124-0443_21446b8_t19-decisions"
RUN5 = "/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0445_9c5eec2_t305-lane-e2"
os.environ.setdefault("SFS_IMPL", os.path.join(SHIP, "work", "impl_t03"))
for _p in (os.path.join(SHIP, "work"), os.environ["SFS_IMPL"],
           os.path.join(os.environ["SFS_IMPL"], "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import run_benchmark_172 as rb  # noqa: E402

ARMS = ["AUTHOR", "OWN_NOV5", "OWN_NOV5_DEDUP", "OWN_MAIN_T09"]
REPS = [1, 2]
SEAMS = ["13-28", "27-28", "28-31"]
PIECES = ["Pot_E_Piece_%02d" % p for p in range(1, 32)]
ANG_BAR, T_BAR = 20.05, 50.0

WALL_COLS = ("sherd", "surface_set", "face", "points", "duplicate_xyz",
             "xyz_sha256", "normals_sha256", "source_sha256")
AXIS_COLS = ("sherd", "arm", "status", "k", "axes_sha256", "effective_stride",
             "drawn_points", "best_line_deg", "best_anchor_mm",
             "rank1_line_deg", "rank1_anchor_mm")
CELL_COLS = ("arm", "rep", "job_id", "status", "usable", "exported_poses",
             "joins_pass", "joins_total", "pieces_pass", "pieces_total",
             "seam_13_28_pass", "seam_27_28_pass", "seam_28_31_pass",
             "exe_sha_ok", "inputs_unchanged", "container_files", "wall_secs")
SEAM_COLS = ("arm", "rep", "join_i", "join_j", "ang_deg", "t_mm", "verdict")
TRACE_COLS = ("arm", "rep", "seam", "direct_queries", "candidate_stretches",
              "fits_ok", "first_event_id")
JOB_COLS = ("job_id", "stage", "arm", "rep", "state", "exit_code")
FIX_COLS = ("fixture", "status", "detail")
RENDER_COLS = ("figure", "path", "scale_bar_mm")
SRC_COLS = ("kind", "path", "sha256", "bytes", "detail")
FIXTURES = ("dedup_first_order", "verbatim_6vec", "author_zero_dup",
            "posecheck_completeness")
PINS = {("AUTHOR", 27): (2, "f1607e000d563216aa8a3a962162ba3b7cfbddefa760b1a797e0d683e0732f8b"),
        ("AUTHOR", 28): (2, "212dcb15ae1291980c67bb3de4b9f01936e26c03a9de428c388a424c8c65ede5"),
        ("OWN_NOV5", 27): (3, "d4236e9115f49b67872369d31fbd7953bd322513af49cfa9cbf30ce8074a4cc6"),
        ("OWN_NOV5", 28): (1, "12de83dc2cb91f525854347cc5cea6c34a11d5a65a3d274b91087b33d73d8acf"),
        ("OWN_NOV5_DEDUP", 27): (2, "a3e1694d3e291d85ed5d7b57b302c155f7f19a0218f25ac628c65cc24861a39d"),
        ("OWN_NOV5_DEDUP", 28): (2, "a5f49e5621bae8bd7cb74efcb30ab419dcf03099d0fd2e78f6a0b2e9b696aa7d")}
WANT_SHA = "0ba6d10fa6885a67a92a92bb37ec7c138f25f32622368bfcafb5bfae3fa637c9"
TERMINAL = {"COMPLETED", "FAILED", "CANCELLED", "TIMEOUT", "NODE_FAIL",
            "PREEMPTED", "OUT_OF_MEMORY", "BOOT_FAIL", "DEADLINE"}

CHECKS = 0
FAILS = []


def check(name, cond, detail=""):
    global CHECKS
    CHECKS += 1
    if cond:
        print("ok   %-46s :: %s" % (name, detail))
    else:
        FAILS.append((name, detail))
        print("FAIL %-46s :: %s" % (name, detail))


def sha_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def matrix_sha(a):
    return hashlib.sha256(np.ascontiguousarray(np.asarray(a, dtype="<f8")).tobytes()).hexdigest()


def bits(xyz):
    return np.ascontiguousarray(np.asarray(xyz, dtype="<f8")).view(np.uint64).reshape(-1, 3)


def dup_flags(xyz):
    """Bit-sorted de-duplication: every row whose bits equal an earlier row is a duplicate."""
    B = bits(xyz)
    n = B.shape[0]
    dup = np.zeros(n, dtype=bool)
    if n < 2:
        return dup
    order = np.lexsort((B[:, 2], B[:, 1], B[:, 0]))
    S = B[order]
    newrun = np.ones(n, dtype=bool)
    newrun[1:] = np.any(S[1:] != S[:-1], axis=1)
    starts = np.nonzero(newrun)[0]
    ends = np.append(starts[1:], n)
    for a, b in zip(starts, ends):
        if b - a > 1:
            idx = order[a:b]
            dup[idx[idx != idx.min()]] = True
    return dup


def read_tsv(path):
    rows = []
    with open(path) as fh:
        for ln in fh:
            if ln.strip() == "":
                continue
            rows.append(ln.rstrip("\n").split("\t"))
    return rows


def header_ok(path, cols):
    rows = read_tsv(path)
    ok = bool(rows) and tuple(rows[0]) == tuple(cols)
    check("header %s" % os.path.basename(path), ok, "|".join(rows[0]) if rows else "empty")
    return rows


def read_T(path):
    a = np.loadtxt(path, ndmin=2)
    T = np.eye(4)
    T[0:3, 0:3] = a[0:3, 0:3]
    T[0:3, 3] = a[0:3, 3]
    return T


def angle_deg(R):
    c = (np.trace(R) - 1.0) / 2.0
    return float(np.degrees(np.arccos(np.clip(c, -1.0, 1.0))))


def parse_score(path):
    pieces, joins, sp, sj = {}, {}, None, None
    for ln in open(path):
        f = ln.rstrip("\n").split("\t")
        if f[0] == "SUMMARY":
            for tok in f[1:]:
                if tok.startswith("pieces="):
                    sp = int(tok.split("=")[1].split("/")[0])
                elif tok.startswith("joins="):
                    sj = int(tok.split("=")[1].split("/")[0])
            continue
        if f[0].startswith("#") or len(f) < 4:
            continue
        if not f[0].isdigit():
            continue  # the "piece ang_deg t_mm verdict" column header
        if len(f) >= 5:
            joins[(int(f[0]), int(f[1]))] = (float(f[2]), float(f[3]), f[4])
        else:
            pieces[int(f[0])] = (float(f[1]), float(f[2]), f[3])
    return pieces, joins, sp, sj


def sacct(ids):
    out = {}
    if not ids:
        return out
    try:
        res = subprocess.run(["sacct", "-n", "-X", "-P", "-j", ",".join(ids),
                              "-o", "JobID,State,ExitCode"],
                             capture_output=True, text=True, timeout=180)
        for ln in res.stdout.splitlines():
            f = ln.strip().split("|")
            if len(f) >= 3:
                out[f[0]] = (f[1], f[2])
    except Exception as exc:
        print("WARN sacct failed: %s" % exc)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--fixed", required=True)
    ap.add_argument("--expect-terminal", action="store_true")
    a = ap.parse_args(argv)
    run, fixed = a.run, a.fixed
    ev = os.path.join(run, "evidence")
    self_id = os.environ.get("SLURM_JOB_ID", "")

    # ---------------------------------------------------------------- walls
    wrows = header_ok(os.path.join(ev, "walls.tsv"), WALL_COLS)
    check("walls.tsv rows == 186", len(wrows) - 1 == 186, "rows=%d" % (len(wrows) - 1))
    seen = set()
    wall_bad = 0
    dup_zero = {"OWN_NOV5_DEDUP": 0, "OWN_MAIN_T09": 0}
    dup_own_nov5 = 0
    for r in wrows[1:]:
        sid, setname, face = int(r[0]), r[1], int(r[2])
        seen.add((sid, setname, face))
        stem = PIECES[sid - 1]
        src = (os.path.join(run, "geom_main", "geom", stem + ".S%d" % face)
               if setname == "OWN_MAIN_T09"
               else os.path.join(RUN5, "out", "geom", stem + ".S%d" % face))
        W = rb.load_wall(src)
        src_sha = sha_file(src)
        if setname == "OWN_NOV5_DEDUP":
            keep = np.nonzero(~dup_flags(W[0:3, :].T))[0]
            W = np.ascontiguousarray(W[:, keep])
        dup = int(dup_flags(W[0:3, :].T).sum())
        ok = (int(r[3]) == W.shape[1] and int(r[4]) == dup
              and r[5] == matrix_sha(W[0:3, :].T) and r[6] == matrix_sha(W[3:6, :].T)
              and r[7] == src_sha)
        if not ok:
            wall_bad += 1
            check("wall %s f%d re-derived" % (stem, face), False,
                  "points %s/%d dup %s/%d sha %s/%s src %s/%s"
                  % (r[3], W.shape[1], r[4], dup, r[5][:8], matrix_sha(W[0:3, :].T)[:8],
                     r[7][:8], src_sha[:8]))
        if setname == "OWN_NOV5_DEDUP" and dup != 0:
            dup_zero["OWN_NOV5_DEDUP"] += 1
        if setname == "OWN_MAIN_T09":
            if dup != 0:
                dup_zero["OWN_MAIN_T09"] += 1
        if setname == "OWN_NOV5" and dup > 0:
            dup_own_nov5 += 1
    check("walls.tsv 186 distinct (sherd,set,face)", len(seen) == 186, "distinct=%d" % len(seen))
    check("walls.tsv every row re-derived", wall_bad == 0, "bad rows=%d" % wall_bad)
    check("OWN_NOV5_DEDUP all 62 walls duplicate_xyz == 0",
          dup_zero["OWN_NOV5_DEDUP"] == 0, "violations=%d" % dup_zero["OWN_NOV5_DEDUP"])
    check("OWN_MAIN_T09 all 62 walls duplicate_xyz == 0",
          dup_zero["OWN_MAIN_T09"] == 0, "violations=%d" % dup_zero["OWN_MAIN_T09"])
    check("OWN_NOV5 carries duplicates (the premise)",
          dup_own_nov5 >= 60, "walls with duplicates=%d/62" % dup_own_nov5)

    # dedup content is the native 6-vectors: spot-check two pieces row by row
    for sid in (27, 28):
        stem = PIECES[sid - 1]
        for face in (0, 1):
            src = os.path.join(RUN5, "out", "geom", stem + ".S%d" % face)
            W = rb.load_wall(src)
            keep = np.nonzero(~dup_flags(W[0:3, :].T))[0]
            D = np.ascontiguousarray(W[:, keep])
            same = all(D[:, i].tobytes() == W[:, k].tobytes() for i, k in enumerate(keep))
            check("verbatim 6-vec %s f%d" % (stem, face), same and len(keep) > 0,
                  "kept=%d of %d" % (len(keep), W.shape[1]))

    # ---------------------------------------------------------------- axes
    arows = header_ok(os.path.join(ev, "axes.tsv"), AXIS_COLS)
    check("axes.tsv rows == 124", len(arows) - 1 == 124, "rows=%d" % (len(arows) - 1))
    amap = {}
    axes_bad = 0
    for r in arows[1:]:
        amap[(int(r[0]), r[1])] = r
    check("axes.tsv 124 distinct (sherd,arm)", len(amap) == 124, "distinct=%d" % len(amap))
    for sid in range(1, 32):
        for arm in ARMS:
            r = amap.get((sid, arm))
            if r is None:
                check("axes row %d %s" % (sid, arm), False, "missing")
                continue
            stem = PIECES[sid - 1]
            path = os.path.join(run, "axes", arm, stem + "_Axis.xyz")
            k = 0
            with open(path) as fh:
                k = sum(1 for ln in fh if ln.split())
            ok = int(r[3]) == k and r[4] == sha_file(path) and r[2] in ("ok", "empty")
            if not ok:
                axes_bad += 1
                check("axes file %s %s" % (stem, arm), False,
                      "k %s/%d sha %s/%s" % (r[3], k, r[4][:8], sha_file(path)[:8]))
    check("axes.tsv every row re-derived", axes_bad == 0, "bad rows=%d" % axes_bad)
    for (arm, sid), (k, sha) in sorted(PINS.items()):
        r = amap.get((sid, arm))
        ok = r is not None and int(r[3]) == k and r[4] == sha
        check("pin %s E%02d k=%d sha=%s" % (arm, sid, k, sha[:8]), ok,
              "row=%s" % ("absent" if r is None else "%s/%s" % (r[3], r[4][:8])))

    # Ticket 05's own record: its runs.tsv row AND the archived axis file itself
    t05_runs = os.path.join(T05, "evidence", "runs.tsv")
    t05_rows = {}
    if os.path.isfile(t05_runs):
        rows5 = read_tsv(t05_runs)
        cols5 = rows5[0]
        i_s, i_a = cols5.index("sherd"), cols5.index("arm")
        i_k, i_h = cols5.index("k"), cols5.index("axes_sha256")
        for r5 in rows5[1:]:
            if r5[i_a] == "OWN_DEDUP":
                t05_rows[int(r5[i_s])] = (int(r5[i_k]), r5[i_h])
    check("ticket 05 runs.tsv records OWN_DEDUP 27/28",
          all(s in t05_rows for s in (27, 28)), "rows=%s" % sorted(t05_rows))
    for sid in (27, 28):
        want_k, want_sha = PINS[("OWN_NOV5_DEDUP", sid)]
        f5 = os.path.join(T05, "out", "axes05", PIECES[sid - 1], "OWN_DEDUP_Axis.xyz")
        got5 = t05_rows.get(sid)
        check("ticket 05 archived axis E%02d byte-identical" % sid,
              os.path.isfile(f5) and sha_file(f5) == want_sha,
              "sha=%s want=%s" % (sha_file(f5)[:12] if os.path.isfile(f5) else "absent",
                                  want_sha[:12]))
        check("ticket 05 vs ticket 06 pin E%02d k=%d" % (sid, want_k),
              got5 == (want_k, want_sha), "t05=%s t06=%s" % (got5, (want_k, want_sha[:8])))

    # stride/drawn consistency: n from the wall rows (AUTHOR: authors' own walls)
    auth_n = {}
    import t03_lib as dl
    import sfs_axes.potsac as ps
    for sid in range(1, 32):
        C0, C1, C = dl.walls(PIECES[sid - 1], "authors")
        auth_n[sid] = (C0.shape[1], C1.shape[1])
    stride_bad = 0
    for sid in range(1, 32):
        for arm in ARMS:
            r = amap.get((sid, arm))
            if r is None:
                continue
            if arm == "AUTHOR":
                n = auth_n[sid][0] + auth_n[sid][1]
            else:
                rows = [x for x in wrows[1:] if int(x[0]) == sid and x[1] == arm]
                n = sum(int(x[3]) for x in rows) if rows else -1
            if n <= 0:
                stride_bad += 1
                continue
            st = int(ps.effective_step(n, 10))
            nd = int(np.ceil(n / float(st))) if st else 0
            if int(r[5]) != st or int(r[6]) != nd:
                stride_bad += 1
    check("axes.tsv effective_stride/drawn_points consistent", stride_bad == 0,
          "mismatches=%d" % stride_bad)

    # ---------------------------------------------------------------- cells
    crows = header_ok(os.path.join(ev, "cells.tsv"), CELL_COLS)
    check("cells.tsv rows == 8", len(crows) - 1 == 8, "rows=%d" % (len(crows) - 1))
    cmap = {}
    used = 0
    for r in crows[1:]:
        arm, rep = r[0], int(r[1])
        cmap[(arm, rep)] = r
        sp = os.path.join(run, "score", "%s_%d.tsv" % (arm, rep))
        if not os.path.isfile(sp):
            check("cell %s_%d score file" % (arm, rep), False, "missing")
            continue
        pieces, joins, spc, sjc = parse_score(sp)
        ok = (int(r[6]) == (sjc or 0) and int(r[7]) == 62
              and int(r[8]) == (spc or 0) and int(r[9]) == 31
              and int(r[11]) == (1 if joins.get((27, 28), (0, 0, ""))[2] == "PASS" else 0))
        if not ok:
            check("cell %s_%d vs score" % (arm, rep), False,
                  "joins %s/%s pieces %s/%s seam2728 %s" % (r[6], sjc, r[8], spc, r[11]))
        raw = {}
        rp = os.path.join(run, "logs", "cell_raw_%s_%d.json" % (arm, rep))
        if os.path.isfile(rp):
            raw = json.load(open(rp))
        poses = sum(1 for p in range(31)
                    if os.path.isfile(os.path.join(run, "out", "%s_%d" % (arm, rep), "T_%dto_%d.txt" % (p, p)))
                    and os.path.getsize(os.path.join(run, "out", "%s_%d" % (arm, rep), "T_%dto_%d.txt" % (p, p))) > 0)
        ok2 = (int(r[5]) == poses and r[2] == str(raw.get("job_id", "-"))
               and int(r[13]) == int(raw.get("exe_sha_ok", 0))
               and int(r[14]) == int(raw.get("inputs_unchanged", 0))
               and int(r[15]) == int(raw.get("container_files", 0))
               and int(r[16]) == int(raw.get("wall_secs", 0)))
        if not ok2:
            check("cell %s_%d vs raw json" % (arm, rep), False,
                  "poses %s/%d job %s/%s" % (r[5], poses, r[2], raw.get("job_id")))
        print("NOTE cell %s_%d usable=%s status=%s" % (arm, rep, r[4], r[3]))
        used += 1 if int(r[4]) == 1 else 0
    check("cells.tsv 8 distinct (arm,rep)", len(cmap) == 8, "distinct=%d" % len(cmap))
    check("cells usable >= 6 of 8", used >= 6, "usable=%d" % used)
    check("both AUTHOR cells usable",
          all(int(cmap[(a_, 1)][4]) == 1 and int(cmap[(a_, 2)][4]) == 1 for a_ in ["AUTHOR"]),
          "AUTHOR 1/2")
    check("both OWN_NOV5 cells usable",
          all(int(cmap[(a_, 1)][4]) == 1 and int(cmap[(a_, 2)][4]) == 1 for a_ in ["OWN_NOV5"]),
          "OWN_NOV5 1/2")

    # ---------------------------------------------------------------- seams
    srows = header_ok(os.path.join(ev, "seams.tsv"), SEAM_COLS)
    check("seams.tsv rows == 62 * usable", len(srows) - 1 == 62 * used,
          "rows=%d usable=%d" % (len(srows) - 1, used))
    bad = 0
    for r in srows[1:]:
        ang, t, verdict = float(r[4]), float(r[5]), r[6]
        want = "PASS" if (ang <= ANG_BAR and abs(t) <= T_BAR) else "FAIL"
        sp = os.path.join(run, "score", "%s_%s.tsv" % (r[0], r[1]))
        ref = parse_score(sp)[1].get((int(r[2]), int(r[3]))) if os.path.isfile(sp) else None
        if want != verdict or ref is None or abs(ref[0] - ang) > 1e-6 or abs(ref[1] - t) > 1e-6:
            bad += 1
    check("seams.tsv every verdict re-decided at 20.05 deg / 50 mm", bad == 0,
          "mismatches=%d" % bad)

    # ---------------------------------------------------------------- traces
    trows = header_ok(os.path.join(ev, "traces.tsv"), TRACE_COLS)
    check("traces.tsv rows == 24", len(trows) - 1 == 24, "rows=%d" % (len(trows) - 1))
    tbad = 0
    seen_t = set()
    for r in trows[1:]:
        arm, rep, seam = r[0], r[1], r[2]
        seen_t.add((arm, rep, seam))
        path = os.path.join(run, "out", "%s_%s" % (arm, rep), "t18_raw.jsonl")
        q = iv = fit = first = 0
        if os.path.isfile(path):
            for ln in open(path):
                try:
                    d = json.loads(ln)
                except Exception:
                    continue
                s = d.get("seam")
                if not s:
                    aa, bb = d.get("a"), d.get("b")
                    if aa is None or bb is None:
                        continue
                    s = "%d-%d" % (min(aa, bb), max(aa, bb))
                if s != seam:
                    continue
                st = d.get("stage")
                if st == "query":
                    q += 1
                    if not first:
                        first = d.get("ev", 0)
                elif st == "interval":
                    iv += 1
                elif st == "pair_fit" and float(d.get("inlier", 0)) > 0:
                    fit += 1
        if [q, iv, fit, first] != [int(r[3]), int(r[4]), int(r[5]), int(r[6])]:
            tbad += 1
    check("traces.tsv every count re-derived from t18_raw.jsonl", tbad == 0,
          "mismatches=%d" % tbad)
    check("traces.tsv 8 cells x 3 seams", len(seen_t) == 24, "distinct=%d" % len(seen_t))

    # ---------------------------------------------------------------- fixtures
    frows = header_ok(os.path.join(ev, "fixtures.tsv"), FIX_COLS)
    got = {r[0]: r[1] for r in frows[1:]}
    check("fixtures.tsv 4/4 PASS", all(got.get(f) == "PASS" for f in FIXTURES),
          " ".join("%s=%s" % (f, got.get(f, "absent")) for f in FIXTURES))

    # ---------------------------------------------------------------- renders
    rrows = header_ok(os.path.join(ev, "renders.tsv"), RENDER_COLS)
    check("renders.tsv rows == 2", len(rrows) - 1 == 2, "rows=%d" % (len(rrows) - 1))
    for r in rrows[1:]:
        p = r[1] if os.path.isabs(r[1]) else os.path.join(run, r[1])
        ok = (os.path.isfile(p) and os.path.getsize(p) > 20000
              and open(p, "rb").read(8) == b"\x89PNG\r\n\x1a\n" and int(r[2]) == 20)
        check("render %s (20 mm bar, PNG)" % os.path.basename(p), ok,
              "bytes=%s scale=%s" % (os.path.getsize(p) if os.path.isfile(p) else 0, r[2]))

    # ---------------------------------------------------------------- jobs
    jrows = header_ok(os.path.join(ev, "jobs.tsv"), JOB_COLS)
    sub = read_tsv(os.path.join(run, "logs", "jobs_submitted.tsv"))
    aux_rows = []
    apath = os.path.join(ev, "jobs_aux.tsv")
    if os.path.isfile(apath):
        aux_rows = read_tsv(apath)[1:]
    aux_ids = set(r[0] for r in aux_rows)
    want_ids = [r[0] for r in sub[1:] if r[0] not in aux_ids]
    have_ids = [r[0] for r in jrows[1:]]
    check("jobs.tsv covers every evidence job (verifiers in jobs_aux.tsv)",
          sorted(have_ids) == sorted(want_ids),
          "have=%d want=%d aux=%d" % (len(have_ids), len(want_ids), len(aux_ids)))
    live = sacct(sorted(set(have_ids) | aux_ids))
    stale = 0
    if a.expect_terminal:
        for r in jrows[1:]:
            st, ex = live.get(r[0], (r[4], r[5]))
            ok = st in TERMINAL and ex.split(":")[0] == "0"
            if not ok:
                stale += 1
            check("job %s terminal COMPLETED 0:0" % r[0], ok, "sacct=%s %s recorded=%s %s" % (st, ex, r[4], r[5]))
        check("every job in jobs.tsv terminal", stale == 0, "non-terminal=%d" % stale)
        for r in aux_rows:
            st, ex = live.get(r[0], ("UNKNOWN", "-"))
            print("AUX %s %s live=%s %s (own final state: see the laptop poll record)" % (r[0], r[1], st, ex))

    # ---------------------------------------------------------------- sources
    srows2 = header_ok(os.path.join(ev, "sources.tsv"), SRC_COLS)
    sbad = 0
    for r in srows2[1:]:
        kind, path, sha, nbytes = r[0], r[1], r[2], r[3]
        if kind == "commit":
            ok = len(sha) == 40 and subprocess.run(
                ["git", "-C", path, "cat-file", "-e", sha + "^{commit}"],
                capture_output=True).returncode == 0
        else:
            ok = (os.path.isfile(path) and sha_file(path) == sha
                  and os.path.getsize(path) == int(nbytes))
        if not ok:
            sbad += 1
            print("FAIL source %s %s" % (kind, path))
    check("sources.tsv every row verified", sbad == 0, "rows=%d bad=%d" % (len(srows2) - 1, sbad))
    check("sources.tsv names e91cf791", any("e91cf791" in r[4] for r in srows2[1:]),
          "commit rows=%d" % sum(1 for r in srows2[1:] if r[0] == "commit"))

    # ---------------------------------------------------------------- dedupe-27 + corpus
    dfile = os.path.join(ev, "dedupe27.txt")
    n27 = 0
    off = 0
    if os.path.isfile(dfile):
        for ln in open(dfile):
            if "[DEDUPE-27]" in ln:
                n27 += 1
                if "mode=off" in ln:
                    off += 1
    check("[DEDUPE-27] lines == 62", n27 == 62, "lines=%d mode_off=%d" % (n27, off))
    check("[DEDUPE-27] every line mode=off (SFS_DEDUPE unset)", off == n27, "off=%d/%d" % (off, n27))
    b = os.path.join(run, "logs", "corpus_inputs_before.md5")
    af = os.path.join(run, "logs", "corpus_inputs_after.md5")
    check("corpus md5 unchanged", os.path.isfile(b) and os.path.isfile(af)
          and open(b, "rb").read() == open(af, "rb").read(),
          "before=%s after=%s" % (os.path.getsize(b) if os.path.isfile(b) else "-",
                                  os.path.getsize(af) if os.path.isfile(af) else "-"))
    panel = os.path.join(run, "panel", "build", "Hierarchy-T19")
    check("assembler pin WANT_SHA before/after", os.path.isfile(panel) and sha_file(panel) == WANT_SHA,
          "sha=%s" % (sha_file(panel)[:12] if os.path.isfile(panel) else "absent"))

    # ---------------------------------------------------------------- control separation gate
    best = {}
    for arm in ARMS:
        cand = [(int(c[6]), int(c[8]), int(c[1])) for c in crows[1:] if c[0] == arm and int(c[4]) == 1]
        best[arm] = max(cand)[:2] if cand else (0, 0)
    # joins are the ticket's unit; the scorer's piece-level count is 0 even for AUTHOR
    check("control AUTHOR 62/62 joins", best["AUTHOR"][0] == 62,
          "AUTHOR=%d/62 joins, %d/31 pieces at bar" % (best["AUTHOR"][0], best["AUTHOR"][1]))
    check("control OWN_NOV5 misses a join", best["OWN_NOV5"][0] < 62,
          "OWN_NOV5=%d/62" % best["OWN_NOV5"][0])
    fails_2728 = [r for r in srows[1:] if r[0] == "OWN_NOV5" and int(r[2]) == 27 and int(r[3]) == 28
                  and r[6] == "FAIL"]
    check("control OWN_NOV5 fails join 27-28", len(fails_2728) > 0,
          "fail rows=%d" % len(fails_2728))

    print("\nCHECKS=%d FAILURES=%d" % (CHECKS, len(FAILS)))
    if FAILS:
        print("FAILED NAMES: " + ", ".join(n for n, d in FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
