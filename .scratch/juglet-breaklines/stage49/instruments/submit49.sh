#!/bin/bash
# ticket 49 -- submit the scale-free fold-radius run (2 radii x 2 cloud sets x 17 pieces).
#
#   bash submit49.sh <tag> <walltime>
#
# The run is built from the PUSHED commit, never from this checkout: it resolves origin/<branch>,
# renders the sbatch template against that sha, and the job git-archives the commit into its own
# build directory.  Nothing local-only can reach the cluster.
#
# Gates before anything is queued (each one has killed a grid here before):
#   no CR in any *.sh/*.py/*.tmpl/*.tsv (a CR makes bash read "set: pipefail: invalid option name");
#   python -m py_compile on every .py;
#   bash -n on every .sh and on the RENDERED template;
#   no __PLACEHOLDER__ survives rendering, and the render really expanded (NEXP floor).
# If any gate fails nothing is submitted and the exit code says which.
set -euo pipefail

TAG=${1:?usage: submit49.sh <tag> <walltime>}
TIME=${2:?usage: submit49.sh <tag> <walltime>}

PHASE=4
PARTA=committed
# The branch is named, not discovered: the submitter runs on Spartan from a plain directory of the
# commit's instruments (the run is built from origin, never from a checkout), so there is no local
# HEAD to ask.  BRANCH=... overrides it for a re-run of an older head.
BRANCH=${BRANCH:-49-make-the-fold-radius-scale-free}
INSTR=$(cd "$(dirname "$0")" && pwd)
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
ATTIC=/data/gpfs/projects/punim2657/SfSpp/attic/20261031-juglet-vertex-dumps

cd "$INSTR"

# ---- the commit that will be built: origin/<branch>, not whatever is checked out here
git -C "$CANON" fetch --no-tags origin "+refs/heads/*:refs/remotes/origin/*" > /dev/null 2>&1 \
  || { echo "[SUBMIT49] FATAL git fetch in $CANON failed"; exit 2; }
NEW=$(git -C "$CANON" rev-parse "refs/remotes/origin/$BRANCH" 2>/dev/null) \
  || { echo "[SUBMIT49] FATAL no origin/$BRANCH in $CANON"; exit 2; }
LOCAL=$(git -C "$INSTR" rev-parse HEAD 2>/dev/null || echo none)
if [ "$LOCAL" != "none" ] && [ "$LOCAL" != "$NEW" ]; then
  echo "[SUBMIT49] WARN the submitter came from $LOCAL but origin/$BRANCH is $NEW -- the run builds origin"
fi
GIT7=$(printf "%s" "$NEW" | cut -c1-7)
echo "[SUBMIT49] branch $BRANCH commit $NEW (${GIT7})"

# ---- gate 1: no CR anywhere in a committed text instrument
CR_BAD=""
for f in *.sh *.py *.tmpl *.tsv .gitattributes .gitignore; do
  [ -f "$f" ] || continue
  if grep -qU $'\r' "$f" 2>/dev/null; then CR_BAD="$CR_BAD $f"; fi
done
if [ -n "$CR_BAD" ]; then
  echo "[SUBMIT49] FATAL CR (CRLF) in:$CR_BAD"
  echo "[SUBMIT49]        fix with: python -c \"import sys,io;p=sys.argv[1];d=open(p,'rb').read().replace(b'\\r\\n',b'\\n');open(p,'wb').write(d)\" <file>"
  exit 3
fi
echo "[SUBMIT49] CRLF gate: no CR in any *.sh *.py *.tmpl *.tsv"

# ---- gate 2: the instruments this run needs are here
for need in run_cell49.sh stage_synth_p40.sh thetas49.tsv submit49.sbatch.tmpl; do
  [ -f "$need" ] || { echo "[SUBMIT49] FATAL missing instrument $need"; exit 3; }
done
echo "[SUBMIT49] instruments present: run_cell49.sh stage_synth_p40.sh thetas49.tsv submit49.sbatch.tmpl"

# ---- gate 3: python compiles, bash parses
for f in *.py; do
  [ -f "$f" ] || continue
  "$PY" -m py_compile "$f" || { echo "[SUBMIT49] FATAL py_compile $f"; exit 3; }
done
rm -rf __pycache__
for f in *.sh; do
  [ -f "$f" ] || continue
  bash -n "$f" || { echo "[SUBMIT49] FATAL bash -n $f"; exit 3; }
done
echo "[SUBMIT49] py_compile and bash -n clean"

# ---- the run directory
RUNID=$(date +%Y%m%d-%H%M)_"$GIT7"_t49-"$TAG"
RUN=$RUNS/$RUNID
if [ -e "$RUN" ]; then echo "[SUBMIT49] FATAL run dir exists: $RUN"; exit 5; fi
mkdir -p "$RUN/logs" "$RUN/out" "$RUN/instruments" || { echo "[SUBMIT49] FATAL mkdir $RUN"; exit 5; }
echo "[SUBMIT49] run $RUNID -> $RUN"

