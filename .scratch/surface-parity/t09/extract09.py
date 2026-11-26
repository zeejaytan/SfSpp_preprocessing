#!/usr/bin/env python3
"""Surface Parity Ticket 09, Stage 3: verify the regenerated own surfaces and extract the
frozen SHIP axes from them.

Read-only inputs: the frozen SHIP run (its work/t03_lib.py, work/t03_extract.py and
work/impl_t03), the Ticket 08 run (evidence/walls.tsv as the deduplication baseline plus its
work/t08/extract08.py dedup helpers), the frozen corpus and this ticket's own out/ geoms.
Writes only under --run.

Steps
  1. For all 314 regenerated walls: duplicate_xyz == 0 (byte identity on the float64 xyz
     triples, the same rule Ticket 08 used), a non-empty .Bl0/.Bl1, and the nearest-neighbour
     spread.  The Ticket 08 baseline is re-derived deterministically from the FROZEN
     own-surface geoms with extract08's dedup_indices (Ticket 08 never wrote its deduplicated
     walls to disk), and the re-derived walls must match Ticket 08's evidence/walls.tsv on
     points and xyz_sha256 for all 314 walls before any number is trusted.
  2. The frozen Ticket 03 estimator (t03_lib.draw_pool -> t03_extract.select_lines ->
     t03_extract.write_lines) on the REGENERATED walls: out/axes09_own_regen (148 pot stems)
     and out/axes09_juglet_def3x_regen (9 def_3x stems, native 3x tree units -- no division
     on the written rows, no canonicalize(); JUG_ROWS is used only for the GT metrics).
  3. The [DEDUPE-27] lines of this run: mode=off, in==out, 0 <= normal_maxdiff <= 1e-6.
  4. evidence/{dedupe27,walls,axes}.tsv, logs/extract09_summary.json, and the corpus (and the
     Ticket 331 input) md5 must be unchanged.

Exit codes: 0 ok, 2 missing input, 3 corpus changed, 4 a verification failed.
"""
import argparse
import json
import os
import subprocess
import sys
import traceback
from multiprocessing import Pool

import numpy as np
from scipy.spatial import cKDTree

TAB = chr(9)
NL = chr(10)

SHIP = "/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-ship"
WORK = os.path.join(SHIP, "work")
IMPL = os.path.join(WORK, "impl_t03")
SHIP_OWN = os.path.join(SHIP, "out", "axes03_own")
T08 = "/data/gpfs/projects/punim2657/SfSpp/runs/20261125-1218_fc5d0ac_t08-ship"
T08_WORK = os.path.join(T08, "work", "t08")
T08_WALLS = os.path.join(T08, "evidence", "walls.tsv")
T08_AX_POT = os.path.join(T08, "out", "axes08_own_dedup")
T08_AX_JUG = os.path.join(T08, "out", "axes08_juglet_def3x_dedup")
T331 = "/data/gpfs/projects/punim2657/SfSpp/runs/20261112-0218_b1e1580_t331-large"
JUG_ROWS = 3.0
JUG_STEMS = ["Juglet_Piece_%d" % i for i in range(1, 10)]
EXCLUDED_BY_PAPER = ["Pot_F_Piece_07", "Pot_I_Piece_28", "Pot_I_Piece_29",
                     "Pot_I_Piece_30", "Pot_J_Piece_12"]
POT_COUNTS = {"A": 8, "B": 9, "C": 4, "D": 29, "E": 31, "F": 7, "G": 7, "H": 11,
              "I": 30, "J": 12}
CAVEATS = {
    "Pot_C_Piece_01": "interior edgeline measures the input (SfSpp_preprocessing/AGENTS.md)",
    "Pot_J_Piece_01": "interior edgeline measures the input (SfSpp_preprocessing/AGENTS.md)",
    "Pot_C_Piece_03": "Bl1 unscored, wrong reference (SfSpp_preprocessing/AGENTS.md)",
    "Pot_J_Piece_09": "unscored, wrong reference (SfSpp_preprocessing/AGENTS.md)",
}
DEDUPE_COLS = ["stem", "pot", "face", "mode", "in_rows", "out_rows", "improved_rows",
               "dups_skipped", "appended", "normal_maxdiff"]
WALL_COLS = ["stem", "pot", "face", "points", "duplicate_xyz", "bl_points",
             "nn_med_mm_vs_t08", "nn_p90_mm_vs_t08", "xyz_sha256", "normals_sha256"]
