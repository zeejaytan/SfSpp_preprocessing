#!/usr/bin/env python3
"""Ticket 08 mechanical checks: tables, headers, row counts, pins, fixtures, jobs.

Runs on Spartan against a finished run directory:
    python check08.py --run <RUN>
    python check08.py --run <RUN> --expect-terminal
Exit 0 = every check passed; 1 = at least one FAIL (printed and saved in
<RUN>/evidence/check08.txt).
"""
import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys

RUNS = "/data/gpfs/projects/punim2657/SfSpp/runs"
T05 = RUNS + "/20261125-0017_57a4da7_t05-sampling-coverage"
POTS = list("ABCDEFGHIJ")
ARMS = ["MOR1", "MOR2", "K3R1", "K3R2"]
FLOORS = {"A": (8, 8, 15, 15), "B": (9, 9, 15, 15), "C": (4, 4, 5, 5),
          "D": (23, 28, 55, 69), "E": (31, 31, 62, 62), "F": (5, 5, 7, 7),
          "G": (7, 7, 10, 10), "H": (11, 11, 17, 17), "I": (25, 26, 59, 62),
          "J": (8, 11, 16, 21)}
EXCLUDED = {"Pot_F_Piece_07", "Pot_I_Piece_28", "Pot_I_Piece_29",
            "Pot_I_Piece_30", "Pot_J_Piece_12"}
PIN = {"Pot_E_Piece_27": "a3e1694d3e291d85ed5d7b57b302c155f7f19a0218f25ac628c65cc24861a39d",
       "Pot_E_Piece_28": "a5f49e5621bae8bd7cb74efcb30ab419dcf03099d0fd2e78f6a0b2e9b696aa7d"}
TERMINAL = {"COMPLETED", "FAILED", "CANCELLED", "TIMEOUT", "NODE_FAIL",
            "PREEMPTED", "OUT_OF_MEMORY", "BOOT_FAIL", "DEADLINE"}
WALLS_HEADER = ["stem", "pot", "face", "native_points", "points", "duplicate_xyz",
                "xyz_sha256", "normals_sha256", "source_sha256"]
AXES_HEADER = ["stem", "pot", "in_141_gt", "excluded_by_paper", "k_raw", "k_dedup",
               "axes_sha256_dedup", "effective_stride", "drawn_points",
               "rank1_deg_raw", "rank1_deg_dedup", "best_deg_raw", "best_deg_dedup",
               "d_gt_to_est_mm_dedup", "d_est_to_gt_mm_dedup", "is_base_dedup"]
POTS_E2E_HEADER = ["pot", "arm", "sherd", "sherd_den", "edge", "edge_den",
                   "sherd_floor", "edge_floor", "floor_pass", "t03_sherd",
                   "t03_edge", "delta_edge", "wall_secs"]
JUG_HEADER = ["arm", "cluster_len", "cluster_seated", "cluster_max_chamfer_mm",
              "cluster_members_le_050", "edges_strict", "edges_of", "p7_strict",
              "floor_pass"]
CMP_HEADER = ["vessel", "mor_best", "t03_own_raw_best", "t08_own_dedup_best",
              "reached_by", "floor_pass", "regression_vs_t03", "note"]

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print("%s %-34s %s" % ("PASS" if ok else "FAIL", name, detail), flush=True)
    return ok


def read_tsv(path):
    if not os.path.isfile(path):
        return None, []
    with open(path) as fh:
        lines = [ln.rstrip("\n") for ln in fh if ln.strip()]
    if not lines:
        return None, []
    head = lines[0].split("\t")
    return head, [dict(zip(head, ln.split("\t"))) for ln in lines[1:]]


def sha_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def axis_first_line(path):
    """First "pos_x pos_y pos_z dir_x dir_y dir_z" line of a write_lines pack."""
    if not os.path.isfile(path):
        return None
    with open(path) as fh:
        for line in fh:
            t = line.split()
            if len(t) >= 6:
                return [float(x) for x in t[:6]]
    return None


def sacct_state(job_id):
    try:
        r = subprocess.run(["sacct", "-j", str(job_id),
                            "--format=JobID,State,ExitCode", "-n", "-P"],
                           capture_output=True, text=True, timeout=120)
    except Exception:  # noqa: BLE001
        return "QUERY_FAILED", ""
    for line in r.stdout.splitlines():
        p = line.strip().split("|")
        if len(p) >= 3 and p[0] and "." not in p[0]:
            return p[1].split()[0].upper(), p[2]
    return "UNKNOWN", ""