cp -p ./*.py ./*.sh ./*.tsv "$RUN/instruments/" 2>/dev/null || true
cp -p ./.gitattributes ./.gitignore "$RUN/instruments/" 2>/dev/null || true
cp -p ./submit49.sbatch.tmpl "$RUN/instruments/" || { echo "[SUBMIT49] FATAL copy tmpl"; exit 5; }

# ---- render the template.  A python heredoc, never sed chains: one pass, one substitution table.
JOBNAME="t49-${TAG}"
RUNDIR="$RUN"
IXTAG="t49-${TAG}"
RENDERED=$RUN/submit.sbatch
NEWCOMMIT=$NEW
export JOBNAME RUNDIR RUNID IXTAG RENDERED NEWCOMMIT PHASE PARTA TIME
"$PY" - <<'PYEOF'
import os
p = os.path.join(os.path.dirname(os.path.abspath("submit49.sbatch.tmpl")), "submit49.sbatch.tmpl")
p = os.path.abspath("submit49.sbatch.tmpl")
txt = open(p, "r", encoding="utf-8").read()
table = {
    "__JOBNAME__": os.environ["JOBNAME"],
    "__RUNDIR__": os.environ["RUNDIR"],
    "__RUNID__": os.environ["RUNID"],
    "__NEWCOMMIT__": os.environ["NEWCOMMIT"],
    "__PHASE__": os.environ["PHASE"],
    "__IXTAG__": os.environ["IXTAG"],
    "__TIME__": os.environ["TIME"],
    "__PARTA__": os.environ["PARTA"],
}
n = 0
for k, v in table.items():
    n += txt.count(k)
    txt = txt.replace(k, v)
out = os.environ["RENDERED"]
open(out, "w", encoding="utf-8", newline="\n").write(txt)
print("[SUBMIT49] rendered %s: %d bytes, %d line(s), %d substitution(s)" % (out, len(txt), txt.count("\n"), n))
PYEOF

# ---- gate 4: the render really happened
if grep -qE '__[A-Z][A-Z]*__' "$RENDERED"; then
  echo "[SUBMIT49] FATAL a placeholder survived rendering:"
  grep -nE '__[A-Z][A-Z]*__' "$RENDERED"
  exit 6
fi
NEXP=$(grep -o '\$[A-Za-z_][A-Za-z0-9_]*' "$RENDERED" | wc -l)
NLINES=$(wc -l < "$RENDERED" | tr -d " ")
echo "[SUBMIT49] render gate: 0 placeholders left, $NEXP shell expansion(s), $NLINES line(s)"
if [ "$NEXP" -lt 40 ]; then echo "[SUBMIT49] FATAL only $NEXP expansions -- the template did not render"; exit 6; fi
if grep -qU $'\r' "$RENDERED"; then echo "[SUBMIT49] FATAL the rendered template has a CR"; exit 6; fi
bash -n "$RENDERED" || { echo "[SUBMIT49] FATAL bash -n on the rendered template"; exit 6; }
echo "[SUBMIT49] rendered template parses (bash -n) and carries no CR"

# ---- run.json: what was asked for, before anything is known about the answer
"$PY" - <<PYEOF
import json, os
meta = {
    "runid": "$RUNID",
    "ticket": "49-make-the-fold-radius-scale-free",
    "tag": "$TAG",
    "commit": "$NEW",
    "commit7": "$GIT7",
    "branch": "$BRANCH",
    "jobid": None,
    "walltime": "$TIME",
    "partition": "sapphire",
    "account": "punim2657",
    "submitted_from": "$INSTR",
    "run_dir": "$RUN",
    "canon": "$CANON",
    "attic": "$ATTIC",
    "patch_radii_mm": [1.0, 1.5],
    "cloud_sets": ["corpus", "attic"],
    "cells_planned": 51,
    "env": {"SFS_GROWTH_FORMULA": "1", "SFS_PATCH_R_MM": "per cell (1.0 or 1.5)"},
    "verdict": "",
    "note": "verdict and human_note are written by the coordinating session, never by this job",
}
open(os.path.join("$RUN", "run.json"), "w").write(json.dumps(meta, indent=2) + "\n")
print("[SUBMIT49] wrote $RUN/run.json")
PYEOF

# ---- submit
cd "$RUN"
JOBID=$(sbatch --parsable submit.sbatch) || { echo "[SUBMIT49] FATAL sbatch failed"; exit 7; }
JOBID=$(printf "%s" "$JOBID" | cut -d";" -f1 | tr -d "[:space:]")
case "$JOBID" in
  ""|*[!0-9]*) echo "[SUBMIT49] FATAL sbatch did not return a numeric job id: '$JOBID'"; exit 7 ;;
esac
printf "%s\n" "$JOBID" > "$RUN/logs/jobid.txt"
echo "[SUBMIT49] submitted job $JOBID"
echo "[SUBMIT49] run dir $RUN"
echo "[SUBMIT49] poll: squeue -j $JOBID ; then sacct -j $JOBID -o JobID,State,ExitCode,Elapsed -P"
echo "$JOBID"