AXES_COLS = ["stem", "pot", "in_141_gt", "excluded_by_paper", "k_t08", "k_t09",
             "axes_sha256_t09", "effective_stride", "drawn_points", "rank1_deg_t08",
             "rank1_deg_t09", "best_deg_t08", "best_deg_t09", "d_gt_to_est_mm_t09",
             "d_est_to_gt_mm_t09", "is_base_t09"]

os.environ.setdefault("SFS_IMPL", IMPL)
for _p in (WORK, IMPL, os.path.join(IMPL, "scripts"), T08_WORK):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

import t03_lib as dl  # noqa: E402
import t03_extract as tx  # noqa: E402
import extract08 as e8  # noqa: E402
from sfs_axes.io_axes import direction_angle_deg  # noqa: E402

BASE_OWN = dict(dl.OWN)
BASE_JUG = dl.JUG_GEOM
EXPECT = {}
RUN = ""
POT_OUT = ""
JUG_OUT = ""
T09_OWN = {}
T09_JUG = ""


def log(msg):
    print("[extract09] " + msg, flush=True)


def read_tsv(path):
    rows = []
    with open(path) as fh:
        head = fh.readline().rstrip(NL).split(TAB)
        for line in fh:
            t = line.rstrip(NL).split(TAB)
            if len(t) != len(head):
                continue
            rows.append(dict(zip(head, t)))
    return rows


def write_tsv(path, cols, rows):
    with open(path, "w") as fh:
        fh.write(TAB.join(cols) + NL)
        for r in rows:
            fh.write(TAB.join(str(r.get(c, "")) for c in cols) + NL)


def count_rows(path):
    n = 0
    with open(path) as fh:
        for line in fh:
            if line.strip():
                n += 1
    return n


def nn_stats(xyz, scale):
    X = np.ascontiguousarray(np.asarray(xyz, dtype=float).T)
    if X.shape[0] < 3:
        return (float("nan"), float("nan"))
    d, _ = cKDTree(X).query(X, k=2)
    d = d[:, 1] * float(scale)
    return (float(np.median(d)), float(np.percentile(d, 90)))


def parse_dedupe(path):
    rows = []
    if not os.path.isfile(path):
        return rows
    with open(path, errors="replace") as fh:
        for line in fh:
            if "[DEDUPE-27]" not in line:
                continue
            rec = {}
            for tok in line.split("[DEDUPE-27]", 1)[1].split():
                if "=" in tok:
                    k, v = tok.split("=", 1)
                    rec[k] = v
            rows.append(rec)
    return rows


def angles(vt, gt):
    v = np.atleast_2d(np.asarray(vt, dtype=float))
    return [float(direction_angle_deg(v[0:3, k], gt[0:3])) for k in range(v.shape[1])]


def select_no_gt(stem):
    """The frozen SHIP selector exactly as t03_extract.job runs it, for the five
    paper-excluded pieces that have no Ground Truth axis: the .xyz is written the same way,
    only the GT-relative metrics are omitted (they are blank in the evidence table)."""
    C0, C1, C = dl.walls(stem, "own")
    reps, sizes, V, st, nd = dl.draw_pool(C, seeds=10, step=10)
    out = tx.select_lines(reps, sizes, C0, C1, C, 6, None)
    is_jug = dl.is_jug(stem)
    path = os.path.join(JUG_OUT if is_jug else POT_OUT, stem + "_Axis.xyz")
    rec = dict(stem=stem, pot=dl.pot_of(stem), is_juglet=is_jug, n=int(C.shape[1]),
               step=int(st), no_gt=True)
    if out is None or out[0].shape[1] == 0:
        open(path, "w").close()
        rec.update(K=0, error="no line")
        return rec
    lines, costs = out
    tx.write_lines(path, lines)
    rec.update(K=int(lines.shape[1]),
               written_pos=[round(float(x), 3) for x in lines[3:6, 0]],
               dir_z=round(float(lines[5, 0]), 6),
               is_base=bool(tx.is_base_fragment(C, lines[:, 0])))
    return rec


