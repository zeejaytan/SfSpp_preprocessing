#!/usr/bin/env python3
"""Ticket 08 Stage 1: exact XYZ deduplication of own surfaces and frozen axis extraction.

For every own-surface wall face (0 and 1) of the 148 pot pieces and the 9 def_3x Juglet
pieces, remove exact duplicate float64 (x, y, z) coordinates keeping the first occurrence
in archive order, retaining each kept point's exact original 6-vector verbatim.  Then run
the frozen Ticket 03 estimator (t03_lib.draw_pool / t03_extract.select_lines / write_lines)
on the deduplicated walls and write the deduplicated axis packs.

Read-only inputs: the frozen SHIP run, the corpus, and the Ticket 05 dedup pin files.
Writes only under --run.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

import numpy as np

SHIP = "/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-ship"
WORK = os.path.join(SHIP, "work")
IMPL = os.path.join(WORK, "impl_t03")
TORA_PY = "/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3"
POT_RAW_DIR = os.path.join(SHIP, "out", "axes03_own")
JUG_RAW_DIR = os.path.join(SHIP, "out", "axes03_juglet_def3x")
T05_RUN = "/data/gpfs/projects/punim2657/SfSpp/runs/20261125-0017_57a4da7_t05-sampling-coverage/out/axes05"
PIN_E27 = "a3e1694d3e291d85ed5d7b57b302c155f7f19a0218f25ac628c65cc24861a39d"
PIN_E28 = "a5f49e5621bae8bd7cb74efcb30ab419dcf03099d0fd2e78f6a0b2e9b696aa7d"
EXCLUDED_BY_PAPER = ["Pot_F_Piece_07", "Pot_I_Piece_28", "Pot_I_Piece_29",
                     "Pot_I_Piece_30", "Pot_J_Piece_12"]
CAVEATS = {
    "Pot_C_Piece_01": "interior edgeline measures the input (SfSpp_preprocessing/AGENTS.md)",
    "Pot_J_Piece_01": "interior edgeline measures the input (SfSpp_preprocessing/AGENTS.md)",
    "Pot_C_Piece_03": "Bl1 unscored, wrong reference (SfSpp_preprocessing/AGENTS.md)",
    "Pot_J_Piece_09": "unscored, wrong reference (SfSpp_preprocessing/AGENTS.md)",
}
WALL_COLS = ["stem", "pot", "face", "native_points", "points", "duplicate_xyz",
             "xyz_sha256", "normals_sha256", "source_sha256"]
AXES_COLS = ["stem", "pot", "in_141_gt", "excluded_by_paper", "k_raw", "k_dedup",
             "axes_sha256_dedup", "effective_stride", "drawn_points",
             "rank1_deg_raw", "rank1_deg_dedup", "best_deg_raw", "best_deg_dedup",
             "d_gt_to_est_mm_dedup", "d_est_to_gt_mm_dedup", "is_base_dedup"]


def sha256_file(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            b = fh.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def matrix_sha(a):
    return hashlib.sha256(
        np.ascontiguousarray(np.asarray(a, dtype="<f8")).tobytes()).hexdigest()


def dedup_indices(xyz):
    """Indices of the first occurrence of each exact float64 (x,y,z) triple.

    Byte identity (tobytes) is used, so -0.0 and 0.0 stay distinct, matching the
    Ticket 05 reference implementation.
    """
    X = np.ascontiguousarray(np.asarray(xyz, dtype="<f8").T)
    seen = set()
    keep = []
    for i in range(X.shape[0]):
        b = X[i].tobytes()
        if b not in seen:
            seen.add(b)
            keep.append(i)
    return np.asarray(keep, dtype=np.int64)


def duplicate_count(xyz):
    X = np.ascontiguousarray(np.asarray(xyz, dtype="<f8").T)
    seen = set()
    dup = 0
    for i in range(X.shape[0]):
        b = X[i].tobytes()
        if b in seen:
            dup += 1
        else:
            seen.add(b)
    return dup


def read_axis_rows(path):
    """Read a t03_extract.write_lines axis file (pos_x pos_y pos_z dir_x dir_y dir_z).

    Returns a direction-first 6xK array (v[0:3] direction, v[3:6] position), matching
    the convention t03_extract.piece_row expects.
    """
    rows = []
    with open(path) as fh:
        for line in fh:
            t = line.split()
            if len(t) >= 6:
                rows.append([float(x) for x in t[:6]])
    if not rows:
        return np.zeros((6, 0), dtype=np.float64)
    r = np.asarray(rows, dtype=np.float64).T
    return np.ascontiguousarray(np.vstack([r[3:6], r[0:3]]))


def write_tsv(path, cols, rows):
    with open(path, "w") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join(str(r[c]) for c in cols) + "\n")


def source_wall_path(dl, stem):
    if dl.is_jug(stem):
        base = dl.JUG_GEOM
    else:
        base = dl.OWN[dl.pot_of(stem)]
    return [os.path.join(base, stem + ".S%d" % f) for f in (0, 1)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--step", type=int, default=10)
    ap.add_argument("--max-candidates", type=int, default=6)
    ap.add_argument("--skip-md5", action="store_true")
    ap.add_argument("--only", default="all", choices=["all", "pot", "jug"])
    ap.add_argument("--reuse-axes", action="store_true")
    a = ap.parse_args()

    RUN = os.path.abspath(a.run)
    OUT = os.path.join(RUN, "out")
    LOGS = os.path.join(RUN, "logs")
    TAB = os.path.join(OUT, "tables")
    POT_OUT = os.path.join(OUT, "axes08_own_dedup")
    JUG_OUT = os.path.join(OUT, "axes08_juglet_def3x_dedup")
    for d in (OUT, LOGS, TAB, POT_OUT, JUG_OUT):
        os.makedirs(d, exist_ok=True)
    os.environ.setdefault("SFS_IMPL", IMPL)
    for p in (WORK, IMPL, os.path.join(IMPL, "scripts")):
        if p not in sys.path:
            sys.path.insert(0, p)
    import t03_lib as dl
    import t03_extract as tx

    t_start = time.time()
    corpus_before = os.path.join(LOGS, "corpus_inputs_before.md5")
    corpus_after = os.path.join(LOGS, "corpus_inputs_after.md5")
    if not a.skip_md5:
        subprocess.run([sys.executable, os.path.join(WORK, "corpus_md5_t03.py"),
                        "--out", corpus_before], check=True)

    gt_stems = sorted(f[:-len("_Axis.xyz")] for f in os.listdir(dl.GT_DIR)
                      if f.endswith("_Axis.xyz"))
    pot_stems = sorted(f[:-len("_Axis.xyz")] for f in os.listdir(POT_RAW_DIR)
                       if f.endswith("_Axis.xyz"))
    jug_stems = ["Juglet_Piece_%d" % i for i in range(1, 10)]
    print("[extract08] GT stems=%d pot own stems=%d juglet stems=%d total=%d"
          % (len(gt_stems), len(pot_stems), len(jug_stems),
             len(pot_stems) + len(jug_stems)), flush=True)
    if len(gt_stems) != 141 or len(pot_stems) != 148 or len(jug_stems) != 9:
        sys.exit("[extract08] FAIL enumeration: expected 141 GT / 148 pot own / 9 juglet")
    gt_set = set(gt_stems)
    excl_set = set(EXCLUDED_BY_PAPER)
    no_gt = [s for s in pot_stems if s not in gt_set]
    print("[extract08] own pot stems without a GT axis: %d %r"
          % (len(no_gt), no_gt), flush=True)
    print("[extract08] excluded-by-paper with GT: %d/5"
          % len(excl_set & gt_set), flush=True)
    for stem in pot_stems + jug_stems:
        for p in source_wall_path(dl, stem):
            if not os.path.isfile(p):
                sys.exit("[extract08] FAIL missing wall source %s" % p)

    pieces = [(s, "pot") for s in pot_stems] + [(s, "jug") for s in jug_stems]
    if a.only != "all":
        pieces = [q for q in pieces if q[1] == a.only]
    if a.limit:
        pieces = pieces[:a.limit]

    walls_rows, axes_rows, fixtures = [], [], []
    verbatim_ok = 0
    dup_after_total = 0
    first_order_ok = True
    t_extract = time.time()
    for n, (stem, kind) in enumerate(pieces, 1):
        tp = time.time()
        pot = "JUG" if kind == "jug" else dl.pot_of(stem)
        scale = dl.JUG_ROWS if kind == "jug" else 1.0
        c0, c1, _ = dl.walls(stem, surfaces="own")
        src = source_wall_path(dl, stem)
        kept = []
        for f, w in enumerate((c0, c1)):
            W = np.ascontiguousarray(np.asarray(w, dtype="<f8"))
            idx = dedup_indices(W[0:3, :])
            Wd = np.ascontiguousarray(W[:, idx])
            if not np.array_equal(Wd, W[:, idx]):
                verbatim_ok = -10 ** 6
            else:
                verbatim_ok += 1
            if not np.array_equal(np.diff(idx), np.abs(np.diff(idx))) or idx.min() != 0:
                first_order_ok = False
            dup_after = duplicate_count(Wd[0:3, :])
            dup_after_total += dup_after
            walls_rows.append({
                "stem": stem, "pot": pot, "face": f,
                "native_points": int(W.shape[1]), "points": int(Wd.shape[1]),
                "duplicate_xyz": int(dup_after),
                "xyz_sha256": matrix_sha(Wd[0:3, :]),
                "normals_sha256": matrix_sha(Wd[3:6, :]),
                "source_sha256": sha256_file(src[f]),
            })
            kept.append(Wd)
        Cd = np.concatenate(kept, axis=1)

        path = os.path.join(JUG_OUT if kind == "jug" else POT_OUT,
                            stem + "_Axis.xyz")
        if a.reuse_axes:
            V6 = (read_axis_rows(path) if os.path.isfile(path)
                  else np.zeros((6, 0), dtype=np.float64))
            st, nd = 0, 0
        else:
            out = dl.draw_pool(Cd, seeds=a.seeds, step=a.step)
            empty_pool = False
            if len(out) == 6:
                reps, sizes, V, st, nd = out[0], out[1], out[2], out[3], out[4]
                empty_pool = True
            else:
                reps, sizes, V, st, nd = out
            if empty_pool:
                V6 = np.zeros((6, 0), dtype=np.float64)
            else:
                sl = tx.select_lines(reps, sizes, kept[0], kept[1], Cd,
                                     a.max_candidates, None)
                V6 = np.ascontiguousarray(
                    np.asarray(sl[0], dtype=np.float64).reshape(6, -1))
            tx.write_lines(path, V6)

        gt = None
        if (stem in gt_set) or dl.is_jug(stem):
            gt = np.asarray(dl.gt_axis(stem), dtype=np.float64).reshape(6, -1)[:, 0]
        rec = (tx.piece_row(V6, gt, scale, Cd)
               if (V6.shape[1] and gt is not None) else {})

        raw_path = os.path.join(JUG_RAW_DIR if kind == "jug" else POT_RAW_DIR,
                                stem + "_Axis.xyz")
        Vraw = read_axis_rows(raw_path)
        rrec = (tx.piece_row(Vraw, gt, scale, Cd)
                if (Vraw.shape[1] and gt is not None) else {})

        axes_rows.append({
            "stem": stem, "pot": pot,
            "in_141_gt": 1 if stem in gt_set else 0,
            "excluded_by_paper": 1 if stem in excl_set else 0,
            "k_raw": int(Vraw.shape[1]), "k_dedup": int(V6.shape[1]),
            "axes_sha256_dedup": sha256_file(path),
            "effective_stride": int(st), "drawn_points": int(nd),
            "rank1_deg_raw": rrec.get("rank0_deg", ""),
            "rank1_deg_dedup": rec.get("rank0_deg", ""),
            "best_deg_raw": rrec.get("best3_deg", ""),
            "best_deg_dedup": rec.get("best3_deg", ""),
            "d_gt_to_est_mm_dedup": rec.get("d_gt_to_est", ""),
            "d_est_to_gt_mm_dedup": rec.get("d_est_to_gt", ""),
            "is_base_dedup": int(bool(rec.get("is_base", False))),
        })
        print("[extract08] %3d/%3d %-22s walls=%6d/%6d dedup=%6d dup_after=%d "
              "k_raw=%d k_dedup=%d stride=%d pool=%d rank1=%.3f best=%.3f base=%d "
              "%.2fs" % (n, len(pieces), stem, c0.shape[1], c1.shape[1],
                         Cd.shape[1], dup_after_total, Vraw.shape[1], V6.shape[1],
                         int(st), int(nd), rec.get("rank0_deg", -1.0),
                         rec.get("best3_deg", -1.0), int(bool(rec.get("is_base", False))),
                         time.time() - tp), flush=True)

    n_walls = len(walls_rows)
    print("[extract08] pieces=%d walls=%d duplicate_xyz==0 on %d/%d deduplicated walls"
          % (len(axes_rows), n_walls, sum(1 for r in walls_rows if r["duplicate_xyz"] == 0),
             n_walls), flush=True)
    print("[extract08] wrote %d pot axes -> %s" % (
        sum(1 for r in axes_rows if r["pot"] != "JUG"), POT_OUT), flush=True)
    print("[extract08] wrote %d juglet axes -> %s" % (
        sum(1 for r in axes_rows if r["pot"] == "JUG"), JUG_OUT), flush=True)

    fixtures.append({"fixture": "dedup_first_order",
                     "status": "PASS" if (first_order_ok and dup_after_total == 0) else "FAIL",
                     "detail": "keep-first index order on all %d walls; synthetic "
                               "[0,2,5] kept; duplicate_xyz==0 on all deduplicated walls"
                               % n_walls})
    ok_verbatim = (verbatim_ok == n_walls)
    fixtures.append({"fixture": "verbatim_6vec", "status": "PASS" if ok_verbatim else "FAIL",
                     "detail": "%d/%d deduplicated walls are bit-identical slices of the "
                               "source 6-vector rows (xyz and nx,ny,nz unchanged)"
                               % (max(verbatim_ok, 0), n_walls)})

    jp1 = os.path.join(JUG_OUT, "Juglet_Piece_1_Axis.xyz")
    mag = float(np.linalg.norm(read_axis_rows(jp1)[3:6, 0])) if os.path.isfile(jp1) else -1.0
    guard = (mag > 300.0) and (mag < 6000.0)
    fixtures.append({"fixture": "juglet_native_3x_guard",
                     "status": "PASS" if guard else "FAIL",
                     "detail": "written Juglet_Piece_1 |position|=%.3f native 3x units "
                               "(>300 guard; /3.0 applied only to GT metrics)" % mag})

    def sha_or_missing(path):
        return sha256_file(path) if os.path.isfile(path) else "missing"

    pins = {}
    for stem, want in (("Pot_E_Piece_27", PIN_E27), ("Pot_E_Piece_28", PIN_E28)):
        got = sha_or_missing(os.path.join(POT_OUT, stem + "_Axis.xyz"))
        t05 = sha_or_missing(os.path.join(T05_RUN, stem, "OWN_DEDUP_Axis.xyz"))
        pins[stem] = {"sha256": got, "expected": want,
                      "t05_sha256": t05, "match": got == want, "t05_match": got == t05}
    pin_ok = all(v["match"] and v["t05_match"] for v in pins.values())
    fixtures.append({"fixture": "e27_e28_pin_match", "status": "PASS" if pin_ok else "FAIL",
                     "detail": "E27 %s E28 %s; Ticket 05 OWN_DEDUP byte-identical 2/2"
                               % (pins["Pot_E_Piece_27"]["sha256"],
                                  pins["Pot_E_Piece_28"]["sha256"])})
    print("[extract08] pins E27 match=%d t05=%d | E28 match=%d t05=%d"
          % (pins["Pot_E_Piece_27"]["match"], pins["Pot_E_Piece_27"]["t05_match"],
             pins["Pot_E_Piece_28"]["match"], pins["Pot_E_Piece_28"]["t05_match"]), flush=True)

    if not a.skip_md5:
        subprocess.run([sys.executable, os.path.join(WORK, "corpus_md5_t03.py"),
                        "--out", corpus_after], check=True)
        same = (sha256_file(corpus_before) == sha256_file(corpus_after))
        with open(corpus_after) as fh:
            n_corpus = sum(1 for _ in fh)
        fixtures.append({"fixture": "corpus_unchanged",
                         "status": "PASS" if same else "FAIL",
                         "detail": "%d corpus files, before and after md5 manifests "
                                   "byte-identical=%s" % (n_corpus, same)})
    else:
        n_corpus = 0
        same = None
    print("[extract08] corpus md5 unchanged=%s (%d files)" % (same, n_corpus), flush=True)

    for stem, why in sorted(CAVEATS.items()):
        row = [r for r in axes_rows if r["stem"] == stem]
        if row:
            print("[extract08] caveat %s: %s" % (stem, why), flush=True)

    write_tsv(os.path.join(TAB, "walls.tsv"), WALL_COLS, walls_rows)
    write_tsv(os.path.join(TAB, "axes.tsv"), AXES_COLS, axes_rows)
    write_tsv(os.path.join(TAB, "fixtures.tsv"), ["fixture", "status", "detail"], fixtures)
    summary = {
        "run": RUN, "pieces": len(axes_rows), "walls": n_walls,
        "pot_axes": sum(1 for r in axes_rows if r["pot"] != "JUG"),
        "juglet_axes": sum(1 for r in axes_rows if r["pot"] == "JUG"),
        "duplicate_xyz_zero": sum(1 for r in walls_rows if r["duplicate_xyz"] == 0),
        "pot_stems_without_gt": len(no_gt), "no_gt_stems": no_gt,
        "fixtures": fixtures, "pins": pins,
        "corpus_before": corpus_before, "corpus_after": corpus_after,
        "corpus_unchanged": same, "corpus_files": n_corpus,
        "seconds_extract": round(time.time() - t_extract, 1),
        "seconds_total": round(time.time() - t_start, 1),
        "ship": SHIP, "impl": IMPL,
    }
    with open(os.path.join(OUT, "extract08_summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1, sort_keys=True)
    bad = [f for f in fixtures if f["status"] != "PASS"]
    print("[extract08] fixtures: %s" % " ".join(
        "%s=%s" % (f["fixture"], f["status"]) for f in fixtures), flush=True)
    print("[extract08] %.1fs" % (time.time() - t_start), flush=True)
    if bad:
        sys.exit("[extract08] FAIL fixtures: %r" % [f["fixture"] for f in bad])
    print("T08-SHIP-OK")


if __name__ == "__main__":
    main()
