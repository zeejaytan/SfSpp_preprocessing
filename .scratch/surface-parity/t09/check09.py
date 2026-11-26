#!/usr/bin/env python3
"""Ticket 09 independent check: re-read the evidence and assert the ticket's invariants.

Exit 0 only if every named check passes; exit 2 otherwise.  With --expect-terminal it also
requires every t09-* job in evidence/jobs.tsv to be in a terminal sacct state (the ticket's
"poll every job to terminal" rule).  Writes evidence/check09.txt either way.
"""
import argparse
import glob
import json
import os
import sys

TERMINAL = {"COMPLETED", "FAILED", "CANCELLED", "TIMEOUT", "NODE_FAIL",
            "PREEMPTED", "OUT_OF_MEMORY", "BOOT_FAIL", "DEADLINE"}
POTS = list("ABCDEFGHIJ")


def read_tsv(path):
    if not os.path.isfile(path):
        return None, []
    with open(path) as fh:
        lines = [ln.rstrip("\n") for ln in fh if ln.strip()]
    if not lines:
        return None, []
    head = lines[0].split("\t")
    return head, [dict(zip(head, ln.split("\t"))) for ln in lines[1:]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--manifest", default="")
    ap.add_argument("--expect-terminal", action="store_true")
    a = ap.parse_args()
    run = a.run
    ev = os.path.join(run, "evidence")
    man = a.manifest or os.path.join(run, "manifest", "own_surfaces.json")
    lines = []
    bad = []

    def check(name, ok, detail):
        lines.append("%s %s: %s" % ("PASS" if ok else "FAIL", name, detail))
        if not ok:
            bad.append(name)

    head, rows = read_tsv(os.path.join(ev, "dedupe27.tsv"))
    check("dedupe27_header", head == ["stem", "pot", "face", "mode", "in_rows",
                                      "out_rows", "improved_rows", "dups_skipped",
                                      "appended", "normal_maxdiff"], str(head))
    check("dedupe27_rows", len(rows) == 314, "%d rows" % len(rows))
    off = [r for r in rows if r.get("mode") == "off"]
    same = [r for r in rows if r.get("in_rows") == r.get("out_rows")]
    md = [float(r.get("normal_maxdiff") or "nan") for r in rows]
    check("dedupe27_mode_off", len(off) == len(rows) == 314, "%d/%d off"
          % (len(off), len(rows)))
    check("dedupe27_in_eq_out", len(same) == len(rows) == 314, "%d/%d in==out"
          % (len(same), len(rows)))
    check("dedupe27_normal_maxdiff", all(0.0 <= x <= 1e-6 for x in md),
          "max=%.3g" % max(md) if md else "no rows")

    head, w = read_tsv(os.path.join(ev, "walls.tsv"))
    check("walls_rows", len(w) == 314, "%d rows" % len(w))
    dup = [r for r in w if r.get("duplicate_xyz") != "0"]
    check("zero_dup_all_314", not dup, "%d walls with duplicate_xyz!=0" % len(dup))
    no_bl = [r for r in w if int(r.get("bl_points") or 0) <= 0]
    check("every_wall_has_breaklines", not no_bl, "%d walls with bl_points==0"
          % len(no_bl))

    head, ax = read_tsv(os.path.join(ev, "axes.tsv"))
    check("axes_rows", len(ax) == 157, "%d rows" % len(ax))
    gt = [r for r in ax if r.get("in_141_gt") == "1"]
    check("axes_141_gt", len(gt) == 141, "%d GT rows" % len(gt))
    exc = sorted(r["stem"] for r in ax if r.get("excluded_by_paper") == "1")
    want = ["Pot_F_Piece_07", "Pot_I_Piece_28", "Pot_I_Piece_29",
            "Pot_I_Piece_30", "Pot_J_Piece_12"]
    check("paper_excluded_5", exc == want, ",".join(exc))
    bases = sorted(r["stem"] for r in ax if r.get("is_base_t09") == "1"
                   and r["stem"].startswith("Juglet"))
    check("juglet_single_base", bases == ["Juglet_Piece_7"], ",".join(bases) or "none")
    p1 = [r for r in ax if r["stem"] == "Juglet_Piece_1"]
    p1pos = 0.0
    try:
        man_obj = json.load(open(man))
        with open(os.path.join(man_obj["axes_juglet_def3x_regen"],
                               "Juglet_Piece_1_Axis.xyz")) as fh:
            p1pos = max(abs(float(x)) for x in fh.readline().split()[:3])
    except (OSError, ValueError, KeyError):
        p1pos = 0.0
    check("juglet_piece1_native_3x", 300.0 < p1pos < 1000.0,
          "|pos|=%.1f tree units (native 3x; /3 would be %.1f mm)"
          % (p1pos, p1pos / 3.0))

    head, fx = read_tsv(os.path.join(ev, "fixtures.tsv"))
    names = [r.get("fixture") for r in fx]
    check("fixtures_four", names == ["zero_dup_all_314", "dedupe27_in_eq_out",
                                     "juglet_native_3x_guard", "manifest_schema_valid"],
          ",".join(str(n) for n in names))
    fails = [r["fixture"] for r in fx if r.get("status") != "PASS"]
    check("fixtures_all_pass", not fails, ",".join(fails) or "4 PASS")

    head, pe = read_tsv(os.path.join(ev, "pots_e2e.tsv"))
    check("pots_e2e_40_rows", len(pe) == 40, "%d rows" % len(pe))
    labs = set(r.get("arm") for r in pe)
    check("pots_e2e_arms", labs == set("%s_%s" % (p, s) for p in POTS
                                       for s in ("MOR1", "MOR2", "K3R1", "K3R2")),
          "%d distinct arms" % len(labs))
    # wall_secs must be the arm's own wall_s from that run's logs/panel.tsv.
    runs_base = os.path.dirname(os.path.abspath(run))
    wall_bad = []
    wall_n = 0
    for P in POTS:
        cands = sorted(glob.glob(os.path.join(runs_base, "*_t09-pot" + P)))
        panel = os.path.join(cands[-1], "logs", "panel.tsv") if cands else ""
        want = {}
        if panel and os.path.isfile(panel):
            with open(panel) as fh:
                hd = fh.readline().rstrip("\n").split("\t")
                if "arm" in hd and "wall_s" in hd:
                    ai, wi = hd.index("arm"), hd.index("wall_s")
                    for ln in fh:
                        c = ln.rstrip("\n").split("\t")
                        if len(c) > max(ai, wi):
                            try:
                                want[c[ai]] = float(c[wi])
                            except ValueError:
                                pass
        for r in pe:
            if r.get("pot") != P:
                continue
            arm = r.get("arm") or ""
            wall_n += 1
            try:
                got = float(r.get("wall_secs"))
            except (TypeError, ValueError):
                wall_bad.append("%s: %s" % (arm, r.get("wall_secs")))
                continue
            if arm in want:
                if abs(got - want[arm]) > 0.6:
                    wall_bad.append("%s: %s vs panel %s" % (arm, got, want[arm]))
            elif got <= 0:
                wall_bad.append("%s: %s" % (arm, got))
    check("pots_wall_secs_vs_panel", wall_n == 40 and not wall_bad,
          "%d/%d match panel.tsv; %s" % (wall_n - len(wall_bad), wall_n,
                                         ",".join(wall_bad[:3]) or "all match"))
    head, je = read_tsv(os.path.join(ev, "juglet_e2e.tsv"))
    check("juglet_e2e_4_rows", len(je) == 4, "%d rows" % len(je))
    head, cv = read_tsv(os.path.join(ev, "comparison_vs_t08.tsv"))
    check("comparison_11_rows", len(cv) == 11, "%d rows" % len(cv))
    check("comparison_vessels", sorted(r.get("vessel") for r in cv)
          == sorted(POTS + ["JUGLET"]), ",".join(r.get("vessel") or "?" for r in cv))

    head, rd = read_tsv(os.path.join(ev, "renders.tsv"))
    png = os.path.join(ev, "renders", "Pot_A_to_J_and_Juglet_t09_regen.png")
    check("render_present", os.path.isfile(png) and os.path.getsize(png) > 100000,
          "%d bytes" % (os.path.getsize(png) if os.path.isfile(png) else 0))
    check("render_scale_bar_20", bool(rd) and rd[0].get("scale_bar_mm") == "20",
          rd[0].get("scale_bar_mm") if rd else "no row")

    head, src = read_tsv(os.path.join(ev, "sources.tsv"))
    kinds = {}
    for r in src:
        kinds.setdefault(r.get("kind"), []).append(r)
    names = sorted(os.path.basename(r["path"]) for r in kinds.get("t09_script", []))
    check("sources_seven_scripts", names == sorted([
        "build09.sbatch", "regen09.sbatch", "extract09.py", "extract09.sbatch",
        "launch_e2e09.sh", "report09.py", "check09.py"]), ",".join(names))
    check("sources_ship_code", len(kinds.get("ship_code", [])) == 3,
          "%d frozen SHIP files" % len(kinds.get("ship_code", [])))
    check("sources_unit_test", len(kinds.get("unit_test", [])) == 1,
          ",".join(os.path.basename(r["path"]) for r in kinds.get("unit_test", [])))
    cb = [r for r in kinds.get("corpus_before", [])
          if "identical to after: yes" in r.get("detail", "")]
    check("sources_corpus_identical", len(cb) == 1,
          cb[0].get("detail", "") if cb else "not proven")
    head, jb = read_tsv(os.path.join(ev, "jobs.tsv"))
    task_rows = [r for r in jb if "_" in (r.get("job_id") or "")]
    parents = set(r["job_id"].split("_")[0] for r in task_rows)
    check("jobs_array_tasks_expanded",
          set(("35713969", "35714095", "35717310")) <= parents,
          "%d task rows over %d array parents" % (len(task_rows), len(parents)))
    failed = [r["job_id"] for r in jb if r.get("state") == "FAILED"]
    check("jobs_failed_tasks_recorded",
          all(("35713969_" + t) in failed for t in ("5", "8", "9")),
          "FAILED rows: " + ",".join(failed[:8]))
    miss = [r["path"] for r in src if r.get("sha256") == "MISSING"]
    check("sources_no_missing", not miss, "%d missing %s" % (len(miss), miss[:3]))

    if os.path.isfile(man):
        d = json.load(open(man))
        check("manifest_pieces_157", int(d.get("total_pieces", -1)) == 157
              and sum(int(v.get("pieces", 0)) for v in d.get("vessels", {}).values()) == 157,
              "%s / %s" % (d.get("total_pieces"),
                           sum(int(v.get("pieces", 0))
                               for v in d.get("vessels", {}).values())))
        check("manifest_commit", str(d.get("preprocessing_commit")) ==
              "a50f8cc0ebe17621e2ce32424808c7414c2d7bbf",
              str(d.get("preprocessing_commit")))
        root = str(d.get("run_root", ""))
        paths = [d.get("axes_own_regen", ""), d.get("axes_juglet_def3x_regen", "")]
        paths += [v.get("geom_dir", "") for v in d.get("vessels", {}).values()]
        check("manifest_paths_under_run", all(p.startswith(root) and
                                              "_t09-own-surfaces" in p for p in paths),
              "%d paths" % len(paths))
    else:
        check("manifest_present", False, "missing " + man)

    head, jb = read_tsv(os.path.join(ev, "jobs.tsv"))
    check("jobs_present", len(jb) >= 3, "%d rows" % len(jb))
    nonterm = [(r.get("job_id"), r.get("state")) for r in jb
               if r.get("state") not in TERMINAL]
    if a.expect_terminal:
        check("jobs_all_terminal", not nonterm, str(nonterm[:6]))
        bad_state = [(r.get("job_id"), r.get("state"), r.get("exit_code"))
                     for r in jb if r.get("state") == "COMPLETED"
                     and str(r.get("exit_code")) not in ("0:0", "0:0:")]
        check("jobs_completed_exit_zero", not bad_state, str(bad_state[:6]))

    out = "\n".join(lines) + "\n"
    os.makedirs(ev, exist_ok=True)
    with open(os.path.join(ev, "check09.txt"), "w") as fh:
        fh.write(out)
    sys.stdout.write(out)
    sys.stdout.write("check09: %d checks, %d failed%s\n"
                     % (len(lines), len(bad), (" -> " + ",".join(bad)) if bad else ""))
    return 2 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