def has_gt(stem):
    """Seven own-surface pot pieces have no reference axis: the five outside the paper's
    set (Pot_F_Piece_07, Pot_I_Piece_28/29/30, Pot_J_Piece_12) plus Pot_D_Piece_22,
    Pot_F_Piece_06 and Pot_J_Piece_09 (unscored, wrong reference).  The Juglet's reference
    lives in Dataset/Juglet_GT in the physical 1x frame."""
    if dl.is_jug(stem):
        return os.path.isfile(os.path.join(dl.JUG_GT, stem + "_Axis.xyz"))
    return os.path.isfile(os.path.join(dl.GT_DIR, stem + "_Axis.xyz"))


def worker(stem):
    try:
        is_jug = dl.is_jug(stem)
        pot = "JUG" if is_jug else dl.pot_of(stem)
        scale = 1.0 / JUG_ROWS if is_jug else 1.0
        base_dir = BASE_JUG if is_jug else BASE_OWN[pot]
        t09_dir = T09_JUG if is_jug else T09_OWN[pot]
        base_rows, wall_rows = [], []
        for f in (0, 1):
            Wb = dl.rb.load_wall(os.path.join(base_dir, stem + ".S%d" % f))
            Wd = np.ascontiguousarray(Wb[:, e8.dedup_indices(Wb[0:3, :])])
            bmed, bp90 = nn_stats(Wd[0:3, :], scale)
            bsha = e8.matrix_sha(Wd[0:3, :])
            bn = int(Wd.shape[1])
            chk = EXPECT.get((stem, f))
            base_rows.append(dict(
                stem=stem, pot=pot, face=f, points=bn, xyz_sha256=bsha,
                t08_points=(chk["points"] if chk else ""),
                t08_xyz_sha256=(chk["xyz_sha256"] if chk else ""),
                match=bool(chk and int(chk["points"]) == bn
                           and chk["xyz_sha256"] == bsha),
                nn_med=bmed, nn_p90=bp90))
            Wt = dl.rb.load_wall(os.path.join(t09_dir, stem + ".S%d" % f))
            tmed, tp90 = nn_stats(Wt[0:3, :], scale)
            wall_rows.append(dict(
                stem=stem, pot=pot, face=f, points=int(Wt.shape[1]),
                duplicate_xyz=int(e8.duplicate_count(Wt[0:3, :])),
                bl_points=count_rows(os.path.join(t09_dir, stem + ".Bl%d" % f)),
                nn_med_mm_vs_t08=round(bmed, 6), nn_p90_mm_vs_t08=round(bp90, 6),
                nn_med_t09=round(tmed, 6), nn_p90_t09=round(tp90, 6),
                xyz_sha256=e8.matrix_sha(Wt[0:3, :]),
                normals_sha256=e8.matrix_sha(Wt[3:6, :])))
        vessel = "Juglet_def3x" if is_jug else "Pot_%s" % pot
        d27 = parse_dedupe(os.path.join(RUN, "out", vessel, "pieces", stem, "mesh.log"))
        if not has_gt(stem):
            rec = select_no_gt(stem)
        else:
            rec = tx.job((stem, "own", POT_OUT, JUG_OUT, None))
        return dict(stem=stem, pot=pot, base=base_rows, walls=wall_rows, d27=d27,
                    axes=rec)
    except Exception as exc:
        traceback.print_exc()
        return dict(stem=stem, error=str(exc))


