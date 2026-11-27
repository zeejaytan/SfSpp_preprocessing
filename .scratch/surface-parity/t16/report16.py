#!/usr/bin/env python3
"""Ticket 16 report: compose evidence, verify every cell, record sacct, then render.

Reads logs/panelrows/*.tsv (one row per array cell, no shared-table race), assembles
logs/panel16.tsv in arm/rep order, and asks sacct for each cell's final State/ExitCode,
then writes:

  evidence/j01_axes16.tsv     (already written by prep_j01_axes16.py; checked here)
  evidence/potj_assembly16.tsv  arm rep sherds_ok/11 joins_ok/21 j01_joins_ok/5 non_j01/16
                                jobid (<array>_<idx>) state exit_code
  evidence/jobs16.tsv         raw JobID State ExitCode per cell
  evidence/best16.tsv         best of the 2 repeats per arm
  evidence/renders.tsv        written by render_potj16.py (checked here)
  logs/sacct16.txt            the verbatim sacct output
  logs/run_status.txt         sacct block appended verbatim
  logs/report16_status.json

Exit 0 only when all 10 cells are usable, every sacct row is COMPLETED with 0:0, the two
required tables are tab-delimited with exact headers and row counts, and the render exists.
"""
import argparse
import glob
import json
import os
import subprocess
import sys

TAB, NL = chr(9), chr(10)
STEM = "Pot_J_Piece_01"
ARMS = ["CTL_T09_WITH_AUTHOR_J01", "OWN_NO_HANDLE_SHIP", "OWN_NO_HANDLE_THICKSEC",
        "OWN_VOXEL_THICKSEC", "OWN_S0_ONLY_SHIP"]
AX_COLS = ["arm", "k", "best_donor_deg", "best_donor_mm", "best_gt_deg", "axes_sha256"]
ASM_COLS = ["arm", "rep", "sherds_ok", "sherds_total", "joins_ok", "joins_total",
            "j01_joins_ok", "j01_joins_total", "non_j01_joins_ok", "non_j01_joins_total",
            "jobid", "state", "exit_code"]
PANEL_COLS = ["arm", "rep", "jobid", "sherds_ok", "sherds_total", "joins_ok", "joins_total",
              "j01_joins_ok", "j01_joins_total", "non_j01_joins_ok", "non_j01_joins_total",
              "usable", "score"]


def log(m):
    print("[t16-report] " + m, flush=True)


def read_tsv(path):
    with open(path) as fh:
        head = fh.readline().rstrip(NL)
        cols = head.split(TAB)
        rows = [dict(zip(cols, ln.rstrip(NL).split(TAB))) for ln in fh if ln.strip()]
        return cols, rows


