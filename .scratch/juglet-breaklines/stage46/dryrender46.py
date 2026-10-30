#!/usr/bin/env python3
"""Ticket 46 local dry render: reproduce submit46.sh's render + gates, on the laptop.

Nothing is submitted: the point is to catch a template that stopped rendering before a
Spartan job is spent on it.
"""
import os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
TMPL = os.path.join(HERE, "instruments", "submit46.sbatch.tmpl")
BAD = 0


def fail(msg):
    global BAD
    BAD += 1
    print("FAIL " + msg)


RUN = "/data/gpfs/projects/punim2657/SfSpp/runs/20261031-0100_abcdef1_t46-covering"
RUNID = "20261031-0100_abcdef1_t46-covering"
NEW = "abcdef1234567890abcdef1234567890abcdef12"
PHASE = "all"
IXTAG = "abcdef1-t46-covering"
WTIME = "01:30:00"
PARTA = "committed"
JOBNAME = "t46-covering"

tmpl = open(TMPL, "r", encoding="utf-8", newline="").read()
if "\r" in tmpl:
    fail("template has CRLF")
subs = {"__JOBNAME__": JOBNAME, "__RUNDIR__": RUN, "__RUNID__": RUNID,
        "__NEWCOMMIT__": NEW, "__PHASE__": PHASE, "__IXTAG__": IXTAG,
        "__TIME__": WTIME, "__PARTA__": PARTA}
text = tmpl
for k, v in subs.items():
    text = text.replace(k, v)

dst = os.path.join(HERE, "_dry46_submit.sbatch")
open(dst, "w", encoding="utf-8", newline="\n").write(text)
print("rendered -> %s (%d bytes, %d lines)" % (dst, len(text.encode()), text.count("\n")))

left = re.findall(r"__[A-Z][A-Z0-9_]*__", text)
if left:
    fail("unrendered placeholders survived: %s" % sorted(set(left)))
else:
    print("OK   no unrendered placeholder survives")

r = subprocess.run(["bash", "-n", os.path.basename(dst)], cwd=HERE, capture_output=True, text=True)
print("     bash -n rc=%d %s" % (r.returncode, r.stderr.strip()))
if r.returncode:
    fail("rendered script does not parse: %s" % r.stderr.strip())
else:
    print("OK   rendered script parses")

nexp = len(re.findall(r"\$[A-Za-z_][A-Za-z0-9_]*", text))
print("     shell expansions surviving render: %d (submit46.sh requires >= 40)" % nexp)
if nexp < 40:
    fail("only %d expansions survived rendering" % nexp)

if "\r" in text:
    fail("rendered submit.sbatch has CR")
else:
    print("OK   rendered submit.sbatch is LF-only")

code_lines = [l for l in tmpl.split("\n") if not l.lstrip().startswith("#")]
nbrace = sum(l.count("${") for l in code_lines)
print("     brace forms in CODE lines: %d" % nbrace)

for name in ("submit46.sh", "run_cell46.sh", "cover_cloud46.py", "theta_check46.py",
             "run_measure34.py", "figures46.py", "spec46.tsv", "stage_synth_p40.sh"):
    p = os.path.join(HERE, "instruments", name)
    print("     %-20s %s" % (name, "present %d B" % os.path.getsize(p) if os.path.exists(p) else "MISSING"))
    if not os.path.exists(p):
        fail("instrument missing: " + name)

print("\n%d failed check(s)" % BAD)
raise SystemExit(1 if BAD else 0)
