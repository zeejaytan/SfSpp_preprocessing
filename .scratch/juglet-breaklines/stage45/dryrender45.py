#!/usr/bin/env python3
"""Ticket 45 local dry render: reproduce submit45.sh's render + gates."""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TMPL = os.path.join(HERE, "submit45.sbatch.tmpl")
BAD = 0

def fail(msg):
    global BAD
    BAD += 1
    print("FAIL " + msg)

RUN = "/data/gpfs/projects/punim2657/SfSpp/runs/20261030-2200_abcdef1_t45-default"
RUNID = "20261030-2200_abcdef1_t45-default"
NEW = "abcdef1234567890abcdef1234567890abcdef12"
PHASE = "4"
IXTAG = "abcdef1-t45-default"
WTIME = "08:00:00"
PARTA = "committed"
JOBNAME = "t45-default"

tmpl = open(TMPL, "r", encoding="utf-8", newline="").read()
if "\r" in tmpl:
    fail("template has CRLF")
subs = {"__JOBNAME__": JOBNAME, "__RUNDIR__": RUN, "__RUNID__": RUNID,
        "__NEWCOMMIT__": NEW, "__PHASE__": PHASE, "__IXTAG__": IXTAG,
        "__TIME__": WTIME, "__PARTA__": PARTA}
text = tmpl
for k, v in subs.items():
    text = text.replace(k, v)

dst = os.path.join(HERE, "_dry45_submit.sbatch")
open(dst, "w", encoding="utf-8", newline="\n").write(text)
print("rendered -> %s (%d bytes, %d lines)" % (dst, len(text.encode()), text.count("\n")))

left = re.findall(r"__[A-Z][A-Z0-9_]*__", text)
if left:
    fail("unrendered placeholders survived: %s" % sorted(set(left)))
else:
    print("OK   no unrendered placeholder survives")

r = subprocess.run(["bash", "-n", "_dry45_submit.sbatch"], cwd=HERE, capture_output=True, text=True)
print("     bash -n rc=%d %s" % (r.returncode, r.stderr.strip()))
if r.returncode:
    fail("rendered script does not parse: %s" % r.stderr.strip())
else:
    print("OK   rendered script parses")

nexp = len(re.findall(r"\$[A-Za-z_][A-Za-z0-9_]*", text))
print("     shell expansions surviving render: %d (submit45.sh requires >= 40)" % nexp)
if nexp < 40:
    fail("only %d expansions survived rendering" % nexp)

if "\r" in text:
    fail("rendered submit.sbatch has CR")
else:
    print("OK   rendered submit.sbatch is LF-only")

code_lines = [l for l in tmpl.split("\n") if not l.lstrip().startswith("#")]
nbrace = sum(l.count("${") for l in code_lines)
print("     brace forms in CODE lines: %d (template documents using none)" % nbrace)
if nbrace:
    fail("template code contains %d brace forms" % nbrace)

bad_brace = [l for l in code_lines if "{" in l and "${" not in l]
print("     code lines with a bare { that is not brace-expansion: %d" % len(bad_brace))

tmpl_ph = re.findall(r"__[A-Z][A-Z0-9_]*__", tmpl)
print("     template placeholder occurrences: %d over %d distinct" % (len(tmpl_ph), len(set(tmpl_ph))))

# byte-for-byte: reversing the substitution must give the template back
# a whole-text reversal is meaningless here (PHASE renders to the one character "4"), so the
# check is line-wise: a line may only change if it carried a placeholder.
tl = tmpl.split("\n")
rl = text.split("\n")
if len(tl) != len(rl):
    fail("render changed the line count (%d -> %d)" % (len(tl), len(rl)))
else:
    stray = [i + 1 for i in range(len(tl))
             if tl[i] != rl[i] and not re.search(r"__[A-Z][A-Z0-9_]*__", tl[i])]
    print("     lines changed by the render: %d, of which without a placeholder: %d"
          % (sum(1 for i in range(len(tl)) if tl[i] != rl[i]), len(stray)))
    if stray:
        fail("lines changed with no placeholder on them: %s" % stray[:10])

os.remove(dst)
print("BAD=%d" % BAD)
sys.exit(1 if BAD else 0)