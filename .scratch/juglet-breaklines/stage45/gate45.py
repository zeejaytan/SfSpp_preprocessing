#!/usr/bin/env python3
"""gate45.py -- the local gates ticket 45 must pass BEFORE anything is submitted.

Run from anywhere:  python .scratch/juglet-breaklines/stage45/gate45.py
Checks the files the job ships (stage45/instruments/) and itself:
  1. no CR byte in any shipped *.sh / *.py / *.tmpl / *.tsv
  2. python -m py_compile on every *.py (shipped and this directory's helpers)
  3. bash -n on run_cell45.sh, submit45.sh, submit45.sbatch.tmpl
  4. the template's placeholders are exactly the eight the renderer substitutes
Exit 0 = all pass.  Any FAIL line is a gate that did not pass.
"""
import os, re, subprocess, sys, glob

HERE = os.path.dirname(os.path.abspath(__file__))
INSTR = os.path.join(HERE, "instruments")
os.chdir(INSTR)
BAD = 0

def fail(msg):
    global BAD
    BAD += 1
    print("FAIL " + msg)

# ---- 1. CR bytes in every file the job ships
targets = sorted(glob.glob("*.sh") + glob.glob("*.py") + glob.glob("*.tmpl") + glob.glob("*.tsv"))
print("== CR census (%d shipped files) ==" % len(targets))
for f in targets:
    b = open(f, "rb").read()
    n = b.count(b"\r")
    print("  %-22s bytes=%7d CR=%d" % (f, len(b), n))
    if n:
        fail("%s has %d CR bytes" % (f, n))

# ---- 2. py_compile: shipped instruments and this stage's own helpers
print("== py_compile ==")
for f in sorted(glob.glob("*.py")):
    r = subprocess.run([sys.executable, "-m", "py_compile", f], capture_output=True, text=True)
    print("  %-22s rc=%d" % (f, r.returncode))
    if r.returncode:
        fail("%s py_compile: %s" % (f, r.stderr.strip()))
for f in sorted(glob.glob(os.path.join(HERE, "*.py"))):
    r = subprocess.run([sys.executable, "-m", "py_compile", f], capture_output=True, text=True)
    print("  %-22s rc=%d (stage45 top)" % (os.path.basename(f), r.returncode))
    if r.returncode:
        fail("%s py_compile: %s" % (os.path.basename(f), r.stderr.strip()))

# ---- 3. bash -n
print("== bash -n ==")
for f in ["run_cell45.sh", "submit45.sh", "submit45.sbatch.tmpl"]:
    r = subprocess.run(["bash", "-n", f], capture_output=True, text=True)
    print("  %-22s rc=%d %s" % (f, r.returncode, r.stderr.strip()))
    if r.returncode:
        fail("%s bash -n: %s" % (f, r.stderr.strip()))

# ---- 4. placeholder census in the template
print("== placeholder census (submit45.sbatch.tmpl) ==")
tmpl = open("submit45.sbatch.tmpl", encoding="utf-8").read()
uniq = sorted(set(re.findall(r"__[A-Z][A-Z0-9_]*__", tmpl)))
print("  found: %s" % uniq)
EXPECT = ["__IXTAG__", "__JOBNAME__", "__NEWCOMMIT__", "__PARTA__", "__PHASE__",
          "__RUNDIR__", "__RUNID__", "__TIME__"]
if uniq != EXPECT:
    fail("template placeholders %s != expected %s" % (uniq, EXPECT))

# ---- 5. the SKIP row must have as many fields as the header (13); it had 14 in stage 44
print("== SKIP row field count vs pipeline_cells.tsv header ==")
cell = open("run_cell45.sh", encoding="utf-8").read()
hdr = re.search(r'printf "pot\\tpiece\\tarm[^"]*"', cell)
nf = re.search(r'printf "((?:%s\\t){2,}%s(?:\\t-)*\\tonly[^"]*)"', cell)
if not hdr or not nf:
    fail("could not locate the pipeline_cells.tsv header or the SKIP printf")
else:
    nh = len(hdr.group(0).replace("%s", "").split("\\t"))
    ns = len(nf.group(1).split("\\t"))
    print("  header fields=%d  SKIP printf fields=%d" % (nh, ns))
    if nh != ns:
        fail("SKIP row has %d fields, header has %d" % (ns, nh))

print("BAD=%d" % BAD)
sys.exit(1 if BAD else 0)
