#!/usr/bin/env python3
"""resubmit307b.py -- re-stage the Stage B assembly runs with LF helper scripts.

The first submission (jobs 34372207..34372378) died in 5 s: arm67.sh arrived with CRLF
line endings ("set: pipefail: invalid option name"), so no arm ever ran. This script
overwrites submit.sbatch in the SAME run dirs, copies the LF copies from
307-stage/helpers/, resubmits, and appends a fresh runs/index.tsv row tagged "<tag>-r2"
(the index is append-only; the first row stays, recording the failed attempt).

usage: resubmit307b.py <spec.json>
"""
import json, os, sys, time, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "driver", os.path.join(HERE, "..", "305-stage", "driver.py"))
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)

RUNS = driver.RUNS
HELPERS = [os.path.join(HERE, "helpers", h) for h in
           ("arm67.sh", "patch_guard67.py", "mk_inc.py", "stage305.py", "acc305.py", "score305.py")]

for r in json.load(open(sys.argv[1])):
    runid = r["runid"]
    d = "%s/%s" % (RUNS, runid)
    body = driver.bake(r["template"], r["subs"], r["envs"])
    tmp = os.path.join(HERE, "_resub_%s.sbatch" % runid)
    open(tmp, "w", newline="\n").write(body)
    driver.scp(HELPERS, d + "/work/")
    driver.scp([tmp], d + "/submit.sbatch")
    os.unlink(tmp)
    out = driver.ssh("cd %s && sbatch --parsable submit.sbatch 2>&1" % d, check=False)
    jobid = out.split(";")[0].strip()
    meta = {"runid": runid, "jobid": jobid, "commit": r["subs"].get("COMMIT", "e6adf69"),
            "tag": r["subs"].get("TAG", ""), "params": r["subs"],
            "resubmitted": "first attempt died on CRLF in arm67.sh; helpers re-copied LF",
            "submitted_from": "307-stage/resubmit307b.py"}
    mtmp = os.path.join(HERE, "_run_%s.json" % runid)
    open(mtmp, "w", newline="\n").write(json.dumps(meta, indent=1) + "\n")
    driver.scp([mtmp], d + "/run.json")
    os.unlink(mtmp)
    if jobid.isdigit():
        row = "%s\t%s\t%s\t%s-r2\t\t\n" % (runid, jobid, meta["commit"], meta["tag"])
        rtmp = os.path.join(HERE, "_ix_%s.tsv" % runid)
        open(rtmp, "w", newline="\n").write(row)
        driver.scp([rtmp], d + "/index_row_r2.tsv")
        driver.ssh("cat %s/index_row_r2.tsv >> %s/index.tsv" % (d, RUNS), check=False)
        os.unlink(rtmp)
    print("%-38s job=%s" % (runid, jobid), flush=True)
    time.sleep(4)