def sacct_day_ids(stamp):
    """Every job named t08-* sacct knows on the run's day (jobs.tsv must list all)."""
    d0 = "%s-%s-%s" % (stamp[0:4], stamp[4:6], stamp[6:8])
    d1 = (datetime.date(int(d0[0:4]), int(d0[5:7]), int(d0[8:10]))
          + datetime.timedelta(days=1)).isoformat()
    try:
        r = subprocess.run(["sacct", "-u", os.environ.get("USER", ""),
                            "-S", d0, "-E", d1, "-n", "-P", "-X",
                            "--format=JobID,JobName%40,State,ExitCode"],
                           capture_output=True, text=True, timeout=300)
    except Exception:  # noqa: BLE001
        return None
    return {f.split("|")[0].split("_")[0] for f in r.stdout.splitlines()
            if len(f.split("|")) > 1 and f.split("|")[1].startswith("t08-")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--expect-terminal", action="store_true")
    a = ap.parse_args()
    run = os.path.normpath(a.run)
    ev = os.path.join(run, "evidence")
    t08 = os.path.join(run, "work", "t08")
    stamp = os.path.basename(run).split("_")[0]

    # 1. deliverables and syntax
    for f in ("extract08.py", "extract08.sbatch", "launch_e2e08.sh",
              "report08.py", "check08.py"):
        check("file:" + f, os.path.isfile(os.path.join(t08, f)),
              os.path.join(t08, f))
    for f in ("extract08.py", "report08.py", "check08.py"):
        r = subprocess.run([sys.executable, "-m", "py_compile", os.path.join(t08, f)],
                           capture_output=True, text=True)
        check("py_compile:" + f, r.returncode == 0, r.stderr.strip()[:200])
    for f in ("extract08.sbatch", "launch_e2e08.sh"):
        r = subprocess.run(["bash", "-n", os.path.join(t08, f)],
                           capture_output=True, text=True)
        check("bash_n:" + f, r.returncode == 0, r.stderr.strip()[:200])

    # 2. walls table
    head, wrows = read_tsv(os.path.join(ev, "walls.tsv"))
    check("walls_header", head == WALLS_HEADER, str(head))
    check("walls_rows_314", len(wrows) == 314, str(len(wrows)))
    pot_stems = {r["stem"] for r in wrows if not r["stem"].startswith("Juglet_")}
    jug_stems = {r["stem"] for r in wrows if r["stem"].startswith("Juglet_")}
    check("walls_pot_stems_148", len(pot_stems) == 148, str(len(pot_stems)))
    check("walls_jug_stems_9", jug_stems == {"Juglet_Piece_%d" % i for i in range(1, 10)},
          str(len(jug_stems)))
    check("walls_faces", sorted({r["face"] for r in wrows}) == ["0", "1"],
          str(sorted({r["face"] for r in wrows})))
    check("walls_pair_unique", len({(r["stem"], r["face"]) for r in wrows}) == 314)
    nz = [r["stem"] + ":" + r["face"] for r in wrows if r["duplicate_xyz"] != "0"]
    check("walls_duplicate_xyz_zero", not nz, str(nz[:4]))
    sh = [r["stem"] for r in wrows
          if len(r.get("xyz_sha256", "")) != 64 or len(r.get("normals_sha256", "")) != 64]
    check("walls_sha_columns", not sh, str(sh[:4]))

    # 3. axes table
    head, arows = read_tsv(os.path.join(ev, "axes.tsv"))
    check("axes_header", head == AXES_HEADER, str(head))
    check("axes_rows_157", len(arows) == 157, str(len(arows)))
    check("axes_in_141_gt", sum(int(r["in_141_gt"]) for r in arows if r["in_141_gt"].isdigit()) == 141,
          str(sum(int(r["in_141_gt"]) for r in arows if r["in_141_gt"].isdigit())))
    exc = {r["stem"] for r in arows if r.get("excluded_by_paper") == "1"}
    check("axes_excluded_5", exc == EXCLUDED, str(sorted(exc)))
    amap = {r["stem"]: r for r in arows}
    ok_pin = True
    for stem, want in PIN.items():
        got = amap.get(stem, {}).get("axes_sha256_dedup", "")
        ok_pin = ok_pin and got == want and amap.get(stem, {}).get("k_dedup") == "2"
    check("axes_e27_e28_pins", ok_pin,
          " ".join("%s=%s" % (s, amap.get(s, {}).get("axes_sha256_dedup", "NA")[:12])
                   for s in PIN))
    jug = [r for r in arows if r["stem"].startswith("Juglet_")]
    base = [r["stem"] for r in jug if r.get("is_base_dedup") == "1"]
    check("axes_juglet_base_sole_p7", base == ["Juglet_Piece_7"], str(base))
    check("axes_k_dedup_positive",
          all(int(r["k_dedup"]) >= 1 for r in arows if r["k_dedup"].isdigit()),
          str([(r["stem"], r["k_dedup"]) for r in arows if not r["k_dedup"].isdigit()][:3]))
    jd = os.path.join(run, "out", "axes08_juglet_def3x_dedup")
    v1 = axis_first_line(os.path.join(jd, "Juglet_Piece_1_Axis.xyz"))
    mag = (float(sum(x * x for x in v1[0:3])) ** 0.5) if v1 else -1.0
    check("axes_juglet_p1_native_3x", v1 is not None and mag > 300.0,
          "|pos|=%.3f native 3x units" % mag)
    v7 = axis_first_line(os.path.join(jd, "Juglet_Piece_7_Axis.xyz"))
    check("axes_juglet_p7_dir_z_neg", v7 is not None and v7[5] < 0.0,
          "dir_z=%.6f" % (v7[5] if v7 else float("nan")))

    # 4. fixtures
    head, frows = read_tsv(os.path.join(ev, "fixtures.tsv"))
    names = {r["fixture"]: r["status"] for r in frows}
    want = {"dedup_first_order", "verbatim_6vec", "juglet_native_3x_guard",
            "e27_e28_pin_match"}
    check("fixtures_header", head == ["fixture", "status", "detail"], str(head))
    check("fixtures_all_pass",
          want <= set(names) and all(v == "PASS" for v in names.values()), str(names))

    # 5. pots_e2e
    head, prows = read_tsv(os.path.join(ev, "pots_e2e.tsv"))
    check("pots_header", head == POTS_E2E_HEADER, str(head))
    check("pots_rows_40", len(prows) == 40, str(len(prows)))
    want_arms = {(P, P + "_" + a) for P in POTS for a in ARMS}
    got_arms = {(r["pot"], r["arm"]) for r in prows}
    check("pots_arms_40", got_arms == want_arms, str(sorted(want_arms - got_arms)[:4]))
    bad_floor = []
    for r in prows:
        fl = FLOORS[r["pot"]]
        exp = 1 if (int(r["sherd"]) >= fl[0] and int(r["edge"]) >= fl[2]) else 0
        if int(r["floor_pass"]) != exp:
            bad_floor.append(r["arm"])
    check("pots_floor_recompute", not bad_floor, str(bad_floor[:4]))
    bad_delta = [r["arm"] for r in prows
                 if r["delta_edge"] not in ("NA", "")
                 and int(r["delta_edge"]) != int(r["edge"]) - int(r["t03_edge"])]
    check("pots_delta_edge", not bad_delta, str(bad_delta[:4]))

    # 6. juglet_e2e
    head, jrows = read_tsv(os.path.join(ev, "juglet_e2e.tsv"))
    check("juglet_header", head == JUG_HEADER, str(head))
    check("juglet_rows_4", len(jrows) == 4
          and sorted(r["arm"] for r in jrows)
          == ["juglet_own_xy_r%d" % i for i in range(1, 5)],
          str([r["arm"] for r in jrows]))
    check("juglet_floor_consistent",
          all((int(r["floor_pass"]) == 1) == (int(r["cluster_seated"]) == 9
                                             and int(r["cluster_len"]) == 9
                                             and float(r["cluster_max_chamfer_mm"]) <= 0.50)
              for r in jrows), "floor <= 0.50 mm on 9/9")

    # 7. comparison
    head, crows = read_tsv(os.path.join(ev, "comparison_vs_t03.tsv"))
    check("cmp_header", head == CMP_HEADER, str(head))
    check("cmp_rows_11", len(crows) == 11
          and {r["vessel"] for r in crows} == set(POTS) | {"JUGLET"},
          str(len(crows)))
    check("cmp_regression_values",
          {r["regression_vs_t03"] for r in crows}
          <= {"none", "improved", "regressed", "improved_sherd", "regressed_sherd", "NA"},
          str(sorted({r["regression_vs_t03"] for r in crows})))

    # 8. sources
    head, srows = read_tsv(os.path.join(ev, "sources.tsv"))
    check("sources_header", head == ["kind", "path", "sha256", "bytes", "detail"], str(head))
    kinds = {r["kind"] for r in srows}
    check("sources_kinds",
          {"t08_script", "ship_code", "corpus_md5", "raw_baseline", "pin",
           "e2e_t08", "table", "render"} <= kinds, str(sorted(kinds)))
    bad = []
    for r in srows:
        if r["sha256"] == "MISSING":
            bad.append(r["path"])
            continue
        if os.path.isfile(r["path"]) and sha_file(r["path"]) != r["sha256"]:
            bad.append(r["path"])
    check("sources_sha_match", not bad, str(bad[:4]))
    t08_hashed = {os.path.basename(r["path"]) for r in srows if r["kind"] == "t08_script"}
    check("sources_t08_scripts",
          {"extract08.py", "report08.py", "check08.py"} <= t08_hashed, str(sorted(t08_hashed)))
    before = os.path.join(run, "logs", "corpus_inputs_before.md5")
    after = os.path.join(run, "logs", "corpus_inputs_after.md5")
    same = (os.path.isfile(before) and os.path.isfile(after)
            and open(before, "rb").read() == open(after, "rb").read())
    check("corpus_unchanged", same, "%s vs %s" % (before, after))

    # 9. jobs
    head, jb = read_tsv(os.path.join(ev, "jobs.tsv"))
    check("jobs_header", head == ["job_id", "stage", "vessel", "state", "exit_code"], str(head))
    check("jobs_rows", len(jb) > 0, str(len(jb)))
    if a.expect_terminal:
        live = []
        for r in jb:
            state, code = sacct_state(r["job_id"])
            if state not in TERMINAL:
                live.append((r["job_id"], state))
            if r["state"] not in TERMINAL:
                live.append((r["job_id"], "table:" + r["state"]))
        check("jobs_all_terminal", not live, str(live[:5]))
        stages = {r["stage"] for r in jb}
        check("jobs_stages", {"2A", "2B", "report"} <= stages, str(sorted(stages)))
        na = [r["job_id"] for r in jb if r["stage"] in ("NA", "") or r["vessel"] in ("NA", "")]
        check("jobs_no_na", not na, str(na[:5]))
        known = sacct_day_ids(stamp)
        listed = {r["job_id"].split("_")[0] for r in jb}
        missing = sorted((known or set()) - listed)
        check("jobs_complete_vs_sacct", known is not None and not missing,
              "sacct=%s missing=%s" % ("NA" if known is None else len(known), missing[:8]))
        check("jobs_count_vs_sacct", known is not None and len(jb) == len(known),
              "rows=%d sacct=%s" % (len(jb), "NA" if known is None else len(known)))

    # 10. render
    head, rrows = read_tsv(os.path.join(ev, "renders.tsv"))
    check("renders_header", head == ["figure", "path", "scale_bar_mm"], str(head))
    ok_png = (len(rrows) == 1 and rrows[0]["scale_bar_mm"] == "20"
              and rrows[0]["path"] == "renders/Pot_A_to_J_and_Juglet_e2e.png")
    png = os.path.join(ev, "renders", "Pot_A_to_J_and_Juglet_e2e.png")
    ok_png = ok_png and os.path.isfile(png) and os.path.getsize(png) > 50000
    check("renders_png_20mm", ok_png,
          "%s bytes=%s" % (png, os.path.getsize(png) if os.path.isfile(png) else "NA"))

    # 11. t08 vs t05 pin files (byte-for-byte)
    for stem in PIN:
        p = os.path.join(T05, "out", "axes05", stem, "OWN_DEDUP_Axis.xyz")
        check("pin_file:" + stem, os.path.isfile(p) and sha_file(p) == PIN[stem],
              sha_file(p)[:16] if os.path.isfile(p) else "missing")

    # 12. budget: no stray caches inside .scratch on the workstation is checked there
    fails = [r for r in RESULTS if not r[1]]
    out = os.path.join(ev, "check08.txt")
    os.makedirs(ev, exist_ok=True)
    with open(out, "w") as fh:
        for name, ok, detail in RESULTS:
            fh.write("%s\t%s\t%s\n" % ("PASS" if ok else "FAIL", name, detail))
    print("\n%d checks, %d passed, %d failed -> %s"
          % (len(RESULTS), len(RESULTS) - len(fails), len(fails), out))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