def main():
    global RUN, POT_OUT, JUG_OUT, T09_OWN, T09_JUG, EXPECT
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--jobs", type=int, default=12)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    RUN = os.path.abspath(a.run)
    EVID = os.path.join(RUN, "evidence")
    LOGS = os.path.join(RUN, "logs")
    POT_OUT = os.path.join(RUN, "out", "axes09_own_regen")
    JUG_OUT = os.path.join(RUN, "out", "axes09_juglet_def3x_regen")
    for d in (EVID, LOGS, POT_OUT, JUG_OUT):
        os.makedirs(d, exist_ok=True)
    for p in (T08_WALLS, T08_AX_POT, T08_AX_JUG, SHIP_OWN):
        if not os.path.exists(p):
            sys.exit("[extract09] FAIL missing input " + p)
    for r in read_tsv(T08_WALLS):
        EXPECT[(r["stem"], int(r["face"]))] = r
    log("ticket 08 baseline walls in evidence/walls.tsv: %d" % len(EXPECT))
    if len(EXPECT) != 314:
        sys.exit("[extract09] FAIL expected 314 baseline wall rows, saw %d" % len(EXPECT))
    pot_stems = sorted(f[:-len("_Axis.xyz")] for f in os.listdir(SHIP_OWN)
                       if f.endswith("_Axis.xyz"))
    per_pot = {}
    for s in pot_stems:
        per_pot[dl.pot_of(s)] = per_pot.get(dl.pot_of(s), 0) + 1
    log("frozen SHIP own stems: %d pot pieces %r" % (len(pot_stems), sorted(per_pot.items())))
    if len(pot_stems) != 148 or per_pot != POT_COUNTS:
        sys.exit("[extract09] FAIL pot piece counts differ from the ticket (148 / %r)" % POT_COUNTS)
    T09_OWN = {p: os.path.join(RUN, "out", "Pot_%s" % p, "geom") for p in "ABCDEFGHIJ"}
    T09_JUG = os.path.join(RUN, "out", "Juglet_def3x", "geom")
    for d in list(T09_OWN.values()) + [T09_JUG]:
        if not os.path.isdir(d):
            sys.exit("[extract09] FAIL missing regenerated geom dir " + d)
    dl.OWN = dict(T09_OWN)
    dl.JUG_GEOM = T09_JUG
    gt_set = set(f[:-len("_Axis.xyz")] for f in os.listdir(dl.GT_DIR)
                 if f.endswith("_Axis.xyz"))
    log("GT stems: %d" % len(gt_set))
    pieces = pot_stems + JUG_STEMS
    if a.limit:
        pieces = pieces[:a.limit]
    log("pieces to process: %d (jobs=%d)" % (len(pieces), a.jobs))
    with Pool(a.jobs) as pool:
        rows = pool.map(worker, pieces, chunksize=1)
    bad = [r for r in rows if "error" in r]
    for r in bad[:20]:
        log("FAILED " + r["stem"] + ": " + r["error"])
    if bad:
        sys.exit("[extract09] FAIL %d pieces errored" % len(bad))

    base_rows, wall_rows, dedupe_rows, axes_rows = [], [], [], []
    problems = []
    for r in rows:
        stem, pot = r["stem"], r["pot"]
        base_rows.extend(r["base"])
        wall_rows.extend(r["walls"])
        for d in r["d27"]:
            dedupe_rows.append(dict(stem=stem, pot=pot, face=d.get("surface", ""),
                                    mode=d.get("mode", ""), in_rows=d.get("in", ""),
                                    out_rows=d.get("out", ""),
                                    improved_rows=d.get("improved_rows", ""),
                                    dups_skipped=d.get("dups_skipped", ""),
                                    appended=d.get("appended", ""),
                                    normal_maxdiff=d.get("normal_maxdiff", "")))
        if len(r["d27"]) != 2:
            problems.append("%s: %d [DEDUPE-27] lines (expected 2)" % (stem, len(r["d27"])))
        for d in r["d27"]:
            if d.get("mode") != "off":
                problems.append("%s face %s: mode=%s" % (stem, d.get("surface"), d.get("mode")))
            try:
                if int(d.get("in", "-1")) != int(d.get("out", "-2")):
                    problems.append("%s face %s: in=%s out=%s" % (stem, d.get("surface"),
                                                                 d.get("in"), d.get("out")))
                nmd = float(d.get("normal_maxdiff", "nan"))
                if not (0.0 <= nmd <= 1e-6):
                    problems.append("%s face %s: normal_maxdiff=%s" % (stem, d.get("surface"),
                                                                      d.get("normal_maxdiff")))
            except ValueError:
                problems.append("%s face %s: unparsable dedupe line %r"
                                % (stem, d.get("surface"), d))
        ax = r["axes"]
        if "error" in ax:
            problems.append("%s: extraction error %s" % (stem, ax["error"]))
        apath = os.path.join(JUG_OUT if dl.is_jug(stem) else POT_OUT, stem + "_Axis.xyz")
        tpath = os.path.join(T08_AX_JUG if dl.is_jug(stem) else T08_AX_POT,
                             stem + "_Axis.xyz")
        k09 = ax.get("K", 0)
        if k09 != count_rows(apath):
            problems.append("%s: written rows %d != K %d" % (stem, count_rows(apath), k09))
        k08 = count_rows(tpath) if os.path.isfile(tpath) else 0
        gt = dl.gt_axis(stem) if has_gt(stem) else None
        rec = dict(stem=stem, pot="JUG" if dl.is_jug(stem) else pot,
                   in_141_gt=int(stem in gt_set),
                   excluded_by_paper=int(stem in EXCLUDED_BY_PAPER),
                   k_t08=k08, k_t09=k09,
                   axes_sha256_t09=e8.sha256_file(apath), effective_stride=ax.get("step", ""),
                   drawn_points=(ax.get("n", 0) // ax.get("step", 1)) if ax.get("step") else 0,
                   rank1_deg_t09=ax.get("rank0_deg", ""), best_deg_t09=ax.get("best3_deg", ""),
                   d_gt_to_est_mm_t09=ax.get("d_gt_to_est", ""),
                   d_est_to_gt_mm_t09=ax.get("d_est_to_gt", ""),
                   is_base_t09=int(bool(ax.get("is_base", False))))
        if k08 and gt is not None:
            V8 = e8.read_axis_rows(tpath)
            ang = angles(V8, gt)
            rec["rank1_deg_t08"] = round(ang[0], 4)
            rec["best_deg_t08"] = round(min(ang[:3]), 4)
        else:
            rec["rank1_deg_t08"] = ""
            rec["best_deg_t08"] = ""
        if dl.is_jug(stem):
            pos = ax.get("written_pos") or [0.0, 0.0, 0.0]
            if stem == "Juglet_Piece_1":
                rec["juglet_piece1_abs_pos"] = round(float(np.linalg.norm(pos)), 3)
                if rec["juglet_piece1_abs_pos"] <= 300.0:
                    problems.append("Juglet_Piece_1 |position|=%.3f not > 300 (native 3x guard)"
                                    % rec["juglet_piece1_abs_pos"])
            if stem == "Juglet_Piece_7":
                dz = ax.get("dir_z", "")
                if int(bool(ax.get("is_base", False))) != 1:
                    problems.append("Juglet_Piece_7 is not the base line")
                if not (float(dz) < 0.0):
                    problems.append("Juglet_Piece_7 dir_z=%s not negative" % dz)
        axes_rows.append(rec)
    jug_bases = [r["stem"] for r in rows if dl.is_jug(r["stem"])
                 and bool(r["axes"].get("is_base", False))]
    log("juglet base pieces: %r" % (jug_bases,))
    if jug_bases != ["Juglet_Piece_7"]:
        problems.append("juglet is_base pieces %r (expected exactly ['Juglet_Piece_7'])"
                        % (jug_bases,))

    mism = [b for b in base_rows if not b["match"]]
    log("baseline walls matching ticket 08 evidence: %d/%d"
        % (len(base_rows) - len(mism), len(base_rows)))
    if mism:
        for b in mism[:10]:
            problems.append("baseline mismatch %s face %s: points %s vs %s"
                            % (b["stem"], b["face"], b["points"], b["t08_points"]))
    dup_walls = [w for w in wall_rows if int(w["duplicate_xyz"]) != 0]
    log("regenerated walls with duplicate_xyz != 0: %d" % len(dup_walls))
    for w in dup_walls[:10]:
        problems.append("duplicate xyz on %s face %s: %s"
                        % (w["stem"], w["face"], w["duplicate_xyz"]))
    empty_bl = [w for w in wall_rows if int(w["bl_points"]) <= 0]
    for w in empty_bl[:10]:
        problems.append("empty breakline on %s face %s" % (w["stem"], w["face"]))
    if len(wall_rows) != 314:
        problems.append("wall rows %d (expected 314)" % len(wall_rows))
    if len(dedupe_rows) != 314:
        problems.append("dedupe rows %d (expected 314)" % len(dedupe_rows))
    if len(axes_rows) != 157:
        problems.append("axes rows %d (expected 157)" % len(axes_rows))
    n_gt = sum(r["in_141_gt"] for r in axes_rows)
    if n_gt != 141:
        problems.append("axes rows with GT %d (expected 141)" % n_gt)
    n_excl = sum(r["excluded_by_paper"] for r in axes_rows)
    if n_excl != 5:
        problems.append("paper-excluded rows %d (expected 5)" % n_excl)

    base_rows.sort(key=lambda r: (r["stem"], r["face"]))
    wall_rows.sort(key=lambda r: (r["stem"], r["face"]))
    dedupe_rows.sort(key=lambda r: (r["stem"], r["face"]))
    axes_rows.sort(key=lambda r: r["stem"])
    write_tsv(os.path.join(EVID, "dedupe27.tsv"), DEDUPE_COLS, dedupe_rows)
    write_tsv(os.path.join(EVID, "walls.tsv"), WALL_COLS, wall_rows)
    write_tsv(os.path.join(EVID, "axes.tsv"), AXES_COLS, axes_rows)
    write_tsv(os.path.join(EVID, "walls_nn_detail.tsv"),
              ["stem", "pot", "face", "points", "nn_med_mm_t09", "nn_p90_mm_t09",
               "nn_med_mm_t08", "nn_p90_mm_t08", "points_t08"],
              [dict(stem=w["stem"], pot=w["pot"], face=w["face"], points=w["points"],
                    nn_med_mm_t09=w["nn_med_t09"], nn_p90_mm_t09=w["nn_p90_t09"],
                    nn_med_mm_t08=w["nn_med_mm_vs_t08"], nn_p90_mm_t08=w["nn_p90_mm_vs_t08"],
                    points_t08=int(b["points"]))
               for w, b in zip(wall_rows, sorted(base_rows, key=lambda r: (r["stem"], r["face"])))])

    nn09 = [float(w["nn_med_t09"]) for w in wall_rows]
    nn08 = [float(w["nn_med_mm_vs_t08"]) for w in wall_rows]
    summary = dict(
        run=RUN, pot_stems=len(pot_stems), juglet_stems=len(JUG_STEMS),
        pieces=len(pieces), walls=len(wall_rows), dedupe_rows=len(dedupe_rows),
        axes_rows=len(axes_rows), axes_with_gt=n_gt, paper_excluded=n_excl,
        duplicate_xyz_total=sum(int(w["duplicate_xyz"]) for w in wall_rows),
        baseline_walls_matching_t08=len(base_rows) - len(mism),
        nn_med_mm_t09_median=round(float(np.median(nn09)), 6),
        nn_med_mm_t08_median=round(float(np.median(nn08)), 6),
        nn_p90_mm_t09_median=round(float(np.median([float(w["nn_p90_t09"]) for w in wall_rows])), 6),
        nn_p90_mm_t08_median=round(float(np.median([float(w["nn_p90_mm_vs_t08"]) for w in wall_rows])), 6),
        juglet_bases=jug_bases, no_gt_stems=sorted(s for s in pot_stems if not has_gt(s)),
        problems=problems, caveats=CAVEATS,
        pot_counts=per_pot)
    with open(os.path.join(LOGS, "extract09_summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1)
    log("summary: " + json.dumps({k: summary[k] for k in
        ("pieces", "walls", "axes_rows", "axes_with_gt", "duplicate_xyz_total",
         "baseline_walls_matching_t08", "nn_med_mm_t09_median", "nn_med_mm_t08_median",
         "juglet_bases")}, sort_keys=True))

    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([WORK, IMPL, os.path.join(IMPL, "scripts")])
    env["SFS_IMPL"] = IMPL
    after = os.path.join(LOGS, "corpus_inputs_after.md5")
    subprocess.run([sys.executable, os.path.join(WORK, "corpus_md5_t03.py"),
                    "--out", after], check=True, env=env)
    before = os.path.join(LOGS, "corpus_inputs_before.md5")
    if not os.path.isfile(before):
        problems.append("no corpus_inputs_before.md5 from the build stage")
    else:
        with open(before) as f1, open(after) as f2:
            if f1.read() != f2.read():
                sys.exit("[extract09] FAIL corpus md5 changed (see %s vs %s)" % (before, after))
        log("corpus md5 unchanged: " + after)
    t331_before = os.path.join(LOGS, "t331_inputs_before.md5")
    if os.path.isfile(t331_before):
        out = subprocess.run("cd %s && sha256sum cloud_mesh/*.pcd mesh_large/*.obj | sort -k2"
                             % T331, shell=True, capture_output=True, text=True)
        t331_after = os.path.join(LOGS, "t331_inputs_after.md5")
        with open(t331_after, "w") as fh:
            fh.write(out.stdout)
        with open(t331_before) as f1, open(t331_after) as f2:
            if f1.read() != f2.read():
                sys.exit("[extract09] FAIL ticket 331 input md5 changed")
        log("ticket 331 input md5 unchanged")
    if problems:
        log("PROBLEMS (%d):" % len(problems))
        for p in problems[:40]:
            log("  " + p)
        sys.exit("[extract09] FAIL verification problems (%d)" % len(problems))
    log("T09-EXTRACT-OK")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
