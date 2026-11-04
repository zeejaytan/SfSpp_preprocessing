#!/usr/bin/env python3
"""driver.py - ticket 305: create run dirs on Spartan, stage instruments, submit.

One concrete submit.sbatch per run (parameters baked in, not --export'ed) so a space in a
piece list or an arm spec cannot be eaten by sbatch. Appends the runs/index.tsv row at
submit time with verdict and human_note EMPTY (they belong to a person).

usage:  driver.py mk   <spec.json>        # create + submit everything in the spec
        driver.py sub  <runid> <jobscript>  # submit one already-staged dir
"""
import json, os, subprocess, sys, time

SSH = r"C:\Windows\System32\OpenSSH\ssh.exe"
SCP = r"C:\Windows\System32\OpenSSH\scp.exe"
RUNS = "/data/gpfs/projects/punim2657/SfSpp/runs"
LOCAL = os.path.dirname(os.path.abspath(__file__))


def sh(cmd, **kw):
    return subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True, **kw)


def _retry(fn, tries=4, delay=6):
    last = None
    for k in range(tries):
        r = fn()
        if r.returncode == 0:
            return r
        last = r
        time.sleep(delay * (k + 1))
    return last


def ssh(remote, check=True):
    r = _retry(lambda: sh([SSH, "spartan", remote]))
    if check and r.returncode != 0:
        raise SystemExit("ssh failed rc=%d\n%s\n%s" % (r.returncode, r.stdout, r.stderr))
    return r.stdout.strip()


def scp(files, remote, check=True):
    if not files:
        return None
    r = _retry(lambda: sh([SCP, "-q"] + files + ["spartan:" + remote]))
    if check and r.returncode != 0:
        raise SystemExit("scp failed rc=%d\n%s\n%s" % (r.returncode, r.stdout, r.stderr))
    return r


def bake(template, subs, envs):
    txt = open(template).read()
    for k, v in subs.items():
        txt = txt.replace("__%s__" % k, v)
    lines = txt.splitlines()
    i = next(i for i, ln in enumerate(lines) if ln.startswith("set -uo pipefail"))
    head = lines[:i]
    tail = lines[i:]
    inj = ["", "# ---- baked by driver.py ----"]
    # single quotes: values carry spaces (piece lists, arm specs) and one unquoted
    # 'export PIECES=a b c' silently keeps only 'a' -- measured on run 34352614.
    inj += ["export %s" % (e.split("=", 1)[0] + "='" + e.split("=", 1)[1] + "'") for e in envs]
    return "\n".join(head + inj + tail) + "\n"


def mkrun(runid, template, subs, envs, helpers, extra_files=None, wait=False):
    d = "%s/%s" % (RUNS, runid)
    exists = ssh("test -f %s/submit.sbatch && echo YES || echo NO" % d, check=False)
    if exists.strip().endswith("YES"):
        raise SystemExit("refusing to reuse run dir %s (submit.sbatch already there)" % d)
    ssh("mkdir -p %s/logs %s/out %s/work" % (d, d, d))
    body = bake(os.path.join(LOCAL, template), subs, envs)
    tmp = os.path.join(LOCAL, "_submit_%s.sbatch" % runid)
    open(tmp, "w", newline="\n").write(body)
    # helpers must sit in work/ because the scripts call $RUN/work/*.py
    filelist = [os.path.join(LOCAL, h) for h in helpers] + (extra_files or [])
    if filelist:
        scp(filelist, d + "/work/")
    scp([tmp], d + "/")
    ssh("mv %s/%s %s/submit.sbatch" % (d, os.path.basename(tmp), d))
    os.unlink(tmp)
    out = ssh("cd %s && sbatch --parsable submit.sbatch 2>&1" % d, check=False)
    jobid = out.split(";")[0].strip()
    meta = {"runid": runid, "jobid": jobid, "commit": subs.get("COMMIT", "9c5eec2"),
            "tag": subs.get("TAG", ""), "params": subs, "env": envs,
            "submitted_from": "laptop driver.py", "slurm_submit_out": out}
    mtmp = os.path.join(LOCAL, "_run_%s.json" % runid)
    open(mtmp, "w", newline="\n").write(json.dumps(meta, indent=1) + "\n")
    scp([mtmp], d + "/run.json")
    os.unlink(mtmp)
    if jobid.isdigit():
        row = "%s\t%s\t%s\t%s\t\t\n" % (runid, jobid, subs.get("COMMIT", "9c5eec2"), subs.get("TAG", ""))
        rtmp = os.path.join(LOCAL, "_ix_%s.tsv" % runid)
        open(rtmp, "w", newline="\n").write(row)
        scp([rtmp], d + "/index_row.tsv")
        print(ssh("cat %s/index_row.tsv >> %s/index.tsv && tail -2 %s/index.tsv"
                  % (d, RUNS, RUNS), check=False))
        os.unlink(rtmp)
    print("%-34s job=%-10s %s" % (runid, jobid, out.replace("\n", " ")[:90]))
    return jobid


if __name__ == "__main__":
    spec = json.load(open(sys.argv[2]))
    for r in spec:
        mkrun(r["runid"], r["template"], r["subs"], r["envs"], r["helpers"], r.get("extra_files"), r.get("wait", False))
        time.sleep(8)   # spartan resets the login if connections come too fast