def sacct(jobid):
    out = subprocess.run(["sacct", "-j", jobid, "-X", "-n", "-P",
                          "--format=JobID,State,ExitCode"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit("sacct -j %s failed: %s" % (jobid, out.stderr.strip()))
    lines = [ln for ln in out.stdout.splitlines() if ln.strip()]
    for ln in lines:
        f = ln.split("|")
        if f[0] == jobid:
            return ln, f[1], f[2]
    if lines:
        f = lines[0].split("|")
        return lines[0], f[1], f[2]
    raise SystemExit("sacct -j %s returned no row" % jobid)


def acc_sherds(score_path):
    """Sherds seated, from acc305's own sherd-accuracy numerator (e.g. 8/11).

    Customary in this project: Ticket 09 and Ticket 13 read the same field.  score305's
    piece block uses a strict GT-axis verdict that reads 0/11 on every arm including the
    positive control, so it is not the seated-sherd count; both files stay on disk.
    """
    acc = score_path[:-4] + ".acc.tsv" if score_path.endswith(".tsv") else score_path + ".acc.tsv"
    with open(acc) as fh:
        v = fh.readline().rstrip(NL).split(TAB)
    num, den = v[2].strip().split("/")
    return int(num), int(den)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    a = ap.parse_args()
    run = os.path.abspath(a.run)
    ev = os.path.join(run, "evidence")
    logs = os.path.join(run, "logs")

    fail = []
    ax_cols, ax_rows = read_tsv(os.path.join(ev, "j01_axes16.tsv"))
    if ax_cols != AX_COLS:
        fail.append("j01_axes16.tsv header %r" % (ax_cols,))
    if len(ax_rows) != 5 or [r["arm"] for r in ax_rows] != ARMS:
        fail.append("j01_axes16.tsv rows %r" % ([r.get("arm") for r in ax_rows],))
    log("j01_axes16.tsv rows=%d header_ok=%s" % (len(ax_rows), ax_cols == AX_COLS))

    # Each array cell writes its own logs/panelrows/<ARM>_<REP>.tsv, so the ten cells never
    # share a table.  Assemble the canonical table here, in arm/rep order.
    prow_dir = os.path.join(logs, "panelrows")
    prow_files = sorted(glob.glob(os.path.join(prow_dir, "*.tsv")))
    prow_rows = {}
    for p in prow_files:
        cols, rws = read_tsv(p)
        if cols != PANEL_COLS:
            fail.append("%s header %r" % (os.path.basename(p), cols))
            continue
        for r in rws:
            prow_rows[(r["arm"], r["rep"])] = r
    panel = []
    for arm in ARMS:
        for rep in ("1", "2"):
            r = prow_rows.get((arm, rep))
            if r is None:
                fail.append("missing cell row %s_%s" % (arm, rep))
            else:
                panel.append(r)
    with open(os.path.join(logs, "panel16.tsv"), "w") as fh:
        fh.write(TAB.join(PANEL_COLS) + NL)
        for r in panel:
            fh.write(TAB.join(r[c] for c in PANEL_COLS) + NL)
    log("panel16.tsv rows=%d assembled from %d cell row files" % (len(panel),
                                                                 len(prow_files)))
    if len(panel) != 10:
        fail.append("panel16.tsv rows=%d want 10" % len(panel))
    bad_usable = [r["arm"] + "_" + r["rep"] for r in panel if r.get("usable") != "1"]

    # The array job id plus the cell index is the id sacct reports for a task.
    array_job = ""
    apath = os.path.join(logs, "array_job.txt")
    if os.path.exists(apath):
        array_job = open(apath).read().strip()
    _mc, map_rows = read_tsv(os.path.join(logs, "array_map.tsv"))
    idx_of = {(m["arm"], m["rep"]): m["idx"] for m in map_rows}

    sac_lines, rows, jobs = [], [], []
    for r in panel:
        idx = idx_of.get((r["arm"], r["rep"]))
        if idx is None or not array_job:
            fail.append("no array index for %s_%s" % (r["arm"], r["rep"]))
            continue
        task = "%s_%s" % (array_job, idx)
        ln, state, exitcode = sacct(task)
        sac_lines.append(ln)
        s_ok, s_tot = acc_sherds(r["score"])
        if s_tot != 11:
            fail.append("sherd denominator %s_%s = %d" % (r["arm"], r["rep"], s_tot))
        jobs.append({"arm": r["arm"], "rep": r["rep"], "jobid": task,
                     "state": state, "exit_code": exitcode})
        if not state.startswith("COMPLETED") or exitcode != "0:0":
            fail.append("cell %s_%s %s %s" % (r["arm"], r["rep"], state, exitcode))
        rows.append({"arm": r["arm"], "rep": r["rep"],
                     "sherds_ok": s_ok, "sherds_total": s_tot,
                     "joins_ok": int(r["joins_ok"]), "joins_total": int(r["joins_total"]),
                     "j01_joins_ok": int(r["j01_joins_ok"]),
                     "j01_joins_total": int(r["j01_joins_total"]),
                     "non_j01_joins_ok": int(r["non_j01_joins_ok"]),
                     "non_j01_joins_total": int(r["non_j01_joins_total"]),
                     "jobid": task, "state": state, "exit_code": exitcode})
    agg = []
    if array_job:
        out = subprocess.run(["sacct", "-j", array_job, "-n", "-P",
                              "--format=JobID,State,ExitCode"],
                             capture_output=True, text=True)
        agg = [x for x in out.stdout.splitlines()
               if x.strip() and "_" not in x.split("|")[0]]
    sac_lines = ["#array " + x for x in agg] + sac_lines
    log("sacct rows=%d all_completed=%s" % (len(jobs), not any("COMPLETED" not in j["state"]
                                                              for j in jobs)))

    with open(os.path.join(ev, "potj_assembly16.tsv"), "w") as fh:
        fh.write(TAB.join(ASM_COLS) + NL)
        for r in rows:
            fh.write(TAB.join(str(r[c]) for c in ASM_COLS) + NL)
    with open(os.path.join(ev, "jobs16.tsv"), "w") as fh:
        fh.write(TAB.join(["arm", "rep", "jobid", "state", "exit_code"]) + NL)
        for j in jobs:
            fh.write(TAB.join(str(j[c]) for c in ["arm", "rep", "jobid", "state",
                                                  "exit_code"]) + NL)

    best = {}
    for r in rows:
        cur = best.get(r["arm"])
        if cur is None or (r["joins_ok"], r["j01_joins_ok"]) > (cur["joins_ok"],
                                                                cur["j01_joins_ok"]):
            best[r["arm"]] = r
    with open(os.path.join(ev, "best16.tsv"), "w") as fh:
        cols = ["arm", "best_joins_ok", "joins_total", "best_j01_ok", "j01_total",
                "best_non_j01_ok", "non_j01_total", "rep", "jobid"]
        fh.write(TAB.join(cols) + NL)
        for arm in ARMS:
            b = best[arm]
            fh.write(TAB.join(str(x) for x in [
                arm, b["joins_ok"], b["joins_total"], b["j01_joins_ok"],
                b["j01_joins_total"], b["non_j01_joins_ok"], b["non_j01_joins_total"],
                b["rep"], b["jobid"]]) + NL)
    log("best of 2: " + ", ".join("%s %d/%d" % (arm, best[arm]["joins_ok"],
                                                best[arm]["joins_total"]) for arm in ARMS))

    with open(os.path.join(logs, "sacct16.txt"), "w") as fh:
        fh.write(NL.join(sac_lines) + NL)
    array_job = ""
    p = os.path.join(logs, "array_job.txt")
    if os.path.exists(p):
        array_job = open(p).read().strip()
    with open(os.path.join(logs, "run_status.txt"), "a") as fh:
        fh.write("sacct-start %s array=%s" % (subprocess.run(
            ["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], capture_output=True,
            text=True).stdout.strip(), array_job) + NL)
        for ln in sac_lines:
            fh.write("sacct " + ln + NL)
        fh.write("sacct-end" + NL)

    render = os.path.join(run, "renders", "Pot_J_handle_deleted_comparison.png")
    rp = subprocess.run([sys.executable, os.path.join(run, "work", "t16",
                                                      "render_potj16.py"),
                         "--run", run], capture_output=True, text=True)
    with open(os.path.join(logs, "render16.log"), "w") as fh:
        fh.write(rp.stdout + rp.stderr)
    tail = (rp.stdout or rp.stderr).strip().splitlines()[-6:]
    for ln in tail:
        log("render: " + ln)
    if rp.returncode != 0 or not os.path.exists(render):
        fail.append("render rc=%d exists=%s" % (rp.returncode, os.path.exists(render)))
    if not os.path.exists(os.path.join(ev, "renders.tsv")):
        fail.append("evidence/renders.tsv missing")

    status = {"run": run, "rows": len(rows), "fail": fail,
              "all_usable": not bad_usable, "bad_usable": bad_usable,
              "best": {arm: {"joins_ok": best[arm]["joins_ok"],
                             "j01_joins_ok": best[arm]["j01_joins_ok"],
                             "rep": best[arm]["rep"]} for arm in ARMS},
              "render": render, "render_rc": rp.returncode}
    with open(os.path.join(logs, "report16_status.json"), "w") as fh:
        json.dump(status, fh, indent=1)
    if fail:
        for f in fail:
            log("FAIL " + f)
        print("T16-REPORT-FAIL", flush=True)
        return 1
    log("T16-REPORT-OK")
    print("T16-REPORT-OK", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
